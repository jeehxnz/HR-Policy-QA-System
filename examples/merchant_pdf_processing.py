import sys
import json
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import torch
from services.file_processing_service import FileProcessingService
from services.tokenization_service import TokenizationService
from lib.chromaDBClient import get_chroma_client
from config import (
    CHROMA_DB_DIR,
    UNPROCESSED_FILES_DIR,
    CHUNKS_DIR,
    EMBEDDINGS_DIR,
    SOURCE_MAPS_DIR,
)


async def main():
    collection_name = 'Merchant_FAQ_V4'

    file_processing_service = FileProcessingService()
    tokenization_service = TokenizationService(
        model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
        chunk_size_tokens=510,  # not 512
        chunk_overlap_tokens=50,
    )
    chroma_client = get_chroma_client()

    # Initialize Chroma client (db path + create default collection)
    chroma_client.initialize(db_path=CHROMA_DB_DIR, collection_name=collection_name)

    # Empty out tmp dirs (do not clear UNPROCESSED_FILES_DIR so PDFs remain)
    file_processing_service.clear_tmp_file_dirs(False)

    # 1) Discover inputs in tmp/unprocessed_files
    pdf_files = [p.name for p in UNPROCESSED_FILES_DIR.glob('*.pdf')]
    txt_files = [p.name for p in UNPROCESSED_FILES_DIR.glob('*.txt')]
    files = pdf_files + txt_files
    if not files:
        print(f"No input files found in {UNPROCESSED_FILES_DIR}")
        return

    print(f"Files: {files}")

    # 2) Convert to cleaned text (auto-detects file types)
    cleaned_files = await file_processing_service.prepare_cleaned_txt_files(files)
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
        collection_name=collection_name,
        documents=all_chunks,
        metadatas=all_metadatas,
        embeddings=embeddings.tolist(),
        ids=ids,
    )

    print(f"Inserted {len(all_chunks)} chunks into Chroma collection '{collection_name}'.")


if __name__ == '__main__':
    asyncio.run(main())







