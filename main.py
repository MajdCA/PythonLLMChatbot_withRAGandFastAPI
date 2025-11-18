from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from pathlib import Path

from config import get_settings, Settings
from rag_service import RAGService
from chatbot_service import ChatbotService
from models import (
    ChatRequest, ChatResponse, AddTextRequest, AddTextResponse,
    UploadDocumentResponse, HealthResponse, ChatHistoryResponse,
    Source, ChatMessage
)


# Initialize FastAPI app
app = FastAPI(
    title="LLM Chatbot with RAG",
    description="A Python-based LLM chatbot with Retrieval-Augmented Generation using FastAPI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services (initialized on startup)
rag_service: RAGService = None
chatbot_service: ChatbotService = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    global rag_service, chatbot_service
    settings = get_settings()
    
    # Validate OpenAI API key
    if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
        print("Warning: OPENAI_API_KEY not set. Please set it in .env file.")
    
    # Initialize services
    rag_service = RAGService()
    chatbot_service = ChatbotService(rag_service)


@app.get("/", response_model=HealthResponse)
async def root(settings: Settings = Depends(get_settings)):
    """Root endpoint - health check."""
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version
    )


@app.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)):
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - send a message and get a response.
    
    Args:
        request: Chat request with message and RAG flag
    
    Returns:
        Chat response with answer and optional sources
    """
    try:
        if request.use_rag:
            # Use RAG for response
            result = chatbot_service.chat(request.message)
            sources = [Source(**source) for source in result["sources"]]
            return ChatResponse(
                answer=result["answer"],
                sources=sources
            )
        else:
            # Direct LLM response without RAG
            answer = chatbot_service.chat_without_rag(request.message)
            return ChatResponse(
                answer=answer,
                sources=None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.post("/documents/add-text", response_model=AddTextResponse)
async def add_text(request: AddTextRequest):
    """
    Add text directly to the knowledge base.
    
    Args:
        request: Text and optional metadata
    
    Returns:
        Success message and number of chunks added
    """
    try:
        chunks_added = rag_service.add_text(request.text, request.metadata)
        return AddTextResponse(
            message="Text successfully added to knowledge base",
            chunks_added=chunks_added
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding text: {str(e)}")


@app.post("/documents/upload", response_model=UploadDocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF or TXT) to the knowledge base.
    
    Args:
        file: Uploaded file
    
    Returns:
        Success message, filename, and number of chunks added
    """
    # Validate file type
    allowed_extensions = [".pdf", ".txt"]
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    # Save uploaded file
    file_path = uploads_dir / file.filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Add document to vector store
        file_type = file_extension[1:]  # Remove the dot
        chunks_added = rag_service.add_documents(str(file_path), file_type)
        
        return UploadDocumentResponse(
            message="Document successfully uploaded and processed",
            filename=file.filename,
            chunks_added=chunks_added
        )
    except Exception as e:
        # Clean up file if processing failed
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    finally:
        # Clean up uploaded file after processing
        if file_path.exists():
            file_path.unlink()


@app.delete("/documents/clear")
async def clear_documents():
    """
    Clear all documents from the knowledge base.
    
    Returns:
        Success message
    """
    try:
        rag_service.clear_vector_store()
        return {"message": "All documents cleared from knowledge base"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")


@app.delete("/chat/history")
async def clear_chat_history():
    """
    Clear chat conversation history.
    
    Returns:
        Success message
    """
    try:
        chatbot_service.clear_memory()
        return {"message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing chat history: {str(e)}")


@app.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history():
    """
    Get chat conversation history.
    
    Returns:
        List of chat messages
    """
    try:
        messages = chatbot_service.get_chat_history()
        chat_messages = [ChatMessage(**msg) for msg in messages]
        return ChatHistoryResponse(messages=chat_messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
