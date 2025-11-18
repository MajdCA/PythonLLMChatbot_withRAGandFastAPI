#!/usr/bin/env python3
"""
Simple test script to verify the API structure and endpoints.
This does not require an OpenAI API key.
"""

import sys
import os

# Suppress startup warnings
os.environ.setdefault("OPENAI_API_KEY", "test-key")


def test_api_structure():
    """Test that the API endpoints are properly defined."""
    print("Testing API structure...")
    
    # Import main to ensure it loads
    try:
        from main import app
        print("   ✓ Main app module loads successfully")
    except Exception as e:
        print(f"   ✗ Failed to load main app: {e}")
        return False
    
    # Check that routes are registered
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append(route.path)
    
    print(f"\n   Found {len(routes)} routes:")
    for route in sorted(routes):
        print(f"     - {route}")
    
    # Verify expected endpoints
    expected_paths = ["/", "/health", "/chat", "/documents/add-text", 
                     "/documents/upload", "/documents/clear", 
                     "/chat/history"]
    
    print("\n   Checking expected endpoints:")
    all_found = True
    for path in expected_paths:
        if path in routes:
            print(f"     ✓ {path}")
        else:
            print(f"     ✗ {path} not found")
            all_found = False
    
    if not all_found:
        return False
    
    print("\n✅ All API structure tests passed!")
    return True


def test_models():
    """Test that Pydantic models are properly defined."""
    print("\nTesting Pydantic models...")
    
    from models import (
        ChatRequest, ChatResponse, AddTextRequest, 
        AddTextResponse, UploadDocumentResponse, 
        HealthResponse, ChatHistoryResponse
    )
    
    # Test ChatRequest model
    print("1. Testing ChatRequest model...")
    try:
        request = ChatRequest(message="Hello", use_rag=True)
        assert request.message == "Hello"
        assert request.use_rag == True
        print("   ✓ ChatRequest model works")
    except Exception as e:
        print(f"   ✗ ChatRequest model failed: {e}")
        return False
    
    # Test HealthResponse model
    print("2. Testing HealthResponse model...")
    try:
        response = HealthResponse(
            status="healthy",
            app_name="Test App",
            version="1.0.0"
        )
        assert response.status == "healthy"
        print("   ✓ HealthResponse model works")
    except Exception as e:
        print(f"   ✗ HealthResponse model failed: {e}")
        return False
    
    print("\n✅ All model tests passed!")
    return True


def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    from config import Settings
    
    try:
        settings = Settings()
        print(f"   App Name: {settings.app_name}")
        print(f"   Version: {settings.app_version}")
        print(f"   LLM Model: {settings.llm_model}")
        print(f"   Chunk Size: {settings.chunk_size}")
        print("   ✓ Configuration loads correctly")
        return True
    except Exception as e:
        print(f"   ✗ Configuration failed: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Running Python LLM Chatbot API Tests")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Configuration", test_config()))
    results.append(("Pydantic Models", test_models()))
    results.append(("API Structure", test_api_structure()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary:")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
