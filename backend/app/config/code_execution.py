"""
Configuration for code execution service.
"""
from pydantic import BaseSettings
from typing import Dict, Any


class CodeExecutionSettings(BaseSettings):
    """Settings for code execution service."""
    
    # Docker configuration
    docker_image: str = "python:3.11-slim"
    container_timeout: int = 30  # seconds
    memory_limit: str = "128m"
    cpu_limit: str = "0.5"
    
    # Security settings
    network_disabled: bool = True
    read_only_filesystem: bool = True
    no_new_privileges: bool = True
    
    # Execution limits
    max_execution_time: int = 60  # seconds
    max_output_size: int = 10240  # bytes (10KB)
    max_concurrent_executions: int = 10
    
    # Allowed Python packages (pre-installed in sandbox)
    allowed_packages: list = [
        "requests",
        "numpy",
        "pandas",
        "matplotlib",
        "flask",
        "fastapi",
        "sqlalchemy",
        "psycopg2-binary"
    ]
    
    # Restricted operations (for future implementation)
    restricted_imports: list = [
        "os",
        "sys",
        "subprocess",
        "socket",
        "urllib",
        "http",
        "ftplib",
        "smtplib",
        "telnetlib",
        "multiprocessing",
        "threading",
        "asyncio",
        "concurrent"
    ]
    
    # File system restrictions
    max_file_size: int = 1024  # bytes (1KB)
    allowed_file_extensions: list = [".py", ".txt"]
    
    class Config:
        env_prefix = "CODE_EXECUTION_"


# Global settings instance
code_execution_settings = CodeExecutionSettings()