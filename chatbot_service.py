from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from rag_service import RAGService
from config import get_settings


class ChatbotService:
    """Service for handling chatbot interactions with RAG."""
    
    def __init__(self, rag_service: RAGService):
        """
        Initialize chatbot service.
        
        Args:
            rag_service: RAG service instance
        """
        self.settings = get_settings()
        self.rag_service = rag_service
        self.llm = ChatOpenAI(
            openai_api_key=self.settings.openai_api_key,
            model_name=self.settings.llm_model,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Initialize the conversational retrieval chain."""
        # Custom prompt template
        template = """You are a helpful AI assistant. Use the following pieces of context to answer the question at the end. 
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

Context: {context}

Question: {question}

Helpful Answer:"""
        
        qa_prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.rag_service.get_retriever(),
            memory=self.memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": qa_prompt}
        )
    
    def chat(self, message: str) -> Dict[str, any]:
        """
        Process a chat message and return response with sources.
        
        Args:
            message: User message
        
        Returns:
            Dictionary with answer and source documents
        """
        result = self.chain({"question": message})
        
        # Extract source information
        sources = []
        if "source_documents" in result:
            for doc in result["source_documents"]:
                sources.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
        
        return {
            "answer": result["answer"],
            "sources": sources
        }
    
    def chat_without_rag(self, message: str) -> str:
        """
        Process a chat message without RAG (direct LLM call).
        
        Args:
            message: User message
        
        Returns:
            LLM response
        """
        from langchain.schema import HumanMessage
        
        response = self.llm([HumanMessage(content=message)])
        return response.content
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Get chat history.
        
        Returns:
            List of chat messages
        """
        messages = []
        if hasattr(self.memory, 'chat_memory') and hasattr(self.memory.chat_memory, 'messages'):
            for msg in self.memory.chat_memory.messages:
                messages.append({
                    "type": msg.type,
                    "content": msg.content
                })
        return messages
