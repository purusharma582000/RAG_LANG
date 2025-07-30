"""
Utility functions for the RAG Chatbot application.
"""
import os
import tempfile
import warnings
from typing import List, Tuple, Any
from config import config

# Suppress warnings
warnings.filterwarnings("ignore")


def detect_language(text: str) -> str:
    """
    Simple language detection for Hindi and English.
    
    Args:
        text (str): Input text to analyze
        
    Returns:
        str: 'hindi' or 'english'
    """
    # Count Hindi characters (Devanagari script)
    hindi_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
    total_chars = len([char for char in text if char.isalpha()])
    
    if total_chars == 0:
        return "english"  # Default to English if no alphabetic characters
    
    hindi_ratio = hindi_chars / total_chars
    
    # Use threshold from config
    if hindi_ratio > config.language.hindi_threshold:
        return "hindi"
    else:
        return "english"


def save_uploaded_files(uploaded_files) -> List[str]:
    """
    Save uploaded files to temporary location.
    
    Args:
        uploaded_files: Streamlit uploaded files
        
    Returns:
        List[str]: List of temporary file paths
    """
    temp_files = []
    
    for file in uploaded_files:
        try:
            # Get file extension
            file_extension = file.name.split('.')[-1].lower()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=f".{file_extension}"
            ) as tmp:
                tmp.write(file.getvalue())
                temp_files.append(tmp.name)
                
        except Exception as e:
            print(f"Error saving file {file.name}: {str(e)}")
            continue
    
    return temp_files


def cleanup_temp_files(temp_files: List[str]) -> None:
    """
    Clean up temporary files.
    
    Args:
        temp_files (List[str]): List of temporary file paths to delete
    """
    for tmp_file in temp_files:
        try:
            if os.path.exists(tmp_file):
                os.unlink(tmp_file)
        except Exception as e:
            print(f"Warning: Could not delete temporary file {tmp_file}: {str(e)}")


def validate_file_type(filename: str) -> bool:
    """
    Validate if file type is supported.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        bool: True if file type is supported
    """
    supported_extensions = ['.pdf', '.txt']
    file_extension = '.' + filename.split('.')[-1].lower()
    return file_extension in supported_extensions


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_language_messages() -> dict:
    """
    Get language-specific UI messages.
    
    Returns:
        dict: Dictionary containing messages in both languages
    """
    return {
        'upload_docs': {
            'hindi': 'दस्तावेज़ अपलोड करें',
            'english': 'Upload Documents'
        },
        'process_docs': {
            'hindi': 'दस्तावेज़ प्रोसेस करें',
            'english': 'Process Documents'
        },
        'clear_all': {
            'hindi': 'सब साफ़ करें',
            'english': 'Clear All'
        },
        'thinking': {
            'hindi': 'सोच रहा हूँ...',
            'english': 'Thinking...'
        },
        'sources': {
            'hindi': 'स्रोत',
            'english': 'Sources'
        },
        'no_docs_error': {
            'hindi': 'कृपया पहले दस्तावेज़ अपलोड करके प्रोसेस करें!',
            'english': 'Please upload and process documents first!'
        },
        'detected_language': {
            'hindi': 'पहचानी गई भाषा',
            'english': 'Detected Language'
        }
    }


def get_system_prompts() -> dict:
    """
    Get system prompts for different languages.
    
    Returns:
        dict: Dictionary containing system prompts
    """
    return {
        'hindi': """आप एक सहायक AI असिस्टेंट हैं। आपको हमेशा हिंदी में जवाब देना है। 
        यदि context दिया गया है तो उसके आधार पर जवाब दें। अगर आपको context में जवाब नहीं मिलता तो कहें कि "मुझे इस बारे में जानकारी नहीं है।"
        स्पष्ट, संक्षिप्त और सही हिंदी में उत्तर दें।""",
        
        'english': """You are a helpful AI assistant. Always respond in English only. 
        If context is provided, base your answer on that context. If you don't know the answer from the context, say "I don't have information about this."
        Provide clear, concise answers in proper English."""
    }


class ErrorHandler:
    """Custom error handler for the application."""
    
    @staticmethod
    def handle_api_error(error: Exception, language: str = 'english') -> str:
        """
        Handle API-related errors.
        
        Args:
            error (Exception): The exception that occurred
            language (str): Language for error message
            
        Returns:
            str: Formatted error message
        """
        if language == 'hindi':
            return f"API त्रुटि: {str(error)}"
        else:
            return f"API Error: {str(error)}"
    
    @staticmethod
    def handle_processing_error(error: Exception, language: str = 'english') -> str:
        """
        Handle document processing errors.
        
        Args:
            error (Exception): The exception that occurred
            language (str): Language for error message
            
        Returns:
            str: Formatted error message
        """
        if language == 'hindi':
            return f"प्रसंस्करण त्रुटि: {str(error)}"
        else:
            return f"Processing Error: {str(error)}"
    
    @staticmethod
    def handle_connection_error(error: Exception, language: str = 'english') -> str:
        """
        Handle connection-related errors.
        
        Args:
            error (Exception): The exception that occurred
            language (str): Language for error message
            
    Returns:
            str: Formatted error message
        """
        if language == 'hindi':
            return f"कनेक्शन त्रुटि: {str(error)}"
        else:
            return f"Connection Error: {str(error)}"