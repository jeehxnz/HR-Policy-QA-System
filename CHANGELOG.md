# Changelog

All notable changes to this project will be documented in this file.

## [2024-08-12] - Major Repository Cleanup and Reorganization

### Added
- **Project Structure**: Reorganized files into logical directories:
  - `src/` - Flask API and backend logic
  - `frontend/` - Static web interface
  - `ingestion/` - Data processing scripts
- **Configuration**: Added environment variable support for all configurable settings
- **Documentation**: Comprehensive README.md with setup instructions, API reference, and troubleshooting
- **Development Tools**: 
  - `Makefile` with common development tasks
  - `env.example` template for environment configuration
  - Updated `.gitignore` to exclude generated files
- **Dependency Management**: 
  - Automatic dependency checking and installation on app startup
  - `/dependencies` endpoint to check and auto-install missing packages
  - `/health` endpoint for system status monitoring
  - `/version` endpoint for application information
  - Standalone `test_dependencies.py` script for dependency verification

### Changed
- **Dependencies**: Updated `requirements.txt` with pinned versions and added missing dependencies:
  - Added: `transformers`, `torch`, `requests`
  - Removed: `pandas` (unused)
  - Pinned all versions for reproducibility
- **Configuration**: Made all hardcoded settings configurable via environment variables:
  - `MODEL_NAME_EMBEDDING`
  - `CHROMA_DB_PATH`
  - `COLLECTION_NAME`
  - `OPENROUTER_MODEL`
  - `EMBEDDINGS_FILE`, `SOURCE_MAP_FILE`, `CHUNKS_DIR` (in ingestion)
- **Data Paths**: Fixed case sensitivity issue in `ingest_data.py` (changed `./data/` to `./Data/`)

### Removed
- **Duplicate Files**: Removed duplicate frontend files from `Frontend/BkashEmployeeQuesAnsSystem/`
- **Unnecessary Files**: 
  - `python-3.13.3-amd64.exe` (Windows installer)
  - `Q_A_bKash.ipynb` (Colab notebook)
- **Empty Directories**: Removed empty `Backend/` directory
- **Directory Restructure**: Moved backend files from `backend/` to `src/` for better git tracking

### Fixed
- **Path Issues**: Fixed data path casing that would break on case-sensitive filesystems
- **Git Hygiene**: Added proper `.gitignore` entries to exclude:
  - `chroma_db/` (generated database)
  - `*.pt`, `*.bin`, `*.sqlite3` (generated files)
  - `.DS_Store`, `Thumbs.db` (OS files)
  - `.env` (environment files)

### Technical Debt
- **Frontend Consolidation**: Standardized on single frontend implementation
- **Configuration Management**: Centralized all settings in environment variables
- **Documentation**: Added comprehensive setup and usage instructions
- **Development Workflow**: Added Makefile for common tasks

## [Previous] - Initial Implementation

### Added
- Basic RAG system with ChromaDB and OpenRouter
- Flask API with `/ask` endpoint
- Static frontend for question submission
- Data processing pipeline for PDF ingestion
- Embedding generation and storage
