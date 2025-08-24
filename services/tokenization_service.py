from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Dict, Any, Optional
import torch, os, json
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
from config import CHUNKS_DIR, EMBEDDINGS_DIR, SOURCE_MAPS_DIR

class TokenizationService:
    """
    Service for text chunking (by tokenizer tokens), embedding generation, and
    source mapping.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size_tokens: int = 512,
        chunk_overlap_tokens: int = 50,
        progress: bool = True,
    ) -> None:
        """
        Initialize the service with tokenizer/embedding model names and defaults.
        """
        self.model_name = model_name
        self.chunk_size_tokens = chunk_size_tokens
        self.chunk_overlap_tokens = chunk_overlap_tokens
        self.progress = progress
        
        # Initialize tokenizer and embedding model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.embedding_model = SentenceTransformer(model_name)
        
        # Set device
        self.device = self.get_device()
        self.embedding_model.to(self.device)
        
        # Validate parameters
        self.validate_chunk_params(chunk_size_tokens, chunk_overlap_tokens)
        
        # Initialize directories
        self._ensure_directories_exist()

    def _ensure_directories_exist(self) -> None:
        """Create all necessary directories if they don't exist."""
        directories = [
            CHUNKS_DIR,
            EMBEDDINGS_DIR,
            SOURCE_MAPS_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"Ensured directory exists: {directory}")

    def get_default_chunks_dir(self) -> Path:
        """Get the default chunks directory."""
        return CHUNKS_DIR

    def get_default_embeddings_path(self, filename: str = "embeddings.pt") -> Path:
        """Get the default embeddings file path."""
        return EMBEDDINGS_DIR / filename

    def get_default_source_map_path(self, filename: str = "source_map.json") -> Path:
        """Get the default source map file path."""
        return SOURCE_MAPS_DIR / filename

    def get_device(self) -> str:
        """Determine the compute device to use."""
        if torch.cuda.is_available():
            return 'cuda'
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return 'mps'
        else:
            return 'cpu'

    def  validate_chunk_params(self, max_tokens: int, overlap: int) -> None:
        """Validate chunking parameters."""
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= max_tokens:
            raise ValueError("overlap must be less than max_tokens")

    async def  count_tokens(self, text: str) -> int:
        """Count tokens for text using the current tokenizer."""
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        return len(tokens)

    async def split_into_chunks_by_tokens(
        self,
        text: str,
        max_tokens: Optional[int] = None,
        overlap: Optional[int] = None,
    ) -> List[str]:
        """Split text into token-bounded chunks using the current tokenizer."""
        max_tokens = max_tokens or self.chunk_size_tokens
        overlap = overlap or self.chunk_overlap_tokens
        
        self.validate_chunk_params(max_tokens, overlap)
        
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        chunks = []
        
        for i in range(0, len(tokens), max_tokens - overlap):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            if chunk_text.strip():  # Only add non-empty chunks
                chunks.append(chunk_text)
        
        return chunks

    async def chunk_file(self, in_path: Path, out_path: Optional[Path] = None) -> Path:
        """Read a cleaned .txt file, split into chunks, and write a JSON list to disk."""
        if out_path is None:
            out_path = in_path.parent / f"{in_path.stem}_chunks.json"
        
        text = in_path.read_text(encoding='utf-8')
        chunks = await self.split_into_chunks_by_tokens(text)
        
        return await self.write_chunks(chunks, out_path)

    async def write_chunks(self, chunks: List[str], out_path: Path) -> Path:
        """Persist chunk strings into a JSON file."""
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        return out_path

    async def read_chunks(self, json_path: Path) -> List[str]:
        """Load chunk strings from a JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    async def encode_chunks(
        self,
        chunks: List[str],
        batch_size: int = 32,
        convert_to_tensor: bool = True,
        show_progress_bar: Optional[bool] = None,
    ) -> torch.Tensor:
        """Generate embeddings for a list of chunks."""
        show_progress_bar = show_progress_bar if show_progress_bar is not None else self.progress
        
        embeddings = self.embedding_model.encode(
            chunks,
            batch_size=batch_size,
            convert_to_tensor=convert_to_tensor,
            show_progress_bar=show_progress_bar,
            device=self.device
        )
        
        # Ensure we always return a tensor
        if not isinstance(embeddings, torch.Tensor):
            embeddings = torch.tensor(embeddings, device=self.device)
        
        return embeddings

    async def  save_embeddings(self, tensor: torch.Tensor, out_path: Path) -> Path:
        """Save embeddings tensor to disk."""
        out_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(tensor, out_path)
        return out_path

    async def build_source_map(
        self,
        chunk_index_lists: Dict[str, List[str]],
    ) -> List[Dict[str, Any]]:
        """Build a flat mapping from source files and chunk indices to embedding indices."""
        mapping = []
        embedding_index = 0
        
        for source_file, chunks in chunk_index_lists.items():
            for chunk_index, chunk in enumerate(chunks):
                mapping.append({
                    "source_file": source_file,
                    "chunk_index": chunk_index,
                    "embedding_index": embedding_index
                })
                embedding_index += 1
        
        return mapping

    async def save_source_map(self, mapping: List[Dict[str, Any]], out_path: Path) -> Path:
        """Save the source map as JSON."""
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        return out_path

    # --- Step 4 helpers: load results and assemble payloads ---
    def load_embeddings(self, path: Path) -> torch.Tensor:
        """Load embeddings tensor from disk."""
        return torch.load(path)

    def load_source_map(self, path: Path) -> Any:
        """Load source map JSON from disk."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_all_chunks_for_files(
        self,
        cleaned_txt_files: Iterable[Path],
        chunks_dir: Optional[Path] = None,
    ) -> Dict[str, List[Any]]:
        """
        Load and concatenate chunk strings for the given cleaned text files, preserving order.

        Returns a dict with keys: 'documents' (List[str]) and 'metadatas' (List[Dict]).
        """
        chunks_dir = chunks_dir or self.get_default_chunks_dir()
        all_chunks: List[str] = []
        all_metadatas: List[Dict[str, Any]] = []

        for txt_path in cleaned_txt_files:
            chunk_file = chunks_dir / f"{txt_path.stem}_chunks.json"
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            all_chunks.extend(chunks)

            # OPPORTUNITY FOR OPTIMIZATION 
            all_metadatas.extend({"source": txt_path.name} for _ in chunks)

        return {"documents": all_chunks, "metadatas": all_metadatas}

    async def run_pipeline(
        self,
        cleaned_txt_files: Iterable[Path],
        chunks_out_dir: Path,
        embeddings_out_path: Path,
        source_map_out_path: Path,
        batch_size: int = 32,
    ) -> Dict[str, Any]:
        """End-to-end pipeline for chunking, embedding, and source mapping."""
        chunks_out_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert iterable to list to ensure we can get length
        cleaned_txt_files_list = list(cleaned_txt_files)
        
        # Step 1: Chunk all text files
        chunk_files = []
        chunk_index_lists = {}
        
        for txt_file in cleaned_txt_files_list:
            chunk_file = await self.chunk_file(txt_file, chunks_out_dir / f"{txt_file.stem}_chunks.json")
            chunk_files.append(chunk_file)
            # Ensure we await the async read to store actual chunk lists
            chunk_index_lists[str(txt_file)] = await self.read_chunks(chunk_file)
        
        # Step 2: Encode all chunks
        all_chunks = []
        for chunk_file in chunk_files:
            chunks = await self.read_chunks(chunk_file)
            all_chunks.extend(chunks)
        
        embeddings = await self.encode_chunks(all_chunks, batch_size)
        
        # Step 3: Save embeddings
        await self.save_embeddings(embeddings, embeddings_out_path)
        
        # Step 4: Build and save source map
        source_map = await self.build_source_map(chunk_index_lists)
        await self.save_source_map(source_map, source_map_out_path)
        
        # Return summary
        total_chunks = sum(len(chunks) for chunks in chunk_index_lists.values())
        
        return {
            "num_files_processed": len(cleaned_txt_files_list),
            "num_chunk_files": len(chunk_files),
            "total_chunks": total_chunks,
            "embedding_dim": embeddings.shape[1],
            "chunks_out_dir": str(chunks_out_dir),
            "embeddings_out_path": str(embeddings_out_path),
            "source_map_out_path": str(source_map_out_path)
        }

    async def run_pipeline_with_defaults(
        self,
        cleaned_txt_files: Iterable[Path],
        batch_size: int = 32,
        embeddings_filename: str = "embeddings.pt",
        source_map_filename: str = "source_map.json"
    ) -> Dict[str, Any]:
        """
        Run the complete pipeline using default directory structure.
        
        Args:
            cleaned_txt_files: Iterable of cleaned .txt file paths.
            batch_size: Batch size for encoding.
            embeddings_filename: Name for the embeddings file.
            source_map_filename: Name for the source map file.
            
        Returns:
            Summary dictionary with processing results.
        """
        chunks_dir = self.get_default_chunks_dir()
        embeddings_path = self.get_default_embeddings_path(embeddings_filename)
        source_map_path = self.get_default_source_map_path(source_map_filename)
        
        return await self.run_pipeline(
            cleaned_txt_files=cleaned_txt_files,
            chunks_out_dir=chunks_dir,
            embeddings_out_path=embeddings_path,
            source_map_out_path=source_map_path,
            batch_size=batch_size
        )
    
    @staticmethod
    def clear_tmp_file_dirs():
        try:
            print(f'Attempting to clear CHUNKS_DIR')
            for file in CHUNKS_DIR.iterdir():
                if file.is_file():
                    os.remove(file)
            print(f'Cleared CHUNKS_DIR') 

            print(f'Attempting to clear EMBEDDINGS_DIR')
            for file in EMBEDDINGS_DIR.iterdir():
                if file.is_file():
                    os.remove(file)
            print(f'Cleared EMBEDDINGS_DIR') 

            print(f'Attempting to clear SOURCE_MAPS_DIR')
            for file in SOURCE_MAPS_DIR.iterdir():
                if file.is_file():
                    os.remove(file)
            print(f'Cleared SOURCE_MAPS_DIR') 
            
        except Exception as e:
            raise RuntimeError(f'Error clearing tmp tokenization dirs: {e}')
        
    async def embedQuestion(self, question: str):
        """
        Takes in question string, and embeds it
        """
        try:
            question_embedding = self.embedding_model.encode(question, convert_to_tensor=True)
            return question_embedding
        except Exception as e:
            raise RuntimeError(f'Error embedding question: {e}')
    
    async def prepareLLMContext(self, flat_chunks):
        """
        Processes Flatened chunks from ChromaDB Query for use for LLM Client
        """
        try:
            if not flat_chunks:
                context = "No relevant data found in the database."
            else:
                max_context_tokens = 3000
                context_tokens = []
                context_chunks = []
                current_token_count = 0

                for chunk in flat_chunks:
                    try:
                        chunk_tokens = self.tokenizer.encode(chunk, add_special_tokens=False)
                        if current_token_count + len(chunk_tokens) <= max_context_tokens:
                            context_tokens.extend(chunk_tokens)
                            context_chunks.append(chunk)
                            current_token_count += len(chunk_tokens)
                        else:
                            break
                    except Exception as e:
                         print(f"Error encoding chunk with tokenizer: {e}. Skipping chunk.")
                         if current_token_count <= max_context_tokens:
                             context_chunks.append(chunk)
                             current_token_count += 100
                
                context = "\n\n".join(context_chunks)

            return context
        
        except Exception as e:
            raise RuntimeError(f'Error embedding question: {e}')