from __future__ import annotations

import re, os, fitz, shutil
from pathlib import Path
from config import DATA_DIR, UNPROCESSED_FILES_DIR, RAW_TXT_FILES_DIR, CLEANED_TXT_FILES_DIR

class FileProcessingService:

    def __init__(self):
        self.__UNPROCESSED_PDF_DIR = UNPROCESSED_FILES_DIR
        self.__RAW_TXT_DIR = RAW_TXT_FILES_DIR
        self.__CLEANED_TXT_DIR = CLEANED_TXT_FILES_DIR
    

    async def __pdf_to_txt(self, file_names: list[str]) -> list[str]:
        """
        Convert one or more PDF files to plain-text files (UTF-8).

        For each input PDF, extracts text from all pages in order and writes
        it to a sibling .txt file with the same basename.

        Args:
            file_names (list[str]): Paths to PDF files.

        Returns:
            list[str]: Paths to the generated .txt files (only those that succeeded).
        """
        extracted_txt_files: list[str] = []

        for file_name in file_names:
            pdf_path = self.__UNPROCESSED_PDF_DIR / file_name

            # Skip non-existent or non-PDF paths early
            if not pdf_path.exists():
                print(f"Skip: file not found -> {pdf_path}")
                continue
            if pdf_path.suffix.lower() != ".pdf":
                print(f"Skip: not a PDF -> {pdf_path}")
                continue

            try:
                # Use context manager so the file is properly closed
                with fitz.open(pdf_path) as doc:
                    text_parts = []
                    for page in doc:
                        text_parts.append(page.get_text())

                text = "".join(text_parts)

                txt_filename = file_name.replace(".pdf", ".txt")
                txt_path = self.__RAW_TXT_DIR / txt_filename
                txt_path.write_text(text, encoding="utf-8")

                extracted_txt_files.append(str(txt_path))
                print(f"Extracted text from {pdf_path} -> {txt_path}")

            except Exception as e:
                raise RuntimeError(f"Error extracting text from {pdf_path}: {e}")

        return extracted_txt_files

    
    async def __clean_text(self, text: str) -> str:
        """
        Clean and normalize text by removing unwanted formatting and whitespace.

        Steps:
        - Remove lines containing only numbers.
        - Collapse multiple newlines into one.
        - Collapse multiple spaces into one.
        - Strip each line and remove empty lines.
        - Join all lines into a single paragraph.
        """
        try:
            # Remove lines that are only digits (with optional surrounding whitespace).
            text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
            # Collapse multiple newlines.
            text = re.sub(r'\n+', '\n', text)
            # Collapse runs of spaces.
            text = re.sub(r'[ ]{2,}', ' ', text)
            # Strip each line and drop empties.
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            # Make it a single paragraph.
            text = text.replace('\n', ' ')
            
            return text.strip()
        except Exception as e:
            # Raise a more descriptive error while preserving traceback
            raise RuntimeError(f"Error cleaning text: {e}") from e


    async def __write_cleaned_txt_file(self, file_names: list[str]) -> list[str]:
        """
        Read raw .txt files from RAW_TXT_DIR, clean them, and write
        new *_cleaned.txt files into CLEANED_TXT_DIR.

        Args:
            file_names: Filenames relative to self.__RAW_TXT_DIR (or absolute paths).

        Returns:
            list[str]: Paths to the cleaned text files that were written.
        """
        cleaned_txt_files: list[str] = []

        try:
            for file_name in file_names:
                candidate = Path(file_name)
                unprocessed_txt_path = (
                    candidate if candidate.is_absolute()
                    else (self.__RAW_TXT_DIR / candidate)
                )

                if not unprocessed_txt_path.exists():
                    print(f"Skip: file not found -> {unprocessed_txt_path}")
                    continue
                if unprocessed_txt_path.suffix.lower() != ".txt":
                    print(f"Skip: not a .txt file -> {unprocessed_txt_path}")
                    continue

                raw_text = unprocessed_txt_path.read_text(encoding="utf-8")
                cleaned_text_content = await self.__clean_text(raw_text)

                # Write to CLEANED_TXT_DIR with *_cleaned.txt suffix
                output_path = self.__CLEANED_TXT_DIR / f"{unprocessed_txt_path.stem}_cleaned.txt"
                output_path.write_text(cleaned_text_content, encoding="utf-8")

                cleaned_txt_files.append(str(output_path))
                print(f"Wrote cleaned text -> {output_path}")

        except Exception as e:
            raise RuntimeError(f"Error writing cleaned text files: {e}")

        return cleaned_txt_files
    
     
    async def prepare_cleaned_txt_files(self, file_names: list[str]):
        """
    Prepare cleaned text files from files in UNPROCESSED_FILES_DIR.
    Automatically detects file extensions and processes accordingly:
    - .pdf files: extracts text using PyMuPDF
    - .txt files: copies and cleans directly

    Workflow:
        1. For PDFs: extracts text using PyMuPDF into RAW_TXT_FILES_DIR
        2. For TXTs: copies files from UNPROCESSED_FILES_DIR into RAW_TXT_FILES_DIR
        3. Cleans all raw text files and writes to CLEANED_TXT_FILES_DIR
        4. Returns the list of cleaned .txt file paths.

    Args:
        file_names (list[str]): List of filenames (absolute or relative
            paths, depending on class configuration).

    Returns:
        list[str]: Paths to the cleaned .txt files generated.

    Raises:
        RuntimeError: If any step in the extraction or cleaning pipeline fails.
    """
        try:
            raw_txt_files: list[str] = []

            for name in file_names:
                candidate = Path(name)
                src = candidate if candidate.is_absolute() else (self.__UNPROCESSED_PDF_DIR / candidate)
                
                if not src.exists():
                    print(f"Skip: file not found -> {src}")
                    continue
                
                extension = src.suffix.lower()
                
                if extension == ".pdf":
                    # Extract text from PDF using PyMuPDF
                    pdf_txt_files = await self.__pdf_to_txt([name])
                    raw_txt_files.extend(pdf_txt_files)
                elif extension == ".txt":
                    # Copy .txt file to RAW_TXT_FILES_DIR
                    dst = self.__RAW_TXT_DIR / src.name
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, dst)
                    raw_txt_files.append(str(dst))
                else:
                    print(f"Skip: unsupported file type -> {src}")
                    continue

            # Clean all raw text files and write to CLEANED_TXT_FILES_DIR
            cleaned_txt_files = await self.__write_cleaned_txt_file(raw_txt_files)

            return cleaned_txt_files

        except Exception as e:
            raise RuntimeError(f"Error with cleaned text files: {e}")
        
    @staticmethod
    def clear_tmp_file_dirs(clear_UNPROCESSED_FILES_DIR: bool = False):
        try:
            if clear_UNPROCESSED_FILES_DIR:
                print(f'Attempting to clear UNPROCESSED_FILES_DIR')
                for file in UNPROCESSED_FILES_DIR.iterdir():
                    if file.is_file():
                        os.remove(file)
                print(f'Cleared UNPROCESSED_FILES_DIR')

            print(f'Attempting to clear RAW_TXT_FILES_DIR')
            for file in RAW_TXT_FILES_DIR.iterdir():
                if file.is_file():
                    os.remove(file)
            print(f'Cleared RAW_TXT_FILES_DIR')

            print(f'Attempting to clear CLEANED_TXT_FILES_DIR')
            for file in CLEANED_TXT_FILES_DIR.iterdir():
                if file.is_file():
                    os.remove(file)
            print(f'Cleared CLEANED_TXT_FILES_DIR')
        except Exception as e:
            raise RuntimeError(f'Failed to clear temporary file dirs: {e}')