import sys
import json
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
from dotenv import load_dotenv
from services.file_processing_service import FileProcessingService
from services.tokenization_service import TokenizationService
from lib.chromaDBClient import ChromaDBClient
from config import (
    CHROMA_DB_DIR,
    UNPROCESSED_FILES_DIR,
    CHUNKS_DIR,
    EMBEDDINGS_DIR,
)

load_dotenv()
ENGLISH_MERCHANT_FAQ_COLLECTION_NAME = os.environ.get('ENGLISH_MERCHANT_FAQ_COLLECTION_NAME')
ENGLISH_SENTENCE_TRANSFORMER_MODEL = os.environ.get('ENGLISH_SENTENCE_TRANSFORMER_MODEL')



async def main():
    assert isinstance(ENGLISH_SENTENCE_TRANSFORMER_MODEL, str)
    assert isinstance(ENGLISH_MERCHANT_FAQ_COLLECTION_NAME, str)
    collection_name = ENGLISH_MERCHANT_FAQ_COLLECTION_NAME

    file_name = input("Enter the file name of the file you want to process: ")

    file_processing_service = FileProcessingService()
    tokenization_service = TokenizationService(
        model_name=ENGLISH_SENTENCE_TRANSFORMER_MODEL,
        chunk_size_tokens=510,  # not 512
        chunk_overlap_tokens=50,
    )
    chroma_client = ChromaDBClient(COLLECTION_NAME=collection_name, CHROMA_DB_PATH=CHROMA_DB_DIR)
    chroma_client.initialize()

    # Empty out tmp dirs (do not clear UNPROCESSED_FILES_DIR so PDFs remain)
    file_processing_service.clear_tmp_file_dirs(False)

    # Find the file in the unprocessed directory
    file_path = UNPROCESSED_FILES_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_name} not found in {UNPROCESSED_FILES_DIR}")
    
    print(f"Processing file: {file_path}")

    # 2) Convert to cleaned text (auto-detects file types)
    cleaned_files = await file_processing_service.prepare_cleaned_txt_files([file_name])
    cleaned_paths = [Path(p) for p in cleaned_files]

    # 3) Run tokenization pipeline (chunks + embeddings + source map)
    result = await tokenization_service.run_pipeline_with_defaults(
        cleaned_paths,
        embeddings_filename=f"{collection_name}_embeddings.pt",
        source_map_filename=f"{collection_name}_source_map.json",
    )
    print("Tokenization pipeline complete:")
    print(json.dumps(result, indent=2))

    # 4) Load chunks and metadatas via helper
    payload = tokenization_service.load_all_chunks_for_files(cleaned_paths, CHUNKS_DIR)
    all_chunks = payload["documents"]
    all_metadatas = payload["metadatas"]

    # 5) Load embeddings via helper
    embeddings_path = EMBEDDINGS_DIR / f"{collection_name}_embeddings.pt"
    embeddings = tokenization_service.load_embeddings(embeddings_path)

    if embeddings.shape[0] != len(all_chunks):
        raise RuntimeError(
            f"Embeddings count ({embeddings.shape[0]}) does not match chunk count ({len(all_chunks)})."
        )

    ids = [f"merchant_chunk_{i}" for i in range(len(all_chunks))]

    # Add to Chroma via helper
    chroma_client.add_documents(
        documents=all_chunks,
        metadatas=all_metadatas,
        embeddings=embeddings.tolist(),
        ids=ids,
    )

    print(f"Inserted {len(all_chunks)} chunks into Chroma collection '{collection_name}'.")


if __name__ == '__main__':
    asyncio.run(main())







