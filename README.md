# Python LLM Chatbot with RAG and FastAPI

A production-ready Python chatbot application that leverages Large Language Models (LLM) with Retrieval-Augmented Generation (RAG) capabilities, built with FastAPI.

## Features

- 🤖 **LLM-Powered Chatbot**: Utilizes OpenAI's GPT models for intelligent conversations
- 📚 **RAG Implementation**: Retrieval-Augmented Generation for context-aware responses
- 🔍 **Vector Search**: ChromaDB for efficient document similarity search
- 📄 **Document Processing**: Support for PDF and TXT file uploads
- 💬 **Conversation Memory**: Maintains chat history for contextual conversations
- 🚀 **FastAPI Backend**: High-performance REST API with automatic documentation
- ⚙️ **Configurable**: Environment-based configuration for easy deployment

## Architecture

The application consists of three main components:

1. **RAG Service** (`rag_service.py`): Handles document processing, embedding, and retrieval
2. **Chatbot Service** (`chatbot_service.py`): Manages LLM interactions and conversation flow
3. **FastAPI Application** (`main.py`): Provides REST API endpoints

## Requirements

- Python 3.8+
- OpenAI API Key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MajdCA/PythonLLMChatbot_withRAGandFastAPI.git
cd PythonLLMChatbot_withRAGandFastAPI
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Configuration

Edit the `.env` file with your settings:

```env
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002
TEMPERATURE=0.7
MAX_TOKENS=500
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=3
```

## Usage

### Running the Server

Start the FastAPI server:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, access the interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Check

**GET** `/` or `/health`

Returns the application health status.

### Chat

**POST** `/chat`

Send a message to the chatbot.

Request body:
```json
{
  "message": "What is RAG?",
  "use_rag": true
}
```

Response:
```json
{
  "answer": "RAG stands for Retrieval-Augmented Generation...",
  "sources": [
    {
      "content": "Relevant document snippet...",
      "metadata": {}
    }
  ]
}
```

### Add Text to Knowledge Base

**POST** `/documents/add-text`

Add text directly to the knowledge base.

Request body:
```json
{
  "text": "Your document text here",
  "metadata": {"source": "manual_entry"}
}
```

### Upload Document

**POST** `/documents/upload`

Upload a PDF or TXT file to the knowledge base.

Request:
- Form data with file field

### Clear Documents

**DELETE** `/documents/clear`

Remove all documents from the knowledge base.

### Chat History

**GET** `/chat/history`

Get the current conversation history.

**DELETE** `/chat/history`

Clear the conversation history.

## Examples

### Using cURL

```bash
# Chat with the bot
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "use_rag": false}'

# Add text to knowledge base
curl -X POST "http://localhost:8000/documents/add-text" \
  -H "Content-Type: application/json" \
  -d '{"text": "RAG is a technique that combines retrieval and generation."}'

# Upload a document
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@document.pdf"
```

### Using Python

```python
import requests

# Chat endpoint
response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "What is machine learning?", "use_rag": true}
)
print(response.json())

# Add text
response = requests.post(
    "http://localhost:8000/documents/add-text",
    json={"text": "Machine learning is a subset of AI..."}
)
print(response.json())
```

## Project Structure

```
PythonLLMChatbot_withRAGandFastAPI/
├── main.py                 # FastAPI application
├── config.py              # Configuration settings
├── rag_service.py         # RAG implementation
├── chatbot_service.py     # Chatbot logic
├── models.py              # Pydantic models
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: Framework for developing LLM applications
- **ChromaDB**: Vector database for embeddings
- **OpenAI**: LLM and embedding models
- **Pydantic**: Data validation using Python type hints

## How RAG Works

1. **Document Ingestion**: Documents are uploaded and split into chunks
2. **Embedding**: Text chunks are converted to vector embeddings
3. **Storage**: Embeddings are stored in ChromaDB vector database
4. **Retrieval**: When a query arrives, relevant chunks are retrieved
5. **Generation**: LLM generates a response using retrieved context

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your `.env` file contains a valid `OPENAI_API_KEY`
   - Check that the API key has sufficient credits

2. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Verify you're using Python 3.8 or higher

3. **Vector Store Issues**
   - Clear the vector store: `DELETE /documents/clear`
   - Delete the `chroma_db` directory and restart

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- OpenAI for GPT models
- LangChain community
- FastAPI framework