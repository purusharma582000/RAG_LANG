"""
RAG (Retrieval Augmented Generation) system core implementation.
"""
from typing import List, Tuple, Any
from groq_client import GroqClient
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from utils import detect_language, get_language_messages, ErrorHandler
from config import config


class RAGSystem:
    """Core RAG system that orchestrates all components."""
    
    def __init__(self):
        """Initialize RAG system components."""
        self.groq_client = None
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStoreManager()
        self.is_initialized = False
        self.messages = get_language_messages()
    
    def initialize(self, api_key: str = None) -> Tuple[bool, str]:
        """
        Initialize all RAG system components.
        
        Args:
            api_key (str, optional): Groq API key
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Initialize Groq client
            self.groq_client = GroqClient(api_key)
            
            # Test Groq connection
            groq_success, groq_message = self.groq_client.test_connection()
            if not groq_success:
                return False, f"Groq initialization failed: {groq_message}"
            
            # Initialize vector store
            vs_success, vs_message = self.vector_store.initialize()
            if not vs_success:
                return False, f"Vector store initialization failed: {vs_message}"
            
            self.is_initialized = True
            return True, "RAG system initialized successfully!"
            
        except Exception as e:
            error_msg = f"RAG system initialization error: {str(e)}"
            return False, error_msg
    
    def process_documents(self, file_paths: List[str]) -> Tuple[bool, str]:
        """
        Process documents and add them to vector store.
        
        Args:
            file_paths (List[str]): List of file paths to process
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.is_initialized:
            return False, "RAG system not initialized"
        
        try:
            # Process documents
            success, message, documents = self.document_processor.process_documents(file_paths)
            
            if not success:
                return False, message
            
            if not documents:
                return False, "No documents were processed"
            
            # Add to vector store
            vs_success, vs_message = self.vector_store.add_documents(documents)
            
            if not vs_success:
                return False, f"Vector store error: {vs_message}"
            
            # Combine messages
            final_message = f"{message}. {vs_message}"
            return True, final_message
            
        except Exception as e:
            error_msg = ErrorHandler.handle_processing_error(e)
            return False, error_msg
    
    def query(self, question: str) -> Tuple[str, List[Any]]:
        """
        Query the RAG system with automatic language detection.
        
        Args:
            question (str): User question
            
        Returns:
            Tuple[str, List[Any]]: (answer, source_documents)
        """
        # Detect language
        detected_language = detect_language(question)
        
        # Check if documents are available
        if self.vector_store.get_document_count() == 0:
            no_docs_msg = self.messages['no_docs_error'][detected_language]
            return no_docs_msg, []
        
        if not self.is_initialized:
            if detected_language == "hindi":
                return "सिस्टम तैयार नहीं है!", []
            else:
                return "System not initialized!", []
        
        try:
            # Get relevant documents
            relevant_docs = self.vector_store.similarity_search(question)
            
            # Create context from relevant documents
            context = self.vector_store.get_context_from_docs(relevant_docs)
            
            # Get answer from Groq
            answer = self.groq_client.chat(question, context, detected_language)
            
            return answer, relevant_docs
            
        except Exception as e:
            error_msg = ErrorHandler.handle_api_error(e, detected_language)
            return error_msg, []
    
    def clear_documents(self) -> Tuple[bool, str]:
        """
        Clear all documents from the system.
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            success, message = self.vector_store.clear_documents()
            return success, message
            
        except Exception as e:
            return False, f"Error clearing documents: {str(e)}"
    
    def get_system_status(self) -> dict:
        """
        Get comprehensive system status.
        
        Returns:
            dict: System status information
        """
        status = {
            'is_initialized': self.is_initialized,
            'document_count': self.vector_store.get_document_count(),
            'groq_model': self.groq_client.get_model_info() if self.groq_client else None,
            'vector_store_info': self.vector_store.get_store_info(),
            'supported_formats': self.document_processor.get_supported_formats()
        }
        
        # Add health check
        if self.is_initialized:
            status['health_check'] = self.vector_store.health_check()
        
        return status
    
    def get_document_stats(self) -> dict:
        """
        Get statistics about processed documents.
        
        Returns:
            dict: Document statistics
        """
        return self.document_processor.get_document_stats(self.vector_store.documents)
    
    def validate_file(self, filename: str) -> bool:
        """
        Validate if file is supported.
        
        Args:
            filename (str): File name to validate
            
        Returns:
            bool: True if supported
        """
        return self.document_processor.validate_file_format(filename)
    
    def get_troubleshooting_info(self) -> dict:
        """
        Get troubleshooting information for common issues.
        
        Returns:
            dict: Troubleshooting information
        """
        health_check = self.vector_store.health_check() if self.is_initialized else {}
        
        troubleshooting = {
            'common_issues': {
                'groq_api': {
                    'issue': 'Groq API connection failed',
                    'solutions': [
                        'Check your Groq API key',
                        'Verify internet connection',
                        'Check API key permissions'
                    ]
                },
                'ollama': {
                    'issue': 'Ollama embeddings failed',
                    'solutions': [
                        'Make sure Ollama is running: ollama serve',
                        'Install required model: ollama pull nomic-embed-text',
                        'Check Ollama base URL configuration'
                    ]
                },
                'documents': {
                    'issue': 'Document processing failed',
                    'solutions': [
                        'Check file format (PDF, TXT supported)',
                        'Verify file is not corrupted',
                        'Check file permissions'
                    ]
                }
            },
            'current_status': health_check,
            'configuration': {
                'groq_model': config.api.groq_model,
                'ollama_model': config.ollama.model,
                'chunk_size': config.vectorstore.chunk_size
            }
        }
        
        return troubleshooting