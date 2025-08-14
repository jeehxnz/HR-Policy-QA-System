import sys
import subprocess
import importlib.util
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
import traceback
from dotenv import load_dotenv

load_dotenv()

def check_and_install_dependencies():
    """Check for required dependencies and install missing ones."""
    required_packages = {
        'flask': 'flask==3.0.0',
        'flask_cors': 'flask-cors==4.0.0',
        'chromadb': 'chromadb==1.0.16',
        'sentence_transformers': 'sentence-transformers==2.7.0',
        'transformers': 'transformers==4.41.1',
        'torch': 'torch==2.3.1',
        'requests': 'requests==2.32.3',
        'python_dotenv': 'python-dotenv==1.0.1'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        if importlib.util.find_spec(package) is None:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"Missing dependencies detected: {missing_packages}")
        print("Attempting to install missing packages...")
        
        try:
            # Install missing packages
            for package in missing_packages:
                print(f"Installing {package}...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], capture_output=True, text=True, check=True)
                print(f"Successfully installed {package}")
            
            print("All missing dependencies installed successfully!")
            print("Please restart the application for changes to take effect.")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            print(f"Error output: {e.stderr}")
            print("Please install missing packages manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

# Check dependencies before importing
# if not check_and_install_dependencies():
#     print("Dependency check failed. Exiting.")
#     sys.exit(1)

# Now import the packages that might have been missing
import chromadb
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

app = Flask(__name__)

CORS(app)

# --- Configuration ---
MODEL_NAME_EMBEDDING = os.environ.get("MODEL_NAME_EMBEDDING", 'sentence-transformers/all-MiniLM-L6-v2')
CHROMA_DB_PATH = os.environ.get("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "hr_policies")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4.1")

print("Loading Sentence Transformer model...")
try:
    model = SentenceTransformer(MODEL_NAME_EMBEDDING)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading Sentence Transformer model: {e}")
    model = None

print(f"Connecting to Chroma DB at {CHROMA_DB_PATH}...")
try:
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    print("Chroma DB connected successfully.")
except Exception as e:
    print(f"Error connecting to Chroma DB or getting collection: {e}")
    client = None
    collection = None

print("Loading tokenizer for context length estimation...")
try:
    tokenizer_llm = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    print("Tokenizer loaded successfully.")
except Exception as e:
    print(f"Error loading tokenizer for context estimation: {e}")
    tokenizer_llm = None


if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY environment variable not set. API calls will likely fail.")
if not model:
    print("Warning: Sentence Transformer model not loaded. Embedding will fail.")
if not collection:
    print("Warning: Chroma DB collection not loaded. Retrieval will fail.")
if not tokenizer_llm:
    print("Warning: LLM tokenizer not loaded. Context length estimation will be inaccurate.")


# --- API Endpoint ---
@app.route('/ask', methods=['POST'])
def ask_hr_question():
    data = request.json
    question: str = data.get('question')

    if not question:
        return jsonify({"error": "No question provided"}), 400
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "AI API key is not configured."}), 500
    if not model:
        return jsonify({"error": "Embedding model not loaded."}), 500
    if not collection:
        return jsonify({"error": "Database not connected."}), 500


    try:
        print(f"\n--- Processing new question ---")
        print(f"Received question: '{question}'")
        print("Embedding question...")
        question_embedding = model.encode(question, convert_to_tensor=True)
        print("Question embedded.")

        print("Attempting to query Chroma DB...")
        print(">>> BEFORE collection.query() call <<<")
        results = collection.query(
            query_embeddings=[question_embedding.tolist()],
            n_results=5 # Get top 5 relevant chunks
        )
        print(">>> AFTER collection.query() call <<<")
        print("Chroma DB query executed.")

        if results is not None:
            print(f"Chroma DB query returned raw results:")
            print(results)
            documents = results.get('documents')
            if documents is None:
                documents = []
            print(f"Chroma DB query returned {len(documents)} results.")
        else:
            print("Chroma DB query returned None results.")

        print("Processing Chroma DB results...")
        retrieved_chunks = results.get('documents', [])
        retrieved_metadatas = results.get('metadatas', [])

        flat_chunks = [item for sublist in retrieved_chunks for item in sublist] if retrieved_chunks else []
        flat_metadatas = [item for sublist in retrieved_metadatas for item in sublist] if retrieved_metadatas else []
        print(f"Flattened {len(flat_chunks)} chunks.")

        if not flat_chunks:
             print("No relevant chunks found in Chroma DB.")
             context = "No relevant HR policies found in the database."
             print("Preparing prompt with no context.")
        else:
            print("Preparing context from retrieved chunks...")
            max_context_tokens = 3000
            context_tokens = []
            context_chunks = []
            current_token_count = 0

            if tokenizer_llm:
                for chunk in flat_chunks:
                    try:
                        chunk_tokens = tokenizer_llm.encode(chunk, add_special_tokens=False)
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

            else:
                 for chunk in flat_chunks:
                     if len(context_chunks) < 5:
                         context_chunks.append(chunk)
                     else:
                         break
                 current_token_count = len("\n\n".join(context_chunks).split())


            context = "\n\n".join(context_chunks)
            print(f"Prepared context with {len(context_chunks)} chunks ({current_token_count} estimated tokens).")


        print("Preparing messages for LLM...")
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant for bKash employees. Answer questions based ONLY on the provided HR policies. If the policies do not contain information relevant to the question, state that the answer is not found in the provided documents. Be concise and directly answer the question."
            "Answer in the language specified, you will be instructed to answer either with bangla or english. Answer in English by default"
            }
        ]

        if context and context.strip() != "No relevant HR policies found in the database.":
             messages.append({"role": "user", "content": f"""Based on the following bKash HR policies:
             {context}

             Question: {question}

             Answer:"""})
        else:
             messages.append({"role": "user", "content": question})

        print("Messages prepared.")

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://127.0.0.1:5000", # Replace with your actual domain when deployed
            "X-Title": "bKash HR Help Desk Local Dev" # Identify your application
        }

        payload = {
            "model": OPENROUTER_MODEL,
            "messages": messages,
            "temperature": 0.0, # Keep temperature low for factual answers
            "max_tokens": 300 # Limit response length
        }

        print("Calling Open Router API...")
        # --- Switch from json=payload to data=json.dumps(payload) ---
        response = requests.post(OPENROUTER_API_BASE, headers=headers, data=json.dumps(payload))

        print(f"Open Router API call made. Status Code: {response.status_code}")
        print(f"Open Router Response Body: {response.text}") # Keep this for debugging if needed

        response.raise_for_status() # This will raise HTTPError for bad responses (like 400)
        print("Open Router API call successful.")

        openrouter_response = response.json()
        llm_answer = openrouter_response['choices'][0]['message']['content'].strip()
        print("Received response from Open Router.")

        print("Returning response to UI...")
        return jsonify({
            "answer": llm_answer,
            "source_chunks": flat_chunks, # Optionally return chunks for debugging/display
            "source_metadata": flat_metadatas # Optionally return metadata
        })

    except requests.exceptions.RequestException as e:
        print(f"\n--- Error calling Open Router API ---")
        print(f"Request Exception: {e}")
        print(f"Response status code: {e.response.status_code if e.response else 'N/A'}")
        print(f"Response body: {e.response.text if e.response else 'N/A'}")
        print(f"-------------------------------------")
        error_message = f"Error communicating with the AI service. Details: {e}"
        if e.response and e.response.text:
            error_message += f" - API Response: {e.response.text}"
        return jsonify({"error": error_message}), 500
    except Exception as e:
        print(f"\n--- An internal error occurred ---")
        print(f"Internal Error: {e}")
        traceback.print_exc()
        print(f"----------------------------------")
        return jsonify({"error": "An internal error occurred while processing your request. Please try again later."}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify system status."""
    status = {
        "status": "healthy",
        "components": {
            "embedding_model": model is not None,
            "chroma_db": collection is not None,
            "tokenizer": tokenizer_llm is not None,
            "openrouter_key": OPENROUTER_API_KEY is not None
        },
        "config": {
            "embedding_model": MODEL_NAME_EMBEDDING,
            "chroma_db_path": CHROMA_DB_PATH,
            "collection_name": COLLECTION_NAME,
            "openrouter_model": OPENROUTER_MODEL
        }
    }
    
    # Check if any critical components are missing
    if not all(status["components"].values()):
        status["status"] = "degraded"
        status["warnings"] = []
        
        if not status["components"]["embedding_model"]:
            status["warnings"].append("Embedding model not loaded")
        if not status["components"]["chroma_db"]:
            status["warnings"].append("ChromaDB not connected")
        if not status["components"]["tokenizer"]:
            status["warnings"].append("Tokenizer not loaded")
        if not status["components"]["openrouter_key"]:
            status["warnings"].append("OpenRouter API key not configured")
    
    return jsonify(status)

@app.route('/dependencies', methods=['GET'])
def check_dependencies():
    """Check and optionally install missing dependencies."""
    required_packages = {
        'flask': 'flask==3.0.0',
        'flask_cors': 'flask-cors==4.0.0',
        'chromadb': 'chromadb==1.0.16',
        'sentence_transformers': 'sentence-transformers==2.7.0',
        'transformers': 'transformers==4.41.1',
        'torch': 'torch==2.3.1',
        'requests': 'requests==2.32.3',
        'python_dotenv': 'python-dotenv==1.0.1'
    }
    
    dependency_status = {}
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        is_installed = importlib.util.find_spec(package) is not None
        dependency_status[package] = {
            "installed": is_installed,
            "pip_name": pip_name
        }
        if not is_installed:
            missing_packages.append(pip_name)
    
    response = {
        "dependencies": dependency_status,
        "missing_count": len(missing_packages),
        "missing_packages": missing_packages
    }
    
    # Auto-install if requested
    auto_install = request.args.get('auto_install', 'false').lower() == 'true'
    if auto_install and missing_packages:
        try:
            response["installation_attempted"] = True
            response["installation_success"] = True
            response["installation_log"] = []
            
            for package in missing_packages:
                response["installation_log"].append(f"Installing {package}...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], capture_output=True, text=True, check=True)
                response["installation_log"].append(f"Successfully installed {package}")
            
            response["message"] = "All missing dependencies installed successfully. Please restart the application."
            
        except subprocess.CalledProcessError as e:
            response["installation_success"] = False
            response["installation_error"] = str(e)
            response["installation_stderr"] = e.stderr
            response["message"] = "Failed to install some dependencies. Please install manually."
    
    return jsonify(response)

@app.route('/version', methods=['GET'])
def get_version():
    """Get application version and information."""
    return jsonify({
        "name": "HR-Policy-QA-System",
        "version": "1.0.0",
        "description": "Intelligent HR policy question-answering system using RAG",
        "architecture": {
            "embedding_model": MODEL_NAME_EMBEDDING,
            "vector_store": "ChromaDB",
            "llm_provider": "OpenRouter",
            "llm_model": OPENROUTER_MODEL
        }
    })

# Debugging off for now
if __name__ == '__main__':
    app.run(debug=False, port=5002)

