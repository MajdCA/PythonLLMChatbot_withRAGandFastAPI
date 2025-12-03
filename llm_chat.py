import os
import requests
from knowledge_base import KnowledgeBase

class ChatBot:
    def __init__(self, ollama_url: str = None):
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://192.168.1.253:11435")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
        self.knowledge_base = KnowledgeBase()
        # Confidence threshold: if KB match > 0.85, skip Ollama
        self.kb_confidence_threshold = float(os.getenv("KB_CONFIDENCE_THRESHOLD", "0.85"))
    
    def answer(self, query: str) -> str:
        """
        RAG with optimization: Skip Ollama if KB match is high confidence
        Flow:
        - If exact/high match in KB (>0.85) ? Return immediately (FAST)
        - Otherwise ? Use Ollama with KB context (ACCURATE)
        """
        
        # Step 1: Search KB and get confidence score
        kb_answer, confidence = self.knowledge_base.search_with_confidence(query)
        
        # Step 2: If high confidence match, return immediately (NO Ollama call)
        if confidence >= self.kb_confidence_threshold:
            return kb_answer  # Fast path - instant response
        
        # Step 3: Low confidence - use Ollama with context for better answer
        context = self.knowledge_base.search_with_context(query)
        return self._ollama_answer_with_rag(query, context)
    
    def _ollama_answer_with_rag(self, query: str, context: str) -> str:
        """Get answer from Ollama using knowledge base as context (GPU accelerated)"""
        
        system_prompt = """You are Geoatlas, a geotechnical monitoring web assistant.
Use the provided knowledge base context to answer accurately. If context doesn't cover the question, use your general knowledge.
Keep responses concise, accurate, and user-friendly. Focus on website navigation and geotechnical monitoring.
If the question is not related to the website or geotechnical monitoring, politely redirect the user.

KNOWLEDGE BASE CONTEXT:
{context}

""".format(context=context if context else "No specific knowledge found. Use general knowledge.")
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\nUser: {query}\nAssistant:",
                    "stream": False,
                    "temperature": 0.5,
                    "num_predict": 200,
                    "top_k": 40,
                    "top_p": 0.9,
                },
                timeout=60
            )
            
            response.raise_for_status()
            return response.json()["response"].strip()
        
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama at 192.168.1.253:11434. Check network connection."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def add_knowledge(self, category: str, query: str, answer: str):
        """Add new knowledge to base"""
        self.knowledge_base.add_knowledge(category, query, answer)
