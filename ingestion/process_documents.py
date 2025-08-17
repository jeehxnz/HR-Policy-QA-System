import os
import fitz

def pdfToTxt(file_names):
    extracted_txt_files = []

    for file_name in file_names:
        try:
            doc = fitz.open(file_name)
            text = ""
            for page in doc:
                text += page.get_text()

            txt_filename = file_name.replace(".pdf", ".txt")
            with open(txt_filename, "w", encoding="utf-8") as f:
                f.write(text)
            extracted_txt_files.append(txt_filename)
            print(f"Extracted text from {file_name} to {txt_filename}")
        except Exception as e:
            print(f"Error extracting text from {file_name}: {e}")

    return extracted_txt_files

# Get all file names
file_names = os.listdir('./Data/unprocessed_files')


