"""
Configuration management for the RAG Chatbot application.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class APIConfig:
    """API configuration settings."""
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_timeout: int = 30
    groq_temperature: float = 0.1
    groq_max_tokens: int = 1000


@dataclass
class OllamaConfig:
    """Ollama configuration settings."""
    model: str = "nomic-embed-text"
    base_url: str = "http://localhost:11434"


@dataclass
class VectorStoreConfig:
    """Vector store configuration."""
    chroma_dir: str = "./chroma_db"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    similarity_search_k: int = 3


@dataclass
class LanguageConfig:
    """Language detection configuration."""
    hindi_threshold: float = 0.3  # Threshold for Hindi character ratio


@dataclass
class AppConfig:
    """Main application configuration."""
    api: APIConfig
    ollama: OllamaConfig
    vectorstore: VectorStoreConfig
    language: LanguageConfig
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables."""
        groq_api_key = os.getenv('GROQ_API_KEY')
        
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        return cls(
            api=APIConfig(
                groq_api_key=groq_api_key,
                groq_model=os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'),
                groq_base_url=os.getenv('GROQ_BASE_URL', 'https://api.groq.com/openai/v1'),
                groq_timeout=int(os.getenv('GROQ_TIMEOUT', '30')),
                groq_temperature=float(os.getenv('GROQ_TEMPERATURE', '0.1')),
                groq_max_tokens=int(os.getenv('GROQ_MAX_TOKENS', '1000'))
            ),
            ollama=OllamaConfig(
                model=os.getenv('OLLAMA_MODEL', 'nomic-embed-text'),
                base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            ),
            vectorstore=VectorStoreConfig(
                chroma_dir=os.getenv('CHROMA_DIR', './chroma_db'),
                chunk_size=int(os.getenv('CHUNK_SIZE', '1000')),
                chunk_overlap=int(os.getenv('CHUNK_OVERLAP', '200')),
                similarity_search_k=int(os.getenv('SIMILARITY_SEARCH_K', '3'))
            ),
            language=LanguageConfig(
                hindi_threshold=float(os.getenv('HINDI_THRESHOLD', '0.3'))
            )
        )


# Load configuration from environment
try:
    config = AppConfig.from_env()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please set the GROQ_API_KEY environment variable or create a .env file")
    raise