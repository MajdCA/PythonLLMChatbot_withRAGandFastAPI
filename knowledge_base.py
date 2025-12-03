import json
from typing import List, Dict, Tuple
from difflib import SequenceMatcher

class KnowledgeBase:
    def __init__(self):
        self.knowledge = {
            "greetings": [
                {"query": "hi", "answer": "Hi I am Geoatlas web assistant how can i help you today"},
                {"query": "hello", "answer": "Hi I am Geoatlas web assistant how can i help you today"},
                {"query": "hey", "answer": "Hi I am Geoatlas web assistant how can i help you today"},
                {"query": "ciao", "answer": "Ciao! Sono Geoatlas, l'assistente web di monitoraggio geotecnico. Come posso aiutarti?"},
            ],
            "navigation": [
                {"query": "how to navigate the website", "answer": "You can navigate using the left sidebar menu. Click on different sections like Dashboard, Monitoring, Reports, and Settings."},
                {"query": "where is the dashboard", "answer": "The dashboard is accessible from the main menu on the left side."},
                {"query": "navigate", "answer": "Use the left sidebar menu to navigate the website."},
            ],
            "configuration": [
                {"query": "how to open configuration page", "answer": "Click on 'Settings' in the left menu, then select 'Configuration' tab."},
            ],
            "geotechnical": [
                {"query": "what is geotechnical monitoring", "answer": "Geotechnical monitoring involves continuous measurement of soil and rock properties to ensure structural stability and safety."},
                {"query": "what is settlement monitoring", "answer": "Settlement monitoring measures the vertical displacement of structures over time."},
            ],
        }
    
    def search_with_confidence(self, query: str) -> Tuple[str, float]:
        """
        Search KB and return answer with confidence score
        Returns: (answer, confidence_score)
        - 1.0 = exact match
        - 0.85-0.99 = high similarity (use KB directly)
        - 0.5-0.84 = medium similarity (use Ollama with context)
        - <0.5 = low similarity (use Ollama with context)
        """
        query_lower = query.lower().strip()
        
        all_items = []
        for category, items in self.knowledge.items():
            all_items.extend(items)
        
        # EXACT MATCH (1.0 confidence)
        for item in all_items:
            if query_lower == item["query"].lower().strip():
                return item["answer"], 1.0
        
        # SIMILARITY MATCH (calculate scores)
        best_match = None
        best_score = 0
        
        for item in all_items:
            stored_query = item["query"].lower().strip()
            ratio = SequenceMatcher(None, query_lower, stored_query).ratio()
            
            if ratio > best_score:
                best_match = item
                best_score = ratio
        
        # Return best match with confidence score
        if best_match:
            return best_match["answer"], best_score
        
        # No match found
        return "", 0.0
    
    def search(self, query: str) -> str:
        """Exact match search (legacy method)"""
        query_lower = query.lower().strip()
        
        all_items = []
        for category, items in self.knowledge.items():
            all_items.extend(items)
        
        for item in all_items:
            if query_lower == item["query"].lower().strip():
                return item["answer"]
        
        return None
    
    def search_with_context(self, query: str, top_k: int = 3) -> str:
        """
        RAG: Retrieve top K relevant knowledge items as context
        Returns formatted context string for Ollama
        """
        query_lower = query.lower().strip()
        
        all_items = []
        for category, items in self.knowledge.items():
            all_items.extend(items)
        
        # Score all items by similarity
        scored_items = []
        for item in all_items:
            stored_query = item["query"].lower().strip()
            ratio = SequenceMatcher(None, query_lower, stored_query).ratio()
            scored_items.append({
                "score": ratio,
                "query": item["query"],
                "answer": item["answer"]
            })
        
        # Sort by score (highest first) and take top K
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        top_items = scored_items[:top_k]
        
        # Filter items with score > 0.3 (minimum relevance)
        relevant_items = [item for item in top_items if item["score"] > 0.3]
        
        # Format context string for Ollama
        if not relevant_items:
            return ""
        
        context = "Related knowledge base entries:\n"
        for i, item in enumerate(relevant_items, 1):
            context += f"{i}. Q: {item['query']}\n   A: {item['answer']}\n"
        
        return context
    
    def add_knowledge(self, category: str, query: str, answer: str):
        """Add new knowledge item"""
        if category not in self.knowledge:
            self.knowledge[category] = []
        
        self.knowledge[category].append({"query": query, "answer": answer})
    
    def save_to_file(self, filepath: str):
        """Save knowledge base to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def load_from_file(self, filepath: str):
        """Load knowledge base from JSON"""
        with open(filepath, 'r') as f:
            self.knowledge = json.load(f)
    
    def get_all_categories(self) -> List[str]:
        """Return all knowledge categories"""
        return list(self.knowledge.keys())
