# Tokenization Service

## Overview

The `TokenizationService` is responsible for text chunking, embedding generation, and source mapping in the RAG Chatbot API. It transforms large text documents into smaller, manageable chunks and converts them into vector embeddings for semantic search.

## Key Responsibilities

- **Text Chunking**: Split documents into token-bounded chunks
- **Embedding Generation**: Create vector representations of text
- **Source Mapping**: Maintain traceability between chunks and source documents
- **Question Embedding**: Generate embeddings for user queries
- **Context Preparation**: Format chunks for LLM consumption

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Text Input    │───►│  Tokenization   │───►│  Text Chunks    │
│                 │    │     Service     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Embedding      │
                       │  Generation     │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Vector         │
                       │  Embeddings     │
                       └─────────────────┘
```

## Configuration

### Model Configuration

```python
# Default configuration
model_name = "sentence-transformers/all-MiniLM-L6-v2"
chunk_size_tokens = 512
chunk_overlap_tokens = 50
```

### Device Selection

```python
def get_device(self) -> str:
    if torch.cuda.is_available():
        return 'cuda'
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return 'mps'
    else:
        return 'cpu'
```

## API Reference

### Class: TokenizationService

#### Constructor

```python
def __init__(
    self,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    chunk_size_tokens: int = 512,
    chunk_overlap_tokens: int = 50,
    progress: bool = True
):
```

**Parameters**:
- `model_name`: Hugging Face model name for embeddings
- `chunk_size_tokens`: Maximum tokens per chunk
- `chunk_overlap_tokens`: Overlap between consecutive chunks
- `progress`: Show progress bars during processing

#### Methods

##### `split_into_chunks_by_tokens(text: str, max_tokens: int = None, overlap: int = None) -> List[str]`

Split text into token-bounded chunks using the current tokenizer.

**Parameters**:
- `text`: Input text to chunk
- `max_tokens`: Maximum tokens per chunk (defaults to instance setting)
- `overlap`: Overlap between chunks (defaults to instance setting)

**Returns**:
- `List[str]`: List of text chunks

**Example**:
```python
service = TokenizationService()
chunks = await service.split_into_chunks_by_tokens(
    "Long document text...",
    max_tokens=512,
    overlap=50
)
print(f"Created {len(chunks)} chunks")
```

##### `generate_embeddings(texts: List[str]) -> torch.Tensor`

Generate embeddings for a list of text chunks.

**Parameters**:
- `texts`: List of text strings to embed

**Returns**:
- `torch.Tensor`: Tensor of embeddings (shape: [num_texts, embedding_dim])

**Example**:
```python
chunks = ["chunk 1", "chunk 2", "chunk 3"]
embeddings = await service.generate_embeddings(chunks)
print(f"Embeddings shape: {embeddings.shape}")
```

##### `embed_question(question: str) -> List[float]`

Generate embedding for a single question.

**Parameters**:
- `question`: Question text to embed

**Returns**:
- `List[float]`: Embedding vector as list

**Example**:
```python
question = "What is the travel policy?"
embedding = await service.embed_question(question)
print(f"Question embedding: {len(embedding)} dimensions")
```

##### `prepare_llm_context(flat_chunks: List[str]) -> str`

Prepare context from chunks for LLM consumption.

**Parameters**:
- `flat_chunks`: List of text chunks

**Returns**:
- `str`: Formatted context string

**Example**:
```python
chunks = ["context 1", "context 2", "context 3"]
context = await service.prepare_llm_context(chunks)
print(f"Context length: {len(context)} characters")
```

## Usage Examples

### Basic Text Chunking

```python
from services.tokenization_service import TokenizationService

async def chunk_document():
    service = TokenizationService()
    
    # Read document text
    with open("document.txt", "r") as f:
        text = f.read()
    
    # Split into chunks
    chunks = await service.split_into_chunks_by_tokens(text)
    
    print(f"Document split into {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i}: {len(chunk)} characters")
