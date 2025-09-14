"""
Code execution service for running Python code in a sandboxed environment.
"""
import asyncio
import json
import tempfile
import os
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import subprocess
import docker
from docker.errors import DockerException, ContainerError, ImageNotFound
import logging

from ..config.code_execution import code_execution_settings

logger = logging.getLogger(__name__)


class CodeExecutionError(Exception):
    """Custom exception for code execution errors."""
    pass


class CodeExecutionService:
    """Service for executing Python code in Docker containers."""
    
    def __init__(self):
        self.docker_client = None
        self.settings = code_execution_settings
        self.image_name = self.settings.docker_image
        self.container_timeout = self.settings.container_timeout
        self.memory_limit = self.settings.memory_limit
        self.cpu_limit = self.settings.cpu_limit
        
    async def initialize(self):
        """Initialize Docker client and pull required image."""
        try:
            self.docker_client = docker.from_env()
            # Check if image exists, pull if not
            try:
                self.docker_client.images.get(self.image_name)
            except ImageNotFound:
                logger.info(f"Pulling Docker image: {self.image_name}")
                self.docker_client.images.pull(self.image_name)
        except DockerException as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise CodeExecutionError(f"Docker initialization failed: {e}")
    
    async def execute_code(
        self,
        code: str,
        input_data: Optional[str] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute Python code in a Docker container.
        
        Args:
            code: Python code to execute
            input_data: Optional input data for the code
            timeout: Execution timeout in seconds
            
        Returns:
            Dict containing execution results
        """
        if not self.docker_client:
            await self.initialize()
            
        execution_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Create temporary files for code and input
            with tempfile.TemporaryDirectory() as temp_dir:
                code_file = os.path.join(temp_dir, "code.py")
                input_file = os.path.join(temp_dir, "input.txt")
                
                # Write code to file
                with open(code_file, "w", encoding="utf-8") as f:
                    f.write(code)
                
                # Write input data if provided
                if input_data:
                    with open(input_file, "w", encoding="utf-8") as f:
                        f.write(input_data)
                
                # Prepare Docker command
                cmd = ["python", "/app/code.py"]
                if input_data:
                    cmd = ["sh", "-c", "python /app/code.py < /app/input.txt"]
                
                # Prepare volumes
                volumes = {code_file: {"bind": "/app/code.py", "mode": "ro"}}
                if input_data:
                    volumes[input_file] = {"bind": "/app/input.txt", "mode": "ro"}
                
                # Create and run container with security settings
                container = self.docker_client.containers.run(
                    self.image_name,
                    command=cmd,
                    volumes=volumes,
                    mem_limit=self.memory_limit,
                    cpu_period=100000,
                    cpu_quota=int(float(self.cpu_limit) * 100000),
                    network_disabled=self.settings.network_disabled,
                    read_only=self.settings.read_only_filesystem,
                    security_opt=["no-new-privileges:true"] if self.settings.no_new_privileges else None,
                    remove=True,
                    detach=True,
                    stdout=True,
                    stderr=True,
                    user="nobody"  # Run as non-root user
                )
                
                # Wait for container to finish with timeout
                try:
                    result = container.wait(timeout=timeout)
                    logs = container.logs(stdout=True, stderr=True).decode("utf-8")
                    
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    return {
                        "execution_id": execution_id,
                        "success": result["StatusCode"] == 0,
                        "output": logs,
                        "error": None if result["StatusCode"] == 0 else logs,
                        "execution_time": int(execution_time),
                        "exit_code": result["StatusCode"]
                    }
                    
                except asyncio.TimeoutError:
                    container.kill()
                    return {
                        "execution_id": execution_id,
                        "success": False,
                        "output": "",
                        "error": f"Code execution timed out after {timeout} seconds",
                        "execution_time": timeout * 1000,
                        "exit_code": -1
                    }
                    
        except ContainerError as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return {
                "execution_id": execution_id,
                "success": False,
                "output": "",
                "error": f"Container error: {e.stderr.decode('utf-8') if e.stderr else str(e)}",
                "execution_time": int(execution_time),
                "exit_code": e.exit_status
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Code execution failed: {e}")
            return {
                "execution_id": execution_id,
                "success": False,
                "output": "",
                "error": f"Execution failed: {str(e)}",
                "execution_time": int(execution_time),
                "exit_code": -1
            }
    
    async def validate_exercise_solution(
        self,
        exercise_id: str,
        submitted_code: str,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate exercise solution against test cases.
        
        Args:
            exercise_id: Exercise identifier
            submitted_code: User's submitted code
            test_cases: List of test cases with input/expected output
            
        Returns:
            Dict containing validation results
        """
        validation_results = {
            "exercise_id": exercise_id,
            "total_tests": len(test_cases),
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": [],
            "overall_success": False,
            "total_execution_time": 0,
            "score": 0
        }
        
        for i, test_case in enumerate(test_cases):
            test_input = test_case.get("input_data", "")
            expected_output = test_case["expected_output"].strip()
            
            # Execute code with test input
            execution_result = await self.execute_code(
                submitted_code,
                test_input,
                timeout=10  # Shorter timeout for test cases
            )
            
            validation_results["total_execution_time"] += execution_result["execution_time"]
            
            # Compare output
            actual_output = execution_result["output"].strip()
            test_passed = (
                execution_result["success"] and 
                actual_output == expected_output
            )
            
            test_result = {
                "test_case_id": i + 1,
                "passed": test_passed,
                "input": test_input if not test_case.get("is_hidden", False) else "[Hidden]",
                "expected_output": expected_output if not test_case.get("is_hidden", False) else "[Hidden]",
                "actual_output": actual_output,
                "execution_time": execution_result["execution_time"],
                "error": execution_result.get("error")
            }
            
            validation_results["test_results"].append(test_result)
            
            if test_passed:
                validation_results["passed_tests"] += 1
            else:
                validation_results["failed_tests"] += 1
        
        # Calculate overall success and score
        validation_results["overall_success"] = validation_results["failed_tests"] == 0
        validation_results["score"] = int(
            (validation_results["passed_tests"] / validation_results["total_tests"]) * 100
        )
        
        return validation_results
    
    async def compare_with_solution(
        self,
        submitted_code: str,
        solution_code: str,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare submitted code with reference solution.
        
        Args:
            submitted_code: User's submitted code
            solution_code: Reference solution code
            test_cases: Test cases to run both solutions against
            
        Returns:
            Dict containing comparison results
        """
        # Run both solutions against test cases
        submitted_results = await self.validate_exercise_solution(
            "comparison", submitted_code, test_cases
        )
        solution_results = await self.validate_exercise_solution(
            "solution", solution_code, test_cases
        )
        
        return {
            "submitted_solution": submitted_results,
            "reference_solution": solution_results,
            "matches_reference": (
                submitted_results["overall_success"] and 
                solution_results["overall_success"] and
                submitted_results["score"] == solution_results["score"]
            )
        }
    
    def cleanup(self):
        """Clean up Docker resources."""
        if self.docker_client:
            try:
                # Remove any dangling containers
                containers = self.docker_client.containers.list(
                    all=True,
                    filters={"status": "exited"}
                )
                for container in containers:
                    if container.image.tags and self.image_name in container.image.tags:
                        container.remove()
            except Exception as e:
                logger.warning(f"Failed to cleanup containers: {e}")


# Global instance
code_execution_service = CodeExecutionService()