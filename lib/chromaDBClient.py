"""
Singleton ChromaDB Client for HR Policy QA System

This module provides a simple singleton ChromaDB client that manages database connections
and collections for the HR Policy QA System. It ensures only one instance of the
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
    
    _instance: Optional['ChromaDBClient'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'ChromaDBClient':
        """Ensure only one instance of the client exists."""
        if cls._instance is None:
            cls._instance = super(ChromaDBClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the ChromaDB client if not already initialized."""
        if not self._initialized:
            self._client: Optional[chromadb.Client] = None
            self._db_path: Optional[Path] = None
            self._initialized = True
            logger.info("ChromaDBClient singleton created")
    
    def initialize(self, db_path: Optional[Path] = None, collection_name: str = "hr_policy_qa") -> None:
        """
        Initialize the ChromaDB client with database path and collection.
        
        Args:
            db_path: Path to the ChromaDB database. If None, uses default from config.
            collection_name: Name of the default collection to create/use.
        """
        if self._client is not None:
            logger.warning("ChromaDB client already initialized")
            return
        
        # Set database path
        if db_path is None:
            self._db_path = CHROMA_DB_DIR
        else:
            self._db_path = Path(db_path)
        
        # Ensure database directory exists
        self._db_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Initialize ChromaDB client
            self._client = chromadb.PersistentClient(
                path=str(self._db_path)
            )
            
            # Create or get the default collection
            self._create_or_get_collection(collection_name)
            
            logger.info(f"ChromaDB client initialized with database at: {self._db_path}")
            logger.info(f"Default collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
    
    def _create_or_get_collection(self, collection_name: str) -> chromadb.Collection:
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
            collection = self._client.get_collection(collection_name)
            logger.info(f"Retrieved existing collection: {collection_name}")
        except Exception:
            # Create new collection if it doesn't exist
            collection = self._client.create_collection(
                name=collection_name,
                metadata={"description": "HR Policy QA System embeddings"}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        return collection
    
    def get_collection(self, collection_name: str = "hr_policy_qa") -> chromadb.Collection:
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
                name=collection_name,
                metadata={"description": "HR Policy QA System embeddings"}
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
    
    def reset_collection(self, collection_name: str = "hr_policy_qa") -> None:
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
            self._create_or_get_collection(collection_name)
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


# Global singleton instance
chroma_client = ChromaDBClient()


def get_chroma_client() -> ChromaDBClient:
    """
    Get the global ChromaDB client instance.
    
    Returns:
        ChromaDBClient singleton instance.
    """
    return chroma_client


def initialize_chroma_client(db_path: Optional[Path] = None, collection_name: str = "hr_policy_qa") -> ChromaDBClient:
    """
    Initialize the global ChromaDB client.
    
    Args:
        db_path: Path to the ChromaDB database.
        collection_name: Name of the default collection.
        
    Returns:
        Initialized ChromaDBClient instance.
    """
    client = get_chroma_client()
    client.initialize(db_path, collection_name)
    return client
