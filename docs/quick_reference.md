# Quick Reference Guide - HR Policy QA System Services

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install pymupdf sentence-transformers transformers torch tqdm
```

### 2. Basic Usage

#### FileProcessingService
```python
from services.file_processing_service import FileProcessingService

# Initialize
file_processor = FileProcessingService()

# Process PDFs
pdf_files = ["document1.pdf", "document2.pdf"]
cleaned_files = file_processor.prepare_cleaned_txt_files(pdf_files)
```

#### TokenizationService
```python
from services.tokenization_service import TokenizationService
from pathlib import Path

# Initialize
tokenizer = TokenizationService()

# Process cleaned text files
cleaned_files = list(Path("Data").glob("*_cleaned.txt"))
result = tokenizer.run_pipeline_with_defaults(cleaned_files)
```

## 📁 Directory Structure

```
Data/
├── unprocessed_files/     # 📄 Place PDF files here
├── raw_txt_files/        # 📝 Raw extracted text
├── cleaned_txt_files/    # ✨ Cleaned text
├── chunks/               # 📦 Text chunks (JSON)
├── embeddings/           # 🔢 Embedding tensors (.pt)
└── source_maps/          # 🗺️ Source mapping (JSON)
```

## 🔧 Common Operations

### Process New PDF Documents
```python
# 1. Copy PDFs to Data/unprocessed_files/
# 2. Run file processing
file_processor = FileProcessingService()
cleaned_files = file_processor.prepare_cleaned_txt_files(["new_document.pdf"])

# 3. Run tokenization
tokenizer = TokenizationService()
result = tokenizer.run_pipeline_with_defaults([Path(f) for f in cleaned_files])
```

### Load Existing Embeddings
```python
from services.tokenization_service import TokenizationService
import torch

tokenizer = TokenizationService()
embeddings = tokenizer.load_embeddings(Path("Data/embeddings/embeddings.pt"))
source_map = tokenizer.load_source_map(Path("Data/source_maps/source_map.json"))
```

### Custom Chunking
```python
tokenizer = TokenizationService(chunk_size_tokens=256, chunk_overlap_tokens=25)
chunks = tokenizer.split_into_chunks_by_tokens(long_text)
```

## ⚙️ Configuration Options

### TokenizationService Parameters
```python
tokenizer = TokenizationService(
    model_name="sentence-transformers/all-MiniLM-L6-v2",  # Embedding model
    chunk_size_tokens=512,                                # Max tokens per chunk
    chunk_overlap_tokens=50,                              # Overlap between chunks
    progress=True                                         # Show progress bars
)
```

### Recommended Models
- `sentence-transformers/all-MiniLM-L6-v2` (384d, fast)
- `sentence-transformers/all-mpnet-base-v2` (768d, high quality)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilingual)

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'fitz'` | `pip install pymupdf` |
| CUDA Out of Memory | Reduce `batch_size` or use CPU |
| Token sequence too long | Reduce `chunk_size_tokens` |
| Directory not found | Services create directories automatically |

## 📊 Output Files

### After FileProcessingService
- `Data/raw_txt_files/*.txt` - Raw extracted text
- `Data/cleaned_txt_files/*_cleaned.txt` - Cleaned text

### After TokenizationService
- `Data/chunks/*_chunks.json` - Text chunks
- `Data/embeddings/embeddings.pt` - Embedding tensor
- `Data/source_maps/source_map.json` - Source mapping

## 🔍 Source Map Structure
```json
[
  {
    "source_file": "path/to/document.txt",
    "chunk_index": 0,
    "embedding_index": 0
  }
]
```

## 📈 Performance Tips

1. **Use GPU if available** - Automatically detected
2. **Adjust batch size** - `batch_size=16` for large documents
3. **Process in batches** - For very large document collections
4. **Monitor memory usage** - Reduce chunk size if needed

## 🎯 Complete Pipeline Example
```python
from services.file_processing_service import FileProcessingService
from services.tokenization_service import TokenizationService
from pathlib import Path

def process_documents(pdf_files):
    # Step 1: Extract and clean text
    file_processor = FileProcessingService()
    cleaned_files = file_processor.prepare_cleaned_txt_files(pdf_files)
    
    # Step 2: Generate embeddings
    tokenizer = TokenizationService()
    cleaned_paths = [Path(f) for f in cleaned_files]
    result = tokenizer.run_pipeline_with_defaults(cleaned_paths)
    
    return result

# Usage
result = process_documents(["hr_policy.pdf", "travel_guide.pdf"])
print(f"Processed {result['total_chunks']} chunks")
```

## 📞 Need Help?

1. Check the full documentation in `docs/services_documentation.md`
2. Review error messages for specific guidance
3. Ensure all dependencies are installed
4. Verify file permissions and directory access
