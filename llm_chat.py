import os
import requests
from knowledge_base import KnowledgeBase
from vector_store import VectorStore
from hybrid_search import HybridSearch

class ChatBot:
    def __init__(self, ollama_url: str = None, use_vector_store: bool = True):
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://192.168.1.253:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
        self.kb_confidence_threshold = float(os.getenv("KB_CONFIDENCE_THRESHOLD", "0.85"))
        
        # Initialize knowledge base
        self.knowledge_base = KnowledgeBase()
        
        # Initialize vector store (if enabled)
        self.use_vector_store = use_vector_store
        if use_vector_store:
            self.vector_store = VectorStore(persist_dir="./chroma_db")
            self.hybrid_search = HybridSearch(self.knowledge_base, self.vector_store)
        else:
            self.vector_store = None
            self.hybrid_search = None
    
    def answer(self, query: str) -> str:
        """
        Answer query using hybrid search + Ollama RAG
        
        Decision Flow:
        1. KB confidence >= 0.85? → Return instantly (FAST)
        2. Vector search good? → Return (SEMANTIC)
        3. Low confidence? → Use Ollama with context (ACCURATE)
        """
        
        if self.use_vector_store and self.hybrid_search:
            # Hybrid search (KB + vector)
            answer, confidence, source = self.hybrid_search.search(query)
            
            if confidence >= self.kb_confidence_threshold:
                # High confidence match found
                return answer
            
            # Low confidence - use Ollama with hybrid context
            context = self.hybrid_search.search_with_context(query)
            return self._ollama_answer_with_rag(query, context)
        
        else:
            # Fallback to KB only (no vector store)
            kb_answer, kb_confidence = self.knowledge_base.search_with_confidence(query)
            
            if kb_confidence >= self.kb_confidence_threshold:
                return kb_answer
            
            context = self.knowledge_base.search_with_context(query)
            return self._ollama_answer_with_rag(query, context)
    
    def _ollama_answer_with_rag(self, query: str, context: str) -> str:
        """Get answer from Ollama using context (KB + vector search)"""
        
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
        """Add new knowledge to KB only (vector store for documents)"""
        self.knowledge_base.add_knowledge(category, query, answer)
