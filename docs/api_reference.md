# API Reference

## Overview

The RAG Chatbot API provides RESTful endpoints for intelligent question-answering using Retrieval-Augmented Generation (RAG). The API supports both HR policy queries and merchant FAQ queries with multi-language support.

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## Authentication

The API uses API key authentication for external service calls. No authentication is required for public endpoints.

## Content Type

All requests and responses use `application/json` content type.

## Endpoints

### Health Check

#### GET /health

Check the health status of the system and its components.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
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

**Status Codes:**
- `200 OK`: System is healthy
- `503 Service Unavailable`: One or more components are unhealthy

### Dependencies Check

#### GET /dependencies

Check the status of required dependencies and optionally install missing packages.

**Query Parameters:**
- `auto_install` (boolean, optional): Automatically install missing dependencies

**Response:**
```json
{
  "dependencies": {
    "flask": {
      "installed": true,
      "version": "3.0.0",
      "pip_name": "flask==3.0.0"
    },
    "chromadb": {
      "installed": false,
      "version": null,
      "pip_name": "chromadb==0.4.24"
    }
  },
  "missing_count": 1,
  "missing_packages": ["chromadb==0.4.24"],
  "auto_install_enabled": false
}
```

### Version Information

#### GET /version

Get application version and architecture information.

**Response:**
```json
{
  "version": "1.0.0",
  "architecture": "x86_64",
  "python_version": "3.10.0",
  "platform": "darwin",
  "dependencies": {
    "fastapi": "0.116.1",
    "chromadb": "0.4.24",
    "sentence_transformers": "2.7.0"
  }
}
```

### HR Policy Query

#### POST /ask

Submit a question about HR policies and receive an intelligent response.

**Request Body:**
```json
{
  "question": "What is the travel policy approval process?",
  "language": "en",
  "max_results": 3
}
```

**Parameters:**
- `question` (string, required): The question to ask
- `language` (string, optional): Response language ("en" or "bn"). Default: "en"
- `max_results` (integer, optional): Maximum number of context chunks to retrieve. Default: 3

**Response:**
```json
{
  "answer": "According to the Employee Travel and Transfer Guideline, the travel policy approval process involves the following steps: 1) Submit travel request through the HR portal, 2) Manager approval within 48 hours, 3) HR review and final approval, 4) Travel authorization document generation.",
  "source_metadata": [
    {
      "source_file": "Employee Travel and Transfer Guideline_cleaned.txt",
      "chunk_index": 12,
      "similarity_score": 0.89
    },
    {
      "source_file": "Employee Travel and Transfer Guideline_cleaned.txt",
      "chunk_index": 13,
      "similarity_score": 0.76
    }
  ],
  "processing_time": 1.23,
  "model_used": "openai/gpt-4.1"
}
```

**Status Codes:**
- `200 OK`: Question answered successfully
- `400 Bad Request`: Invalid question or parameters
- `500 Internal Server Error`: Processing error

### Merchant FAQ Query

#### POST /merchant/ask

Submit a question about merchant services and receive a response in Bengali.

**Request Body:**
```json
{
  "question": "মার্চেন্ট অ্যাকাউন্ট কীভাবে খুলব?",
  "language": "bn"
}
```

**Parameters:**
- `question` (string, required): The question to ask (Bengali or English)
- `language` (string, optional): Response language ("bn" or "en"). Default: "bn"

**Response:**
```json
{
  "answer": "মার্চেন্ট অ্যাকাউন্ট খোলার জন্য নিম্নলিখিত ধাপগুলি অনুসরণ করুন: ১) bKash অ্যাপে লগইন করুন, ২) 'মার্চেন্ট' অপশনে যান, ৩) প্রয়োজনীয় তথ্য দিয়ে ফর্ম পূরণ করুন, ৪) প্রয়োজনীয় কাগজপত্র আপলোড করুন, ৫) সাবমিট করুন।",
  "source_metadata": [
    {
      "source_file": "bKash-Merchant-FAQ-v3_cleaned.txt",
      "chunk_index": 5,
      "similarity_score": 0.92
    }
  ],
  "processing_time": 0.98,
  "model_used": "openai/gpt-4.1"
}
```

### Document Processing

#### POST /process-documents

Process and ingest new documents into the system.

**Request Body:**
```json
{
  "file_paths": [
    "Data/raw_pdfs/new_policy.pdf",
    "Data/raw_pdfs/updated_guidelines.pdf"
  ],
  "collection_name": "hr_policies",
  "chunk_size": 512,
  "chunk_overlap": 50
}
```

