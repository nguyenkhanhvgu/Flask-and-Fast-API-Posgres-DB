#!/usr/bin/env python3
"""
Verification script to check if the development environment is set up correctly
"""
import os
import subprocess
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} (missing)")
        return False

def check_directory_structure():
    """Check if the project directory structure is correct"""
    print("Checking project directory structure...")
    
    required_files = [
        ("docker-compose.yml", "Docker Compose configuration"),
        ("backend/app/main.py", "FastAPI main application"),
        ("backend/requirements.txt", "Python dependencies"),
        ("backend/Dockerfile.dev", "Backend Docker configuration"),
        ("frontend/package.json", "Frontend package configuration"),
        ("frontend/src/App.tsx", "React main component"),
        ("frontend/Dockerfile.dev", "Frontend Docker configuration"),
        ("database/init/01_init.sql", "Database initialization script"),
        (".env.example", "Environment variables example"),
        ("README.md", "Project documentation"),
    ]
    
    all_good = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    return all_good

def check_python_dependencies():
    """Check if Python virtual environment and dependencies are set up"""
    print("\nChecking Python environment...")
    
    if os.path.exists("venv"):
        print("✓ Python virtual environment exists")
        
        # Check if FastAPI is installed in venv
        try:
            if os.name == 'nt':  # Windows
                pip_path = "venv\\Scripts\\pip"
            else:  # Unix/Linux/macOS
                pip_path = "venv/bin/pip"
            
            result = subprocess.run([pip_path, "list"], capture_output=True, text=True)
            if "fastapi" in result.stdout.lower():
                print("✓ FastAPI is installed in virtual environment")
                return True
            else:
                print("✗ FastAPI not found in virtual environment")
                return False
        except Exception as e:
            print(f"✗ Error checking Python dependencies: {e}")
            return False
    else:
        print("✗ Python virtual environment not found")
        return False

def check_frontend_dependencies():
    """Check if frontend dependencies are installed"""
    print("\nChecking frontend environment...")
    
    if os.path.exists("frontend/node_modules"):
        print("✓ Frontend dependencies are installed")
        return True
    else:
        print("✗ Frontend dependencies not installed (run 'npm install' in frontend directory)")
        return False

def check_docker_setup():
    """Check if Docker and Docker Compose are available"""
    print("\nChecking Docker setup...")
    
    try:
        # Check Docker
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        print("✓ Docker is available")
        
        # Check Docker Compose
        subprocess.run(["docker-compose", "--version"], capture_output=True, check=True)
        print("✓ Docker Compose is available")
        
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Docker or Docker Compose not available")
        return False

def main():
    """Main verification function"""
    print("🔍 Verifying Web Frameworks Tutorial development environment setup...\n")
    
    checks = [
        check_directory_structure(),
        check_python_dependencies(),
        check_frontend_dependencies(),
        check_docker_setup(),
    ]
    
    if all(checks):
        print("\n✅ All checks passed! Your development environment is ready.")
        print("\nTo start the services:")
        print("1. docker-compose up -d")
        print("2. Visit http://localhost:3000 for the frontend")
        print("3. Visit http://localhost:8000/docs for the API documentation")
    else:
        print("\n❌ Some checks failed. Please review the issues above.")
        print("Run 'python setup_dev.py' to set up the environment automatically.")

if __name__ == "__main__":
    main()