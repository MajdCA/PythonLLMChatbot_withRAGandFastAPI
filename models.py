from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User message", min_length=1)
    use_rag: bool = Field(default=True, description="Whether to use RAG for response")


class Source(BaseModel):
    """Model for source document information."""
    content: str = Field(..., description="Document content snippet")
    metadata: Dict = Field(default_factory=dict, description="Document metadata")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str = Field(..., description="Chatbot response")
    sources: Optional[List[Source]] = Field(default=None, description="Source documents used")


class AddTextRequest(BaseModel):
    """Request model for adding text to knowledge base."""
    text: str = Field(..., description="Text content to add", min_length=1)
    metadata: Optional[Dict] = Field(default=None, description="Optional metadata")


class AddTextResponse(BaseModel):
    """Response model for adding text."""
    message: str = Field(..., description="Success message")
    chunks_added: int = Field(..., description="Number of text chunks added")


class UploadDocumentResponse(BaseModel):
    """Response model for document upload."""
    message: str = Field(..., description="Success message")
    filename: str = Field(..., description="Uploaded filename")
    chunks_added: int = Field(..., description="Number of document chunks added")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")


class ChatMessage(BaseModel):
    """Model for chat message."""
    type: str = Field(..., description="Message type (human/ai)")
    content: str = Field(..., description="Message content")


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    messages: List[ChatMessage] = Field(..., description="Chat history messages")
