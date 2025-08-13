#!/usr/bin/env python3
"""
WSGI entry point for HR-Policy-QA-System
This file is used by cPanel and other WSGI servers to serve the Flask application.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app from app.py
from app import app

# WSGI callable that cPanel expects
application = app

# For local development, you can still run this file directly
if __name__ == '__main__':
    app.run(debug=True, port=5000)