**Parameters:**
- `file_paths` (array, required): List of PDF file paths to process
- `collection_name` (string, optional): Target ChromaDB collection. Default: "hr_policies"
- `chunk_size` (integer, optional): Token size for text chunking. Default: 512
- `chunk_overlap` (integer, optional): Overlap between chunks. Default: 50

**Response:**
```json
{
  "status": "success",
  "processed_files": 2,
  "total_chunks": 45,
  "collection_name": "hr_policies",
  "processing_time": 12.34,
  "details": {
    "new_policy.pdf": {
      "chunks": 23,
      "status": "success"
    },
    "updated_guidelines.pdf": {
      "chunks": 22,
      "status": "success"
    }
  }
}
```

### Collection Management

#### GET /collections

List all available ChromaDB collections.

**Response:**
```json
{
  "collections": [
    {
      "name": "hr_policies",
      "count": 1250,
      "metadata": {
        "description": "HR policy documents",
        "created_at": "2024-01-10T09:00:00Z"
      }
    },
    {
      "name": "merchant_faqs",
      "count": 450,
      "metadata": {
        "description": "Merchant FAQ documents",
        "created_at": "2024-01-12T14:30:00Z"
      }
    }
  ]
}
```

#### DELETE /collections/{collection_name}

Delete a specific collection and all its data.

**Parameters:**
- `collection_name` (string, required): Name of the collection to delete

**Response:**
```json
{
  "status": "success",
  "message": "Collection 'test_collection' deleted successfully",
  "deleted_count": 150
}
```

## Error Responses

### Standard Error Format

All error responses follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid question format",
    "details": {
      "field": "question",
      "issue": "Question cannot be empty"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `AUTHENTICATION_ERROR` | 401 | Authentication required |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default Limit**: 100 requests per minute per IP
- **Burst Limit**: 10 requests per second
- **Headers**: Rate limit information is included in response headers

**Response Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642234567
```

## Pagination

For endpoints that return lists, pagination is supported:

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)

**Response Headers:**
```
X-Total-Count: 150
X-Page-Count: 8
X-Current-Page: 2
```

## WebSocket Support

### WebSocket Endpoint

#### WS /ws/chat

Real-time chat interface for streaming responses.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');
```

**Message Format:**
```json
{
  "type": "question",
  "question": "What is the leave policy?",
  "language": "en"
}
```

**Response Format:**
```json
{
  "type": "answer",
  "answer": "According to the HR policy...",
  "source_metadata": [...],
  "completed": true
}
```

## SDK Examples

### Python SDK

```python
import requests

# Health check
response = requests.get('http://localhost:8000/health')
print(response.json())

# Ask a question
question_data = {
    "question": "What is the travel policy?",
    "language": "en"
}
response = requests.post('http://localhost:8000/ask', json=question_data)
print(response.json())
```

### JavaScript SDK

```javascript
// Health check
const healthResponse = await fetch('http://localhost:8000/health');
const health = await healthResponse.json();

// Ask a question
const questionData = {
    question: "What is the travel policy?",
    language: "en"
};
const response = await fetch('http://localhost:8000/ask', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(questionData)
});
const result = await response.json();
```

### cURL Examples

```bash
# Health check
curl -X GET http://localhost:8000/health

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the travel policy?", "language": "en"}'

# Process documents
curl -X POST http://localhost:8000/process-documents \
  -H "Content-Type: application/json" \
  -d '{"file_paths": ["Data/raw_pdfs/new_policy.pdf"]}'
```

## Testing

### Test Endpoints

#### GET /test/embedding

Test embedding generation functionality.

**Response:**
```json
{
  "status": "success",
  "embedding_dimension": 384,
  "model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "test_text": "This is a test sentence for embedding generation."
}
```

#### GET /test/chroma

Test ChromaDB connection and basic operations.

**Response:**
```json
{
  "status": "success",
  "connection": "healthy",
  "collections": ["hr_policies", "merchant_faqs"],
  "total_documents": 1700
}
```

## Monitoring

### Metrics Endpoint

#### GET /metrics

Get system metrics and performance data.

**Response:**
```json
{
  "requests_total": 15420,
  "requests_per_minute": 45,
  "average_response_time": 1.23,
  "error_rate": 0.02,
  "active_connections": 12,
  "memory_usage": "256MB",
  "cpu_usage": "15%"
}
```

## Changelog

### Version 1.0.0
- Initial API release
- HR policy querying
- Merchant FAQ support
- Basic health checks

### Version 1.1.0 (Planned)
- WebSocket support
- Advanced caching
- Performance improvements
- Enhanced error handling
