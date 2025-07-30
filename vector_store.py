"""
Vector store management for document embeddings and similarity search.
"""
from typing import List, Any, Tuple, Optional
from config import config
from utils import ErrorHandler

# Import with error handling
try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import OllamaEmbeddings
except ImportError as e:
    raise ImportError(f"Required packages not installed: {e}")


class VectorStoreManager:
    """Manage vector store operations for document embeddings."""
    
    def __init__(self):
        """Initialize vector store manager."""
        self.embeddings = None
        self.vectorstore = None
        self.documents = []
        self.is_initialized = False
    
    def initialize(self) -> Tuple[bool, str]:
        """
        Initialize embeddings and vector store.
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Initialize Ollama embeddings
            self.embeddings = OllamaEmbeddings(
                model=config.ollama.model,
                base_url=config.ollama.base_url
            )
            
            # Test embeddings
            test_success, test_message = self._test_embeddings()
            if not test_success:
                return False, test_message
            
            # Initialize vector store
            self.vectorstore = Chroma(
                persist_directory=config.vectorstore.chroma_dir,
                embedding_function=self.embeddings
            )
            
            self.is_initialized = True
            return True, "Vector store initialized successfully"
            
        except Exception as e:
            error_msg = f"Vector store initialization failed: {str(e)}"
            return False, error_msg
    
    def _test_embeddings(self) -> Tuple[bool, str]:
        """
        Test embeddings functionality.
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            test_embed = self.embeddings.embed_query("test")
            if not test_embed:
                return False, "Ollama embeddings failed - make sure Ollama is running"
            return True, "Embeddings test successful"
            
        except Exception as e:
            error_msg = f"Ollama Error: {str(e)}. Make sure Ollama is running with 'ollama serve'"
            return False, error_msg
    
    def add_documents(self, documents: List[Any]) -> Tuple[bool, str]:
        """
        Add documents to vector store.
        
        Args:
            documents (List[Any]): List of document chunks to add
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.is_initialized:
            return False, "Vector store not initialized"
        
        if not documents:
            return False, "No documents provided"
        
        try:
            # Add documents to vector store
            self.vectorstore.add_documents(documents)
            
            # Store documents for reference
            self.documents.extend(documents)
            
            success_msg = f"Added {len(documents)} document chunks to vector store"
            return True, success_msg
            
        except Exception as e:
            error_msg = ErrorHandler.handle_processing_error(e)
            return False, error_msg
    
    def similarity_search(self, query: str, k: Optional[int] = None) -> List[Any]:
        """
        Perform similarity search on documents.
        
        Args:
            query (str): Search query
            k (Optional[int]): Number of results to return
            
        Returns:
            List[Any]: List of relevant documents
        """
        if not self.is_initialized or not self.vectorstore:
            return []
        
        try:
            k = k or config.vectorstore.similarity_search_k
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k}
            )
            
            relevant_docs = retriever.get_relevant_documents(query)
            return relevant_docs
            
        except Exception as e:
            print(f"Similarity search error: {str(e)}")
            return []
    
    def get_context_from_docs(self, documents: List[Any]) -> str:
        """
        Extract context text from documents.
        
        Args:
            documents (List[Any]): List of documents
            
        Returns:
            str: Combined context text
        """
        if not documents:
            return ""
        
        try:
            context_parts = []
            for doc in documents:
                if hasattr(doc, 'page_content'):
                    context_parts.append(doc.page_content)
                elif isinstance(doc, str):
                    context_parts.append(doc)
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            print(f"Error extracting context: {str(e)}")
            return ""
    
    def clear_documents(self) -> Tuple[bool, str]:
        """
        Clear all documents from vector store.
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Clear in-memory documents
            self.documents = []
            
            # Reinitialize vector store to clear persisted data
            if self.is_initialized:
                self.vectorstore = Chroma(
                    persist_directory=config.vectorstore.chroma_dir,
                    embedding_function=self.embeddings
                )
            
            return True, "Documents cleared successfully"
            
        except Exception as e:
            error_msg = f"Error clearing documents: {str(e)}"
            return False, error_msg
    
    def get_document_count(self) -> int:
        """
        Get the number of documents in the store.
        
        Returns:
            int: Number of documents
        """
        return len(self.documents)
    
    def get_store_info(self) -> dict:
        """
        Get information about the vector store.
        
        Returns:
            dict: Store information
        """
        return {
            'is_initialized': self.is_initialized,
            'document_count': len(self.documents),
            'embedding_model': config.ollama.model,
            'chunk_size': config.vectorstore.chunk_size,
            'chunk_overlap': config.vectorstore.chunk_overlap,
            'similarity_search_k': config.vectorstore.similarity_search_k,
            'chroma_directory': config.vectorstore.chroma_dir
        }
    
    def health_check(self) -> dict:
        """
        Perform health check on vector store components.
        
        Returns:
            dict: Health check results
        """
        health_status = {
            'vector_store_initialized': self.is_initialized,
            'embeddings_available': self.embeddings is not None,
            'document_count': len(self.documents),
            'last_error': None
        }
        
        # Test embeddings if available
        if self.embeddings:
            try:
                test_embed = self.embeddings.embed_query("health check")
                health_status['embeddings_working'] = bool(test_embed)
            except Exception as e:
                health_status['embeddings_working'] = False
                health_status['last_error'] = str(e)
        else:
            health_status['embeddings_working'] = False
        
        return health_status