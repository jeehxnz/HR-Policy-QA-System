# File Processing Service

## Overview

The `FileProcessingService` is responsible for handling document ingestion and text processing in the RAG Chatbot API. It provides functionality to convert PDF documents to text, clean and normalize text content, and prepare documents for further processing by the tokenization service.

## Purpose

The service serves as the first step in the document processing pipeline, taking raw PDF documents and converting them into clean, normalized text files that can be processed by downstream services.

## Key Responsibilities

- **PDF to Text Conversion**: Extract text content from PDF documents
- **Text Cleaning**: Remove formatting artifacts and normalize text
- **File Management**: Organize processed files in appropriate directories
- **Batch Processing**: Handle multiple documents efficiently
- **Error Handling**: Provide robust error handling for various file formats

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF Files     │───►│  File Processing │───►│  Cleaned Text   │
│   (Input)       │    │     Service     │    │   Files         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Error Logging  │
                       │   & Reporting   │
                       └─────────────────┘
```

## File Structure

The service operates on the following directory structure:

```
Data/
├── unprocessed_files/     # Original PDF documents
├── raw_txt_files/         # Extracted text files (UTF-8)
└── cleaned_txt_files/     # Normalized and cleaned text files
```

## Configuration

The service uses configuration from `config.py`:

```python
from config import (
    DATA_DIR,
    UNPROCESSED_FILES_DIR,
    RAW_TXT_FILES_DIR,
    CLEANED_TXT_FILES_DIR
)
```

## API Reference

### Class: FileProcessingService

#### Constructor

```python
def __init__(self):
    """
    Initialize the FileProcessingService with directory paths.
    """
```

#### Methods

##### `pdf_to_txt(file_names: list[str]) -> list[str]`

Convert one or more PDF files to plain-text files (UTF-8).

**Parameters:**
- `file_names` (list[str]): List of PDF filenames to process

**Returns:**
- `list[str]`: List of paths to successfully generated .txt files

**Example:**
```python
service = FileProcessingService()
txt_files = await service.pdf_to_txt(["document1.pdf", "document2.pdf"])
print(f"Generated {len(txt_files)} text files")
```

**Process:**
1. Validates file existence and PDF format
2. Opens PDF using PyMuPDF (fitz)
3. Extracts text from all pages
4. Writes text to UTF-8 encoded .txt file
5. Returns list of successful conversions

##### `clean_text(text: str) -> str`

Clean and normalize text by removing unwanted formatting and whitespace.

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

**Example:**
```python
raw_text = """
Page 1

    This is some text with    extra spaces.

Page 2

123
More text here.
"""

cleaned_text = await service.clean_text(raw_text)
# Result: "This is some text with extra spaces. More text here."
```

##### `write_cleaned_txt_file(file_names: list[str]) -> list[str]`

Read raw .txt files, clean them, and write new `*_cleaned.txt` files.

**Parameters:**
- `file_names` (list[str]): List of raw text filenames to process

**Returns:**
- `list[str]`: List of paths to successfully created cleaned text files

**Example:**
```python
raw_files = ["document1.txt", "document2.txt"]
cleaned_files = await service.write_cleaned_txt_file(raw_files)
print(f"Created {len(cleaned_files)} cleaned files")
```

##### `process_files(file_names: list[str]) -> dict`

Orchestrate the complete file processing pipeline.

**Parameters:**
- `file_names` (list[str]): List of PDF filenames to process

**Returns:**
- `dict`: Processing results with file counts and status

**Example:**
```python
pdf_files = ["policy1.pdf", "policy2.pdf"]
results = await service.process_files(pdf_files)

print(f"Processed {results['pdf_files']} PDF files")
print(f"Generated {results['txt_files']} text files")
print(f"Created {results['cleaned_files']} cleaned files")
```

**Pipeline Steps:**
1. Convert PDFs to text files
2. Clean and normalize text files
3. Generate processing report

## Usage Examples

### Basic Usage

```python
from services.file_processing_service import FileProcessingService

async def process_documents():
    service = FileProcessingService()
    
    # Process a single PDF
    pdf_files = ["employee_handbook.pdf"]
    results = await service.process_files(pdf_files)
    
    print(f"Processing complete: {results}")

# Run the processing
import asyncio
asyncio.run(process_documents())
```

### Batch Processing

```python
async def batch_process():
    service = FileProcessingService()
    
    # Process multiple PDFs
    pdf_files = [
        "hr_policy.pdf",
        "travel_guidelines.pdf",
        "benefits_guide.pdf"
    ]
    
    results = await service.process_files(pdf_files)
    
    if results['status'] == 'success':
        print(f"Successfully processed {results['pdf_files']} files")
    else:
        print(f"Processing failed: {results['errors']}")
