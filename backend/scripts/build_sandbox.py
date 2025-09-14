#!/usr/bin/env python3
"""
Script to build the code execution sandbox Docker image.
"""
import subprocess
import sys
import os
from pathlib import Path


def build_sandbox_image():
    """Build the code execution sandbox Docker image."""
    # Get the project root directory
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    docker_dir = backend_dir / "docker" / "code-sandbox"
    
    if not docker_dir.exists():
        print(f"Error: Docker directory not found at {docker_dir}")
        return False
    
    print("Building code execution sandbox Docker image...")
    print(f"Docker context: {docker_dir}")
    
    try:
        # Build the Docker image
        result = subprocess.run([
            "docker", "build",
            "-t", "web-tutorial-sandbox:latest",
            "-f", str(docker_dir / "Dockerfile"),
            str(docker_dir)
        ], check=True, capture_output=True, text=True)
        
        print("✅ Sandbox image built successfully!")
        print(f"Image: web-tutorial-sandbox:latest")
        
        # Verify the image was created
        result = subprocess.run([
            "docker", "images", "web-tutorial-sandbox:latest"
        ], check=True, capture_output=True, text=True)
        
        print("\nImage details:")
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build sandbox image: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Docker command not found. Please install Docker.")
        return False


def test_sandbox_image():
    """Test the sandbox image with a simple Python script."""
    print("\nTesting sandbox image...")
    
    try:
        # Test basic Python execution
        result = subprocess.run([
            "docker", "run", "--rm",
            "--memory=128m",
            "--cpus=0.5",
            "--network=none",
            "--user=sandbox",
            "web-tutorial-sandbox:latest",
            "python", "-c", "print('Sandbox test successful!')"
        ], check=True, capture_output=True, text=True, timeout=10)
        
        print("✅ Sandbox test passed!")
        print(f"Output: {result.stdout.strip()}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Sandbox test failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Sandbox test timed out")
        return False


def main():
    """Main function."""
    print("Code Execution Sandbox Builder")
    print("=" * 40)
    
    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker is not available. Please install Docker first.")
        sys.exit(1)
    
    # Build the sandbox image
    if not build_sandbox_image():
        sys.exit(1)
    
    # Test the sandbox image
    if not test_sandbox_image():
        print("⚠️  Sandbox image built but test failed. Please check the configuration.")
        sys.exit(1)
    
    print("\n🎉 Sandbox setup completed successfully!")
    print("\nThe sandbox is ready for code execution.")
    print("You can now start the backend server and use the code execution features.")


if __name__ == "__main__":
    main()