# RAG Chatbot API

A sophisticated Retrieval-Augmented Generation (RAG) chatbot system built with Flask, ChromaDB, and OpenRouter. This system provides intelligent question-answering capabilities for HR policies and merchant FAQs with support for multiple languages.

## 🚀 Features

- **Multi-Domain Support**: HR policies and merchant FAQs
- **Multi-Language**: Bengali and English support (For mechants only)
- **Advanced RAG**: Context-aware responses with source citations
- **Scalable Architecture**: Microservices-based design

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Flask         │    │   ChromaDB      │
│   Backend       │◄──►│   Vector Store  │
└─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   OpenRouter    │
                       │   LLM Service   │
                       └─────────────────┘
```

## 📁 Project Structure

```
RAG-chatbot-api/
├── src/                          # Main application files
│   ├── hr_app.py                 # HR policy API endpoints
│   └── merchant_app.py           # Merchant FAQ API endpoints
├── services/                     # Core business logic services
│   ├── file_processing_service.py    # PDF/text processing
│   ├── tokenization_service.py       # Text chunking & embeddings
│   ├── llm_querying_service.py       # LLM integration
│   ├── merchant_querying_service.py  # Merchant FAQ handling
│   └── __init__.py
├── lib/                          # Shared libraries
│   ├── chromaDBClient.py         # ChromaDB client wrapper
│   └── __init__.py
├── ingestion/                    # Data ingestion scripts
│   └── q_a_bkash.py             # PDF processing pipeline
├── scripts/                      # Utility scripts
│   ├── merchant_pdf_processing.py    # Document processing
│   ├── clear_all_collections.py      # Database cleanup
│   └── update_requirements.py        # Requirements management
├── Data/                         # Data storage
│   ├── chunks/                   # Text chunks
│   ├── source_files/             # Original documents
│   └── embedding_source_map.json # Source mapping
├── chroma_db/                    # ChromaDB storage 
├── examples/                     # Usage examples
│   ├── query_merchants.py        # Merchant query examples
│   └── merchant_pdf_processing.py # PDF processing examples
├── requirements.txt              # Full development dependencies
├── requirements-light.txt        # Production dependencies
├── requirements-dev.txt          # Development tools
├── config.py                     # Configuration settings
├── env.example                   # Environment template
└── README.md                     # This file
```

## 📋 Prerequisites

- **Python**: 3.10 - 3.12
- **OpenRouter API Key**: For LLM access
- **Memory**: 4GB+ RAM (for embedding models)
- **Storage**: 2GB+ free space

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd RAG-chatbot-api

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# For production deployment
pip install -r requirements-light.txt

# For full development environment
pip install -r requirements.txt

# For development tools only
pip install -r requirements-dev.txt
```

### 3. Environment Configuration

```bash
cp env.example .env
```

Edit `.env` with your configuration:
```env
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here
SENTENCE_TRANSFORMER_MODEL=sentence-transformers/shihab17/bangla-sentence-transformer (for Merchant API)
MODEL_NAME_EMBEDDING=sentence-transformers/all-MiniLM-L6-v2 (for HR API)

# Optional (with defaults)
CHROMA_DB_PATH=./chroma_db
COLLECTION_NAME=hr_policies (for merchant api)
OPENROUTER_MODEL=openai/gpt-4.1
MERCHANT_FAQ_COLLECTION_NAME=Merchant_FAQ_V7

```

### 4. Data Ingestion

```bash
# Process and ingest HR policy documents
python scripts/merchant_pdf_processing.py

# Or use the ingestion service directly
python -c "
from services.file_processing_service import FileProcessingService
from services.tokenization_service import TokenizationService
# ... ingestion code
"
```

### 5. Start the Application

```bash
# Development server
python3 src/merchant_app.py
```

### 6. Access the Application

- **API**: http://localhost:5555

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Required | OpenRouter API key for LLM access |
| `CHROMA_DB_PATH` | `./chroma_db` | ChromaDB storage directory |
| `COLLECTION_NAME` | `hr_policies` | HR App collection |
| `MODEL_NAME_EMBEDDING` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `OPENROUTER_MODEL` | `openai/gpt-4.1` | LLM model via OpenRouter |
| `MERCHANT_FAQ_COLLECTION_NAME` | `merchant_faqs` | Merchant FAQ collection |
| `SENTENCE_TRANSFORMER_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Sentence transformer model |

### Configuration Files

- **`config.py`** - Application configuration
- **`requirements-light.txt`** - Production dependencies
- **`requirements.txt`** - Full development dependencies
- **`requirements-dev.txt`** - Development tools

## 📚 How to Use

### 1. Merchant FAQ Queries

#### Using the API

```bash
# Ask a question about merchant services (Bengali)
curl -X POST http://localhost:5555/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "মার্চেন্ট অ্যাকাউন্ট কীভাবে খুলব?",
    "language": "bn"
  }'
```

#### Using Python

```python
from services.merchant_querying_service import MerchantQueryingService

# Initialize merchant service
merchant_service = MerchantQueryingService()

# Ask a question
response = await merchant_service.query(
    question="মার্চেন্ট অ্যাকাউন্ট কীভাবে খুলব?",
    language="bn"
)

print(response)
```

### 3. Document Processing

#### Process New Documents

```python
from services.file_processing_service import FileProcessingService
from services.tokenization_service import TokenizationService

# Initialize services
file_service = FileProcessingService()
token_service = TokenizationService()

# Process PDF documents
pdf_files = ["new_policy.pdf", "updated_guidelines.pdf"]
results = await file_service.process_files(pdf_files)

print(f"Processed {results['pdf_files']} files")
print(f"Generated {results['txt_files']} text files")
print(f"Created {results['cleaned_files']} cleaned files")
```

#### Using the Script

```bash
# Process documents using the provided script
python scripts/merchant_pdf_processing.py
```

### 4. Database Management

#### Clear Collections

```bash
# Clear all ChromaDB collections
python scripts/clear_all_collections.py
```

#### Using Python

```python
from lib.chromaDBClient import get_chroma_client

# Initialize ChromaDB client
chroma_client = get_chroma_client()
chroma_client.initialize(db_path="./chroma_db", collection_name="Merchant_FAQ_V7")

# List collections
collections = chroma_client.list_collections()
print(f"Available collections: {collections}")

# Delete a collection
chroma_client.delete_collection("test_collection")
```

---

**Built with ❤️ using Flask, ChromaDB, and OpenRouter**
