import json
from typing import List, Dict
from document_loader import DocumentLoader
from knowledge_base import KnowledgeBase

class KnowledgeLoader:
    """Load documents into knowledge base"""
    
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.doc_loader = DocumentLoader(chunk_size=300, chunk_overlap=50)
    
    def load_pdf_to_kb(self, pdf_path: str, category: str = "documents"):
        """Load PDF into knowledge base"""
        documents = self.doc_loader.load_pdf(pdf_path)
        
        for doc in documents:
            # Use first 100 chars as query key
            query = doc["content"][:100] + "..."
            self.kb.add_knowledge(
                category=category,
                query=query,
                answer=doc["content"],
                source=doc["source"]
            )
        
        print(f"✓ Added {len(documents)} entries from PDF to knowledge base")
    
    def load_powerpoint_to_kb(self, pptx_path: str, category: str = "presentations"):
        """Load PowerPoint into knowledge base"""
        documents = self.doc_loader.load_powerpoint(pptx_path)
        
        for doc in documents:
            query = doc["content"][:100] + "..."
            self.kb.add_knowledge(
                category=category,
                query=query,
                answer=doc["content"],
                source=doc["source"]
            )
        
        print(f"✓ Added {len(documents)} entries from PowerPoint to knowledge base")
    
    def load_directory_to_kb(self, directory: str):
        """Load all documents from directory"""
        documents = self.doc_loader.load_directory(directory)
        
        for doc in documents:
            category = "pdf_documents" if doc["type"].startswith("pdf") else "presentations"
            query = doc["content"][:100] + "..."
            self.kb.add_knowledge(
                category=category,
                query=query,
                answer=doc["content"],
                source=doc["source"]
            )
        
        print(f"✓ Added {len(documents)} entries from directory to knowledge base")
    
    def save_kb_to_file(self, filepath: str = "knowledge_base.json"):
        """Persist knowledge base to file"""
        self.kb.save_to_file(filepath)
        print(f"✓ Knowledge base saved to {filepath}")
    
    def load_kb_from_file(self, filepath: str = "knowledge_base.json"):
        """Load knowledge base from file"""
        self.kb.load_from_file(filepath)
        print(f"✓ Knowledge base loaded from {filepath}")