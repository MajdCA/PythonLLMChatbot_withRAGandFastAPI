from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document
import os
from config import get_settings


class RAGService:
    """Service for Retrieval-Augmented Generation operations."""
    
    def __init__(self):
        """Initialize RAG service with vector store and embeddings."""
        self.settings = get_settings()
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.settings.openai_api_key,
            model=self.settings.embedding_model
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
        )
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize or load existing vector store."""
        if os.path.exists(self.settings.vector_store_path):
            self.vector_store = Chroma(
                persist_directory=self.settings.vector_store_path,
                embedding_function=self.embeddings,
                collection_name=self.settings.collection_name
            )
        else:
            self.vector_store = Chroma(
                persist_directory=self.settings.vector_store_path,
                embedding_function=self.embeddings,
                collection_name=self.settings.collection_name
            )
    
    def add_documents(self, file_path: str, file_type: str = "txt") -> int:
        """
        Add documents to the vector store.
        
        Args:
            file_path: Path to the document file
            file_type: Type of file ('txt' or 'pdf')
        
        Returns:
            Number of chunks added
        """
        # Load documents based on file type
        if file_type.lower() == "pdf":
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)
        
        documents = loader.load()
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Add to vector store
        self.vector_store.add_documents(chunks)
        
        return len(chunks)
    
    def add_text(self, text: str, metadata: Optional[dict] = None) -> int:
        """
        Add text directly to the vector store.
        
        Args:
            text: Text content to add
            metadata: Optional metadata for the document
        
        Returns:
            Number of chunks added
        """
        # Create document from text
        doc = Document(page_content=text, metadata=metadata or {})
        
        # Split into chunks
        chunks = self.text_splitter.split_documents([doc])
        
        # Add to vector store
        self.vector_store.add_documents(chunks)
        
        return len(chunks)
    
    def retrieve_relevant_docs(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            k: Number of documents to retrieve (defaults to settings.top_k_results)
        
        Returns:
            List of relevant documents
        """
        if k is None:
            k = self.settings.top_k_results
        
        return self.vector_store.similarity_search(query, k=k)
    
    def get_retriever(self, k: Optional[int] = None):
        """
        Get a retriever instance.
        
        Args:
            k: Number of documents to retrieve
        
        Returns:
            Retriever instance
        """
        if k is None:
            k = self.settings.top_k_results
        
        return self.vector_store.as_retriever(search_kwargs={"k": k})
    
    def clear_vector_store(self):
        """Clear all documents from the vector store."""
        # Delete and recreate the vector store
        if os.path.exists(self.settings.vector_store_path):
            import shutil
            shutil.rmtree(self.settings.vector_store_path)
        
        self._initialize_vector_store()
