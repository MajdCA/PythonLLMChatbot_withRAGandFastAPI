# Models
ollama pull mistral
# or use other models: ollama pull neural-chat, ollama pull orca-mini
# embeddings model for vector store
ollama pull nomic-embed-text:latest

# Run Ollama
ollama serve

# Install deps
pip install -r requirements.txt

# Create PDFs folder (put your PDFs here)
# Windows CMD:
mkdir pdfs
# PowerShell:
New-Item -ItemType Directory -Path pdfs -Force | Out-Null

# Build the vector store (one-time or when PDFs change)
# Default paths:
# - PDFs folder: ./pdfs
# - Output store: ./vectorstore/vector_store.json
python vectorstore/build_vectorstore.py
# Optional: save builder logs
python vectorstore/build_vectorstore.py > build.log 2>&1

# Environment (optional)
# LOG_LEVEL can be INFO or DEBUG; LOG_DIR controls log file directory
# OLLAMA_URL defaults to http://192.168.1.253:11435
# OLLAMA_EMBED_MODEL defaults to nomic-embed-text:latest
# VECTOR_STORE_PATH defaults to ./vectorstore/vector_store.json
# Example:
#   set LOG_LEVEL=DEBUG
#   set LOG_DIR=C:\temp\geoatlas-logs
#   set OLLAMA_URL=http://localhost:11434

# Run API (logs go to console and to logs/app-YYYYMMDD-HHMMSS.log)
python main.py

# CLI example (if you have a cli.py)
python cli.py "how to navigate the website"