"""
Configuration file for HR Policy QA System.
Contains project-wide constants and settings.
"""

from pathlib import Path

# Absolute path to the project root
ROOT_DIR = Path(__file__).resolve().parent

# Data directory
DATA_DIR = ROOT_DIR / "Data"

# Temporary files directory 

TMP_DIR = ROOT_DIR / "tmp"

# Services directory
SERVICES_DIR = ROOT_DIR / "services"

# Unprocessed files directory
UNPROCESSED_FILES_DIR = TMP_DIR / "unprocessed_files"

# Raw text files directory
RAW_TXT_FILES_DIR = TMP_DIR / "raw_txt_files"

# Cleaned text files directory
CLEANED_TXT_FILES_DIR = TMP_DIR / "cleaned_txt_files"

# TokenizationService directories
CHUNKS_DIR = TMP_DIR / "chunks"
EMBEDDINGS_DIR = TMP_DIR / "embeddings"
SOURCE_MAPS_DIR = TMP_DIR / "source_maps"

# ChromaDB directory
CHROMA_DB_DIR = ROOT_DIR / "chroma_db"
