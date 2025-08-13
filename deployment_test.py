#!/usr/bin/env python3
"""
Comprehensive deployment test to verify the application works.
"""
import sys
import os
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_chroma_db():
    """Test Chroma DB connection and functionality."""
    print("\n🔍 Testing Chroma DB connection...")
    
    try:
        import chromadb
        print(f"✅ Chroma DB version: {chromadb.__version__}")
        
        # Test basic client creation
        client = chromadb.PersistentClient(path="./chroma_db")
        print("✅ Chroma DB client created successfully")
        
        # Test collection access
        collection = client.get_collection(name="hr_policies")
        print("✅ Collection 'hr_policies' accessed successfully")
        
        # Test collection count
        count = collection.count()
        print(f"✅ Collection has {count} documents")
        
        if count == 0:
            print("⚠️  Warning: Collection is empty. You may need to run data ingestion.")
        
        # Test a simple query
        dummy_embedding = [[0.0] * 384]  # Standard embedding size for all-MiniLM-L6-v2
        results = collection.query(
            query_embeddings=dummy_embedding,
            n_results=1
        )
        print("✅ Chroma DB query test successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Chroma DB test failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    print("\n🔍 Testing dependencies...")
    
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
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {missing_packages}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    
    return True

def test_environment():
    """Test environment variables and configuration."""
    print("\n🔍 Testing environment configuration...")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except Exception as e:
        print(f"❌ Failed to load environment variables: {e}")
        return False
    
    # Check for required environment variables
    required_vars = ['OPENROUTER_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            print(f"⚠️  {var} - NOT SET")
            missing_vars.append(var)
        else:
            print(f"✅ {var} - SET")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
        print("Please set these in your .env file")
        return False
    
    return True

def test_flask_app():
    """Test Flask app import and basic functionality."""
    print("\n🔍 Testing Flask application...")
    
    try:
        from app import app
        print("✅ Flask app imported successfully")
        print(f"✅ App name: {app.name}")
        
        # Test that the app has the expected routes
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        expected_routes = ['/ask']
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} found")
            else:
                print(f"❌ Route {route} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def main():
    """Run all deployment tests."""
    print("🚀 Starting comprehensive deployment test...")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Environment", test_environment),
        ("Chroma DB", test_chroma_db),
        ("Flask App", test_flask_app)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Application is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
