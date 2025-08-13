#!/usr/bin/env python3
"""
cPanel Deployment Script for HR-Policy-QA-System
This script helps set up the application for cPanel deployment.
"""

import os
import shutil
import subprocess
import sys

def create_deployment_structure():
    """Create the necessary files and structure for cPanel deployment."""
    
    print("Setting up cPanel deployment structure...")
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('tmp', exist_ok=True)
    
    # Copy environment template
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            shutil.copy('env.example', '.env')
            print("✅ Created .env from env.example")
            print("⚠️  Please edit .env with your actual configuration values")
        else:
            print("❌ env.example not found")
    
    # Create a simple deployment test
    with open('deployment_test.py', 'w') as f:
        f.write('''#!/usr/bin/env python3
"""
Simple deployment test to verify the application works.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app import app
    print("✅ Flask app imported successfully")
    print(f"✅ App name: {app.name}")
    print("✅ Application is ready for deployment")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    sys.exit(1)
''')
    
    print("✅ Created deployment_test.py")
    
    # Make files executable
    os.chmod('src/wsgi.py', 0o755)
    os.chmod('passenger_wsgi.py', 0o755)
    os.chmod('deployment_test.py', 0o755)
    
    print("✅ Made WSGI files executable")
    
    return True

def check_dependencies():
    """Check if all required dependencies are available."""
    print("\nChecking dependencies for deployment...")
    
    required_packages = [
        'flask', 'flask_cors', 'chromadb', 'sentence_transformers',
        'transformers', 'torch', 'requests', 'python_dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {missing}")
        print("Please install missing packages before deployment:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies available")
    return True

def create_requirements_production():
    """Create a production requirements file."""
    print("\nCreating production requirements...")
    
    production_requirements = [
        'flask==3.0.0',
        'flask-cors==4.0.0',
        'chromadb==0.5.5',
        'sentence-transformers==2.7.0',
        'transformers==4.41.1',
        'torch==2.3.1',
        'requests==2.32.3',
        'python-dotenv==1.0.1',
        'gunicorn==21.2.0'
    ]
    
    with open('requirements-production.txt', 'w') as f:
        f.write('\n'.join(production_requirements))
    
    print("✅ Created requirements-production.txt")

def main():
    """Main deployment setup function."""
    print("🚀 HR-Policy-QA-System cPanel Deployment Setup")
    print("=" * 50)
    
    # Create deployment structure
    if not create_deployment_structure():
        print("❌ Failed to create deployment structure")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        sys.exit(1)
    
    # Create production requirements
    create_requirements_production()
    
    print("\n" + "=" * 50)
    print("✅ Deployment setup complete!")
    print("\nNext steps:")
    print("1. Edit .env with your configuration")
    print("2. Upload files to your cPanel hosting")
    print("3. Set up Python app in cPanel")
    print("4. Point to passenger_wsgi.py or src/wsgi.py")
    print("5. Run deployment_test.py to verify setup")
    print("\nFor more information, see README.md")

if __name__ == '__main__':
    main()
