import chromadb
import torch
import json
import os
from sentence_transformers import SentenceTransformer # Still needed to ensure model compatibility, though not for ingestion itself

EMBEDDINGS_FILE = os.environ.get("EMBEDDINGS_FILE", './Data/all_chunks_embeddings.pt')
SOURCE_MAP_FILE = os.environ.get("SOURCE_MAP_FILE", './Data/embedding_source_map.json')
CHUNKS_DIR = os.environ.get("CHUNKS_DIR", './Data/') # Directory where your chunk JSON files are
CHROMA_DB_PATH = os.environ.get("CHROMA_DB_PATH", "./chroma_db") # Path for the Chroma DB data

COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "hr_policies")

print("Starting local data ingestion script...")

print(f"Initializing Chroma DB client at {CHROMA_DB_PATH}...")
try:
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    print("Chroma DB client initialized.")
except Exception as e:
    print(f"Error initializing Chroma DB client: {e}")
    exit() # Exit if we can't initialize the database

try:
    # Try to get the collection if it exists
    collection = client.get_collection(name=COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' already exists. It will be used.")
except:
    # Create the collection if it doesn't exist
    collection = client.create_collection(name=COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' created.")


# --- Load Processed Data Files ---
print(f"Loading embeddings from {EMBEDDINGS_FILE}...")
try:
    chunk_embeddings = torch.load(EMBEDDINGS_FILE)
    print(f"Loaded embeddings of shape: {chunk_embeddings.shape}")
except FileNotFoundError:
    print(f"Error: Embeddings file not found at {EMBEDDINGS_FILE}. Please check the path.")
    exit()
except Exception as e:
    print(f"Error loading embeddings file: {e}")
    exit()


print(f"Loading embedding source map from {SOURCE_MAP_FILE}...")
try:
    with open(SOURCE_MAP_FILE, 'r', encoding='utf-8') as f:
        embedding_source_map = json.load(f)
    print(f"Loaded {len(embedding_source_map)} source map entries.")
except FileNotFoundError:
    print(f"Error: Source map file not found at {SOURCE_MAP_FILE}. Please check the path.")
    exit()
except Exception as e:
    print(f"Error loading embedding source map: {e}")
    exit()

print(f"Loading original chunk text files from {CHUNKS_DIR}...")
all_original_chunks = {}
try:
    for root, dirs, files_in_dir in os.walk(CHUNKS_DIR):
         for file in files_in_dir:
             if file.endswith("_chunks.json"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        all_original_chunks[file] = json.load(f)
                    print(f"Loaded chunk file: {file}")
                except Exception as e:
                    print(f"Error loading chunk file {filepath}: {e}")
    print(f"Loaded {len(all_original_chunks)} chunk files.")
except Exception as e:
    print(f"Error walking chunk directory {CHUNKS_DIR}: {e}")
    # Continue even if there's an error here, but warn


# --- Prepare Data for Chroma DB ---
print("Preparing data for Chroma DB ingestion...")
ids = [str(item['embedding_index']) for item in embedding_source_map]
embeddings = chunk_embeddings.tolist()
documents = []
metadatas = []

for item in embedding_source_map:
    source_file_base = os.path.basename(item['source_file'])
    chunk_json_filename = source_file_base.replace("_cleaned.txt", "_chunks.json")
    chunk_index = item['chunk_index']

    if chunk_json_filename in all_original_chunks and chunk_index < len(all_original_chunks[chunk_json_filename]):
         chunk_text = all_original_chunks[chunk_json_filename][chunk_index]
         documents.append(chunk_text)
         metadatas.append({
            'source_file': item['source_file'],
            'chunk_index': chunk_index
         })
    else:
         print(f"Warning: Could not find original chunk text for embedding index {item['embedding_index']}. Source: {item.get('source_file')}, Index: {chunk_index}")
         documents.append("Content Not Available")
         metadatas.append({
            'source_file': item.get('source_file', 'Unknown Source'),
            'chunk_index': chunk_index,
            'warning': 'Original chunk text missing or index out of bounds'
         })
print(f"Prepared {len(documents)} documents and {len(metadatas)} metadatas for ingestion.")

# --- Add Data to Chroma DB ---
print("Adding data to Chroma DB...")
batch_size = 1000 # Adjust batch size if needed
for i in range(0, len(ids), batch_size):
    batch_ids = ids[i:i+batch_size]
    batch_embeddings = embeddings[i:i+batch_size]
    batch_documents = documents[i:i+batch_size]
    batch_metadatas = metadatas[i:i+batch_size]

    min_batch_size = min(len(batch_ids), len(batch_embeddings), len(batch_documents), len(batch_metadatas))
    if min_batch_size == 0:
        print(f"Warning: Batch {int(i/batch_size) + 1} is empty.")
        continue

    try:
        collection.add(
            embeddings=batch_embeddings[:min_batch_size],
            documents=batch_documents[:min_batch_size],
            metadatas=batch_metadatas[:min_batch_size],
            ids=batch_ids[:min_batch_size]
        )
        print(f"Added batch {int(i/batch_size) + 1} (size: {min_batch_size}) to Chroma DB")
    except Exception as e:
         print(f"Error adding batch {int(i/batch_size) + 1} to Chroma DB: {e}")

print("Data ingestion into Chroma DB complete.")
print(f"Total items in collection: {collection.count()}")
