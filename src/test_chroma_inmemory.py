import chromadb

client = chromadb.Client()
collection = client.create_collection(name="test_collection")
collection.add(
    embeddings=[[0.0]*384],
    documents=["test document"],
    metadatas=[{"source": "test"}],
    ids=["1"]
)
print("About to run a minimal query on in-memory DB...")
results = collection.query(
    query_embeddings=[[0.0]*384],
    n_results=1
)
print("Query succeeded!")
print(results)
