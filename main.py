import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from llm_chat import ChatBot
from knowledge_loader import KnowledgeLoader
from vector_store import VectorStore
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Geoatlas Chatbot API")

# Initialize with vector store enabled
chatbot = ChatBot(use_vector_store=True)
vector_store = chatbot.vector_store
knowledge_loader = KnowledgeLoader(chatbot.knowledge_base, vector_store)

# Auto-load KB and vector store on startup
@app.on_event("startup")
async def startup_event():
    """Load saved KB and vector store on app start"""
    if os.path.exists("knowledge_base.json"):
        chatbot.knowledge_base.load_from_file("knowledge_base.json")
        print("✓ KB loaded from knowledge_base.json")
    
    # Vector store auto-loads from chroma_db/ (handled by ChromaDB)
    stats = vector_store.get_stats()
    print(f"✓ Vector store ready: {stats['total_documents']} documents")

class QueryRequest(BaseModel):
    query: str

class AddKnowledgeRequest(BaseModel):
    category: str
    query: str
    answer: str

@app.post("/chat")
async def chat(request: QueryRequest):
    """Query the chatbot (KB + vector search + Ollama)"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    answer = chatbot.answer(request.query)
    return {"query": request.query, "answer": answer}

@app.post("/add-knowledge")
async def add_knowledge(request: AddKnowledgeRequest):
    """Add knowledge manually"""
    chatbot.add_knowledge(request.category, request.query, request.answer)
    return {"status": "success", "message": f"Knowledge added to {request.category}"}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), category: str = "documents"):
    """Upload PDF (processed into vector store + KB)"""
    try:
        filepath = f"temp_{file.filename}"
        with open(filepath, "wb") as f:
            f.write(await file.read())
        
        # Load into BOTH KB and vector store (ONE-TIME)
        knowledge_loader.load_pdf_to_kb(filepath, category)
        knowledge_loader.save_kb()
        
        os.remove(filepath)
        return {"status": "success", "message": f"PDF processed: {file.filename}"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/upload-powerpoint")
async def upload_powerpoint(file: UploadFile = File(...), category: str = "presentations"):
    """Upload PowerPoint (processed into vector store + KB)"""
    try:
        filepath = f"temp_{file.filename}"
        with open(filepath, "wb") as f:
            f.write(await file.read())
        
        knowledge_loader.load_powerpoint_to_kb(filepath, category)
        knowledge_loader.save_kb()
        
        os.remove(filepath)
        return {"status": "success", "message": f"PowerPoint processed: {file.filename}"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/categories")
async def get_categories():
    """List KB categories"""
    return {"categories": chatbot.knowledge_base.get_all_categories()}

@app.get("/kb-stats")
async def kb_stats():
    """Get KB and vector store statistics"""
    kb_stats = {}
    for category, items in chatbot.knowledge_base.knowledge.items():
        kb_stats[category] = len(items)
    
    return {
        "knowledge_base": {
            "total_entries": sum(kb_stats.values()),
            "by_category": kb_stats
        },
        "vector_store": vector_store.get_stats()
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "assistant": "Geoatlas"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
