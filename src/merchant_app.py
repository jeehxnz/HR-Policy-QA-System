import sys
import subprocess
import importlib.util
import asyncio
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
import traceback
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.merchant_querying_service import MerchantQueryingService

app = Flask(__name__)

# Configure CORS explicitly to avoid browser preflight issues
allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "*")
if allowed_origins_env.strip() == "*":
    # With wildcard origins, do NOT enable credentials
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)
else:
    allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
    CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response

load_dotenv()

# Initialize MerchantQueryingService
merchant_querying_service = MerchantQueryingService()

@app.route('/ask', methods=['POST'])
def ask_merchant_question():
    try:
        data = request.json
        question = data.get('question')
        language = data.get('language')
        if not question:
            return jsonify({'error': 'Question is required'}), 400

        # Run async function in sync context
        response = asyncio.run(merchant_querying_service.query(question, language))
        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Merchant API server...")
    print("Server will be available at: http://127.0.0.1:5555")
    app.run(debug=True, host='0.0.0.0', port=5555)