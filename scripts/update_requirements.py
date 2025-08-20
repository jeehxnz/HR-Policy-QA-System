#!/usr/bin/env python3
"""
Requirements Management Script
Helps manage and update requirements files with security checks.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return None


def check_security_vulnerabilities():
    """Check for security vulnerabilities in requirements."""
    print("🔒 Checking for security vulnerabilities...")
    
    # Check if safety is installed
    if run_command("which safety", check=False):
        result = run_command("safety check -r requirements-light.txt")
        if result:
            print("Security check results:")
            print(result)
        else:
            print("✅ No security vulnerabilities found")
    else:
        print("⚠️  Safety not installed. Install with: pip install safety")


def update_packages():
    """Update packages to latest secure versions."""
    print("\n🔄 Updating packages...")
    
    # Update urllib3 and bcrypt specifically
    packages_to_update = ["urllib3", "bcrypt"]
    
    for package in packages_to_update:
        print(f"Updating {package}...")
        run_command(f"pip install --upgrade {package}")


def generate_requirements():
    """Generate requirements from current environment."""
    print("\n📦 Generating requirements from current environment...")
    
    # Generate requirements for current environment
    result = run_command("pip freeze")
    if result:
        with open("requirements-generated.txt", "w") as f:
            f.write(result)
        print("✅ Generated requirements-generated.txt")


def main():
    """Main function."""
    print("🚀 Requirements Management Script")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/update_requirements.py check    # Check security")
        print("  python scripts/update_requirements.py update   # Update packages")
        print("  python scripts/update_requirements.py generate # Generate requirements")
        return
    
    command = sys.argv[1]
    
    if command == "check":
        check_security_vulnerabilities()
    elif command == "update":
        update_packages()
    elif command == "generate":
        generate_requirements()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
