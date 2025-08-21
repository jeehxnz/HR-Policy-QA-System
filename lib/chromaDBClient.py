"""
Singleton ChromaDB Client for HR Policy QA System

This module provides a simple singleton ChromaDB client that manages database connections
and collections. It ensures only one instance of the
client exists throughout the application lifecycle.
"""

import chromadb
from pathlib import Path
from typing import Optional
import logging
from config import CHROMA_DB_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChromaDBClient:
    """
    Simple singleton ChromaDB client for managing vector database connections.
    
    This class provides a centralized interface for:
    - Database connection management
    - Collection creation and management
    """
    

    
    
    def __init__(self,
                 COLLECTION_NAME : str,
                 CHROMA_DB_PATH: Path = CHROMA_DB_DIR
                 ):
        """Initialize the ChromaDB client."""
        self._db_path: Path = CHROMA_DB_PATH
        self.collection_name: str = COLLECTION_NAME
        self._client: Optional[chromadb.Client] = None
        logger.info(f"ChromaDBClient instance created for collection: {self.collection_name}")
    
    def initialize(self) -> None:
        """
        Initialize the ChromaDB client with database path and collection.
        
        Args:
            db_path: Path to the ChromaDB database. If None, uses default from config.
            collection_name: Name of the default collection to create/use.
        """
        if self._client is not None:
            logger.warning("ChromaDB client already initialized")
            return
        
        
        # Ensure database directory exists
        self._db_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Initialize ChromaDB client
            self._client = chromadb.PersistentClient(
                path=str(self._db_path)
            )
            
            # Create or get the default collection
            self._create_or_get_collection(self.collection_name, "")
            
            logger.info(f"ChromaDB client initialized with database at: {self._db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
    
    def _create_or_get_collection(self, collection_name: str, description_metadata: str) -> chromadb.Collection:
        """
        Create a new collection or get an existing one.
        
        Args:
            collection_name: Name of the collection.
            
        Returns:
            ChromaDB collection object.
        """
        if self._client is None:
            raise RuntimeError("ChromaDB client not initialized. Call initialize() first.")
        
        try:
            # Try to get existing collection
            if collection_name in self.list_collections():
                collection = self._client.get_collection(collection_name)
                logger.info(f"Retrieved existing collection: {collection_name}")
            else:
                # Create new collection if it doesn't exist
                collection = self._client.create_collection(
                name=collection_name,
                metadata={"description": f"{description_metadata}"}
                )
                logger.info(f"Created new collection: {collection_name}")
            return collection
        except Exception as e:
            raise RuntimeError(f"Error creating or getting collection {collection_name}: {e}")
    
    def get_collection(self, collection_name: str) -> chromadb.Collection:
        """
        Get a collection by name, creating it if it doesn't exist.
        
        Args:
            collection_name: Name of the collection.
            
        Returns:
            ChromaDB collection object.
        """
        if self._client is None:
            raise RuntimeError("ChromaDB client not initialized. Call initialize() first.")
        
        try:
            # Try to get existing collection
            collection = self._client.get_collection(collection_name)
        except Exception:
            # Create new collection if it doesn't exist
            collection = self._client.create_collection(
                name=collection_name
            )
        
        return collection
    
    def list_collections(self) -> list[str]:
        """
        List all collections in the database.
        
        Returns:
            List of collection names.
        """
        if self._client is None:
            raise RuntimeError("ChromaDB client not initialized. Call initialize() first.")
        
        try:
            collections = self._client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            raise
    
    def reset_collection(self, collection_name: str) -> None:
        """
        Reset (delete and recreate) a collection.
        
        Args:
            collection_name: Name of the collection to reset.
        """
        if self._client is None:
            raise RuntimeError("ChromaDB client not initialized. Call initialize() first.")
        
        try:
            # Delete collection if it exists
            try:
                self._client.delete_collection(collection_name)
                logger.info(f"Deleted collection: {collection_name}")
            except Exception:
                # Collection doesn't exist, which is fine
                pass
            
            # Recreate collection
            self._create_or_get_collection(collection_name, "")
            logger.info(f"Reset collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to reset collection {collection_name}: {e}")
            raise
    
    def close(self) -> None:
        """Close the ChromaDB client connection."""
        if self._client is not None:
            try:
                # ChromaDB PersistentClient doesn't have a close method
                # But we can clear our references
                self._client = None
                logger.info("ChromaDB client closed")
            except Exception as e:
                logger.error(f"Error closing ChromaDB client: {e}")
    
    @property
    def is_initialized(self) -> bool:
        """Check if the client is initialized."""
        return self._client is not None
    
    @property
    def db_path(self) -> Optional[Path]:
        """Get the database path."""
        return self._db_path
    
    @property
    def client(self) -> Optional[chromadb.Client]:
        """Get the underlying ChromaDB client."""
        return self._client

    # --- Step 4 helpers: add/upsert convenience methods ---
    def add_documents(
        self,
        documents: list[str],
        metadatas: Optional[list[dict]] = None,
        embeddings: Optional[list[list[float]]] = None,
        ids: Optional[list[str]] = None,
    ) -> None:
        """Add documents (and optional embeddings) into the instance's collection."""
        collection = self.get_collection(self.collection_name)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids,
        )

    def upsert_documents(
        self,
        documents: list[str],
        metadatas: Optional[list[dict]] = None,
        embeddings: Optional[list[list[float]]] = None,
        ids: Optional[list[str]] = None,
    ) -> None:
        """Upsert documents (and optional embeddings) into the instance's collection."""
        collection = self.get_collection(self.collection_name)
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids,
        )

    async def getTopNQueryResults(self, n: int, question_embedding):
        try:
            collection = self.get_collection(self.collection_name)

            results = collection.query(
                query_embeddings=[question_embedding.tolist()],
                n_results= n, # Get top n relevant chunks
                include=["documents", "distances"]  # <= get scores back
            )

            documents = results.get("documents")
            distances = results.get("distances")  # List[List[float]] | None

            
            print(distances)


            return [results, documents]
        except Exception as e:
            raise RuntimeError(f'Failed to query ChromaDB: {e}')
    
    async def getFlattenedChunks(self, chroma_query_results):
        try:
            # Normalize input shape: can be dict (results) or list [results, documents]
            results_dict = None
            if isinstance(chroma_query_results, dict):
                results_dict = chroma_query_results
            elif isinstance(chroma_query_results, (list, tuple)):
                if len(chroma_query_results) > 0 and isinstance(chroma_query_results[0], dict):
                    results_dict = chroma_query_results[0]
                else:
                    # Fallback: treat second or first element as documents list
                    docs_candidate = None
                    if len(chroma_query_results) > 1:
                        docs_candidate = chroma_query_results[1]
                    elif len(chroma_query_results) == 1:
                        docs_candidate = chroma_query_results[0]
                    results_dict = {"documents": docs_candidate or []}
            else:
                raise TypeError(f"Unsupported chroma_query_results type: {type(chroma_query_results)}")

            retrieved_chunks = results_dict.get('documents') or []

            # Handle shapes: [[str]] or [str]
            if retrieved_chunks and isinstance(retrieved_chunks[0], list):
                flat_chunks = [item for sublist in retrieved_chunks for item in sublist]
            else:
                flat_chunks = retrieved_chunks

            # For temporary testing purpose only 
            # with open("retrieved_chunks.txt", "w", encoding="utf-8") as f:
            #     for index, chunk in enumerate(flat_chunks, start=1):
            #         f.write(f"Chunk {index}:\n{chunk}\n\n")

            return flat_chunks

        except Exception as e:
            raise RuntimeError(f'Failed to retrieve flattened chunks: {e}')


def get_chroma_client(collection_name: str, db_path: Optional[Path] = None) -> ChromaDBClient:
    """
    Helper function to create and initialize a ChromaDB client instance.
    
    Args:
        collection_name: Name of the collection for this client instance
        db_path: Optional database path (uses default if not provided)
        
    Returns:
        Initialized ChromaDBClient instance
    """
    if db_path is None:
        db_path = CHROMA_DB_DIR
    
    client = ChromaDBClient(COLLECTION_NAME=collection_name, CHROMA_DB_PATH=db_path)
    client.initialize()
    return client