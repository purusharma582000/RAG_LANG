"""
Main application entry point for the RAG Chatbot.
"""
import streamlit as st
import warnings
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables")

from rag_system import RAGSystem
from ui_components import UIComponents
from config import config

# Suppress warnings
warnings.filterwarnings("ignore")

# Print import status for debugging
print("✅ Starting RAG Chatbot Application")
print(f"✅ Configuration loaded - Groq Model: {config.api.groq_model}")
print(f"✅ Configuration loaded - Ollama Model: {config.ollama.model}")


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    
    if 'initialization_attempted' not in st.session_state:
        st.session_state.initialization_attempted = False
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'document_count' not in st.session_state:
        st.session_state.document_count = 0


def initialize_rag_system():
    """Initialize the RAG system with error handling."""
    if st.session_state.rag_system is None:
        st.session_state.rag_system = RAGSystem()
    
    if not st.session_state.initialization_attempted:
        st.session_state.initialization_attempted = True
        
        with st.spinner("Initializing RAG system..."):
            success, message = st.session_state.rag_system.initialize()
            
            if success:
                st.success(f"✅ {message}")
                return True
            else:
                st.error(f"❌ Initialization failed: {message}")
                return False
    
    return st.session_state.rag_system.is_initialized


def show_api_key_warning():
    """Show API key configuration warning."""
    st.error("🔑 **Please configure your Groq API key!**")
    
    with st.expander("How to set up your API key"):
        st.markdown("""
        ### Option 1: Environment Variable (Recommended)
        ```bash
        export GROQ_API_KEY="your_actual_groq_api_key_here"
        ```
        
        ### Option 2: Create .env file
        Create a `.env` file in your project directory:
        ```
        GROQ_API_KEY=your_actual_groq_api_key_here
        ```
        
        ### Option 3: Docker Environment
        Set the environment variable in your docker-compose.yml or when running Docker.
        
        **Get your API key from:** https://console.groq.com
        """)


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Create UI components
    if st.session_state.rag_system:
        ui = UIComponents(st.session_state.rag_system)
    else:
        # Create temporary UI for initialization
        temp_rag = RAGSystem()
        ui = UIComponents(temp_rag)
    
    # Render header
    ui.render_header()
    
    # Render language demo
    ui.render_language_demo()
    
    # Check API key configuration
    try:
        api_key = config.api.groq_api_key
        if not api_key:
            show_api_key_warning()
            st.stop()
    except Exception as e:
        st.error(f"Configuration error: {str(e)}")
        show_api_key_warning()
        st.stop()
    
    # Initialize RAG system
    if not initialize_rag_system():
        st.stop()
    
    # Update UI with initialized RAG system
    ui = UIComponents(st.session_state.rag_system)
    
    # Check if system is properly initialized
    if not ui.check_initialization():
        st.stop()
    
    # Render main interface
    ui.render_sidebar()
    ui.render_chat_interface()
    
    # Render troubleshooting section
    ui.render_troubleshooting()
    
    # Footer with system status
    render_footer(ui)


def render_footer(ui):
    """Render application footer with system status."""
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = st.session_state.rag_system.get_system_status()
        if status['is_initialized']:
            st.success("🟢 System Ready")
        else:
            st.error("🔴 System Not Ready")
    
    with col2:
        doc_count = st.session_state.rag_system.vector_store.get_document_count()
        st.info(f"📄 Documents: {doc_count}")
    
    with col3:
        st.info(f"🤖 Model: {config.api.groq_model}")
    
    # Debug information (only in development)
    if st.checkbox("Show Debug Info", value=False):
        with st.expander("Debug Information"):
            debug_info = {
                'Config': {
                    'Groq Model': config.api.groq_model,
                    'Ollama Model': config.ollama.model,
                    'Chunk Size': config.vectorstore.chunk_size,
                    'Similarity K': config.vectorstore.similarity_search_k,
                    'API Key Set': bool(config.api.groq_api_key)  # Don't show actual key!
                },
                'System Status': st.session_state.rag_system.get_system_status(),
                'Session State Keys': list(st.session_state.keys())
            }
            st.json(debug_info)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please check the troubleshooting section for common solutions.")
        
        # Show detailed error in debug mode
        if st.checkbox("Show detailed error"):
            st.exception(e)