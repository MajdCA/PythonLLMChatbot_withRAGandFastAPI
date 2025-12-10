import json
import os
import logging
from difflib import SequenceMatcher

logger = logging.getLogger("geoatlas.kb")

class KnowledgeBase:
    def __init__(self, filepath: str = "knowledge_base_data.json"):
        self.filepath = filepath
        self.knowledge = self._load_from_file()
        logger.info(f"KnowledgeBase loaded | path={self.filepath} | categories={list(self.knowledge.keys())}")
    
    def _load_from_file(self):
        """Load knowledge base from JSON file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load KB: {e}")
                return {}
        return {}
    
    def _save_to_file(self):
        """Save knowledge base to JSON file"""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.knowledge, f, indent=2)
            logger.info("KnowledgeBase saved")
        except Exception as e:
            logger.error(f"Failed to save KB: {e}")
    
    def add_knowledge(self, category: str, query: str, answer: str):
        """Add new knowledge entry"""
        if category not in self.knowledge:
            self.knowledge[category] = []
        
        self.knowledge[category].append({
            "query": query,
            "answer": answer
        })
        logger.debug(f"KB entry added | category={category} | query_len={len(query)} | answer_len={len(answer)}")
        self._save_to_file()
    
    def search_with_confidence(self, query: str):
        """Search KB and return answer with confidence score"""
        best_match = None
        best_score = 0
        
        for category, entries in self.knowledge.items():
            for entry in entries:
                score = SequenceMatcher(None, query.lower(), entry["query"].lower()).ratio()
                logger.debug(f"Score match | query='{query}' | kb_query='{entry['query']}' | score={score:.3f}")  # ADD
                if score > best_score:
                    best_score = score
                    best_match = entry["answer"]
        
        logger.debug(f"Best match found | score={best_score:.3f} | matched={bool(best_match)}")  # ADD
        return best_match or "", best_score
    
    def search_with_context(self, query: str):
        """Search KB and return relevant context"""
        results = []
        for category, entries in self.knowledge.items():
            for entry in entries:
                score = SequenceMatcher(None, query.lower(), entry["query"].lower()).ratio()
                if score > 0.4:
                    results.append(f"[{category}] Q: {entry['query']}\nA: {entry['answer']}")
        ctx = "\n\n".join(results)
        logger.debug(f"KB context search | query_len={len(query)} | matches={len(results)} | ctx_len={len(ctx)}")
        return ctx
    
    def get_all_categories(self):
        """Get all knowledge categories"""
        return list(self.knowledge.keys())
