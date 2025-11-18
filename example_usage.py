#!/usr/bin/env python3
"""
Example usage script for the Python LLM Chatbot with RAG.

This script demonstrates how to:
1. Start the FastAPI server
2. Make requests to the API
3. Upload documents
4. Chat with the bot

Before running, make sure to:
- Set your OPENAI_API_KEY in a .env file
- Install dependencies: pip install -r requirements.txt
"""

import requests
import json
import os
from pathlib import Path


# API base URL (adjust if running on different host/port)
API_BASE_URL = "http://localhost:8000"


def check_health():
    """Check if the API is running and healthy."""
    print("\n" + "="*60)
    print("Checking API Health...")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API is healthy")
            print(f"  App Name: {data['app_name']}")
            print(f"  Version: {data['version']}")
            print(f"  Status: {data['status']}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure the server is running:")
        print("  python main.py")
        return False


def add_text_to_knowledge_base(text, metadata=None):
    """Add text to the knowledge base."""
    print("\n" + "="*60)
    print("Adding text to knowledge base...")
    print("="*60)
    
    payload = {
        "text": text,
        "metadata": metadata or {}
    }
    
    response = requests.post(
        f"{API_BASE_URL}/documents/add-text",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Text added successfully")
        print(f"  Message: {data['message']}")
        print(f"  Chunks added: {data['chunks_added']}")
        return True
    else:
        print(f"✗ Failed to add text: {response.status_code}")
        print(f"  {response.text}")
        return False


def upload_document(file_path):
    """Upload a document to the knowledge base."""
    print("\n" + "="*60)
    print(f"Uploading document: {file_path}")
    print("="*60)
    
    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return False
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        response = requests.post(
            f"{API_BASE_URL}/documents/upload",
            files=files
        )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Document uploaded successfully")
        print(f"  Message: {data['message']}")
        print(f"  Filename: {data['filename']}")
        print(f"  Chunks added: {data['chunks_added']}")
        return True
    else:
        print(f"✗ Failed to upload document: {response.status_code}")
        print(f"  {response.text}")
        return False


def chat(message, use_rag=True):
    """Send a chat message and get a response."""
    print("\n" + "="*60)
    print(f"Chat (RAG={'ON' if use_rag else 'OFF'})")
    print("="*60)
    print(f"You: {message}")
    
    payload = {
        "message": message,
        "use_rag": use_rag
    }
    
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nBot: {data['answer']}")
        
        if data.get('sources') and use_rag:
            print("\nSources:")
            for i, source in enumerate(data['sources'], 1):
                print(f"\n  Source {i}:")
                print(f"    {source['content'][:200]}...")
                if source.get('metadata'):
                    print(f"    Metadata: {source['metadata']}")
        return True
    else:
        print(f"✗ Chat failed: {response.status_code}")
        print(f"  {response.text}")
        return False


def get_chat_history():
    """Get the chat history."""
    print("\n" + "="*60)
    print("Chat History")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/chat/history")
    
    if response.status_code == 200:
        data = response.json()
        messages = data.get('messages', [])
        
        if not messages:
            print("No chat history yet.")
        else:
            for msg in messages:
                role = "You" if msg['type'] == 'human' else "Bot"
                print(f"\n{role}: {msg['content']}")
        return True
    else:
        print(f"✗ Failed to get chat history: {response.status_code}")
        return False


def clear_chat_history():
    """Clear the chat history."""
    print("\n" + "="*60)
    print("Clearing chat history...")
    print("="*60)
    
    response = requests.delete(f"{API_BASE_URL}/chat/history")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ {data['message']}")
        return True
    else:
        print(f"✗ Failed to clear chat history: {response.status_code}")
        return False


def clear_knowledge_base():
    """Clear all documents from the knowledge base."""
    print("\n" + "="*60)
    print("Clearing knowledge base...")
    print("="*60)
    
    response = requests.delete(f"{API_BASE_URL}/documents/clear")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ {data['message']}")
        return True
    else:
        print(f"✗ Failed to clear knowledge base: {response.status_code}")
        return False


def main():
    """Run example interactions with the API."""
    print("\n")
    print("*"*60)
    print("Python LLM Chatbot with RAG - Example Usage")
    print("*"*60)
    
    # Check if API is running
    if not check_health():
        print("\nPlease start the API server first:")
        print("  python main.py")
        return
    
    # Example 1: Add some knowledge to the database
    print("\n\nExample 1: Adding knowledge to the database")
    print("-"*60)
    knowledge = """
    Retrieval-Augmented Generation (RAG) is a technique that enhances 
    large language models by combining them with a retrieval mechanism. 
    RAG allows the model to access and utilize external knowledge from 
    a vector database, making responses more accurate and contextual.
    """
    add_text_to_knowledge_base(knowledge, {"source": "example"})
    
    # Example 2: Chat with RAG enabled
    print("\n\nExample 2: Chatting with RAG enabled")
    print("-"*60)
    chat("What is RAG?", use_rag=True)
    
    # Example 3: Chat without RAG
    print("\n\nExample 3: Chatting without RAG")
    print("-"*60)
    chat("What's the weather like today?", use_rag=False)
    
    # Example 4: View chat history
    print("\n\nExample 4: Viewing chat history")
    print("-"*60)
    get_chat_history()
    
    print("\n\n" + "*"*60)
    print("Examples completed!")
    print("*"*60)
    print("\nTo explore more:")
    print("  - Visit http://localhost:8000/docs for interactive API documentation")
    print("  - Upload PDF or TXT files using the /documents/upload endpoint")
    print("  - Try different questions to see how RAG improves responses")
    print("\n")


if __name__ == "__main__":
    main()
