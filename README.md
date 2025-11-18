# Geoatlas Chatbot

**Hybrid AI chatbot combining Knowledge Base + Ollama LLM for geotechnical monitoring assistance.**

## Quick Links

- 📚 **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design & code explanation
- 🚀 **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - How to use, add knowledge, load documents

## Quick Start

```bash
# 1. Install
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt

# 2. Start Ollama (on 192.168.1.253)
ollama serve

# 3. Start app
python main.py

# 4. Test
curl http://localhost:8000/chat -H "Content-Type: application/json" -d '{"query":"Hi"}'
```

## Core Features

✅ **Hybrid Response Engine**
- Fast path: Knowledge Base (< 10ms)
- Accurate path: Ollama LLM (2-3s)

✅ **Document Processing**
- Load PDFs with text + tables
- Load PowerPoints with slides
- Auto-chunking & formatting

✅ **Knowledge Management**
- Add Q&A manually
- Load from documents
- Persist to disk
- Auto-load on startup

✅ **GPU Acceleration**
- NVIDIA RTX 5060 (7.5GB VRAM)
- llama3.1:latest model
- Sub-second inference

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | Query the chatbot |
| `/add-knowledge` | POST | Add Q&A manually |
| `/upload-pdf` | POST | Load PDF file |
| `/upload-powerpoint` | POST | Load PowerPoint |
| `/categories` | GET | List KB categories |
| `/kb-stats` | GET | KB statistics |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |

## Architecture

```
User Query
  ↓
FastAPI
  ↓
ChatBot (decision engine)
  ├→ KB confidence >= 0.85? → Return fast ⚡
  └→ KB confidence < 0.85? → Use Ollama 🤖
  ↓
Response
```

## Storage

- **Runtime:** Python dictionary (RAM)
- **Persistent:** `knowledge_base.json`
- **Auto-load:** Enabled (restart-proof)

## Technologies

- **Framework:** FastAPI + Uvicorn
- **AI:** Ollama + llama3.1
- **Documents:** pdfplumber, python-pptx
- **Processing:** LangChain
- **Storage:** JSON

## Team

Built for Geoatlas geotechnical monitoring platform.

---

See **[USAGE_GUIDE.md](USAGE_GUIDE.md)** for detailed instructions!