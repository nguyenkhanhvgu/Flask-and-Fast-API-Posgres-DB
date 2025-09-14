"""
Tests for code execution service.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from docker.errors import DockerException, ContainerError

from app.services.code_execution import CodeExecutionService, CodeExecutionError


class TestCodeExecutionService:
    """Test cases for CodeExecutionService."""
    
    @pytest.fixture
    def service(self):
        """Create a CodeExecutionService instance for testing."""
        return CodeExecutionService()
    
    @pytest.fixture
    def mock_docker_client(self):
        """Mock Docker client for testing."""
        mock_client = Mock()
        mock_container = Mock()
        mock_container.wait.return_value = {"StatusCode": 0}
        mock_container.logs.return_value = b"Hello, World!\n"
        mock_client.containers.run.return_value = mock_container
        return mock_client
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, service):
        """Test successful Docker client initialization."""
        with patch('docker.from_env') as mock_docker:
            mock_client = Mock()
            mock_client.images.get.return_value = Mock()  # Image exists
            mock_docker.return_value = mock_client
            
            await service.initialize()
            
            assert service.docker_client == mock_client
            mock_docker.assert_called_once()
            mock_client.images.get.assert_called_once_with(service.image_name)
    
    @pytest.mark.asyncio
    async def test_initialize_pull_image(self, service):
        """Test Docker client initialization with image pull."""
        with patch('docker.from_env') as mock_docker:
            mock_client = Mock()
            mock_client.images.get.side_effect = Exception("Image not found")
            mock_client.images.pull.return_value = Mock()
            mock_docker.return_value = mock_client
            
            await service.initialize()
            
            assert service.docker_client == mock_client
            mock_client.images.pull.assert_called_once_with(service.image_name)
    
    @pytest.mark.asyncio
    async def test_initialize_docker_error(self, service):
        """Test Docker client initialization failure."""
        with patch('docker.from_env') as mock_docker:
            mock_docker.side_effect = DockerException("Docker not available")
            
            with pytest.raises(CodeExecutionError, match="Docker initialization failed"):
                await service.initialize()
    
    @pytest.mark.asyncio
    async def test_execute_code_success(self, service, mock_docker_client):
        """Test successful code execution."""
        service.docker_client = mock_docker_client
        
        code = "print('Hello, World!')"
        result = await service.execute_code(code)
        
        assert result["success"] is True
        assert "Hello, World!" in result["output"]
        assert result["error"] is None
        assert result["exit_code"] == 0
        assert "execution_id" in result
        assert result["execution_time"] > 0
    
    @pytest.mark.asyncio
    async def test_execute_code_with_input(self, service, mock_docker_client):
        """Test code execution with input data."""
        service.docker_client = mock_docker_client
        
        code = "name = input('Enter name: '); print(f'Hello, {name}!')"
        input_data = "Alice"
        
        result = await service.execute_code(code, input_data)
        
        assert result["success"] is True
        mock_docker_client.containers.run.assert_called_once()
        call_args = mock_docker_client.containers.run.call_args
        assert "sh" in call_args[1]["command"]  # Should use shell command for input
    
    @pytest.mark.asyncio
    async def test_execute_code_timeout(self, service):
        """Test code execution timeout."""
        mock_client = Mock()
        mock_container = Mock()
        mock_container.wait.side_effect = asyncio.TimeoutError()
        mock_client.containers.run.return_value = mock_container
        service.docker_client = mock_client
        
        code = "import time; time.sleep(60)"
        result = await service.execute_code(code, timeout=1)
        
        assert result["success"] is False
        assert "timed out" in result["error"]
        assert result["exit_code"] == -1
        mock_container.kill.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_code_container_error(self, service):
        """Test code execution with container error."""
        mock_client = Mock()
        mock_client.containers.run.side_effect = ContainerError(
            container=Mock(),
            exit_status=1,
            command="python",
            image="python:3.11-slim",
            stderr=b"SyntaxError: invalid syntax"
        )
        service.docker_client = mock_client
        
        code = "print('Hello World'"  # Missing closing parenthesis
        result = await service.execute_code(code)
        
        assert result["success"] is False
        assert "Container error" in result["error"]
        assert result["exit_code"] == 1
    
    @pytest.mark.asyncio
    async def test_validate_exercise_solution_all_pass(self, service, mock_docker_client):
        """Test exercise validation with all test cases passing."""
        service.docker_client = mock_docker_client
        
        # Mock successful execution for all test cases
        mock_container = mock_docker_client.containers.run.return_value
        mock_container.wait.return_value = {"StatusCode": 0}
        mock_container.logs.return_value = b"5\n"  # Expected output
        
        code = "print(2 + 3)"
        test_cases = [
            {"input_data": "", "expected_output": "5", "is_hidden": False},
            {"input_data": "", "expected_output": "5", "is_hidden": True}
        ]
        
        result = await service.validate_exercise_solution("test_exercise", code, test_cases)
        
        assert result["overall_success"] is True
        assert result["total_tests"] == 2
        assert result["passed_tests"] == 2
        assert result["failed_tests"] == 0
        assert result["score"] == 100
        assert len(result["test_results"]) == 2
    
    @pytest.mark.asyncio
    async def test_validate_exercise_solution_partial_pass(self, service):
        """Test exercise validation with some test cases failing."""
        mock_client = Mock()
        mock_container = Mock()
        
        # First test passes, second fails
        mock_container.wait.side_effect = [
            {"StatusCode": 0},  # First test passes
            {"StatusCode": 0}   # Second test passes but output differs
        ]
        mock_container.logs.side_effect = [
            b"5\n",   # Correct output
            b"6\n"    # Incorrect output
        ]
        mock_client.containers.run.return_value = mock_container
        service.docker_client = mock_client
        
        code = "print(2 + 3)"
        test_cases = [
            {"input_data": "", "expected_output": "5", "is_hidden": False},
            {"input_data": "", "expected_output": "5", "is_hidden": False}
        ]
        
        result = await service.validate_exercise_solution("test_exercise", code, test_cases)
        
        assert result["overall_success"] is False
        assert result["total_tests"] == 2
        assert result["passed_tests"] == 1
        assert result["failed_tests"] == 1
        assert result["score"] == 50
    
    @pytest.mark.asyncio
    async def test_compare_with_solution(self, service, mock_docker_client):
        """Test solution comparison functionality."""
        service.docker_client = mock_docker_client
        
        # Mock successful execution for both solutions
        mock_container = mock_docker_client.containers.run.return_value
        mock_container.wait.return_value = {"StatusCode": 0}
        mock_container.logs.return_value = b"5\n"
        
        submitted_code = "print(2 + 3)"
        solution_code = "result = 2 + 3; print(result)"
        test_cases = [
            {"input_data": "", "expected_output": "5", "is_hidden": False}
        ]
        
        result = await service.compare_with_solution(submitted_code, solution_code, test_cases)
        
        assert "submitted_solution" in result
        assert "reference_solution" in result
        assert result["matches_reference"] is True
        assert result["submitted_solution"]["overall_success"] is True
        assert result["reference_solution"]["overall_success"] is True
    
    def test_cleanup(self, service):
        """Test cleanup functionality."""
        mock_client = Mock()
        mock_container = Mock()
        mock_container.image.tags = ["python:3.11-slim"]
        mock_client.containers.list.return_value = [mock_container]
        service.docker_client = mock_client
        
        service.cleanup()
        
        mock_client.containers.list.assert_called_once_with(
            all=True,
            filters={"status": "exited"}
        )
        mock_container.remove.assert_called_once()
    
    def test_cleanup_error_handling(self, service):
        """Test cleanup error handling."""
        mock_client = Mock()
        mock_client.containers.list.side_effect = Exception("Cleanup failed")
        service.docker_client = mock_client
        
        # Should not raise exception
        service.cleanup()
        
        mock_client.containers.list.assert_called_once()


@pytest.mark.asyncio
async def test_code_execution_integration():
    """Integration test for code execution (requires Docker)."""
    # This test will be skipped if Docker is not available
    try:
        service = CodeExecutionService()
        await service.initialize()
        
        # Test simple code execution
        code = "print('Integration test successful')"
        result = await service.execute_code(code, timeout=10)
        
        assert result["success"] is True
        assert "Integration test successful" in result["output"]
        
        service.cleanup()
        
    except CodeExecutionError:
        pytest.skip("Docker not available for integration test")
    except Exception as e:
        pytest.skip(f"Integration test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])