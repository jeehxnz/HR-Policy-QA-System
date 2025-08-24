# RAG Chatbot API

A Retrieval-Augmented Generation (RAG) chatbot system built with Flask, ChromaDB, and OpenRouter. This system provides intelligent question-answering capabilities for HR policies and merchant FAQs with support for multiple languages.

## 🚀 Features

- **Multi-Language**: Bengali and English support (For merchants only)
- **Advanced RAG**: Context-aware responses with source citations
- **Scalable Architecture**: Microservices-based design
- **Separate Collections**: Independent ChromaDB collections for English and Bengali data

## 📋 Prerequisites

- **Python**: 3.10 - 3.12
- **OpenRouter API Key**: For LLM access
- **Memory**: 4GB+ RAM (for embedding models)
- **Storage**: 2GB+ free space

## 🛠️ Installation

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
pip install -r requirements.txt
```

### 3. Environment Configuration

1. **Copy the environment template:**
   ```bash
   cp env.example .env
   ```

2. **Create your `.env` file** with the following configuration:
   ```env
   # Global OpenRouter API Configuration
   OPENROUTER_API_KEY=your-api-key

   # ChromaDB Configuration
   CHROMA_DB_PATH=./chroma_db

   # Model Configuration
   OPENROUTER_MODEL=openai/gpt-4.1

   # Flask Configuration
   FLASK_ENV=development
   FLASK_DEBUG=True
   ALLOWED_ORIGINS="http://127.0.0.1:3000,http://localhost:3000,http://127.0.0.1:5555,http://localhost:5555,http://127.0.0.1:3001,http://localhost:3001"

   # Merchant FAQ Configuration
   BANGLA_SENTENCE_TRANSFORMER_MODEL=shihab17/bangla-sentence-transformer
   BANGLA_MERCHANT_FAQ_COLLECTION_NAME=Merchant_FAQ_V8
   ENGLISH_SENTENCE_TRANSFORMER_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ENGLISH_MERCHANT_FAQ_COLLECTION_NAME=Merchant_FAQ_EN_V1

   # HR Policy Configuration
   COLLECTION_NAME=hr_policies
   MODEL_NAME_EMBEDDING=sentence-transformers/all-MiniLM-L6-v2
   ```

## 🏗️ Main Concepts

### 1. REST API Startup

The system provides a REST API for merchant FAQ queries. To start the API server:

```bash
# Start the merchant API server
python src/merchant_app.py
```

The server will be available at: **http://127.0.0.1:5555**

#### API Reference

**Endpoint**: `POST /ask`

**Request Body**:
```json
{
  "question": "Your question here",
  "language": "en"  // or "bn" for Bengali
}
```

**Response**:
```json
{
  "response": "AI-generated answer based on relevant context"
}
```

**Example Usage**:
```bash
curl -X POST http://127.0.0.1:5555/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I open a merchant account?",
    "language": "en"
  }'
```

### 2. Data Ingestion

The system maintains **2 separate ChromaDB collections** for English and Bengali data:

- **English Collection**: `Merchant_FAQ_EN_V1` (configurable via `ENGLISH_MERCHANT_FAQ_COLLECTION_NAME`)
- **Bengali Collection**: `Merchant_FAQ_V8` (configurable via `BANGLA_MERCHANT_FAQ_COLLECTION_NAME`)

#### Ingestion Process

1. **Update Collection Names** (if needed):
   - Edit the `.env` file to change collection names
   - Update `BANGLA_MERCHANT_FAQ_COLLECTION_NAME` for Bengali data
   - Update `ENGLISH_MERCHANT_FAQ_COLLECTION_NAME` for English data

2. **Prepare Your Data**:
   - Place your files in the `tmp/unprocessed_files/` directory
   - Supported formats: PDF, TXT (TXT preferred)

3. **Run Ingestion Scripts**:

   **For Bengali Data**:
   ```bash
   python scripts/bangla_merchant_faq_processing.py
   ```

   **For English Data**:
   ```bash
   python scripts/english_merchant_faq_processing.py
   ```

4. **Follow the Prompts**:
   - Enter the filename with extension when prompted
   - The script will process the file and log the ingestion progress
   - Data will be chunked, embedded, and stored in the appropriate ChromaDB collection

#### Testing Queries

After ingestion, you can test queries using the example scripts:

```bash
# Test Bengali queries
python examples/bangla_test_query.py

