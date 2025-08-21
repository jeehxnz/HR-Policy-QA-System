import asyncio, time, sys
import logging
from pathlib import Path
# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.merchant_querying_service import MerchantQueryingService
# Logger Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

queries = [
    "Where can I view my transaction history?",
    "How can I do mobile recharge?",
    "Is it true that Bangabandhu had six fingers?",
    "How can I download and install the bKash Merchant App?",
    "How do I register as a merchant in bKash?",
    "How can I collect payments from customers using the bKash Merchant App?",
    "How do I use the 'Request Payment' feature in the Merchant App?",
    "How will I get a notification when a customer makes a payment?",
    "How can I view daily/monthly sales reports?",
    "Are there any charges or fees to use the Merchant App?",
    "How can I solve the problem if a payment fails?",
    "Can I transfer money from my bKash Merchant Account to a bank account?",
    "How can I play games in bKash?"
]

GPT_4_1_MINI = "openai/gpt-4.1-mini"
GPT_4_1 = "openai/gpt-4.1"
GPT_4_1_NANO = "openai/gpt-4.1-nano"
GPT_5_NANO = "openai/gpt-5-nano"

async def main():

    llm_model_name = GPT_4_1_NANO
    logger.info(f"Beginning the English queries test with {llm_model_name}")
    querying_service = MerchantQueryingService(
        llm_model_name=llm_model_name
    )

    
    t0 = time.perf_counter()
    logger.info(f"Started processing queries")
    results = await asyncio.gather(*(querying_service.query(query , language='en') for query in queries))
    total_time = time.perf_counter() - t0

    logger.info(f"Total time taken: {total_time} seconds")
    
    # Ensure output directory exists
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    # Sanitize model name for filesystem (avoid creating nested dirs from slashes)
    safe_model_name = llm_model_name.replace('/', '_')
    output_file = output_dir / f"english_queries_test_{safe_model_name}.txt"

    # Write results to text file in q:/a: format
    with output_file.open("w", encoding="utf-8") as f:
        for question, answer in zip(queries, results):
            f.write(f"q: {question}\n")
            f.write(f"a: {answer}\n\n")


asyncio.run(main())
