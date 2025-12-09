import os
import requests
import logging
from knowledge_base import KnowledgeBase
from prompt_builder import PromptBuilder
from vectorstore.vector_store import VectorStore

logger = logging.getLogger("geoatlas.chatbot")

class ChatBot:
    def __init__(self, ollama_url: str = None, kb_filepath: str = "knowledge_base_data.json"):
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://192.168.1.253:11435")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
        self.knowledge_base = KnowledgeBase(kb_filepath)
        # Confidence threshold: if KB match > 0.85, skip Ollama
        self.kb_confidence_threshold = float(os.getenv("KB_CONFIDENCE_THRESHOLD", "0.85"))
        # Load vector store if it exists
        self.vector_store_path = os.getenv(
            "VECTOR_STORE_PATH",
            os.path.join(os.path.dirname(__file__), "vectorstore", "vector_store.json"),
        )
        self.vector_store = VectorStore(self.vector_store_path, self.ollama_url) if os.path.exists(self.vector_store_path) else None
        # Hint in logs where log files are stored
        log_dir = os.getenv("LOG_DIR", os.path.join(os.path.dirname(__file__), "logs"))
        logger.info(f"ChatBot initialized | ollama_url={self.ollama_url} | model={self.model} | kb_threshold={self.kb_confidence_threshold} | vector_store_loaded={self.vector_store is not None} | log_dir={log_dir}")
    
    def answer(self, query: str) -> str:
        """
        RAG with optimization: Skip Ollama if KB match is high confidence
        Flow:
        - If exact/high match in KB (>0.85) ? Return immediately (FAST)
        - Otherwise ? Use Ollama with KB context + vector store context (ACCURATE)
        """
        logger.info(f"Answer called | query='{query}'")
        # Step 1: Search KB and get confidence score
        kb_answer, confidence = self.knowledge_base.search_with_confidence(query)
        logger.info(f"KB search | confidence={confidence:.3f} | matched={bool(kb_answer)}")
        
        # Step 2: If high confidence match, return immediately (NO Ollama call)
        if confidence >= self.kb_confidence_threshold:
            logger.info("High-confidence KB match: returning KB answer without Ollama")
            logger.debug(f"KB answer: {kb_answer}")
            return kb_answer  # Fast path - instant response
        
        # Step 3: Low confidence - use Ollama with context for better answer
        kb_context = self.knowledge_base.search_with_context(query)
        vs_context = ""
        if self.vector_store:
            try:
                # Log detailed vector hits with scores
                hits = self.vector_store.search(query, top_k=5)
                logger.info(f"VectorStore search | hits={len(hits)}")
                for idx, (score, rec) in enumerate(hits, start=1):
                    src = rec.get("metadata", {}).get("source")
                    preview = (rec.get("text", "")[:200] + ("..." if len(rec.get("text", "")) > 200 else ""))
                    logger.debug(f"VS hit {idx} | score={score:.4f} | source={src} | text_preview={preview}")
                # Compose VS context from hits
                vs_context = "\n\n".join([f"[{rec.get('metadata', {}).get('source', 'source')}] {rec['text']}" for _, rec in hits])
            except Exception as e:
                logger.error(f"VectorStore search error: {e}")
        else:
            logger.info("VectorStore not loaded; skipping VS context")
        
        # Merge contexts (if available)
        merged_context_parts = [part for part in [kb_context, vs_context] if part]
        context = "\n\n".join(merged_context_parts)
        logger.info(f"Context prepared | kb_len={len(kb_context)} | vs_len={len(vs_context)} | merged_len={len(context)}")
        return self._ollama_answer_with_rag(query, context)
    
    def _ollama_answer_with_rag(self, query: str, context: str) -> str:
        """Get answer from Ollama using knowledge base as context (GPU accelerated)"""
        # Build full prompt using PromptBuilder
        full_prompt = PromptBuilder.build_full_prompt(query, context)
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "temperature": 0.5,
            "num_predict": 200,
            "top_k": 40,
            "top_p": 0.9,
        }
        logger.info(f"Ollama request | url={self.ollama_url}/api/generate | model={self.model}")
        payload_repr = {k: v if k != 'prompt' else f'[prompt length: {len(full_prompt)}]' for k, v in payload.items()}
        logger.debug(f"Ollama payload (truncated prompt len={len(full_prompt)}): {payload_repr}")
        logger.debug(f"Full prompt content sent to Ollama:\n{full_prompt}")
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
            msg = "Error: Cannot connect to Ollama at 192.168.1.253:11434. Check network connection."
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
