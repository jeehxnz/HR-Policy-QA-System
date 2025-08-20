import sys, argparse
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
from config import CHROMA_DB_DIR

async def main(collection_name):

    chroma_client = get_chroma_client()

    # Initialize Chroma client (db path + create default collection)
    chroma_client.initialize(db_path=CHROMA_DB_DIR, collection_name=collection_name)

    chroma_client.reset_collection(collection_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("collection_name", type=str, help="Which collection to delete")
    args = parser.parse_args()

    asyncio.run(main(args.collection_name))


