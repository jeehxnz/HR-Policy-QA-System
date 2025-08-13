.PHONY: setup install ingest run test clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  setup    - Create virtual environment and install dependencies"
	@echo "  install  - Install dependencies in existing environment"
	@echo "  check-deps - Check and optionally install missing dependencies"
	@echo "  ingest   - Ingest data into ChromaDB"
	@echo "  run      - Start the Flask API server"
	@echo "  test     - Run ChromaDB tests"
	@echo "  health   - Check system health status"
	@echo "  deploy-setup - Setup for cPanel deployment"
	@echo "  deploy-test  - Test deployment setup"
	@echo "  clean    - Remove generated files"

# Setup virtual environment and install dependencies
setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	@echo "Setup complete! Activate with: source .venv/bin/activate"

# Install dependencies in existing environment
install:
	pip install -r requirements.txt

# Check and optionally install missing dependencies
check-deps:
	cd src && python3 test_dependencies.py

# Ingest data into ChromaDB
ingest:
	cd src && python3 ingest_data.py

# Start the Flask API server
run:
	cd src && python3 app.py

# Run ChromaDB tests
test:
	cd src && python3 test_chroma_query.py

# Check system health status
health:
	@echo "Checking system health..."
	@curl -s http://localhost:5000/health | python -m json.tool 2>/dev/null || echo "Server not running. Start with 'make run' first."

# Setup for cPanel deployment
deploy-setup:
	python3 cpanel_deploy.py

# Test deployment setup
deploy-test:
	python3 deployment_test.py

# Clean generated files
clean:
	rm -rf chroma_db/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf ingestion/__pycache__/
	find . -name "*.pyc" -delete
