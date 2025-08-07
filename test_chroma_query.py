import chromadb
import os

CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "hr_policies"

print("Starting minimal Chroma DB test script...")

if not os.path.exists(CHROMA_DB_PATH):
    print(f"Error: Chroma DB path not found at {CHROMA_DB_PATH}.")
    print("Please run the ingest_data.py script first to create the database.")
    exit() 

print(f"Attempting to connect to Chroma DB at {CHROMA_DB_PATH} and get collection '{COLLECTION_NAME}'...")
try:
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    print("Successfully connected to Chroma DB and got collection.")

    count = collection.count()
    print(f"Collection '{COLLECTION_NAME}' has {count} items.")
    if count == 0:
        print("Warning: Collection is empty. Please run the ingest_data.py script to populate it.")


except Exception as e:
    print(f"\n--- Error connecting to Chroma DB or getting collection ---")
    print(f"Error: {e}")
    print(f"Please ensure ingest_data.py ran successfully to create and populate the database.")
    print(f"----------------------------------------------------------")
    exit() 

print("\nAbout to run a minimal query...")
try:

    dummy_query_embedding = [[0.0] * 384]

    results = collection.query(
        query_embeddings=dummy_query_embedding,
        n_results=1 # Just get one result
    )
    print("Query succeeded!")
    print(results) # Print the results to see them

except Exception as e:
    print("\n--- Query failed with exception ---")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    print("-----------------------------------")
    exit() # Exit if the query fails

print("\nMinimal Chroma DB test script finished.")
