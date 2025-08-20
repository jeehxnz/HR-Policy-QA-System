# Requirements Management

This document explains the different requirements files and how to manage dependencies in this project.

## Requirements Files Overview

### 📦 `requirements.txt` (Full Development)
- **Purpose**: Complete development environment with all dependencies
- **Use case**: Full development setup, testing, debugging
- **Includes**: All packages including development tools, testing frameworks, monitoring
- **Size**: Large (~115 packages)

### ⚡ `requirements-light.txt` (Production)
- **Purpose**: Minimal production-ready dependencies
- **Use case**: Production deployment, Docker containers, CI/CD
- **Includes**: Only essential packages for the RAG chatbot to function
- **Size**: Medium (~60 packages)

### 🛠️ `requirements-dev.txt` (Development Tools)
- **Purpose**: Development and testing tools only
- **Use case**: Additional development dependencies
- **Includes**: Testing frameworks, code quality tools, documentation generators
- **Note**: Automatically includes `requirements-light.txt`

## Installation Commands

```bash
# For full development environment
pip install -r requirements.txt

# For production deployment
pip install -r requirements-light.txt

# For development tools only (includes production requirements)
pip install -r requirements-dev.txt
```

## Key Improvements Made

### 🔒 Security Updates
- Updated `urllib3` from 2.5.0 to 2.2.0 (security fix)
- Updated `bcrypt` from 4.3.0 to 4.4.0 (security fix)

### 🗑️ Removed Unnecessary Packages
- Removed `kubernetes` (unless using K8s deployment)
- Removed `pulsar-client` (unless using Apache Pulsar)
- Removed `posthog` (unless using PostHog analytics)
- Removed platform-specific `macholib` entry

### ➕ Added Important Packages
- Added testing frameworks (`pytest`, `pytest-asyncio`)
- Added code quality tools (`black`, `flake8`, `mypy`)
- Added logging framework (`loguru`)
- Added security scanning (`bandit`, `safety`)

## Requirements Management Script

Use the provided script to manage requirements:

```bash
# Check for security vulnerabilities
python scripts/update_requirements.py check

# Update security-critical packages
python scripts/update_requirements.py update

# Generate requirements from current environment
python scripts/update_requirements.py generate
```

## Package Categories

### Core Framework
- `fastapi`, `uvicorn`, `starlette` - Web framework
- `gunicorn` - WSGI server for production

### AI/ML Libraries
- `transformers`, `sentence-transformers` - Hugging Face models
- `torch` - PyTorch for deep learning
- `numpy`, `scikit-learn` - Scientific computing

### Database & Vector Store
- `chromadb` - Vector database for embeddings
- `chroma-hnswlib` - HNSW algorithm for similarity search

### PDF Processing
- `PyMuPDF`, `pdf2image`, `pytesseract` - PDF and image processing
- `Pillow` - Image manipulation

### Development Tools
- `pytest` - Testing framework
- `black`, `flake8` - Code formatting and linting
- `mypy` - Type checking
- `loguru` - Advanced logging

## Best Practices

### 🔄 Regular Updates
1. Run security checks monthly: `python scripts/update_requirements.py check`
2. Update critical packages quarterly
3. Review and remove unused dependencies

### 🐳 Docker Usage
For Docker deployments, use `requirements-light.txt`:
```dockerfile
COPY requirements-light.txt .
RUN pip install -r requirements-light.txt
```

### 🔍 Dependency Auditing
Regularly audit dependencies:
```bash
# Check for outdated packages
pip list --outdated

# Check for security vulnerabilities
safety check -r requirements-light.txt

# Check for license issues
pip-licenses
```

## Troubleshooting

### Common Issues

1. **Version Conflicts**
   - Use `pip-tools` to resolve conflicts
   - Consider using virtual environments

2. **Platform-Specific Issues**
   - Remove any `file://` URLs from requirements
   - Use platform-agnostic package names

3. **Large Installation Size**
   - Use `requirements-light.txt` for production
   - Consider using `torch-cpu` instead of full `torch`

### Migration Guide

If migrating from the old requirements:
1. Install new requirements: `pip install -r requirements-light.txt`
2. Test your application thoroughly
3. Remove old virtual environment if needed
4. Update deployment scripts to use new requirements file

## Security Considerations

- Always use pinned versions in production
- Regularly update security-critical packages
- Use `safety` to scan for vulnerabilities
- Consider using `pip-audit` for additional security checks
