"""
Document processing module for loading and splitting documents.
"""
from typing import List, Tuple, Any
from config import config
from utils import ErrorHandler

# Import with error handling
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
except ImportError as e:
    raise ImportError(f"Required packages not installed: {e}")


class DocumentProcessor:
    """Handle document loading and processing."""
    
    def __init__(self):
        """Initialize document processor."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.vectorstore.chunk_size,
            chunk_overlap=config.vectorstore.chunk_overlap,
            length_function=len
        )
        self.supported_formats = ['.pdf', '.txt']
    
    def load_documents(self, file_paths: List[str]) -> Tuple[List[Any], List[str]]:
        """
        Load documents from files.
        
        Args:
            file_paths (List[str]): List of file paths to load
            
        Returns:
            Tuple[List[Any], List[str]]: (documents, errors)
        """
        documents = []
        errors = []
        
        for file_path in file_paths:
            try:
                loader = self._get_loader(file_path)
                if loader:
                    docs = loader.load()
                    documents.extend(docs)
                    print(f"✅ Loaded: {file_path}")
                else:
                    errors.append(f"Unsupported file type: {file_path}")
                    
            except Exception as e:
                error_msg = f"Error loading {file_path}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        return documents, errors
    
    def _get_loader(self, file_path: str):
        """
        Get appropriate document loader based on file extension.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            Document loader or None
        """
        file_extension = '.' + file_path.split('.')[-1].lower()
        
        if file_extension == '.pdf':
            return PyPDFLoader(file_path)
        elif file_extension == '.txt':
            return TextLoader(file_path, encoding='utf-8')
        else:
            return None
    
    def split_documents(self, documents: List[Any]) -> List[Any]:
        """
        Split documents into chunks.
        
        Args:
            documents (List[Any]): List of documents to split
            
        Returns:
            List[Any]: List of document chunks
        """
        if not documents:
            return []
        
        try:
            splits = self.text_splitter.split_documents(documents)
            print(f"✅ Split {len(documents)} documents into {len(splits)} chunks")
            return splits
            
        except Exception as e:
            print(f"❌ Error splitting documents: {str(e)}")
            raise e
    
    def process_documents(self, file_paths: List[str]) -> Tuple[bool, str, List[Any]]:
        """
        Complete document processing pipeline.
        
        Args:
            file_paths (List[str]): List of file paths to process
            
        Returns:
            Tuple[bool, str, List[Any]]: (success, message, processed_documents)
        """
        try:
            # Load documents
            documents, load_errors = self.load_documents(file_paths)
            
            if load_errors:
                error_msg = "Some files failed to load:\n" + "\n".join(load_errors)
                print(f"⚠️ {error_msg}")
            
            if not documents:
                return False, "No documents loaded successfully", []
            
            # Split documents
            splits = self.split_documents(documents)
            
            if not splits:
                return False, "No document chunks created", []
            
            success_msg = f"Successfully processed {len(splits)} document chunks"
            if load_errors:
                success_msg += f" (with {len(load_errors)} errors)"
            
            return True, success_msg, splits
            
        except Exception as e:
            error_msg = ErrorHandler.handle_processing_error(e)
            return False, error_msg, []
    
    def get_document_stats(self, documents: List[Any]) -> dict:
        """
        Get statistics about processed documents.
        
        Args:
            documents (List[Any]): List of processed documents
            
        Returns:
            dict: Document statistics
        """
        if not documents:
            return {
                'total_chunks': 0,
                'total_characters': 0,
                'average_chunk_size': 0
            }
        
        total_chars = sum(len(doc.page_content) for doc in documents)
        avg_chunk_size = total_chars // len(documents) if documents else 0
        
        return {
            'total_chunks': len(documents),
            'total_characters': total_chars,
            'average_chunk_size': avg_chunk_size
        }
    
    def validate_file_format(self, filename: str) -> bool:
        """
        Validate if file format is supported.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            bool: True if supported
        """
        file_extension = '.' + filename.split('.')[-1].lower()
        return file_extension in self.supported_formats
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List[str]: Supported file extensions
        """
        return self.supported_formats.copy()