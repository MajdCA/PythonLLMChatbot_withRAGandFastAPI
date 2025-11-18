from typing import Tuple
from knowledge_base import KnowledgeBase
from vector_store import VectorStore

class HybridSearch:
    """
    Combines traditional KB search with semantic vector search
    
    Flow:
    1. Try exact/high-confidence KB match (FAST)
    2. If no match, use vector search (SEMANTIC)
    3. Combine both for best results
    """
    
    def __init__(self, kb: KnowledgeBase, vs: VectorStore):
        self.kb = kb
        self.vs = vs
    
    def search(self, query: str, threshold: float = 0.85) -> Tuple[str, float, str]:
        """
        Hybrid search with fallback chain
        
        Returns: (answer, confidence, source_type)
            - source_type: "kb" | "vector" | "combined"
        
        Priority:
        1. KB exact match (1.0 confidence)
        2. KB high similarity (>= threshold)
        3. Vector semantic search
        4. No match
        """
        
        # Step 1: Try KB search
        kb_answer, kb_confidence = self.kb.search_with_confidence(query)
        
        if kb_confidence >= threshold:
            return kb_answer, kb_confidence, "kb"
        
        # Step 2: Try vector search (semantic)
        vector_results = self.vs.search(query, top_k=1)
        
        if vector_results:
            best_result = vector_results[0]
            vector_answer = best_result["text"]
            vector_confidence = best_result["distance"]
            
            # If vector search is good, use it
            if vector_confidence >= 0.5:
                return vector_answer, vector_confidence, "vector"
        
        # Step 3: No good match found
        return "", 0.0, "none"
    
    def search_with_context(self, query: str, top_k_kb: int = 2, top_k_vector: int = 3) -> str:
        """
        Get context from both KB and vector store for Ollama
        
        Combines:
        - Top KB matches (keyword search)
        - Top vector matches (semantic search)
        
        Returns:
            Formatted context string
        """
        context = ""
        
        # Get KB context
        kb_context = self.kb.search_with_context(query, top_k=top_k_kb)
        if kb_context:
            context += "=== Knowledge Base (Keyword Match) ===\n"
            context += kb_context + "\n"
        
        # Get vector context
        vector_results = self.vs.search(query, top_k=top_k_vector)
        if vector_results:
            context += "=== Vector Store (Semantic Match) ===\n"
            for i, result in enumerate(vector_results, 1):
                source = result["metadata"].get("source", "unknown")
                similarity = result["distance"]
                context += f"{i}. [{similarity:.1%}] From {source}\n"
                context += f"   {result['text'][:300]}...\n\n"
        
        return context
    
    def get_stats(self) -> dict:
        """Get statistics for both stores"""
        return {
            "knowledge_base": {
                "entries": sum(len(v) for v in self.kb.knowledge.values()),
                "categories": list(self.kb.knowledge.keys())
            },
            "vector_store": self.vs.get_stats()
        }