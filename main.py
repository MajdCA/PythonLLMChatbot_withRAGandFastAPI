from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm_chat import ChatBot
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
