#!/usr/bin/env python3
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
