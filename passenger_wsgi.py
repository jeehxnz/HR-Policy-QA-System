#!/usr/bin/env python3
"""
Passenger WSGI entry point for HR-Policy-QA-System
Alternative WSGI entry point for cPanel Passenger deployments.
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Import the Flask app from app.py
from app import app

# Passenger expects this variable name
application = app
