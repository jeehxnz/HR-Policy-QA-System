# HR Policy QA System - Services Documentation

## Overview

This document provides comprehensive documentation for the two core services in the HR Policy QA System:

1. **FileProcessingService** - Handles PDF text extraction and cleaning
2. **TokenizationService** - Manages text chunking, embedding generation, and source mapping

## Table of Contents

- [FileProcessingService](#fileprocessingservice)
- [TokenizationService](#tokenizationservice)
- [Complete Pipeline Example](#complete-pipeline-example)
- [Directory Structure](#directory-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## FileProcessingService

### Overview

The `FileProcessingService` is responsible for converting PDF documents into clean, structured text files. It handles the initial data processing pipeline from raw PDFs to cleaned text ready for further processing.

### Key Features

- **PDF Text Extraction** - Extracts text from PDF files using PyMuPDF
- **Text Cleaning** - Normalizes and cleans extracted text
- **Organized Output** - Saves files in structured directories
- **Error Handling** - Robust error handling with detailed logging

### Directory Structure

```
Data/
├── unprocessed_files/     # Input PDF files
├── raw_txt_files/        # Raw extracted text
└── cleaned_txt_files/    # Cleaned and normalized text
```

### Class Definition

```python
class FileProcessingService:
    def __init__(self):
        self.__UNPROCESSED_PDF_DIR = DATA_DIR / "unprocessed_files"
        self.__RAW_TXT_DIR = DATA_DIR / "raw_txt_files"
        self.__CLEANED_TXT_DIR = DATA_DIR / "cleaned_txt_files"
```

### Methods

#### `prepare_cleaned_txt_files(file_names: list[str]) -> list[str]`

**Purpose:** Complete pipeline to convert PDFs to cleaned text files.

**Parameters:**
- `file_names` (list[str]): List of PDF filenames to process

**Returns:**
- `list[str]`: Paths to the generated cleaned text files

**Example:**
```python
from services.file_processing_service import FileProcessingService

# Initialize service
file_processor = FileProcessingService()

# Process PDF files
pdf_files = ["hr_policy.pdf", "travel_guide.pdf"]
cleaned_files = file_processor.prepare_cleaned_txt_files(pdf_files)

print(f"Generated {len(cleaned_files)} cleaned text files")
```

#### `__pdf_to_txt(file_names: list[str]) -> list[str]`

**Purpose:** Extract text from PDF files and save as raw text files.

**Parameters:**
- `file_names` (list[str]): List of PDF filenames

**Returns:**
- `list[str]`: Paths to generated raw text files

**Process:**
1. Reads PDF files from `unprocessed_files/` directory
2. Extracts text from all pages
3. Saves as `.txt` files in `raw_txt_files/` directory

#### `__clean_text(text: str) -> str`

**Purpose:** Clean and normalize extracted text.

**Parameters:**
- `text` (str): Raw text to clean

**Returns:**
- `str`: Cleaned and normalized text

**Cleaning Steps:**
1. Remove lines containing only numbers
2. Collapse multiple newlines into single newlines
3. Collapse multiple spaces into single spaces
4. Strip whitespace from each line
5. Remove empty lines
6. Join all lines into a single paragraph

#### `__write_cleaned_txt_file(file_names: list[str]) -> list[str]`

**Purpose:** Read raw text files, clean them, and save as cleaned text files.

**Parameters:**
- `file_names` (list[str]): List of raw text file paths

**Returns:**
- `list[str]`: Paths to generated cleaned text files

**Process:**
1. Reads raw text files from `raw_txt_files/` directory
2. Applies text cleaning
3. Saves as `*_cleaned.txt` files in `cleaned_txt_files/` directory

### Usage Example

```python
from services.file_processing_service import FileProcessingService
from pathlib import Path

# Initialize service
file_processor = FileProcessingService()

# List PDF files to process
pdf_files = [
    "bKash HR Service Rules Handbook 2025.pdf",
    "Workplace Anti Harassment Guideline.pdf",
    "Employee Travel and Transfer Guideline.pdf"
]

# Process all PDFs
try:
    cleaned_files = file_processor.prepare_cleaned_txt_files(pdf_files)
    print(f"Successfully processed {len(cleaned_files)} files")
    
    for file_path in cleaned_files:
        print(f"  - {Path(file_path).name}")
        
except RuntimeError as e:
    print(f"Error processing files: {e}")
```

---

## TokenizationService

### Overview

The `TokenizationService` handles text chunking, embedding generation, and source mapping. It converts cleaned text files into numerical representations suitable for semantic search and Q&A systems.

### Key Features

- **Token-based Chunking** - Splits text into token-bounded chunks
- **Embedding Generation** - Creates vector representations using Sentence-Transformers
- **Source Mapping** - Maintains traceability between embeddings and source documents
- **Batch Processing** - Efficient processing of large document collections
- **Flexible Configuration** - Customizable chunk sizes and overlap

### Directory Structure

```
Data/
├── chunks/           # JSON chunk files
├── embeddings/       # PyTorch tensor files
└── source_maps/      # JSON source mapping files
```

### Class Definition

```python
class TokenizationService:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size_tokens: int = 512,
        chunk_overlap_tokens: int = 50,
        progress: bool = True,
    ) -> None:
```

### Parameters

- **`model_name`** (str): Sentence-Transformers model for embeddings
- **`chunk_size_tokens`** (int): Maximum tokens per chunk (default: 512)
- **`chunk_overlap_tokens`** (int): Overlap between chunks (default: 50)
- **`progress`** (bool): Show progress bars (default: True)

### Methods

#### `run_pipeline_with_defaults(cleaned_txt_files, batch_size=32) -> Dict[str, Any]`

**Purpose:** Complete pipeline using default directory structure.

**Parameters:**
- `cleaned_txt_files` (Iterable[Path]): Cleaned text files to process
- `batch_size` (int): Batch size for embedding generation
- `embeddings_filename` (str): Name for embeddings file
- `source_map_filename` (str): Name for source map file

**Returns:**
- `Dict[str, Any]`: Processing summary with statistics

**Example:**
```python
from services.tokenization_service import TokenizationService
from pathlib import Path

# Initialize service
tokenizer = TokenizationService(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    chunk_size_tokens=512,
    chunk_overlap_tokens=50
)

# Find cleaned text files
cleaned_files = list(Path("Data").glob("*_cleaned.txt"))

# Run pipeline
result = tokenizer.run_pipeline_with_defaults(cleaned_files)

print(f"Processed {result['num_files_processed']} files")
print(f"Generated {result['total_chunks']} chunks")
print(f"Embedding dimension: {result['embedding_dim']}")
```

#### `split_into_chunks_by_tokens(text, max_tokens=None, overlap=None) -> List[str]`

**Purpose:** Split text into token-bounded chunks.

**Parameters:**
- `text` (str): Input text to chunk
- `max_tokens` (Optional[int]): Override chunk size
- `overlap` (Optional[int]): Override overlap size

**Returns:**
- `List[str]`: List of text chunks

**Example:**
```python
text = "Your long document text here..."
chunks = tokenizer.split_into_chunks_by_tokens(text, max_tokens=256)
print(f"Split into {len(chunks)} chunks")
```

#### `encode_chunks(chunks, batch_size=32) -> torch.Tensor`

**Purpose:** Generate embeddings for text chunks.

**Parameters:**
- `chunks` (List[str]): List of text chunks
- `batch_size` (int): Batch size for processing
- `convert_to_tensor` (bool): Return as tensor
- `show_progress_bar` (Optional[bool]): Show progress

**Returns:**
- `torch.Tensor`: Embeddings tensor of shape [num_chunks, embedding_dim]

**Example:**
```python
embeddings = tokenizer.encode_chunks(chunks, batch_size=16)
print(f"Embeddings shape: {embeddings.shape}")
```

#### `chunk_file(in_path, out_path=None) -> Path`

**Purpose:** Process a single text file into chunks.

**Parameters:**
- `in_path` (Path): Input text file path
- `out_path` (Optional[Path]): Output JSON file path

**Returns:**
- `Path`: Path to generated chunk JSON file

**Example:**
```python
chunk_file = tokenizer.chunk_file(
    Path("Data/document_cleaned.txt"),
    Path("Data/chunks/document_chunks.json")
)
```

#### `build_source_map(chunk_index_lists) -> List[Dict[str, Any]]`

**Purpose:** Create mapping between chunks and embeddings.

**Parameters:**
- `chunk_index_lists` (Dict[str, List[str]]): Mapping of source files to chunks

**Returns:**
- `List[Dict[str, Any]]`: Source mapping with metadata

**Structure:**
```json
[
  {
    "source_file": "path/to/document.txt",
    "chunk_index": 0,
    "embedding_index": 0
  }
]
```

### Configuration Methods

#### `get_default_chunks_dir() -> Path`
Returns the default chunks directory (`Data/chunks/`).

#### `get_default_embeddings_path(filename="embeddings.pt") -> Path`
Returns the default embeddings file path.

#### `get_default_source_map_path(filename="source_map.json") -> Path`
Returns the default source map file path.

### Utility Methods

#### `count_tokens(text: str) -> int`
Count tokens in text using the current tokenizer.

#### `validate_chunk_params(max_tokens: int, overlap: int) -> None`
Validate chunking parameters and raise errors if invalid.

#### `save_embeddings(tensor: torch.Tensor, out_path: Path) -> Path`
Save embeddings tensor to disk.

#### `load_embeddings(path: Path) -> torch.Tensor`
Load embeddings tensor from disk.

---

## Complete Pipeline Example

### End-to-End Processing

```python
from services.file_processing_service import FileProcessingService
from services.tokenization_service import TokenizationService
from pathlib import Path

def process_hr_documents():
    """Complete pipeline to process HR documents."""
    
    # Step 1: File Processing
    print("Step 1: Processing PDF files...")
    file_processor = FileProcessingService()
    
    pdf_files = [
        "bKash HR Service Rules Handbook 2025.pdf",
        "Workplace Anti Harassment Guideline.pdf",
        "Employee Travel and Transfer Guideline.pdf",
        "Group Anti-Bribery and Corruption Policy.pdf"
    ]
    
    cleaned_files = file_processor.prepare_cleaned_txt_files(pdf_files)
    print(f"Generated {len(cleaned_files)} cleaned text files")
    
    # Step 2: Tokenization and Embedding
    print("\nStep 2: Generating embeddings...")
    tokenizer = TokenizationService(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        chunk_size_tokens=512,
        chunk_overlap_tokens=50
    )
    
    # Convert file paths to Path objects
    cleaned_paths = [Path(file_path) for file_path in cleaned_files]
    
    # Run tokenization pipeline
    result = tokenizer.run_pipeline_with_defaults(cleaned_paths)
    
    print(f"Processing complete!")
    print(f"  - Files processed: {result['num_files_processed']}")
    print(f"  - Total chunks: {result['total_chunks']}")
    print(f"  - Embedding dimension: {result['embedding_dim']}")
    print(f"  - Chunks directory: {result['chunks_out_dir']}")
    print(f"  - Embeddings file: {result['embeddings_out_path']}")
    print(f"  - Source map file: {result['source_map_out_path']}")

if __name__ == "__main__":
    process_hr_documents()
```

### Output Structure

After running the complete pipeline, you'll have:

```
Data/
├── unprocessed_files/
│   ├── bKash HR Service Rules Handbook 2025.pdf
│   ├── Workplace Anti Harassment Guideline.pdf
│   └── ...
├── raw_txt_files/
│   ├── bKash HR Service Rules Handbook 2025.txt
│   ├── Workplace Anti Harassment Guideline.txt
│   └── ...
├── cleaned_txt_files/
│   ├── bKash HR Service Rules Handbook 2025_cleaned.txt
│   ├── Workplace Anti Harassment Guideline_cleaned.txt
│   └── ...
├── chunks/
│   ├── bKash HR Service Rules Handbook 2025_cleaned_chunks.json
│   ├── Workplace Anti Harassment Guideline_cleaned_chunks.json
│   └── ...
├── embeddings/
│   └── embeddings.pt
└── source_maps/
    └── source_map.json
```

---

## Configuration

### Environment Setup

1. **Install Dependencies:**
```bash
pip install pymupdf sentence-transformers transformers torch tqdm
```

2. **Directory Structure:**
The services automatically create necessary directories:
- `Data/unprocessed_files/` - Place PDF files here
- `Data/raw_txt_files/` - Raw extracted text
- `Data/cleaned_txt_files/` - Cleaned text
- `Data/chunks/` - Text chunks
- `Data/embeddings/` - Embedding tensors
- `Data/source_maps/` - Source mapping files

### Model Configuration

**Recommended Models:**
- `sentence-transformers/all-MiniLM-L6-v2` (default, 384 dimensions)
- `sentence-transformers/all-mpnet-base-v2` (768 dimensions, higher quality)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilingual)

**Chunking Parameters:**
- **Chunk Size:** 512 tokens (good balance between context and efficiency)
- **Overlap:** 50 tokens (prevents information loss at chunk boundaries)

---

## Troubleshooting

### Common Issues

#### 1. **ModuleNotFoundError: No module named 'fitz'**
**Solution:** Install PyMuPDF
```bash
pip install pymupdf
```

#### 2. **CUDA Out of Memory**
**Solution:** Reduce batch size or use CPU
```python
tokenizer = TokenizationService()
embeddings = tokenizer.encode_chunks(chunks, batch_size=8)  # Smaller batch
```

#### 3. **Token Sequence Too Long**
**Solution:** Reduce chunk size
```python
tokenizer = TokenizationService(chunk_size_tokens=256)
```

#### 4. **Directory Not Found**
**Solution:** Services create directories automatically, but ensure write permissions.

### Performance Optimization

1. **Use GPU if available:**
```python
# Check device
print(f"Using device: {tokenizer.get_device()}")
```

2. **Adjust batch size based on memory:**
```python
# For large documents
embeddings = tokenizer.encode_chunks(chunks, batch_size=16)
```

3. **Process files in batches:**
```python
# For very large document collections
for batch in file_batches:
    result = tokenizer.run_pipeline_with_defaults(batch)
```

### Error Handling

Both services include comprehensive error handling:

```python
try:
    result = file_processor.prepare_cleaned_txt_files(pdf_files)
except RuntimeError as e:
    print(f"File processing error: {e}")
    # Handle error appropriately

try:
    result = tokenizer.run_pipeline_with_defaults(cleaned_files)
except Exception as e:
    print(f"Tokenization error: {e}")
    # Handle error appropriately
```

---

## API Reference

### FileProcessingService

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `prepare_cleaned_txt_files` | `file_names: list[str]` | `list[str]` | Complete PDF to cleaned text pipeline |
| `__pdf_to_txt` | `file_names: list[str]` | `list[str]` | Extract text from PDFs |
| `__clean_text` | `text: str` | `str` | Clean and normalize text |
| `__write_cleaned_txt_file` | `file_names: list[str]` | `list[str]` | Write cleaned text files |

### TokenizationService

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `run_pipeline_with_defaults` | `cleaned_txt_files, batch_size=32` | `Dict[str, Any]` | Complete pipeline with defaults |
| `run_pipeline` | `cleaned_txt_files, chunks_out_dir, embeddings_out_path, source_map_out_path` | `Dict[str, Any]` | Complete pipeline with custom paths |
| `split_into_chunks_by_tokens` | `text, max_tokens=None, overlap=None` | `List[str]` | Split text into chunks |
| `encode_chunks` | `chunks, batch_size=32` | `torch.Tensor` | Generate embeddings |
| `chunk_file` | `in_path, out_path=None` | `Path` | Process single file |
| `build_source_map` | `chunk_index_lists` | `List[Dict[str, Any]]` | Create source mapping |
| `count_tokens` | `text: str` | `int` | Count tokens in text |
| `save_embeddings` | `tensor, out_path` | `Path` | Save embeddings |
| `load_embeddings` | `path` | `torch.Tensor` | Load embeddings |

---

## Version History

- **v1.0.0** - Initial implementation with basic PDF processing and tokenization
- **v1.1.0** - Added source mapping and improved error handling
- **v1.2.0** - Added automatic directory creation and default paths
- **v1.3.0** - Enhanced documentation and examples

---

## Support

For issues, questions, or contributions:

1. Check the troubleshooting section above
2. Review the error messages for specific guidance
3. Ensure all dependencies are properly installed
4. Verify file permissions and directory access

The services are designed to be robust and provide clear error messages to help with debugging.
