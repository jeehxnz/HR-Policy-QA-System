#!/usr/bin/env python3
"""
Complete Pipeline Example - HR Policy QA System

This script demonstrates the complete pipeline from PDF documents to embeddings
using both FileProcessingService and TokenizationService.

Usage:
    python examples/complete_pipeline_example.py
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.file_processing_service import FileProcessingService
from services.tokenization_service import TokenizationService
from config import DATA_DIR, UNPROCESSED_FILES_DIR, CLEANED_TXT_FILES_DIR

def main():
    """Run the complete pipeline example."""
    
    print("🚀 HR Policy QA System - Complete Pipeline Example")
    print("=" * 60)
    
    # Step 1: Check for PDF files
    print("\n📋 Step 1: Checking for PDF files...")
    pdf_files = list(UNPROCESSED_FILES_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {UNPROCESSED_FILES_DIR}")
        print("   Please place PDF files in the Data/unprocessed_files/ directory")
        return
    
    print(f"✅ Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        print(f"   - {pdf_file.name}")
    
    # Step 2: File Processing
    print(f"\n📄 Step 2: Processing PDF files...")
    try:
        file_processor = FileProcessingService()
        
        # Get just the filenames for the service
        pdf_filenames = [pdf_file.name for pdf_file in pdf_files]
        
        # Process PDFs to cleaned text
        cleaned_files = file_processor.prepare_cleaned_txt_files(pdf_filenames)
        
        print(f"✅ Successfully processed {len(cleaned_files)} files")
        for file_path in cleaned_files:
            print(f"   - {Path(file_path).name}")
            
    except Exception as e:
        print(f"❌ Error during file processing: {e}")
        return
    
    # Step 3: Tokenization and Embedding
    print(f"\n🔢 Step 3: Generating embeddings...")
    try:
        # Initialize tokenization service
        tokenizer = TokenizationService(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            chunk_size_tokens=512,
            chunk_overlap_tokens=50,
            progress=True
        )
        
        # Convert file paths to Path objects
        cleaned_paths = [Path(file_path) for file_path in cleaned_files]
        
        # Run the complete tokenization pipeline
        result = tokenizer.run_pipeline_with_defaults(cleaned_paths)
        
        print(f"✅ Tokenization pipeline completed successfully!")
        print(f"\n📊 Results Summary:")
        print(f"   - Files processed: {result['num_files_processed']}")
        print(f"   - Chunk files created: {result['num_chunk_files']}")
        print(f"   - Total chunks generated: {result['total_chunks']}")
        print(f"   - Embedding dimension: {result['embedding_dim']}")
        print(f"   - Chunks directory: {result['chunks_out_dir']}")
        print(f"   - Embeddings file: {result['embeddings_out_path']}")
        print(f"   - Source map file: {result['source_map_out_path']}")
        
    except Exception as e:
        print(f"❌ Error during tokenization: {e}")
        return
    
    # Step 4: Verify output files
    print(f"\n🔍 Step 4: Verifying output files...")
    
    # Check chunks directory
    chunks_dir = Path(result['chunks_out_dir'])
    chunk_files = list(chunks_dir.glob("*.json"))
    print(f"   - Chunk files: {len(chunk_files)} found")
    
    # Check embeddings file
    embeddings_path = Path(result['embeddings_out_path'])
    if embeddings_path.exists():
        print(f"   - Embeddings file: ✅ {embeddings_path.name}")
    else:
        print(f"   - Embeddings file: ❌ Not found")
    
    # Check source map file
    source_map_path = Path(result['source_map_out_path'])
    if source_map_path.exists():
        print(f"   - Source map file: ✅ {source_map_path.name}")
    else:
        print(f"   - Source map file: ❌ Not found")
    
    print(f"\n🎉 Pipeline completed successfully!")
    print(f"   Your HR Policy QA System is ready to use!")
    
    # Step 5: Show how to use the results
    print(f"\n📖 Next Steps:")
    print(f"   1. Load embeddings: embeddings = torch.load('{embeddings_path}')")
    print(f"   2. Load source map: source_map = json.load(open('{source_map_path}'))")
    print(f"   3. Load chunks: chunks = json.load(open('{chunk_files[0]}'))")
    print(f"   4. Use for semantic search and Q&A!")

def show_usage_example():
    """Show how to use the generated embeddings."""
    print(f"\n💡 Usage Example:")
    print(f"""
# Load the generated files
import torch
import json
from pathlib import Path

# Load embeddings
embeddings = torch.load('Data/embeddings/embeddings.pt')
print(f"Embeddings shape: {{embeddings.shape}}")

# Load source map
with open('Data/source_maps/source_map.json', 'r') as f:
    source_map = json.load(f)
print(f"Source map entries: {{len(source_map)}}")

# Load chunks (example for first file)
chunk_files = list(Path('Data/chunks').glob('*.json'))
if chunk_files:
    with open(chunk_files[0], 'r') as f:
        chunks = json.load(f)
    print(f"Chunks in first file: {{len(chunks)}}")

# Now you can use these for semantic search!
""")

if __name__ == "__main__":
    try:
        main()
        show_usage_example()
    except KeyboardInterrupt:
        print(f"\n⚠️  Pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
