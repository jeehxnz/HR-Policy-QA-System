# cPanel Deployment Guide

This guide will help you deploy the HR-Policy-QA-System to cPanel hosting.

## Prerequisites

- cPanel hosting with Python support
- Python 3.10 or higher
- Access to cPanel File Manager or FTP

## Step-by-Step Deployment

### 1. Prepare Your Local Environment

```bash
# Run the deployment setup script
python3 cpanel_deploy.py

# Test that everything works locally
python3 deployment_test.py
```

### 2. Upload Files to cPanel

Upload the following files and directories to your cPanel hosting:

**Required Files:**
- `src/` (entire directory)
- `frontend/` (entire directory)
- `Data/` (entire directory)
- `passenger_wsgi.py`
- `.htaccess`
- `requirements-production.txt`
- `.env` (create from env.example)

**Optional Files:**
- `ingestion/` (if you need to process new documents)
- `README.md`
- `CHANGELOG.md`

### 3. Configure cPanel Python App

1. **Login to cPanel**
2. **Find "Setup Python App"**
3. **Create New Application:**
   - **Python version:** 3.10 or higher
   - **Application root:** Your domain/subdomain
   - **Application URL:** Your domain/subdomain
   - **Application startup file:** `passenger_wsgi.py`
   - **Application Entry point:** `application`

### 4. Set Environment Variables

Edit the `.env` file in your cPanel File Manager:

```bash
# Required
OPENROUTER_API_KEY=sk-your-actual-api-key

# Optional (use defaults if not set)
CHROMA_DB_PATH=./chroma_db
COLLECTION_NAME=hr_policies
MODEL_NAME_EMBEDDING=sentence-transformers/all-MiniLM-L6-v2
OPENROUTER_MODEL=openai/gpt-4.1
```

### 5. Install Dependencies

In cPanel Terminal or via SSH:

```bash
# Navigate to your application directory
cd /home/username/public_html/your-app

# Install dependencies
pip install -r requirements-production.txt
```

### 6. Ingest Data (if needed)

```bash
# Navigate to src directory
cd src

# Ingest data into ChromaDB
python3 ingest_data.py
```

### 7. Test Deployment

```bash
# Test the application
python3 deployment_test.py

# Check if the app starts correctly
python3 passenger_wsgi.py
```

### 8. Access Your Application

- **API Endpoints:** `https://yourdomain.com/ask`, `/health`, `/dependencies`, `/version`
- **Frontend:** Upload `frontend/` files to a web-accessible directory or serve via the same domain

## Troubleshooting

### Common Issues

1. **"Module not found" errors:**
   - Ensure all dependencies are installed: `pip install -r requirements-production.txt`
   - Check Python version compatibility

2. **"ChromaDB not connected":**
   - Run data ingestion: `cd src && python3 ingest_data.py`
   - Check file permissions on `chroma_db/` directory

3. **"OpenRouter API error":**
   - Verify `OPENROUTER_API_KEY` is set correctly in `.env`
   - Check API key validity and model availability

4. **"Permission denied":**
   - Ensure WSGI files are executable: `chmod +x passenger_wsgi.py`
   - Check directory permissions

### Debugging

1. **Check application logs:**
   - Look in cPanel error logs
   - Check Python application logs in cPanel

2. **Test individual components:**
   ```bash
   # Test dependency checking
   cd src && python3 test_dependencies.py
   
   # Test ChromaDB connection
   cd src && python3 test_chroma_query.py
   ```

3. **Verify environment:**
   ```bash
   # Check Python version
   python3 --version
   
   # Check installed packages
   pip list
   ```

## Security Considerations

1. **Environment Variables:** Never commit `.env` files to version control
2. **API Keys:** Use strong, unique API keys for OpenRouter
3. **File Permissions:** Set appropriate permissions on sensitive directories
4. **HTTPS:** Enable SSL/TLS for production deployments

## Performance Optimization

1. **Caching:** Consider implementing response caching for frequently asked questions
2. **Database:** Monitor ChromaDB performance and consider optimization
3. **Model Loading:** The embedding model is loaded once at startup for better performance

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review application logs in cPanel
3. Test components individually using the provided test scripts
4. Ensure all dependencies are correctly installed

## File Structure After Deployment

```
your-domain.com/
├── passenger_wsgi.py          # WSGI entry point
├── .htaccess                  # Apache configuration
├── .env                       # Environment variables
├── src/                       # Application source
│   ├── app.py                # Main Flask application
│   ├── ingest_data.py        # Data ingestion
│   └── test_*.py             # Test scripts
├── frontend/                  # Web interface
├── Data/                      # Policy documents
├── chroma_db/                 # Vector database (generated)
└── logs/                      # Application logs
```
