#!/usr/bin/env python3
"""
Development environment setup script for Web Frameworks Tutorial
"""
import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {command}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return None

def setup_python_env():
    """Set up Python virtual environment and install dependencies"""
    print("Setting up Python virtual environment...")
    
    # Create virtual environment
    if not os.path.exists("venv"):
        run_command(f"{sys.executable} -m venv venv")
    
    # Determine activation script path
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        pip_path = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_script = "venv/bin/activate"
        pip_path = "venv/bin/pip"
    
    # Install backend dependencies
    print("Installing backend dependencies...")
    run_command(f"{pip_path} install -r backend/requirements.txt")
    
    print(f"Python environment setup complete!")
    print(f"To activate: source {activate_script}")

def setup_frontend():
    """Set up frontend dependencies"""
    print("Setting up frontend dependencies...")
    
    frontend_path = Path("frontend")
    if frontend_path.exists():
        run_command("npm install", cwd="frontend")
        print("Frontend dependencies installed!")
    else:
        print("Frontend directory not found!")

def create_env_file():
    """Create .env file from example if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            run_command("cp .env.example .env")
            print("Created .env file from .env.example")
        else:
            print("Warning: .env.example not found")

def main():
    """Main setup function"""
    print("🚀 Setting up Web Frameworks Tutorial development environment...")
    
    # Check if we're in the right directory
    if not os.path.exists("docker-compose.yml"):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Setup steps
    create_env_file()
    setup_python_env()
    setup_frontend()
    
    print("\n✅ Development environment setup complete!")
    print("\nNext steps:")
    print("1. Activate Python virtual environment: source venv/bin/activate (or venv\\Scripts\\activate on Windows)")
    print("2. Start services: docker-compose up -d")
    print("3. Backend will be available at: http://localhost:8000")
    print("4. Frontend will be available at: http://localhost:3000")
    print("5. PostgreSQL will be available at: localhost:5432")

if __name__ == "__main__":
    main()