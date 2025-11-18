import json
from typing import List, Dict
from document_loader import DocumentLoader
from knowledge_base import KnowledgeBase
from vector_store import VectorStore

class KnowledgeLoader:
    """Load documents into both KB and vector store (ONE-TIME ONLY)"""
    
    def __init__(self, kb: KnowledgeBase, vs: VectorStore):
        self.kb = kb
        self.vs = vs
        self.doc_loader = DocumentLoader(chunk_size=300, chunk_overlap=50)
    
    def load_pdf_to_kb(self, pdf_path: str, category: str = "documents"):
        """
        Load PDF into BOTH knowledge base AND vector store
        
        ONE-TIME OPERATION - Never needs re-uploading
        
        On restart:
        - KB loads from knowledge_base.json
        - Vector store loads from chroma_db/
        - Everything available instantly
        """
        documents = self.doc_loader.load_pdf(pdf_path)
        
        # Documents for vector store (semantic search)
        vector_docs = []
        
        for idx, doc in enumerate(documents):
            # Add to traditional KB
            query = doc["content"][:100] + "..."
            self.kb.add_knowledge(
                category=category,
                query=query,
                answer=doc["content"],
                source=doc["source"]
            )
            
            # Add to vector store (semantic search)
            vector_docs.append({
                "id": f"pdf_{pdf_path}_{idx}",
                "text": doc["content"],
                "metadata": {
                    "source": doc["source"],
                    "type": doc["type"],
                    "file": pdf_path
                }
            })
        
        # Batch add to vector store (efficient)
        self.vs.add_documents_batch(vector_docs)
        
        print(f"✓ PDF added to KB and vector store: {pdf_path}")
        print(f"  - KB entries: {len(documents)}")
        print(f"  - Vector embeddings: {len(vector_docs)}")
    
    def load_powerpoint_to_kb(self, pptx_path: str, category: str = "presentations"):
        """Load PowerPoint into BOTH KB and vector store"""
        documents = self.doc_loader.load_powerpoint(pptx_path)
        
        vector_docs = []
        
        for idx, doc in enumerate(documents):
            query = doc["content"][:100] + "..."
            self.kb.add_knowledge(
                category=category,
                query=query,
                answer=doc["content"],
                source=doc["source"]
            )
            
            vector_docs.append({
                "id": f"pptx_{pptx_path}_{idx}",
                "text": doc["content"],
                "metadata": {
                    "source": doc["source"],
                    "type": doc["type"],
                    "file": pptx_path
                }
            })
        
        self.vs.add_documents_batch(vector_docs)
        
        print(f"✓ PowerPoint added to KB and vector store: {pptx_path}")
        print(f"  - KB entries: {len(documents)}")
        print(f"  - Vector embeddings: {len(vector_docs)}")
    
    def load_directory_to_kb(self, directory: str):
        """Load ALL PDFs and PPTXs from directory (ONE-TIME)"""
        import os
        
        count = 0
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            if filename.lower().endswith('.pdf'):
                self.load_pdf_to_kb(filepath, "pdf_documents")
                count += 1
            
            elif filename.lower().endswith(('.pptx', '.ppt')):
                self.load_powerpoint_to_kb(filepath, "presentations")
                count += 1
        
        print(f"\n✓ Loaded {count} files from directory")
        self.save_kb()
    
    def save_kb(self):
        """Save KB to disk for persistence"""
        self.kb.save_to_file("knowledge_base.json")
        self.vs.persist()
        print("✓ KB and vector store saved to disk")
    
    def get_stats(self):
        """Get statistics"""
        return {
            "knowledge_base_entries": sum(len(v) for v in self.kb.knowledge.values()),
            "vector_store_documents": self.vs.collection.count(),
            "embedding_model": "all-MiniLM-L6-v2 (384-dim)",
            "storage": {
                "kb_file": "knowledge_base.json",
                "vector_db": "chroma_db/"
            }
        }