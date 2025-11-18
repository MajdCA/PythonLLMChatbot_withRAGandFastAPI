# Geoatlas Chatbot - Architecture & Code Explanation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Component Breakdown](#component-breakdown)
3. [Data Flow](#data-flow)
4. [Storage & Persistence](#storage--persistence)
5. [Key Technologies](#key-technologies)

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                 │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  FastAPI     │  │  CLI Tool    │  │  Postman     │  │
│  │  REST API    │  │  (local)     │  │  (testing)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                    │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐  │
│  │  ChatBot (llm_chat.py)                           │  │
│  │  - Orchestrates query processing                 │  │
│  │  - Decides: KB only vs KB + Ollama               │  │
│  └──────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                    KNOWLEDGE LAYER                      │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │ KnowledgeBase    │  │ KnowledgeLoader         │   │
│  │ - Search/Match   │  │ - Load PDFs             │   │
│  │ - Calculate      │  │ - Load PowerPoints      │   │
│  │   confidence     │  │ - Chunk documents      │   │
│  │ - Store data     │  │ - Format tables        │   │
│  └──────────────────┘  └──────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ DocumentLoader (document_loader.py)              │  │
│  │ - PDF extraction (text + tables)                 │  │
│  │ - PowerPoint extraction (slides + tables)        │  │
│  │ - Text chunking (RecursiveCharacterTextSplitter) │  │
│  └──────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                    STORAGE LAYER                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐   │
│  │  Memory (Python Dictionary)                     │   │
│  │  - Fast access during runtime                   │   │
│  │  - Lost when app restarts (unless persisted)    │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Persistent Storage (knowledge_base.json)       │   │
│  │  - Survives app restarts                        │   │
│  │  - Manual backup/restore                        │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│                    AI LAYER                             │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐  │
│  │  Ollama (Local LLM Server)                       │  │
│  │  - Model: llama3.1:latest                        │  │
│  │  - GPU: NVIDIA RTX 5060 (7.5GB VRAM)            │  │
│  │  - Location: 192.168.1.253:11434                │  │
│  │  - Used when KB confidence < 0.85               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. **main.py** - FastAPI Server

**Purpose:** REST API endpoint server

**Key Endpoints:**
```python
POST /chat
  - Input: {"query": "your question"}
  - Output: {"query": "...", "answer": "..."}
  - Uses: ChatBot.answer()

POST /add-knowledge
  - Input: {"category": "...", "query": "...", "answer": "..."}
  - Output: {"status": "success"}
  - Uses: ChatBot.add_knowledge()

POST /upload-pdf
  - Input: File upload (PDF)
  - Output: {"status": "success", "message": "..."}
  - Uses: KnowledgeLoader.load_pdf_to_kb()

POST /upload-powerpoint
  - Input: File upload (PPTX)
  - Output: {"status": "success", "message": "..."}
  - Uses: KnowledgeLoader.load_powerpoint_to_kb()

GET /categories
  - Output: {"categories": ["greetings", "navigation", ...]}
  
GET /health
  - Output: {"status": "ok", "assistant": "Geoatlas"}

GET /kb-stats
  - Output: {"total_entries": 100, "by_category": {...}}
```

---

### 2. **llm_chat.py** - ChatBot Orchestrator

**Purpose:** Central logic for answering queries with RAG + confidence-based optimization

**Classes & Methods:**

```python
class ChatBot:
    def __init__(self, ollama_url, model, kb_confidence_threshold)
        # Initialization
        # self.ollama_url = "http://192.168.1.253:11434"
        # self.model = "llama3.1:latest"
        # self.kb_confidence_threshold = 0.85
    
    def answer(query: str) -> str:
        """
        MAIN ENTRY POINT
        
        Flow:
        1. Call KB.search_with_confidence(query)
           Returns: (answer, confidence_score)
        
        2. If confidence >= 0.85:
           - Return KB answer immediately (FAST ~5-10ms)
           - Skip Ollama completely
        
        3. If confidence < 0.85:
           - Get context: KB.search_with_context(query)
           - Call _ollama_answer_with_rag()
           - Return AI-enhanced answer (SLOW ~2-3s)
        """
    
    def _ollama_answer_with_rag(query, context) -> str:
        """
        RAG (Retrieval-Augmented Generation)
        
        Flow:
        1. Build system_prompt with knowledge context
        2. Send HTTP POST to Ollama server
           - URL: http://192.168.1.253:11434/api/generate
           - Body: {model, prompt, stream, temperature, ...}
        3. Wait for response (GPU processing)
        4. Extract and return answer
        """
    
    def add_knowledge(category, query, answer) -> None:
        """Add new Q&A to knowledge base"""
```

**Decision Tree:**

```
Query: "how to navigate"
  ↓
KB.search_with_confidence("how to navigate")
  → Returns: ("Use left sidebar...", 0.95)
  ↓
Is 0.95 >= 0.85? YES
  ↓
Return KB answer immediately ⚡ FAST
  
---

Query: "geotechnical monitoring challenges"
  ↓
KB.search_with_confidence("geotechnical monitoring challenges")
  → Returns: ("", 0.15)  [no good match]
  ↓
Is 0.15 >= 0.85? NO
  ↓
Get context: KB.search_with_context()
  → Returns top 3 relevant entries
  ↓
Call Ollama with context 🤖 SLOW but ACCURATE
  ↓
Return AI-generated answer
```

---

### 3. **knowledge_base.py** - Data Storage & Retrieval

**Purpose:** Store and search Q&A pairs

**Data Structure:**

```python
self.knowledge = {
    "greetings": [
        {"query": "hi", "answer": "Hi I am Geoatlas...", "source": "manual"},
        {"query": "hello", "answer": "Hi I am Geoatlas...", "source": "manual"},
    ],
    "navigation": [
        {"query": "how to navigate", "answer": "Use left sidebar...", "source": "manual"},
    ],
    "technical": [
        {
            "query": "What is pore pressure?",
            "answer": "Pore pressure is the pressure exerted by pore water...",
            "source": "geotechnical_monitoring.pdf (Page 5)"
        }
    ],
    "pdf_documents": [...],
    "presentations": [...]
}
```

**Key Methods:**

```python
def search_with_confidence(query: str) -> Tuple[str, float]:
    """
    Purpose: Find best matching KB entry with confidence score
    
    Returns: (answer, score) where score = 0.0 to 1.0
    
    Logic:
    1. Exact match?
       query_lower == stored_query_lower → return (answer, 1.0)
    
    2. Similarity match?
       Calculate SequenceMatcher ratio for all entries
       Return best match with score
    
    3. No match?
       Return ("", 0.0)
    
    Examples:
    - "hi" vs "hi" → 1.0 (exact)
    - "how to navigate" vs "how to navigate the website" → 0.95
    - "random gibberish" vs any → < 0.3
    """

def search_with_context(query: str, top_k=3) -> str:
    """
    Purpose: Find top K relevant entries for context (RAG)
    
    Returns: Formatted string for Ollama
    
    Logic:
    1. Calculate similarity scores for ALL entries
    2. Sort by score (highest first)
    3. Take top K entries
    4. Filter: only scores > 0.3
    5. Format as readable context
    
    Example Output:
    "Related knowledge base entries:
    1. Q: What is pore pressure?
       A: Pore pressure is the pressure exerted by pore water...
    2. Q: How does settlement occur?
       A: Settlement is the vertical displacement of structures..."
    """

def save_to_file(filepath) -> None:
    """Save entire KB to JSON for persistence"""

def load_from_file(filepath) -> None:
    """Load KB from JSON file"""
```

**Similarity Scoring - How It Works:**

```python
from difflib import SequenceMatcher

# Example: user query vs stored query
user_query = "how to navigate"
stored_query = "how to navigate the website"

ratio = SequenceMatcher(None, user_query, stored_query).ratio()
# ratio = 0.95 (95% similar)

# Thresholds:
# >= 0.85 → Use KB directly (FAST)
# 0.5-0.84 → Use Ollama with context (ACCURATE)
# < 0.5 → Use Ollama with context (explore more)
```

---

### 4. **document_loader.py** - Document Processing

**Purpose:** Extract knowledge from PDFs and PowerPoints

**Data Processing Pipeline:**

```
PDF/PowerPoint File
  ↓
1. EXTRACTION
  ├─ PDF: Use pdfplumber
  │  ├─ Extract text from pages
  │  └─ Extract tables (technical data)
  └─ PPTX: Use python-pptx
     ├─ Extract text from slides
     └─ Extract tables from shapes
  ↓
2. CHUNKING
  ├─ RecursiveCharacterTextSplitter
  │  ├─ chunk_size = 300 characters
  │  ├─ chunk_overlap = 50 characters
  │  └─ Separators: ["\n\n", "\n", ". ", " ", ""]
  ↓
3. FORMATTING
  ├─ Tables formatted as readable text
  ├─ Each chunk has metadata:
  │  ├─ source: "filename (Page X)"
  │  ├─ type: "pdf_text" | "pdf_table" | "pptx_text"
  │  └─ content: actual text
  ↓
4. OUTPUT
  └─ List[Dict[str, str]]
     [
       {"source": "...", "type": "pdf_text", "content": "...", "page": 1},
       {"source": "...", "type": "pdf_table", "content": "...", "page": 1},
       ...
     ]
```

**Example - PDF Table Processing:**

```
Original PDF Table:
┌──────────────────┬──────────┬─────────────┐
│ Instrument       │ Range    │ Accuracy    │
├──────────────────┼──────────┼─────────────┤
│ Tiltmeter        │ ±10°     │ ±0.01°      │
│ Piezometer       │ 0-500kPa │ ±2kPa       │
└──────────────────┴──────────┴─────────────┘

Extracted as:
"TABLE:
Instrument | Range | Accuracy
Tiltmeter | ±10° | ±0.01°
Piezometer | 0-500kPa | ±2kPa"

Then chunked and added to KB:
{
  "query": "Tiltmeter TABLE: Instrument | Range | Accuracy...",
  "answer": "[full table text]",
  "source": "instruments.pdf (Page 3, Table 1)"
}
```

---

### 5. **knowledge_loader.py** - Document → KB Integration

**Purpose:** Bridge between documents and knowledge base

**Key Methods:**

```python
def load_pdf_to_kb(pdf_path, category="documents") -> None:
    """
    1. Call DocumentLoader.load_pdf()
    2. Get list of document chunks
    3. For each chunk:
       - Add to KB with category
       - Track source (filename + page)
    """

def load_powerpoint_to_kb(pptx_path, category="presentations") -> None:
    """
    1. Call DocumentLoader.load_powerpoint()
    2. Get list of slide chunks
    3. For each chunk:
       - Add to KB with category
       - Track source (filename + slide)
    """

def load_directory_to_kb(directory) -> None:
    """
    Scan directory for all PDFs and PPTXs
    Auto-load everything
    """

def save_kb_to_file(filepath="knowledge_base.json") -> None:
    """Persist KB to disk"""

def load_kb_from_file(filepath="knowledge_base.json") -> None:
    """Restore KB from disk"""
```

---

## Data Flow

### Flow 1: User Sends Query via API

```
┌─────────────────────────────────────────────────────────┐
│ User sends POST request to /chat                        │
│ {"query": "how to navigate"}                            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ FastAPI (main.py)                                       │
│ @app.post("/chat")                                      │
│ - Validate query (not empty)                            │
│ - Call chatbot.answer(query)                            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ ChatBot.answer()                                        │
│ 1. kb.search_with_confidence(query)                     │
│    → ("Use left sidebar...", 0.95)                      │
│ 2. Is 0.95 >= 0.85? YES                                 │
│ 3. Return KB answer immediately                         │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ FastAPI returns response                                │
│ {                                                       │
│   "query": "how to navigate",                           │
│   "answer": "Use left sidebar..."                       │
│ }                                                       │
└─────────────────────────────────────────────────────────┘
```

### Flow 2: User Sends Query via CLI

```
┌─────────────────────────────────────────────────────────┐
│ CLI (load_documents.py)                                 │
│ python load_documents.py --pdf "file.pdf" --save        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ KnowledgeLoader.load_pdf_to_kb()                        │
│ 1. DocumentLoader.load_pdf()                            │
│    - Extract text + tables from PDF                     │
│    - Chunk into 300-char pieces                         │
│    - Return list of documents                           │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ KnowledgeBase.add_knowledge()                           │
│ For each chunk:                                         │
│ - Add to self.knowledge[category]                       │
│ - Store source reference                               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ KnowledgeLoader.save_kb_to_file()                       │
│ - Serialize KB to knowledge_base.json                   │
│ - Persists for next app run                             │
└─────────────────────────────────────────────────────────┘
```

### Flow 3: Upload Document via API

```
┌─────────────────────────────────────────────────────────┐
│ User uploads file to POST /upload-pdf                   │
│ multipart/form-data: file="document.pdf"                │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ FastAPI (main.py)                                       │
│ @app.post("/upload-pdf")                                │
│ 1. Save temp file                                       │
│ 2. Create KnowledgeLoader                               │
│ 3. Call loader.load_pdf_to_kb()                         │
│ 4. Delete temp file                                     │
│ 5. Return success                                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ IMPORTANT: Changes only in MEMORY                       │
│ Knowledge NOT persisted to disk unless:                 │
│ - Manually save with /save-kb endpoint                  │
│ - Or restart app (will lose changes!)                   │
└─────────────────────────────────────────────────────────┘
```

---

## Storage & Persistence

### How Data is Stored

**Runtime Storage (Memory):**
```python
# When app is running
self.knowledge = {
    "category": [
        {"query": "...", "answer": "...", "source": "..."},
        ...
    ]
}

# Stored in RAM
# FAST access (microseconds)
# LOST when app stops
```

**Persistent Storage (Disk):**
```json
// knowledge_base.json
{
  "greetings": [
    {
      "query": "hi",
      "answer": "Hi I am Geoatlas...",
      "source": "manual"
    }
  ],
  "pdf_documents": [...]
}

// Stored on disk
// SURVIVES app restarts
// Must be explicitly saved/loaded
```

### Save/Load Process

**Saving:**
```python
# In code
kb.save_to_file("knowledge_base.json")

# In CLI
python load_documents.py --pdf "file.pdf" --save

# API endpoint (not implemented yet)
# POST /save-kb → kb.save_to_file()
```

**Loading:**
```python
# On app startup
if os.path.exists("knowledge_base.json"):
    kb.load_from_file("knowledge_base.json")

# In CLI
python load_documents.py --dir "./docs" --save

# This loads previously saved KB into memory
```

---

## Key Technologies

### 1. **FastAPI** - Web Framework
- REST API creation
- Automatic documentation (Swagger UI at /docs)
- Request validation with Pydantic

### 2. **Ollama** - Local LLM Server
- Runs on 192.168.1.253:11434
- Model: llama3.1:latest
- GPU: NVIDIA RTX 5060 (7.5GB VRAM)
- Used for complex queries when KB confidence < 0.85

### 3. **pdfplumber** - PDF Processing
- Extracts text from PDF pages
- Extracts tables as structured data
- Handles complex PDFs

### 4. **python-pptx** - PowerPoint Processing
- Extracts text from slides
- Extracts tables from shapes
- Works with .pptx files

### 5. **LangChain** - Text Processing
- RecursiveCharacterTextSplitter
- Intelligent text chunking
- Preserves context with overlap

### 6. **SequenceMatcher** - Similarity Scoring
- Fuzzy string matching
- Confidence calculation (0-1 scale)
- Used for query similarity

---

## Performance Characteristics

### Response Times

| Scenario | Time | Path |
|----------|------|------|
| KB exact match | ~5ms | KB only (fast) |
| KB high confidence (0.85+) | ~10ms | KB only (fast) |
| Low confidence query | ~2-3s | KB + Ollama (accurate) |
| First Ollama call | +500ms | Model load overhead |
| Complex reasoning query | ~3-5s | Ollama GPU processing |

### Memory Usage

| Component | Memory |
|-----------|--------|
| Python process | ~150MB |
| KB in RAM (100 entries) | ~5MB |
| Ollama model (llama3.1) | ~4.7GB (on GPU) |
| Total system | ~4.8GB |

---

## Scalability Considerations

**Current Limitations:**
- KB stored in single Python dictionary (not distributed)
- All data in memory (RAM constrained)
- Single Ollama instance (sequential queries)

**Future Improvements:**
- Vector database (Pinecone, Weaviate)
- ElasticSearch for full-text search
- Distributed KB across multiple servers
- Query queuing for concurrent requests
