# GEOATLAS CHATBOT - Setup & Running Guide (Linux)
# 
# === PREREQUISITES ===
# - Python 3.8+
# - Ollama running locally or on your network
# - PDFs for knowledge base (optional)
# 


////////////  RUN OLLAMA :
OLLAMA_HOST=0.0.0.0:11435 ollama serve










# === INSTALLATION ===
# 
# 1. Clone/extract project to ~/chatbotv3
#    cd ~/chatbotv3
# 
# 2. Create and run the virtual environment
#    python3 -m venv venv
#    source venv/bin/activate
# 
# 3. Install dependencies
#    pip install -r requirements.txt
# 
# === ENVIRONMENT SETUP ===
# 
# 4. Create .env file in project root
#    cp .env.example .env  (or create manually)
#    
#    Add these variables:
#    OLLAMA_URL=http://192.168.1.253:11435
#    OLLAMA_MODEL=llama3.1:latest
#    OLLAMA_EMBED_MODEL=nomic-embed-text
#    KB_CONFIDENCE_THRESHOLD=0.85
#    LOG_LEVEL=INFO
#    LOG_DIR=./logs
# 
# === BUILD VECTOR STORE if not created ===
# 
# 5. Place PDF documents in: ~/chatbotv3/pdfs/
# 
# 6. Build vector store from PDFs
#    cd ~/chatbotv3
#    python3 -m vectorstore.build_vectorstore
#    
#    Optional parameters:
#    python3 -m vectorstore.build_vectorstore --pdf-dir ./pdfs --chunk-size 1000 --overlap 200
# 
#    Output: ~/chatbotv3/vectorstore/vector_store.json
# 
# === RUN THE CHATBOT API ===
# 
# 7. Start the FastAPI server
#    cd ~/chatbotv3
#    python3 main.py
#    
#    Server runs on: http://0.0.0.0:8001
# 
# 8. Test the API
#    curl -X POST http://localhost:8001/chat \
#      -H "Content-Type: application/json" \
#      -d '{"query": "hello"}'
# 
# === UPDATE KNOWLEDGE BASE ===
# 
# 9. Add knowledge via API
#    curl -X POST http://localhost:8001/add-knowledge \
#      -H "Content-Type: application/json" \
#      -d '{"category": "navigation", "query": "how to navigate", "answer": "Use the sidebar menu"}'
# 
# 10. Or edit knowledge_base_data.json manually and restart server
# 
# === UPDATE VECTOR STORE ===
# 
# 11. Add new PDFs to ~/chatbotv3/pdfs/
# 
# 12. Rebuild vector store
#     cd ~/chatbotv3
#     python3 -m vectorstore.build_vectorstore
# 
# 13. Restart API server
# 
# === LOGS ===
# Logs are stored in: ./logs/app-YYYYMMDD-HHMMSS.log
# 
# === TROUBLESHOOTING ===
# - If Ollama connection fails: Check OLLAMA_URL in .env
# - If vector store not loading: Ensure vector_store.json exists
# - If PDFs not found: Place PDFs in ~/chatbotv3/pdfs/ directory

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
#   set OLLAMA_URL=http://localhost:11435

# Run API (logs go to console and to logs/app-YYYYMMDD-HHMMSS.log)
python main.py

# CLI example (if you have a cli.py)
python cli.py "how to navigate the website"