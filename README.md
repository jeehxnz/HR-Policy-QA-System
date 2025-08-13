# HR-Policy-QA-System

An intelligent question-answering system for HR policies using Retrieval-Augmented Generation (RAG) with ChromaDB and OpenRouter.

## Overview

This system provides bKash employees with instant, accurate answers to HR policy questions by:
- Embedding questions using sentence transformers
- Retrieving relevant policy chunks from a vector database
- Generating contextual answers using an LLM via OpenRouter

## Architecture

- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Store**: ChromaDB persistent collection
- **LLM**: OpenRouter (default: `openai/gpt-4.1`)
- **Backend**: Flask API
- **Frontend**: Static HTML/CSS/JS

## Quick Start

### Prerequisites
- Python 3.10-3.12
- OpenRouter API key

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd HR-Policy-QA-System
   ```

2. Create virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   cp env.example .env
   # Edit .env with your OpenRouter API key
   ```

5. Ingest data (if using provided data):
   ```bash
   cd src
   python ingest_data.py
   ```

6. Start the API:
   ```bash
   cd src
   python app.py
   ```

7. Open the frontend:
   - Open `frontend/index.html` in your browser
   - Or serve it via a local server

## Project Structure

```
HR-Policy-QA-System/
├── src/                    # Flask API and backend logic
│   ├── app.py              # Main Flask application
│   ├── ingest_data.py      # Data ingestion script
│   └── test_*.py           # ChromaDB tests
├── frontend/               # Static web interface
│   ├── index.html          # Landing page
│   ├── query.html          # Question interface
│   ├── script.js           # Frontend logic
│   ├── style.css           # Styling
│   └── assets/             # Images and static assets
├── ingestion/              # Data processing scripts
│   └── q_a_bkash.py        # PDF processing and embedding
├── Data/                   # Processed data files
│   ├── *_cleaned.txt       # Cleaned text files
│   ├── *_chunks.json       # Text chunks
│   ├── all_chunks_embeddings.pt  # Embeddings
│   └── embedding_source_map.json # Source mapping
├── chroma_db/              # ChromaDB storage (generated)
├── requirements.txt        # Python dependencies
├── env.example             # Environment template
└── README.md               # This file
```

## API Reference

### POST /ask
Submit a question about HR policies.

### GET /health
Check system health and component status.

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "embedding_model": true,
    "chroma_db": true,
    "tokenizer": true,
    "openrouter_key": true
  },
  "config": {
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "chroma_db_path": "./chroma_db",
    "collection_name": "hr_policies",
    "openrouter_model": "openai/gpt-4.1"
  }
}
```

### GET /dependencies
Check dependency status and optionally auto-install missing packages.

**Parameters:**
- `auto_install=true` - Automatically install missing dependencies

**Response:**
```json
{
  "dependencies": {
    "flask": {"installed": true, "pip_name": "flask==3.0.0"},
    "chromadb": {"installed": false, "pip_name": "chromadb==0.5.5"}
  },
  "missing_count": 1,
  "missing_packages": ["chromadb==0.5.5"]
}
```

### GET /version
Get application version and architecture information.

**Request:**
```json
{
  "question": "What is the travel policy approval process?"
}
```

**Response:**
```json
{
  "answer": "According to the Employee Travel and Transfer Guideline...",
  "source_metadata": [
    {
      "source_file": "Employee Travel and Transfer Guideline_cleaned.txt",
      "chunk_index": 12
    }
  ]
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Required | Your OpenRouter API key |
| `CHROMA_DB_PATH` | `./chroma_db` | Path to ChromaDB storage |
| `COLLECTION_NAME` | `hr_policies` | ChromaDB collection name |
| `MODEL_NAME_EMBEDDING` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `OPENROUTER_MODEL` | `openai/gpt-4.1` | LLM model via OpenRouter |

## Data Processing

To add new HR policy documents:

1. Place PDFs in `Data/raw_pdfs/`
2. Run the ingestion script:
   ```bash
   cd ingestion
   python q_a_bkash.py
   ```
3. Ingest into ChromaDB:
   ```bash
   cd backend
   python ingest_data.py
   ```

## Troubleshooting

- **"Database not connected"**: Ensure `chroma_db/` exists and run ingestion
- **"Embedding model not loaded"**: Check internet connection for model download
- **"OpenRouter error"**: Verify API key and model availability

## Development

### Running Tests
```bash
cd src
python test_chroma_query.py
```

### Checking Dependencies
```bash
# Check dependency status
make check-deps

# Or run the test script directly
cd src
python test_dependencies.py
```

### Checking System Health
```bash
# Start the server first
make run

# Then check health in another terminal
make health

# Or use curl directly
curl http://localhost:5000/health
```

### Adding New Features
1. Backend changes: Modify files in `src/`
2. Frontend changes: Modify files in `frontend/`
3. Data processing: Modify files in `ingestion/`

## Deployment

### cPanel Deployment

1. **Prepare for deployment:**
   ```bash
   python3 cpanel_deploy.py
   ```

2. **Upload files to cPanel:**
   - Upload all files to your cPanel hosting directory
   - Ensure `src/`, `frontend/`, and `Data/` directories are included

3. **Configure cPanel Python App:**
   - Go to cPanel → "Setup Python App"
   - Create a new Python application
   - Set the application root to your domain/subdomain
   - Set the application startup file to `passenger_wsgi.py` or `src/wsgi.py`
   - Set Python version to 3.10 or higher

4. **Set environment variables:**
   - Edit `.env` file with your production settings
   - Ensure `OPENROUTER_API_KEY` is set
   - Update paths for production environment

5. **Install dependencies:**
   ```bash
   pip install -r requirements-production.txt
   ```

6. **Test deployment:**
   ```bash
   python3 deployment_test.py
   ```

### Other Deployment Options

- **Containerization**: Use Docker with `chroma_db/` as a persistent volume
- **Static hosting**: Serve frontend via NGINX with API reverse proxy
- **Cloud platforms**: Deploy to Heroku, Railway, or similar platforms

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
