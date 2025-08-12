#!/usr/bin/env python3
"""
Test script for dependency checking functionality.
This script can be used to test the dependency checking without running the full Flask app.
"""

import sys
import subprocess
import importlib.util

def check_dependencies():
    """Check for required dependencies and return status."""
    required_packages = {
        'flask': 'flask==3.0.0',
        'flask_cors': 'flask-cors==4.0.0',
        'chromadb': 'chromadb==0.5.5',
        'sentence_transformers': 'sentence-transformers==2.7.0',
        'transformers': 'transformers==4.41.1',
        'torch': 'torch==2.3.1',
        'requests': 'requests==2.32.3',
        'python_dotenv': 'python-dotenv==1.0.1'
    }
    
    dependency_status = {}
    missing_packages = []
    
    print("Checking dependencies...")
    print("=" * 50)
    
    for package, pip_name in required_packages.items():
        is_installed = importlib.util.find_spec(package) is not None
        dependency_status[package] = {
            "installed": is_installed,
            "pip_name": pip_name
        }
        
        status_icon = "✅" if is_installed else "❌"
        print(f"{status_icon} {package}: {'Installed' if is_installed else 'Missing'}")
        
        if not is_installed:
            missing_packages.append(pip_name)
    
    print("=" * 50)
    print(f"Total packages: {len(required_packages)}")
    print(f"Installed: {len(required_packages) - len(missing_packages)}")
    print(f"Missing: {len(missing_packages)}")
    
    if missing_packages:
        print(f"\nMissing packages: {missing_packages}")
        print("\nTo install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        
        # Ask user if they want to auto-install
        response = input("\nWould you like to auto-install missing packages? (y/N): ")
        if response.lower() in ['y', 'yes']:
            print("\nInstalling missing packages...")
            try:
                for package in missing_packages:
                    print(f"Installing {package}...")
                    result = subprocess.run([
                        sys.executable, '-m', 'pip', 'install', package
                    ], capture_output=True, text=True, check=True)
                    print(f"✅ Successfully installed {package}")
                
                print("\n🎉 All missing dependencies installed successfully!")
                print("You can now run the main application.")
                
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Failed to install dependencies: {e}")
                print(f"Error output: {e.stderr}")
                return False
        else:
            print("Skipping auto-installation.")
            return False
    else:
        print("\n🎉 All dependencies are installed!")
        return True
    
    return True

if __name__ == "__main__":
    check_dependencies()
