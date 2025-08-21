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
    "ট্রানসাকশান হিস্ট্রি কোথায় দেখতে পারবো ?",
    "আমি মোবাইল রিচার্জ কিভাবে করতে পারবো?",
    "বঙ্গবন্ধুর নাকি ছয়টা আঙ্গুল ছিল , এটা কি সত্যি ?",
    "bKash Merchant App কীভাবে ডাউনলোড ও ইন্সটল করতে পারি?",
    "Merchant হিসেবে bKash এ কীভাবে রেজিস্ট্রেশন করতে হবে?",
    "bKash Merchant App থেকে আমি কীভাবে কাস্টমারদের থেকে পেমেন্ট নিতে পারি?",
    "Merchant App-এ ‘Request Payment’ ফিচার কীভাবে ব্যবহার করবো?",
    "কাস্টমার পেমেন্ট করলে আমি কীভাবে নোটিফিকেশন পাবো?",
    "আমি কীভাবে দৈনিক/মাসিক সেলস রিপোর্ট দেখতে পারি?",
    "Merchant App ব্যবহার করতে কোনো চার্জ বা ফি আছে কি?",
    "পেমেন্ট ব্যর্থ হলে আমি কীভাবে সমস্যার সমাধান করবো?",
    "bKash Merchant Account থেকে ব্যাংক অ্যাকাউন্টে টাকা ট্রান্সফার করা যাবে কি?",
    "আমি বিকাশ এ গেম খেলবো কি করে ?"
]
GPT_4_1_MINI = "openai/gpt-4.1-mini"
GPT_4_1 = "openai/gpt-4.1"
GPT_4_1_NANO = "openai/gpt-4.1-nano"
GPT_5_NANO = "openai/gpt-5-nano"

async def main():

    llm_model_name = GPT_4_1_NANO
    logger.info(f"Beginning the bangla queries test with {llm_model_name}")
    querying_service = MerchantQueryingService(
        llm_model_name=llm_model_name
    )

    
    t0 = time.perf_counter()
    logger.info(f"Started processing queries")
    results = await asyncio.gather(*(querying_service.query(query , language='bn') for query in queries))
    total_time = time.perf_counter() - t0

    logger.info(f"Total time taken: {total_time} seconds")
    
    # Ensure output directory exists
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    # Sanitize model name for filesystem (avoid creating nested dirs from slashes)
    safe_model_name = llm_model_name.replace('/', '_')
    output_file = output_dir / f"bangla_queries_test_{safe_model_name}.txt"

    # Write results to text file in q:/a: format
    with output_file.open("w", encoding="utf-8") as f:
        for question, answer in zip(queries, results):
            f.write(f"q: {question}\n")
            f.write(f"a: {answer}\n\n")


asyncio.run(main())