# Test English queries
python examples/english_test_query.py
```

### 3. Merchant Querying

The system uses the `MerchantQueryingService` for processing queries:

```python
from services.merchant_querying_service import MerchantQueryingService

# Initialize the service
merchant_service = MerchantQueryingService(llm_model_name="openai/gpt-4.1")

# Query with question and language
response = await merchant_service.query(
    question="Your question here",
    language="en"  # or "bn" for Bengali
)
```

#### Query Process

1. **Question Embedding**: The question is embedded using the appropriate sentence transformer model
2. **Chroma Query**: Relevant chunks are retrieved from the appropriate collection based on language
3. **LLM Processing**: Retrieved chunks are passed to the LLM API with the question
4. **Response Generation**: A formatted answer is generated and returned

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
├── scripts/                      # Data ingestion scripts
│   ├── bangla_merchant_faq_processing.py    # Bengali data processing
│   ├── english_merchant_faq_processing.py   # English data processing
│   └── clear_all_collections.py      # Database cleanup
├── examples/                     # Testing examples
│   ├── bangla_test_query.py      # Bengali query testing
│   └── english_test_query.py     # English query testing
├── tmp/                          # Temporary processing files
│   ├── unprocessed_files/        # Place new files here for ingestion
│   ├── chunks/                   # Generated text chunks
│   ├── embeddings/               # Generated embeddings
│   └── source_maps/              # Source mapping files
├── chroma_db/                    # ChromaDB storage
├── Data/                         # Data storage
├── requirements.txt              # Dependencies
├── config.py                     # Configuration settings
├── env.example                   # Environment template
└── README.md                     # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Required | OpenRouter API key for LLM access |
| `CHROMA_DB_PATH` | `./chroma_db` | ChromaDB storage directory |
| `OPENROUTER_MODEL` | `openai/gpt-4.1` | LLM model via OpenRouter |
| `BANGLA_MERCHANT_FAQ_COLLECTION_NAME` | `Merchant_FAQ_V8` | Bengali merchant FAQ collection |
| `ENGLISH_MERCHANT_FAQ_COLLECTION_NAME` | `Merchant_FAQ_EN_V1` | English merchant FAQ collection |
| `BANGLA_SENTENCE_TRANSFORMER_MODEL` | `shihab17/bangla-sentence-transformer` | Bengali embedding model |
| `ENGLISH_SENTENCE_TRANSFORMER_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | English embedding model |
| `COLLECTION_NAME` | `hr_policies` | HR policies collection |
| `MODEL_NAME_EMBEDDING` | `sentence-transformers/all-MiniLM-L6-v2` | HR embedding model |

### Configuration Files

- **`config.py`** - Application configuration
- **`requirements.txt`** - Full development dependencies

## 🧪 Testing

### Test Queries

Use the example scripts to test your setup:

```bash
# Test Bengali queries
python examples/bangla_test_query.py

# Test English queries
python examples/english_test_query.py
```

### Clear Collections

To clear all ChromaDB collections:

```bash
python scripts/clear_all_collections.py
```

## 🚀 Quick Start Summary

1. **Setup**: Clone, install dependencies, configure `.env`
2. **Ingest Data**: Place files in `tmp/unprocessed_files/`, run appropriate ingestion script
3. **Start API**: Run `python src/merchant_app.py`
4. **Test**: Use example scripts or make API calls to `http://127.0.0.1:5555/ask`

---

**Built with Flask, ChromaDB, and OpenRouter**
