# Geoatlas Chatbot - Usage Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Starting the Application](#starting-the-application)
3. [Adding Knowledge Manually](#adding-knowledge-manually)
4. [Loading Documents (PDFs & PowerPoints)](#loading-documents-pdfs--powerpoints)
5. [Using the API](#using-the-api)
6. [Using the CLI](#using-the-cli)
7. [Data Persistence](#data-persistence)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Python 3.9+
- Ollama running on network
- Git (optional)

### Installation

```bash
# 1. Navigate to project directory
cd c:\Users\Ase2\Desktop\chatbotv3

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Windows:
.\.venv\Scripts\Activate
# On Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### First Run

```bash
# Terminal 1: Start Ollama (on Linux server)
ollama serve

# Terminal 2: Start FastAPI
python main.py

# Terminal 3: Test the chatbot
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Hi"}'
```

---

## Starting the Application

### Step-by-Step Startup

**Step 1: Start Ollama (Linux Server - 192.168.1.253)**

```bash
# SSH into server or local terminal
ollama serve

# Expected output:
# Listening on 127.0.0.1:11434 (version 0.12.1)
# Looking for compatible GPUs
# GPU-... NVIDIA GeForce RTX 5060
```

**Step 2: Verify Ollama is Running**

```bash
# From your Windows machine
curl http://192.168.1.253:11434/api/tags

# Expected output:
# {"models":[{"name":"llama3.1:latest",...}]}
```

**Step 3: Start FastAPI Server**

```bash
# Windows Terminal
cd c:\Users\Ase2\Desktop\chatbotv3
.\.venv\Scripts\Activate
python main.py

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

**Step 4: Verify FastAPI is Running**

```bash
curl http://localhost:8000/health

# Expected output:
# {"status":"ok","assistant":"Geoatlas"}
```

**Step 5: Open Swagger UI (Optional)**

```
Browser: http://localhost:8000/docs
```

You'll see all available endpoints with test forms.

---

## Adding Knowledge Manually

### Method 1: Direct Code Edit (Simple)

Edit `knowledge_base.py`:

```python
// filepath: c:\Users\Ase2\Desktop\chatbotv3\knowledge_base.py

self.knowledge = {
    "geotechnical": [
        # Add new entry here
        {
            "query": "what is pore pressure",
            "answer": "Pore pressure is the pressure exerted by pore water in soil. It affects effective stress and stability."
        },
        {
            "query": "settlement monitoring definition",
            "answer": "Settlement monitoring measures vertical displacement of structures over time to ensure safety."
        }
    ]
}
```

**Then restart app:**
```bash
# Stop current app (Ctrl+C)
# Restart
python main.py
```

### Method 2: Via API During Runtime (No Restart)

**Using Postman:**

```
POST http://localhost:8000/add-knowledge
Content-Type: application/json

{
  "category": "geotechnical",
  "query": "what causes differential settlement",
  "answer": "Differential settlement occurs when different parts of a foundation settle by different amounts, causing structural stress."
}
```

**Using curl:**

```bash
curl -X POST http://localhost:8000/add-knowledge \
  -H "Content-Type: application/json" \
  -d '{
    "category": "instruments",
    "query": "what is a tiltmeter",
    "answer": "A tiltmeter is an instrument that measures small changes in angle/tilt. Range: ±10 degrees, Accuracy: ±0.01 degrees"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Knowledge added to instruments"
}
```

### Method 3: Via CLI (Programmatically)

This is NOT directly supported yet. You would need to create a script:

```python
// filepath: c:\Users\Ase2\Desktop\chatbotv3\add_knowledge_cli.py

import argparse
from knowledge_base import KnowledgeBase

def main():
    parser = argparse.ArgumentParser(description="Add knowledge to Geoatlas")
    parser.add_argument("--category", required=True, help="Knowledge category")
    parser.add_argument("--query", required=True, help="Question/keyword")
    parser.add_argument("--answer", required=True, help="Answer text")
    parser.add_argument("--save", action="store_true", help="Save to file")
    
    args = parser.parse_args()
    
    kb = KnowledgeBase()
    kb.add_knowledge(args.category, args.query, args.answer)
    
    if args.save:
        kb.save_to_file("knowledge_base.json")
        print(f"✓ Knowledge saved to file")
    else:
        print(f"✓ Knowledge added to memory (not persisted)")

if __name__ == "__main__":
    main()
```

Usage:
```bash
python add_knowledge_cli.py \
  --category "instruments" \
  --query "what is a piezometer" \
  --answer "A piezometer measures pore water pressure in soil" \
  --save
```

---

## Loading Documents (PDFs & PowerPoints)

### Important Notes

**Before Loading Documents:**
- Ensure app is running: `python main.py`
- Have your PDF/PPTX files ready
- Know the file paths

**After Loading Documents:**
- Changes are in MEMORY ONLY
- App restart = loss of changes
- Must SAVE to persist

---

### Method 1: Upload via API (Easiest)

**Using Postman:**

1. Open Postman
2. Create new request: `POST http://localhost:8000/upload-pdf`
3. Go to **Body** tab → select **form-data**
4. Add field:
   - Key: `file`
   - Value: (click file picker, select PDF)
5. Add field:
   - Key: `category`
   - Value: `technical_data`
6. Click **Send**

**Expected Response:**
```json
{
  "status": "success",
  "message": "PDF loaded: geotechnical_monitoring.pdf"
}
```

**Using curl:**

```bash
# Upload PDF
curl -X POST http://localhost:8000/upload-pdf \
  -F "file=@geotechnical_monitoring.pdf" \
  -F "category=technical_data"

# Upload PowerPoint
curl -X POST http://localhost:8000/upload-powerpoint \
  -F "file=@instruments.pptx" \
  -F "category=instruments"
```

---

### Method 2: CLI Command (for batch loading)

**Load single PDF:**

```bash
python load_documents.py --pdf "geotechnical_monitoring.pdf" --category "technical"
```

**Load single PowerPoint:**

```bash
python load_documents.py --pptx "instruments.pptx" --category "instruments"
```

**Load entire directory:**

```bash
python load_documents.py --dir "./documents"
```

This will:
- Scan folder for all PDFs and PPTXs
- Auto-categorize: PDFs → "pdf_documents", PPTXs → "presentations"
- Load all files

**Load and save to disk:**

```bash
python load_documents.py --dir "./documents" --save
```

This also saves the KB to `knowledge_base.json` for persistence.

---

### Method 3: Manual Script (Advanced)

Create a custom loading script:

```python
// filepath: c:\Users\Ase2\Desktop\chatbotv3\custom_load.py

from knowledge_base import KnowledgeBase
from knowledge_loader import KnowledgeLoader

# Initialize
kb = KnowledgeBase()
loader = KnowledgeLoader(kb)

# Load multiple documents
loader.load_pdf_to_kb("documents/geotechnical_monitoring.pdf", "technical")
loader.load_pdf_to_kb("documents/soil_properties.pdf", "technical")
loader.load_powerpoint_to_kb("documents/instruments.pptx", "equipment")

# Check stats
print(f"Total entries: {sum(len(v) for v in kb.knowledge.values())}")

# Save for next app run
loader.save_kb_to_file("knowledge_base.json")
```

Run it:
```bash
python custom_load.py
```

---

## Using the API

### Endpoint: POST /chat (Query Chatbot)

**Request:**
```json
POST http://localhost:8000/chat
Content-Type: application/json

{
  "query": "how to navigate the website"
}
```

**Response (Fast - KB Match):**
```json
{
  "query": "how to navigate the website",
  "answer": "You can navigate using the left sidebar menu. Click on different sections like Dashboard, Monitoring, Reports, and Settings."
}
```

**Response (Slow - Ollama Generation):**
```json
{
  "query": "what are the challenges of geotechnical monitoring",
  "answer": "Geotechnical monitoring faces several challenges including sensor accuracy, data interpretation, environmental factors, and cost-effectiveness. Modern solutions use automated monitoring systems with real-time alerts..."
}
```

### Endpoint: POST /add-knowledge (Add Q&A)

**Request:**
```json
POST http://localhost:8000/add-knowledge
Content-Type: application/json

{
  "category": "geotechnical",
  "query": "what is differential settlement",
  "answer": "Differential settlement occurs when different parts of a foundation settle by different amounts..."
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Knowledge added to geotechnical"
}
```

### Endpoint: POST /upload-pdf (Load PDF)

**Request:**
```
POST http://localhost:8000/upload-pdf
Content-Type: multipart/form-data

file: [binary PDF data]
category: technical_data
```

**Response:**
```json
{
  "status": "success",
  "message": "PDF loaded: monitoring_guide.pdf"
}
```

### Endpoint: GET /categories (List Categories)

**Request:**
```
GET http://localhost:8000/categories
```

**Response:**
```json
{
  "categories": [
    "greetings",
    "navigation",
    "configuration",
    "geotechnical",
    "technical_data",
    "instruments"
  ]
}
```

### Endpoint: GET /kb-stats (Knowledge Base Statistics)

**Request:**
```
GET http://localhost:8000/kb-stats
```

**Response:**
```json
{
  "total_entries": 127,
  "by_category": {
    "greetings": 4,
    "navigation": 3,
    "configuration": 2,
    "geotechnical": 5,
    "technical_data": 89,
    "instruments": 24
  }
}
```

---

## Using the CLI

### Load Documents from Terminal

**Load PDF with specific category:**

```bash
python load_documents.py --pdf "geotechnical_monitoring.pdf" --category "technical"
```

Output:
```
✓ Loaded 45 chunks from PDF: geotechnical_monitoring.pdf
✓ Added 45 entries from PDF to knowledge base
```

**Load PowerPoint:**

```bash
python load_documents.py --pptx "instruments.pptx" --category "equipment"
```

**Load directory (all PDFs & PPTXs):**

```bash
python load_documents.py --dir "./documents"
```

**Load and save to disk:**

```bash
python load_documents.py --dir "./documents" --save
```

Output:
```
✓ Loaded 15 chunks from PDF: doc1.pdf
✓ Loaded 28 chunks from PDF: doc2.pdf
✓ Loaded 12 chunks from PPTX: presentation.pptx
✓ Knowledge base saved to knowledge_base.json
```

---

## Data Persistence

### How Persistence Works

**App Runtime:**
```
Python Process
  ↓
Knowledge Base (in RAM)
  ├─ Predefined entries
  └─ Loaded from PDFs/PPTXs
  ↓
Available until app stops
```

**Persistent Storage:**
```
knowledge_base.json (on disk)
  ├─ Contains complete KB
  ├─ Survives app restarts
  └─ Must be manually saved
```

### Do I Need to Reload Documents?

**Each Time App Restarts:**

| Scenario | Need Reload? | Explanation |
|----------|--------------|-------------|
| Modified code KB entries | No | Auto-loaded from knowledge_base.py |
| Uploaded PDFs via API | **YES** | Lost when app stopped (unless saved) |
| Loaded via CLI without --save | **YES** | Lost when app stopped |
| Loaded via CLI with --save | No | Persisted in knowledge_base.json |
| Loaded with load_kb_from_file() | No | Auto-loads at startup |

### Auto-Load on Startup

Edit `main.py` to auto-load KB:

```python
// filepath: c:\Users\Ase2\Desktop\chatbotv3\main.py

import os
from fastapi import FastAPI
from llm_chat import ChatBot
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Geoatlas Chatbot API")
chatbot = ChatBot()

# Auto-load KB from file on startup
if os.path.exists("knowledge_base.json"):
    chatbot.knowledge_base.load_from_file("knowledge_base.json")
    print("✓ Knowledge base loaded from file")
else:
    print("ℹ No saved knowledge base found, using defaults")

# ... rest of code
```

Now KB persists across restarts automatically!

### Manual Save

```bash
# In Python REPL or script
from knowledge_base import KnowledgeBase

kb = KnowledgeBase()
kb.save_to_file("knowledge_base.json")
```

---

## Storage: Vector vs JSON

### Current Implementation: JSON (Simple)

**Pros:**
- ✅ Simple to understand
- ✅ Human-readable
- ✅ Easy to backup/edit
- ✅ No database needed

**Cons:**
- ❌ Slow for large datasets (1000+ entries)
- ❌ Full text search not optimized
- ❌ Not suitable for semantic search

**Example:**
```json
{
  "geotechnical": [
    {
      "query": "pore pressure",
      "answer": "Pore pressure is...",
      "source": "monitoring.pdf"
    }
  ]
}
```

### Future: Vector Database (Advanced)

**NOT currently implemented, but recommended for scale:**

```
Document
  ↓
Split into chunks (300 chars)
  ↓
Convert to embeddings (768-dim vectors)
  ↓
Store in vector DB (Pinecone, Weaviate)
  ↓
Query returns semantic matches
```

**Benefits:**
- Fast semantic search
- Find similar content
- Scale to 1M+ documents

---

## Troubleshooting

### Problem: "Cannot connect to Ollama"

**Error:**
```
Error: Cannot connect to Ollama at 192.168.1.253:11434
```

**Solution:**
```bash
# 1. Check Ollama is running
curl http://192.168.1.253:11434/api/tags

# 2. Verify firewall allows port 11434
# 3. Check network connectivity
ping 192.168.1.253

# 4. Restart Ollama
# On Linux server:
pkill ollama
ollama serve
```

### Problem: "Query returns wrong answer"

**Reason:** KB confidence < 0.85, using Ollama

**Check confidence:**

```python
from knowledge_base import KnowledgeBase

kb = KnowledgeBase()
answer, confidence = kb.search_with_confidence("your query")
print(f"Confidence: {confidence}")
```

**If confidence is low:**
- Add exact Q&A match to KB
- Restart app
- Query again (should be instant)

### Problem: "PDF not loading"

**Error:**
```json
{"status": "error", "message": "..."}
