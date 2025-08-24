import sys, argparse
import json, os
from dotenv import load_dotenv
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.merchant_querying_service import MerchantQueryingService
from lib.chromaDBClient import ChromaDBClient
from config import (
    CHROMA_DB_DIR)

# Load environment variables from .env
load_dotenv()
# Name of the open router model being used
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL")

# Names of sentence transformer model and ChromaDB collection name
ENGLISH_MERCHANT_FAQ_COLLECTION_NAME = os.environ.get('ENGLISH_MERCHANT_FAQ_COLLECTION_NAME')
ENGLISH_SENTENCE_TRANSFORMER_MODEL = os.environ.get('ENGLISH_MERCHANT_FAQ_COLLECTION_NAME')

async def main():
    collection_name = ENGLISH_SENTENCE_TRANSFORMER_MODEL
    sentence_transformer_model_name = ENGLISH_SENTENCE_TRANSFORMER_MODEL
    assert isinstance(sentence_transformer_model_name, str)
    assert isinstance(collection_name, str)
    assert isinstance(OPENROUTER_MODEL, str)

    chroma_client = ChromaDBClient(collection_name)
    chroma_client.initialize()

    question = input("Please ask your question: ")

    # Initialize MerchantQueryingService
    merchant_querying_service = MerchantQueryingService(
        llm_model_name=OPENROUTER_MODEL
    )

    response = await merchant_querying_service.query(
        question=question, 
        language='bn')
    
    print(response)
    

if __name__ == '__main__':
    asyncio.run(main())

