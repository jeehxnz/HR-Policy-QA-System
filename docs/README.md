# HR Policy QA System - Documentation

Welcome to the documentation for the HR Policy QA System services. This directory contains comprehensive documentation for understanding and using the system's core services.

## 📚 Documentation Files

### [Services Documentation](services_documentation.md)
**Complete technical documentation** for both FileProcessingService and TokenizationService.

**Includes:**
- Detailed API reference
- Method descriptions and parameters
- Complete usage examples
- Configuration options
- Troubleshooting guide
- Performance optimization tips

**Best for:** Developers who need comprehensive technical details and API reference.

### [Quick Reference Guide](quick_reference.md)
**Concise reference** for common operations and quick setup.

**Includes:**
- Quick start guide
- Common code snippets
- Directory structure overview
- Troubleshooting table
- Performance tips

**Best for:** Developers who need quick answers and common patterns.

## 🎯 Getting Started

### For New Users
1. Start with the [Quick Reference Guide](quick_reference.md) for basic setup
2. Review the [Services Documentation](services_documentation.md) for detailed understanding

### For Experienced Users
1. Use the [Quick Reference Guide](quick_reference.md) for common operations
2. Refer to the [Services Documentation](services_documentation.md) for specific API details

## 🏗️ System Architecture

The HR Policy QA System consists of two main services:

### FileProcessingService
- **Purpose:** PDF text extraction and cleaning
- **Input:** PDF files in `Data/unprocessed_files/`
- **Output:** Cleaned text files in `Data/cleaned_txt_files/`
- **Key Features:** Text extraction, cleaning, normalization

### TokenizationService
- **Purpose:** Text chunking and embedding generation
- **Input:** Cleaned text files
- **Output:** Embeddings, chunks, and source mapping
- **Key Features:** Token-based chunking, embedding generation, source tracking

## 📁 Directory Structure

```
docs/
├── README.md                    # This file
├── services_documentation.md    # Complete technical documentation
└── quick_reference.md          # Quick reference guide
```

## 🔧 Quick Setup

```bash
# Install dependencies
pip install pymupdf sentence-transformers transformers torch tqdm

# Basic usage
from services.file_processing_service import FileProcessingService
from services.tokenization_service import TokenizationService

# Process PDFs
file_processor = FileProcessingService()
cleaned_files = file_processor.prepare_cleaned_txt_files(["document.pdf"])

# Generate embeddings
tokenizer = TokenizationService()
result = tokenizer.run_pipeline_with_defaults([Path(f) for f in cleaned_files])
```

## 📞 Support

If you need help:

1. **Check the documentation** - Most questions are answered in the guides above
2. **Review error messages** - Services provide detailed error information
3. **Verify setup** - Ensure dependencies and directories are correct
4. **Check examples** - Working examples are provided in both guides

## 🚀 Next Steps

After reading the documentation:

1. **Set up your environment** using the quick reference guide
2. **Process your first documents** following the examples
3. **Customize the configuration** based on your needs
4. **Integrate with your Q&A system** using the generated embeddings

The services are designed to be robust and well-documented, making it easy to get started and scale as needed.
