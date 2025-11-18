import os
import json
from typing import List, Dict, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class VectorStore:
    """
    Vector embedding database using ChromaDB
    - One-time document processing
    - Semantic search (not just string similarity)
    - Persistent storage (survives restarts)
    - No re-upload needed
    """
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        """
        Initialize ChromaDB with persistent storage
        
        Args:
            persist_dir: Directory to store vector embeddings
        """
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize ChromaDB with persistent storage
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir,
            anonymized_telemetry=False
        )
        self.client = chromadb.Client(settings)
        
        # Initialize embedding model (runs locally, no API needed)
        # all-MiniLM-L6-v2: 384-dim embeddings, fast & accurate
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="geoatlas_kb",
            metadata={"hnsw:space": "cosine"}  # Cosine similarity
        )
        
        print(f"✓ Vector store initialized at: {persist_dir}")
        print(f"✓ Embeddings: {self.collection.count()} documents")
    
    def add_document(self, doc_id: str, text: str, metadata: Dict = None) -> None:
        """
        Add document to vector store (one-time)
        
        Args:
            doc_id: Unique document identifier
            text: Document content
            metadata: Additional info (source, page, etc)
        
        Example:
            vector_store.add_document(
                doc_id="geo_monitoring_p5",
                text="Pore pressure is the pressure exerted by pore water...",
                metadata={"source": "monitoring.pdf", "page": 5, "type": "pdf_text"}
            )
        """
        # Generate embedding (semantic representation)
        embedding = self.embedding_model.encode(text).tolist()
        
        # Store in vector database
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata] if metadata else [{}]
        )
    
    def add_documents_batch(self, documents: List[Dict]) -> None:
        """
        Add multiple documents at once (efficient)
        
        Args:
            documents: List of dicts with keys:
                - id: unique identifier
                - text: content
                - metadata: (optional) source info
        
        Example:
            docs = [
                {
                    "id": "doc1",
                    "text": "Geotechnical monitoring involves...",
                    "metadata": {"source": "file1.pdf", "page": 1}
                },
                {
                    "id": "doc2",
                    "text": "Settlement is vertical displacement...",
                    "metadata": {"source": "file1.pdf", "page": 2}
                }
            ]
            vector_store.add_documents_batch(docs)
        """
        # Extract components
        ids = [doc["id"] for doc in documents]
        texts = [doc["text"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        
        # Generate embeddings for all (batched = faster)
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Store in vector database
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        print(f"✓ Added {len(documents)} documents to vector store")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Semantic search (NOT string matching!)
        
        Returns most similar documents by meaning
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of dicts with keys:
            - id: document id
            - text: document content
            - metadata: source info
            - distance: similarity score (0-1, higher = more similar)
        
        Example:
            results = vector_store.search("pore pressure measurement", top_k=3)
            for result in results:
                print(f"Similarity: {result['distance']:.2f}")
                print(f"Text: {result['text']}")
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search for similar documents
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results["ids"] and len(results["ids"]) > 0:
                for i, doc_id in enumerate(results["ids"][0]):
                    formatted_results.append({
                        "id": doc_id,
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": 1 - results["distances"][0][i]  # Convert to similarity
                    })
            
            return formatted_results
        
        except Exception as e:
            print(f"✗ Search error: {str(e)}")
            return []
    
    def search_with_context(self, query: str, top_k: int = 3) -> str:
        """
        Search and format as context for Ollama
        
        Returns:
            Formatted string with top K results
        
        Same interface as KnowledgeBase.search_with_context()
        """
        results = self.search(query, top_k=top_k)
        
        if not results:
            return ""
        
        context = "Related documents (semantic search):\n"
        for i, result in enumerate(results, 1):
            source = result["metadata"].get("source", "unknown")
            similarity = result["distance"]
            context += f"{i}. [{similarity:.1%} match] {source}\n"
            context += f"   {result['text'][:200]}...\n\n"
        
        return context
    
    def delete_document(self, doc_id: str) -> None:
        """Remove document from vector store"""
        self.collection.delete(ids=[doc_id])
        print(f"✓ Deleted document: {doc_id}")
    
    def clear_all(self) -> None:
        """Clear entire vector store"""
        # Delete and recreate collection
        self.client.delete_collection(name="geoatlas_kb")
        self.collection = self.client.get_or_create_collection(
            name="geoatlas_kb",
            metadata={"hnsw:space": "cosine"}
        )
        print("✓ Vector store cleared")
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        count = self.collection.count()
        return {
            "total_documents": count,
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding_dimension": 384,
            "storage_path": self.persist_dir,
            "metric": "cosine_similarity"
        }
    
    def persist(self) -> None:
        """Force save to disk (ChromaDB does this automatically)"""
        self.client.persist()
        print("✓ Vector store persisted to disk")