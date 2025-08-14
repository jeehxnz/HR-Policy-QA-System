#!/usr/bin/env python3
"""
Comprehensive test suite for HR Policy QA System
Runs all tests to verify system functionality
"""
import sys
import os
import subprocess
import time
import requests
import json
import traceback
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_success(message):
    """Print a success message."""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message."""
    print(f"❌ {message}")

def print_warning(message):
    """Print a warning message."""
    print(f"⚠️  {message}")

def print_info(message):
    """Print an info message."""
    print(f"ℹ️  {message}")

def test_dependencies():
    """Test that all required dependencies are available."""
    print_header("Testing Dependencies")
    
    required_packages = [
        'flask',
        'flask_cors', 
        'chromadb',
        'sentence_transformers',
        'transformers',
        'torch',
        'requests',
        'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print_error(f"Missing packages: {missing_packages}")
        return False
    
    return True

def test_environment():
    """Test environment variables and configuration."""
    print_header("Testing Environment Configuration")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print_success("Environment variables loaded")
    except Exception as e:
        print_error(f"Failed to load environment variables: {e}")
        return False
    
    required_vars = ['OPENROUTER_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            print_warning(f"{var} - NOT SET")
            missing_vars.append(var)
        else:
            print_success(f"{var} - SET")
    
    if missing_vars:
        print_warning(f"Missing environment variables: {missing_vars}")
        print_info("Some tests may fail without these variables")
    
    return True

def test_chroma_db():
    """Test Chroma DB connection and functionality."""
    print_header("Testing Chroma DB")
    
    try:
        import chromadb
        print_success(f"Chroma DB version: {chromadb.__version__}")
        
        # Test basic client creation
        client = chromadb.PersistentClient(path="./chroma_db")
        print_success("Chroma DB client created successfully")
        
        # Test collection access
        collection = client.get_collection(name="hr_policies")
        print_success("Collection 'hr_policies' accessed successfully")
        
        # Test collection count
        count = collection.count()
        print_success(f"Collection has {count} documents")
        
        if count == 0:
            print_warning("Collection is empty. You may need to run data ingestion.")
        
        # Test a simple query
        dummy_embedding = [[0.0] * 384]  # Standard embedding size for all-MiniLM-L6-v2
        results = collection.query(
            query_embeddings=dummy_embedding,
            n_results=1
        )
        print_success("Chroma DB query test successful")
        
        return True
        
    except Exception as e:
        print_error(f"Chroma DB test failed: {e}")
        print_info("Full traceback:")
        traceback.print_exc()
        return False

def test_data_ingestion():
    """Test data ingestion script."""
    print_header("Testing Data Ingestion")
    
    try:
        result = subprocess.run([
            sys.executable, 'src/ingest_data.py'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print_success("Data ingestion completed successfully")
            if "Total items in collection:" in result.stdout:
                print_success("Documents were loaded into ChromaDB")
            return True
        else:
            print_error(f"Data ingestion failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print_error("Data ingestion timed out")
        return False
    except Exception as e:
        print_error(f"Data ingestion test failed: {e}")
        return False

def test_flask_app_import():
    """Test Flask app import and basic functionality."""
    print_header("Testing Flask Application Import")
    
    try:
        from app import app
        print_success("Flask app imported successfully")
        print_success(f"App name: {app.name}")
        
        # Test that the app has the expected routes
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        expected_routes = ['/ask', '/health', '/version', '/dependencies']
        
        for route in expected_routes:
            if route in routes:
                print_success(f"Route {route} found")
            else:
                print_error(f"Route {route} missing")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Flask app test failed: {e}")
        print_info("Full traceback:")
        traceback.print_exc()
        return False

def test_flask_server():
    """Test Flask server startup and API endpoints."""
    print_header("Testing Flask Server")
    
    # Start the server in background
    try:
        server_process = subprocess.Popen([
            sys.executable, 'src/app.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(5)
        
        # Test health endpoint
        try:
            response = requests.get('http://localhost:5002/health', timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print_success("Health endpoint working")
                print_info(f"Status: {health_data.get('status', 'unknown')}")
                
                # Check components
                components = health_data.get('components', {})
                for component, status in components.items():
                    if status:
                        print_success(f"Component {component}: OK")
                    else:
                        print_error(f"Component {component}: FAILED")
            else:
                print_error(f"Health endpoint returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print_error(f"Health endpoint test failed: {e}")
            return False
        
        # Test version endpoint
        try:
            response = requests.get('http://localhost:5002/version', timeout=10)
            if response.status_code == 200:
                version_data = response.json()
                print_success("Version endpoint working")
                print_info(f"Version: {version_data.get('version', 'unknown')}")
            else:
                print_error(f"Version endpoint returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print_error(f"Version endpoint test failed: {e}")
            return False
        
        # Test ask endpoint with a simple query
        try:
            test_data = {"question": "What is the leave policy?"}
            response = requests.post('http://localhost:5002/ask', 
                                   json=test_data, timeout=30)
            if response.status_code == 200:
                print_success("Ask endpoint working")
                answer_data = response.json()
                if 'answer' in answer_data:
                    print_success("Received answer from AI")
                else:
                    print_warning("No answer in response")
            elif response.status_code == 500:
                print_error("Ask endpoint returned 500 error")
                print_info("This might be due to missing API key or other configuration")
                return False
            else:
                print_error(f"Ask endpoint returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print_error(f"Ask endpoint test failed: {e}")
            return False
        
        # Stop the server
        server_process.terminate()
        server_process.wait(timeout=5)
        
        return True
        
    except Exception as e:
        print_error(f"Flask server test failed: {e}")
        return False

def test_chroma_query():
    """Test the ChromaDB query script."""
    print_header("Testing ChromaDB Query Script")
    
    try:
        result = subprocess.run([
            sys.executable, 'src/test_chroma_query.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_success("ChromaDB query test completed successfully")
            if "Query succeeded!" in result.stdout:
                print_success("Query executed successfully")
            return True
        else:
            print_error(f"ChromaDB query test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print_error("ChromaDB query test timed out")
        return False
    except Exception as e:
        print_error(f"ChromaDB query test failed: {e}")
        return False

def run_performance_test():
    """Run a basic performance test."""
    print_header("Performance Test")
    
    try:
        import time
        start_time = time.time()
        
        # Test ChromaDB query performance
        import chromadb
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection(name="hr_policies")
        
        # Test multiple queries
        for i in range(5):
            dummy_embedding = [[0.0] * 384]
            results = collection.query(
                query_embeddings=dummy_embedding,
                n_results=5
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print_success(f"Performance test completed in {duration:.2f} seconds")
        print_info(f"Average query time: {duration/5:.3f} seconds")
        
        return True
        
    except Exception as e:
        print_error(f"Performance test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Comprehensive Test Suite for HR Policy QA System")
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Environment", test_environment),
        ("ChromaDB", test_chroma_db),
        ("Data Ingestion", test_data_ingestion),
        ("Flask App Import", test_flask_app_import),
        ("ChromaDB Query Script", test_chroma_query),
        ("Flask Server", test_flask_server),
        ("Performance", run_performance_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"{test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print_header("Test Results Summary")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
            passed += 1
        else:
            print_error(f"{test_name}: FAILED")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print_success("🎉 All tests passed! System is ready for deployment.")
        return 0
    else:
        print_error(f"⚠️  {failed} test(s) failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
