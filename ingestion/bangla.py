import os 
from config import UNPROCESSED_FILES_DIR
from services import FileProcessingService, TokenizationService

file_processing_service = FileProcessingService()
tokenization_service = TokenizationService()

# Clear temp files 
file_processing_service.clear_tmp_file_dirs(True)
tokenization_service.clear_tmp_file_dirs()

# Prepare cleaned txt files

# First pass in the required file names

file_names = os.listdir(UNPROCESSED_FILES_DIR)

file_processing_service.prepare_cleaned_txt_files(file_names)