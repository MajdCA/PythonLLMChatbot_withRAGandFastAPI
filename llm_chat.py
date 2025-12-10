import os
import requests
import logging
from knowledge_base import KnowledgeBase
from prompt_builder import PromptBuilder
from vectorstore.vector_store import VectorStore
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger("geoatlas.chatbot")

class ChatBot:
    def __init__(self, ollama_url: str = None, kb_filepath: str = "knowledge_base_data.json"):
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://192.168.1.253:11435")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
        self.knowledge_base = KnowledgeBase(kb_filepath)
        self.kb_confidence_threshold = float(os.getenv("KB_CONFIDENCE_THRESHOLD", "0.85"))
        self.vs_threshold = float(os.getenv("VS_THRESHOLD", "0.75"))  # ⭐ Increased from 0.6
        self.vs_top_k = int(os.getenv("VS_TOP_K", "5"))  # ⭐ Limit total chunks
        
        self.vector_store_path = os.getenv(
            "VECTOR_STORE_PATH",
            os.path.join(os.path.dirname(__file__), "vectorstore", "vector_store.json"),
        )
        self.vector_store = VectorStore(self.vector_store_path, self.ollama_url) if os.path.exists(self.vector_store_path) else None
        
        log_dir = os.getenv("LOG_DIR", os.path.join(os.path.dirname(__file__), "logs"))
        logger.info(f"ChatBot initialized | ollama_url={self.ollama_url} | model={self.model} | kb_threshold={self.kb_confidence_threshold} | vs_threshold={self.vs_threshold} | vs_top_k={self.vs_top_k} | vector_store_loaded={self.vector_store is not None}")
    
    def answer(self, query: str) -> str:
        """RAG with optimization: Skip Ollama if KB match is high confidence"""
        logger.info(f"Answer called | query='{query}'")
        
        # Step 1: Search KB
        kb_answer, confidence = self.knowledge_base.search_with_confidence(query)
        logger.info(f"KB search | confidence={confidence:.3f} | matched={bool(kb_answer)}")
        
        # Step 2: High confidence? Return immediately
        if confidence >= self.kb_confidence_threshold:
            logger.info("High-confidence KB match: returning KB answer without context")
            return kb_answer
        
        # Step 3: Build combined context
        context_parts = []
        
        # Add KB context if moderate confidence
        if confidence > 0.5:
            kb_context = self.knowledge_base.search_with_context(query)
            if kb_context:
                context_parts.append(kb_context)
                logger.debug(f"Added KB context | len={len(kb_context)}")
        
        # Add vector store context - ALWAYS take top hits
        if self.vector_store:
            try:
                hits = self.vector_store.search(query, top_k=10)
                logger.info(f"VectorStore search | total_hits={len(hits)}")

                # Take the best N hits regardless of score
                top_hits = hits[: self.vs_top_k]
                logger.info(f"VectorStore top hits (no threshold) | selected={len(top_hits)} | max={self.vs_top_k}")

                if top_hits:
                    for idx, (score, rec) in enumerate(top_hits, start=1):
                        src = rec.get("metadata", {}).get("source", "unknown")
                        text = rec.get("text", "")
                        logger.debug(f"VS hit {idx} | INCLUDED | score={score:.4f} | source={src} | len={len(text)}")
                        if text.strip():
                            context_parts.append(f"[{src}]\n{text}")
                else:
                    logger.info("No VectorStore results returned")
            except Exception as e:
                logger.error(f"VectorStore search error: {e}")
        else:
            logger.info("VectorStore not loaded")
        
        # Merge all context
        context = "\n\n---\n\n".join(context_parts) if context_parts else ""
        logger.info(f"Context prepared | total_len={len(context)} | parts={len(context_parts)}")
        
        if not context:
            logger.warning("No context found, using LLM with just the query")
        
        return self._ollama_answer_with_rag(query, context)
    
    def _ollama_answer_with_rag(self, query: str, context: str) -> str:
        """Get answer from Ollama with context"""
        full_prompt = PromptBuilder.build_full_prompt(query, context)
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "temperature": 0.2,
            "num_predict": 80,
            "top_k": 40,
            "top_p": 0.9,
            "stop": ["\n\nQuestion:", "\nUser:", "---"],
        }
        
        logger.info(f"Ollama request | url={self.ollama_url}/api/generate | model={self.model}")
        logger.debug(f"Ollama config | temp={payload['temperature']} | max_tokens={payload['num_predict']} | top_k={payload['top_k']}")
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            resp_text = response.json().get("response", "").strip()
            logger.info(f"Ollama response received | answer_len={len(resp_text)}")
            logger.debug(f"Ollama answer:\n{resp_text}")
            return resp_text
        except requests.exceptions.ConnectionError:
            msg = f"Error: Cannot connect to Ollama at {self.ollama_url}. Check network connection."
            logger.error(msg)
            return msg
        except Exception as e:
            msg = f"Error: {str(e)}"
            logger.error(msg)
            return msg
    
    def add_knowledge(self, category: str, query: str, answer: str):
        """Add new knowledge to base"""
        logger.info(f"Add knowledge | category={category} | query='{query}'")
        self.knowledge_base.add_knowledge(category, query, answer)
        logger.info("Knowledge saved")
