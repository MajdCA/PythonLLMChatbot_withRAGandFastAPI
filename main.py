from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from llm_chat import ChatBot
from knowledge_loader import KnowledgeLoader
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Geoatlas Chatbot API")
chatbot = ChatBot()

class QueryRequest(BaseModel):
    query: str

class AddKnowledgeRequest(BaseModel):
    category: str
    query: str
    answer: str

@app.post("/chat")
async def chat(request: QueryRequest):
    """Send query and get answer from chatbot"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    answer = chatbot.answer(request.query)
    return {"query": request.query, "answer": answer}

@app.post("/add-knowledge")
async def add_knowledge(request: AddKnowledgeRequest):
    """Add new knowledge to chatbot"""
    chatbot.add_knowledge(request.category, request.query, request.answer)
    return {"status": "success", "message": f"Knowledge added to {request.category}"}

@app.get("/categories")
async def get_categories():
    """Get all knowledge categories"""
    return {"categories": chatbot.knowledge_base.get_all_categories()}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "assistant": "Geoatlas"}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), category: str = "documents"):
    """Upload and process PDF"""
    try:
        # Save uploaded file
        filepath = f"temp_{file.filename}"
        with open(filepath, "wb") as f:
            f.write(await file.read())
        
        # Load into KB
        loader = KnowledgeLoader(chatbot.knowledge_base)
        loader.load_pdf_to_kb(filepath, category)
        
        # Clean up
        os.remove(filepath)
        
        return {"status": "success", "message": f"PDF loaded: {file.filename}"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/upload-powerpoint")
async def upload_powerpoint(file: UploadFile = File(...), category: str = "presentations"):
    """Upload and process PowerPoint"""
    try:
        filepath = f"temp_{file.filename}"
        with open(filepath, "wb") as f:
            f.write(await file.read())
        
        loader = KnowledgeLoader(chatbot.knowledge_base)
        loader.load_powerpoint_to_kb(filepath, category)
        
        os.remove(filepath)
        
        return {"status": "success", "message": f"PowerPoint loaded: {file.filename}"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/kb-stats")
async def kb_stats():
    """Get knowledge base statistics"""
    stats = {}
    for category, items in chatbot.knowledge_base.knowledge.items():
        stats[category] = len(items)
    return {"total_entries": sum(stats.values()), "by_category": stats}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