```

### Error Handling

```python
async def robust_processing():
    service = FileProcessingService()
    
    try:
        results = await service.process_files(["document.pdf"])
        
        if results['errors']:
            print("Some files failed to process:")
            for error in results['errors']:
                print(f"- {error}")
        
    except Exception as e:
        print(f"Processing failed: {e}")
```

## Error Handling

### Common Errors

1. **File Not Found**
   ```
   Error: File not found -> /path/to/document.pdf
   ```

2. **Invalid File Format**
   ```
   Error: Not a PDF -> /path/to/document.txt
   ```

3. **PDF Processing Error**
   ```
   Error: Error extracting text from document.pdf: [error details]
   ```

4. **Text Cleaning Error**
   ```
   Error: Error cleaning text: [error details]
   ```

### Error Recovery

The service implements graceful error handling:

- **Individual File Failures**: Processing continues for other files
- **Detailed Error Reporting**: Specific error messages for each failure
- **Partial Success**: Returns successfully processed files even if some fail

## Performance Considerations

### Optimization Tips

1. **Batch Processing**: Process multiple files together for better efficiency
2. **Memory Management**: Large PDFs are processed page by page
3. **Async Operations**: All operations are asynchronous for better performance
4. **Error Isolation**: Individual file failures don't affect other files

### Resource Usage

- **Memory**: Minimal memory usage with page-by-page processing
- **CPU**: Moderate CPU usage during text extraction and cleaning
- **Disk I/O**: Sequential file operations for optimal performance

## Integration

### With Tokenization Service

The File Processing Service is typically used before the Tokenization Service:

```python
from services.file_processing_service import FileProcessingService
from services.tokenization_service import TokenizationService

async def full_pipeline():
    # Step 1: Process files
    file_service = FileProcessingService()
    results = await file_service.process_files(["document.pdf"])
    
    # Step 2: Tokenize and embed
    token_service = TokenizationService()
    cleaned_files = results['cleaned_files']
    
    for file_path in cleaned_files:
        with open(file_path, 'r') as f:
            text = f.read()
            chunks = await token_service.split_into_chunks_by_tokens(text)
            # Continue with embedding generation...
```

### With API Endpoints

The service can be called from API endpoints:

```python
@app.post("/process-documents")
async def process_documents_endpoint(request: DocumentProcessRequest):
    service = FileProcessingService()
    results = await service.process_files(request.file_paths)
    return results
```

## Testing

### Unit Tests

```python
import pytest
from services.file_processing_service import FileProcessingService

@pytest.mark.asyncio
async def test_pdf_to_txt():
    service = FileProcessingService()
    result = await service.pdf_to_txt(["test_document.pdf"])
    assert len(result) > 0
    assert all(file.endswith('.txt') for file in result)

@pytest.mark.asyncio
async def test_clean_text():
    service = FileProcessingService()
    raw_text = "  Test   text  with   spaces  \n\n\n"
    cleaned = await service.clean_text(raw_text)
    assert cleaned == "Test text with spaces"
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_pipeline():
    service = FileProcessingService()
    results = await service.process_files(["sample.pdf"])
    
    assert results['status'] == 'success'
    assert results['pdf_files'] == 1
    assert results['txt_files'] == 1
    assert results['cleaned_files'] == 1
```

## Troubleshooting

### Common Issues

1. **PDF Text Extraction Fails**
   - Check if PDF is password protected
   - Verify PDF contains extractable text (not just images)
   - Ensure PyMuPDF is properly installed

2. **Memory Issues with Large PDFs**
   - Process files individually instead of in batches
   - Monitor system memory usage
   - Consider splitting very large PDFs

3. **File Permission Errors**
   - Check read permissions for input files
   - Check write permissions for output directories
   - Ensure proper file ownership

### Debug Mode

Enable debug logging for detailed processing information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

service = FileProcessingService()
# Processing will now show detailed logs
```

## Future Enhancements

### Planned Features

1. **OCR Support**: Extract text from image-based PDFs
2. **Multiple Format Support**: Handle DOCX, RTF, and other formats
3. **Parallel Processing**: Process multiple files concurrently
4. **Progress Tracking**: Real-time progress reporting
5. **Compression Support**: Handle compressed PDF files

### Performance Improvements

1. **Streaming Processing**: Process large files without loading entirely into memory
2. **Caching**: Cache processed results for repeated operations
3. **Background Processing**: Process files asynchronously in the background
