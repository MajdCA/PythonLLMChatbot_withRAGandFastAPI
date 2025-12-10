import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm_chat import ChatBot
import os
from datetime import datetime
from dotenv import load_dotenv

# Initialize logging once
log_level = os.getenv("LOG_LEVEL", "INFO")
log_dir = os.getenv("LOG_DIR", os.path.join(os.path.dirname(__file__), "logs"))
os.makedirs(log_dir, exist_ok=True)
log_filename = os.path.join(log_dir, f"app-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log")

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))

# File handler
file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setLevel(log_level)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))

logging.basicConfig(level=log_level, handlers=[console_handler, file_handler])
logger = logging.getLogger("geoatlas.api")
logger.info(f"Logging initialized | level={log_level} | file={log_filename}")

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
    logger.debug(f"Request payload | query='{request.query}' | query_len={len(request.query)}")  # ADD
    logger.info("Incoming /chat request")
    logger.info(f"User query: {request.query}")
    answer = chatbot.answer(request.query)
    logger.debug(f"Response payload | answer_len={len(answer)}")  # ADD
    logger.info("Outgoing /chat response")
    logger.info(f"Answer: {answer}")
    return {"query": request.query, "answer": answer}

@app.post("/add-knowledge")
async def add_knowledge(request: AddKnowledgeRequest):
    """Add new knowledge to chatbot"""
    logger.info("Incoming /add-knowledge request")
    logger.info(f"Category: {request.category} | Query: {request.query}")
    chatbot.add_knowledge(request.category, request.query, request.answer)
    logger.info("Knowledge added successfully")
    return {"status": "success", "message": f"Knowledge added to {request.category}"}

@app.get("/categories")
async def get_categories():
    """Get all knowledge categories"""
    cats = chatbot.knowledge_base.get_all_categories()
    logger.info(f"Categories requested: {cats}")
    return {"categories": cats}

@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.debug("Health check")
    return {"status": "ok", "assistant": "Geoatlas"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Geoatlas Chatbot API")
    uvicorn.run(app, host="0.0.0.0", port=8001)
