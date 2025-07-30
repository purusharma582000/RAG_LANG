"""
Streamlit UI components for the RAG chatbot application.
"""
import streamlit as st
from typing import List, Dict, Any
from utils import detect_language, format_file_size, save_uploaded_files, cleanup_temp_files
from config import config


class UIComponents:
    """Streamlit UI components for the RAG chatbot."""
    
    def __init__(self, rag_system):
        """
        Initialize UI components.
        
        Args:
            rag_system: RAG system instance
        """
        self.rag_system = rag_system
    
    def render_header(self):
        """Render application header."""
        st.set_page_config(
            page_title="Language-Smart RAG Chatbot",
            page_icon="🤖",
            layout="wide"
        )
        
        st.title("🤖 भाषा-स्मार्ट RAG चैटबॉट | Language-Smart RAG Chatbot")
        st.markdown("**हिंदी और अंग्रेजी में अपने दस्तावेज़ों से चैट करें | Chat with your documents in Hindi and English**")
    
    def render_language_demo(self):
        """Render language detection demo."""
        with st.expander("🔍 भाषा पहचान डेमो | Language Detection Demo"):
            test_text = st.text_input(
                "टेस्ट टेक्स्ट डालें | Enter test text:", 
                "Cyber Security क्या है"
            )
            if test_text:
                detected = detect_language(test_text)
                if detected == "hindi":
                    st.success("✅ पहचानी गई भाषा: हिंदी | Detected Language: Hindi")
                else:
                    st.success("✅ पहचानी गई भाषा: अंग्रेजी | Detected Language: English")
    
    def render_sidebar(self):
        """Render sidebar with document upload and system info."""
        with st.sidebar:
            self._render_document_upload()
            st.divider()
            self._render_system_info()
            self._render_clear_button()
    
    def _render_document_upload(self):
        """Render document upload section."""
        st.header("📁 दस्तावेज़ अपलोड | Upload Documents")
        
        uploaded_files = st.file_uploader(
            "PDF या TXT फाइलें चुनें | Choose PDF or TXT files",
            accept_multiple_files=True,
            type=['pdf', 'txt']
        )
        
        if uploaded_files:
            # Show file information
            st.write("**Selected Files:**")
            for file in uploaded_files:
                file_size = format_file_size(file.size)
                is_valid = self.rag_system.validate_file(file.name)
                status_icon = "✅" if is_valid else "❌"
                st.write(f"{status_icon} {file.name} ({file_size})")
        
        if st.button("📤 दस्तावेज़ प्रोसेस करें | Process Documents", type="primary"):
            if uploaded_files:
                self._process_uploaded_files(uploaded_files)
            else:
                st.warning("Please select files first!")
    
    def _process_uploaded_files(self, uploaded_files):
        """Process uploaded files."""
        with st.spinner("Processing documents..."):
            # Save uploaded files
            temp_files = save_uploaded_files(uploaded_files)
            
            try:
                # Process documents
                success, message = self.rag_system.process_documents(temp_files)
                
                if success:
                    st.success(f"✅ {message}")
                    # Update document count in session state
                    st.session_state.document_count = self.rag_system.vector_store.get_document_count()
                else:
                    st.error(f"❌ {message}")
                    
            except Exception as e:
                st.error(f"❌ Processing error: {str(e)}")
            
            finally:
                # Cleanup temporary files
                cleanup_temp_files(temp_files)
    
    def _render_system_info(self):
        """Render system information."""
        st.header("ℹ️ सिस्टम जानकारी | System Info")
        
        # Get system status
        status = self.rag_system.get_system_status()
        
        # Display basic info
        st.info(f"**मॉडल | Model:** {config.api.groq_model}")
        st.info(f"**एम्बेडिंग | Embeddings:** {config.ollama.model}")
        st.success("🌏 **भाषा समर्थन | Language Support:** हिंदी + English")
        
        # Document count
        doc_count = self.rag_system.vector_store.get_document_count()
        if doc_count > 0:
            st.metric("दस्तावेज़ खंड | Document Chunks", doc_count)
            
            # Show document stats
            stats = self.rag_system.get_document_stats()
            with st.expander("📊 Document Statistics"):
                st.write(f"**Total Characters:** {stats['total_characters']:,}")
                st.write(f"**Average Chunk Size:** {stats['average_chunk_size']:,}")
        else:
            st.metric("दस्तावेज़ खंड | Document Chunks", 0)
    
    def _render_clear_button(self):
        """Render clear all button."""
        if st.button("🗑️ सब साफ़ करें | Clear All"):
            # Clear documents
            success, message = self.rag_system.clear_documents()
            
            # Clear chat history
            if 'messages' in st.session_state:
                st.session_state.messages = []
            
            if success:
                st.success("✅ Cleared all data!")
            else:
                st.error(f"❌ {message}")
            
            st.rerun()
    
    def render_chat_interface(self):
        """Render main chat interface."""
        st.header("💬 अपने दस्तावेज़ों से चैट करें | Chat with your documents")
        
        # Show examples
        self._render_examples()
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        self._render_chat_messages()
        
        # Chat input
        self._render_chat_input()
    
    def _render_examples(self):
        """Render example queries."""
        st.markdown("""
        **उदाहरण | Examples:**
        - हिंदी: "साइबर सिक्योरिटी क्या है?"
        - English: "What is cyber security?"
        - Mixed: "Machine Learning क्या है और इसके फायदे बताइए"
        """)
    
    def _render_chat_messages(self):
        """Render chat message history."""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show detected language for user messages
                if message["role"] == "user" and "detected_language" in message:
                    lang_emoji = "🇮🇳" if message["detected_language"] == "hindi" else "🇺🇸"
                    lang_name = "हिंदी" if message["detected_language"] == "hindi" else "English"
                    st.caption(f"{lang_emoji} पहचानी गई भाषा | Detected: {lang_name}")
                
                # Show sources for assistant messages
                if message["role"] == "assistant" and "sources" in message:
                    self._render_sources(message["sources"], message.get("detected_language", "english"))
    
    def _render_sources(self, sources: List[str], language: str = "english"):
        """Render source documents."""
        sources_header = "📚 स्रोत | Sources" if language == "hindi" else "📚 Sources"
        
        with st.expander(sources_header):
            for i, source in enumerate(sources, 1):
                source_label = f"**स्रोत | Source {i}:**" if language == "hindi" else f"**Source {i}:**"
                st.markdown(source_label)
                st.markdown(f"```\n{source}\n```")
    
    def _render_chat_input(self):
        """Render chat input and handle user queries."""
        if prompt := st.chat_input("अपने दस्तावेज़ों के बारे में पूछें... | Ask about your documents..."):
            # Check if documents are loaded
            if self.rag_system.vector_store.get_document_count() == 0:
                detected_lang = detect_language(prompt)
                if detected_lang == "hindi":
                    st.error("❌ कृपया पहले दस्तावेज़ अपलोड करके प्रोसेस करें!")
                else:
                    st.error("❌ Please upload and process documents first!")
                return
            
            # Detect language
            detected_language = detect_language(prompt)
            
            # Add user message
            user_message = {
                "role": "user",
                "content": prompt,
                "detected_language": detected_language
            }
            st.session_state.messages.append(user_message)
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
                lang_emoji = "🇮🇳" if detected_language == "hindi" else "🇺🇸"
                lang_name = "हिंदी" if detected_language == "hindi" else "English"
                st.caption(f"{lang_emoji} पहचानी गई भाषा | Detected: {lang_name}")
            
            # Get AI response
            with st.chat_message("assistant"):
                thinking_text = "सोच रहा हूँ..." if detected_language == "hindi" else "Thinking..."
                
                with st.spinner(thinking_text):
                    answer, sources = self.rag_system.query(prompt)
                    
                    st.markdown(answer)
                    
                    # Prepare and display sources
                    source_texts = []
                    if sources:
                        source_texts = [doc.page_content[:300] + "..." for doc in sources]
                        self._render_sources(source_texts, detected_language)
                    
                    # Add assistant message to history
                    assistant_message = {
                        "role": "assistant",
                        "content": answer,
                        "detected_language": detected_language
                    }
                    if source_texts:
                        assistant_message["sources"] = source_texts
                    
                    st.session_state.messages.append(assistant_message)
    
    def render_troubleshooting(self):
        """Render troubleshooting information."""
        with st.expander("🔧 Troubleshooting | समस्या निवारण"):
            troubleshooting = self.rag_system.get_troubleshooting_info()
            
            st.write("**Common Issues:**")
            for issue_type, issue_info in troubleshooting['common_issues'].items():
                st.write(f"**{issue_info['issue']}:**")
                for solution in issue_info['solutions']:
                    st.write(f"- {solution}")
                st.write("")
            
            # Current status
            if troubleshooting['current_status']:
                st.write("**Current System Status:**")
                status = troubleshooting['current_status']
                for key, value in status.items():
                    if key != 'last_error':
                        icon = "✅" if value else "❌"
                        st.write(f"{icon} {key.replace('_', ' ').title()}: {value}")
                
                if status.get('last_error'):
                    st.error(f"Last Error: {status['last_error']}")
    
    def check_initialization(self) -> bool:
        """
        Check if RAG system is properly initialized.
        
        Returns:
            bool: True if initialized, False otherwise
        """
        if not self.rag_system.is_initialized:
            st.error("❌ RAG system is not properly initialized!")
            self.render_troubleshooting()
            return False
        return True