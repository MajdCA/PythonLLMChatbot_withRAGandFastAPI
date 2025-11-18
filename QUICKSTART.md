# Quick Start Guide

Get the Python LLM Chatbot with RAG up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Installation

### 1. Clone the repository (if not already done)

```bash
git clone https://github.com/MajdCA/PythonLLMChatbot_withRAGandFastAPI.git
cd PythonLLMChatbot_withRAGandFastAPI
```

### 2. Create a virtual environment

**On Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Running the Application

### Start the server

```bash
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Access the API

- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **API Base**: http://localhost:8000

## First Steps

### Option 1: Use the Interactive Documentation (Recommended)

1. Open http://localhost:8000/docs in your browser
2. Click on any endpoint to expand it
3. Click "Try it out" button
4. Fill in the required fields
5. Click "Execute" to test the endpoint

### Option 2: Use the Example Script

```bash
# In a new terminal (keep the server running)
python example_usage.py
```

This will demonstrate:
- Adding text to the knowledge base
- Chatting with RAG enabled
- Chatting without RAG
- Viewing chat history

### Option 3: Use cURL

**Add some knowledge:**
```bash
curl -X POST "http://localhost:8000/documents/add-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Python is a high-level programming language known for its simplicity and readability.",
    "metadata": {"source": "manual"}
  }'
```

**Chat with the bot:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Python?",
    "use_rag": true
  }'
```

### Option 4: Use Python Requests

```python
import requests

# Add knowledge
response = requests.post(
    "http://localhost:8000/documents/add-text",
    json={
        "text": "RAG stands for Retrieval-Augmented Generation.",
        "metadata": {"source": "example"}
    }
)
print(response.json())

# Chat
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "What is RAG?",
        "use_rag": True
    }
)
print(response.json()["answer"])
```

## Common Tasks

### Upload a Document

Using the web interface:
1. Go to http://localhost:8000/docs
2. Find "POST /documents/upload"
3. Click "Try it out"
4. Click "Choose File" and select a PDF or TXT file
5. Click "Execute"

Using cURL:
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@/path/to/your/document.pdf"
```

### Clear the Knowledge Base

```bash
curl -X DELETE "http://localhost:8000/documents/clear"
```

### Clear Chat History

```bash
curl -X DELETE "http://localhost:8000/chat/history"
```

## Testing

Run the test suite to verify everything is working:

```bash
python test_api.py
```

Expected output:
```
🎉 All tests passed successfully!
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not set"

**Solution**: Make sure you've created a `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add your key
```

### Issue: "Module not found" errors

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Port 8000 already in use

**Solution**: Use a different port:
```bash
uvicorn main:app --port 8001
```

### Issue: "Cannot connect to API"

**Solution**: Make sure the server is running:
```bash
python main.py
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [IMPLEMENTATION.md](IMPLEMENTATION.md) for technical details
- Explore the code in the Python files
- Customize the configuration in `.env`
- Build your own knowledge base by uploading documents

## Configuration Options

You can customize the behavior by editing `.env`:

```env
# Change the LLM model
LLM_MODEL=gpt-4

# Adjust response length
MAX_TOKENS=1000

# Control creativity (0.0-1.0)
TEMPERATURE=0.5

# Adjust chunk size for documents
CHUNK_SIZE=1500

# Number of relevant documents to retrieve
TOP_K_RESULTS=5
```

## Production Deployment

For production use:

1. **Use environment variables** instead of `.env` file
2. **Set DEBUG=False**
3. **Use a production WSGI server** like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```
4. **Set up HTTPS** using a reverse proxy (nginx, Apache)
5. **Monitor logs** and set up error tracking
6. **Backup the vector database** regularly

## Support

For issues or questions:
- Check the [README.md](README.md) troubleshooting section
- Review the [IMPLEMENTATION.md](IMPLEMENTATION.md) technical details
- Open an issue on GitHub

Happy chatting! 🤖💬