```

### Embedding Generation

```python
async def generate_embeddings():
    service = TokenizationService()
    
    # Sample text chunks
    texts = [
        "This is the first chunk of text.",
        "This is the second chunk of text.",
        "This is the third chunk of text."
    ]
    
    # Generate embeddings
    embeddings = await service.generate_embeddings(texts)
    
    print(f"Generated embeddings: {embeddings.shape}")
    return embeddings
```

### Complete Pipeline

```python
async def process_document():
    service = TokenizationService()
    
    # 1. Read and chunk document
    with open("document.txt", "r") as f:
        text = f.read()
    
    chunks = await service.split_into_chunks_by_tokens(text)
    
    # 2. Generate embeddings
    embeddings = await service.generate_embeddings(chunks)
    
    # 3. Store in ChromaDB
    chroma_client = get_chroma_client()
    
    metadatas = [
        {
            "source_file": "document.txt",
            "chunk_index": i,
            "created_at": datetime.now().isoformat()
        }
        for i in range(len(chunks))
    ]
    
    chroma_client.add_documents(
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )
    
    print(f"Processed {len(chunks)} chunks")
```

## Performance Considerations

### Memory Management

- **Batch Processing**: Process chunks in batches to manage memory
- **GPU Utilization**: Automatically use GPU if available
- **Progress Tracking**: Show progress for long operations

### Optimization Tips

1. **Chunk Size**: Balance between context and performance
2. **Overlap**: Ensure semantic continuity between chunks
3. **Batch Size**: Optimize for available memory
4. **Model Selection**: Choose appropriate model for your use case

## Error Handling

### Common Errors

1. **Model Loading Errors**
   ```python
   try:
       service = TokenizationService()
   except Exception as e:
       print(f"Failed to load model: {e}")
   ```

2. **Memory Errors**
   ```python
   # Reduce batch size for large documents
   service = TokenizationService()
   chunks = await service.split_into_chunks_by_tokens(
       text, max_tokens=256  # Smaller chunks
   )
   ```

3. **Tokenization Errors**
   ```python
   # Handle special characters
   text = clean_text_for_tokenization(text)
   chunks = await service.split_into_chunks_by_tokens(text)
   ```

## Integration

### With File Processing Service

```python
from services.file_processing_service import FileProcessingService
from services.tokenization_service import TokenizationService

async def full_pipeline():
    # Process files
    file_service = FileProcessingService()
    results = await file_service.process_files(["document.pdf"])
    
    # Tokenize and embed
    token_service = TokenizationService()
    
    for cleaned_file in results['cleaned_files']:
        with open(cleaned_file, 'r') as f:
            text = f.read()
        
        chunks = await token_service.split_into_chunks_by_tokens(text)
        embeddings = await token_service.generate_embeddings(chunks)
        
        # Store in database...
```

### With ChromaDB

```python
from lib.chromaDBClient import get_chroma_client

async def store_embeddings(chunks, embeddings, metadata):
    chroma_client = get_chroma_client()
    
    chroma_client.add_documents(
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadata
    )
```

## Testing

### Unit Tests

```python
import pytest
from services.tokenization_service import TokenizationService

@pytest.mark.asyncio
async def test_chunking():
    service = TokenizationService()
    
    text = "This is a test document. " * 100  # Long text
    chunks = await service.split_into_chunks_by_tokens(text)
    
    assert len(chunks) > 1
    assert all(len(chunk) > 0 for chunk in chunks)

@pytest.mark.asyncio
async def test_embedding():
    service = TokenizationService()
    
    texts = ["Test text 1", "Test text 2"]
    embeddings = await service.generate_embeddings(texts)
    
    assert embeddings.shape[0] == 2
    assert embeddings.shape[1] == 384  # Model dimension
```

## Troubleshooting

### Common Issues

1. **Model Download Fails**
   - Check internet connection
   - Verify model name is correct
   - Clear model cache if needed

2. **Memory Issues**
   - Reduce chunk size
   - Process documents in smaller batches
   - Use CPU instead of GPU if needed

3. **Slow Performance**
   - Use GPU if available
   - Increase batch size
   - Optimize chunk size and overlap

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

service = TokenizationService(progress=True)
# Detailed logging will be shown
```
