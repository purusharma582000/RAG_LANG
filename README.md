# 🤖 Language-Smart RAG Chatbot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)](https://streamlit.io/)

A production-ready bilingual (Hindi + English) document chat system that lets you chat with your PDF and TXT files using advanced AI. Upload documents and get intelligent answers in your preferred language!

## ✨ Features

- 🌏 **Bilingual Support**: Automatic language detection for Hindi and English
- 📄 **Document Processing**: Support for PDF and TXT files  
- 🤖 **Smart Retrieval**: Vector-based document search with Chroma
- 🚀 **Production Ready**: Dockerized with proper error handling
- 💬 **Interactive Chat**: Clean Streamlit web interface
- 🔧 **Easy Setup**: One-command deployment with Docker

---

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop** - [Download here](https://docs.docker.com/get-docker/)
- **Groq API Key** - [Get free key here](https://console.groq.com)

### Installation & Setup (5 minutes)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/rag-chatbot.git
   cd rag-chatbot
   ```

2. **Install Docker Desktop** and make sure it's running

3. **Get your Groq API key:**
   - Go to https://console.groq.com
   - Sign up/login
   - Create an API key
   - Copy the key (starts with `gsk_`)

4. **Configure environment:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env file and replace:
   GROQ_API_KEY=your_groq_api_key_here
   # With your actual key:
   GROQ_API_KEY=gsk_your_actual_key_here
   ```

5. **Start the application with Docker:**
   ```bash
   docker-compose up --build
   ```

6. **Open your browser:**
   - Go to http://localhost:8501
   - Upload documents and start chatting!

That's it! 🎉

---

## 🎮 How to Use

1. **Upload Documents**: Use sidebar to upload PDF or TXT files
2. **Process**: Click "Process Documents" to create embeddings
3. **Chat**: Ask questions in Hindi or English
4. **Get Answers**: AI responds intelligently in the same language

### Example Questions
- **English**: "What is this document about?"
- **Hindi**: "इस दस्तावेज़ का मुख्य विषय क्या है?"
- **Mixed**: "Machine learning क्या है और इसके फायदे बताइए?"

### Demo
```bash
# Example interactions:
User: "What are the main benefits mentioned in this document?"
Bot: "Based on the document, the main benefits include..."

User: "इस दस्तावेज़ में कौन से मुख्य लाभ बताए गए हैं?"  
Bot: "दस्तावेज़ के अनुसार, मुख्य लाभों में शामिल हैं..."
```

---

## 🐳 Docker Commands

### Basic Operations
```bash
# Start application (first time)
docker-compose up --build

# Start application (subsequent runs)
docker-compose up

# Start in background
docker-compose up -d

# Stop application  
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

### Monitoring & Debugging
```bash
# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f rag-chatbot
docker-compose logs -f ollama

# Check service status
docker-compose ps

# Restart services
docker-compose restart

# Rebuild and start fresh
docker-compose up --build --force-recreate
```

### Health Checks
```bash
# Check if application is running
curl http://localhost:8501/_stcore/health

# Check Ollama API
curl http://localhost:11434/api/tags

# View Docker containers
docker ps
```

---

## 🛠️ Development Setup

### Local Development (without Docker)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY=your_key_here

# Start Ollama (separate terminal)
ollama serve
ollama pull nomic-embed-text

# Run application
streamlit run main.py
```

### Project Structure
```
rag-chatbot/
├── 📋 main.py                 # Main application entry point
├── ⚙️  config.py              # Configuration management  
├── 🛠️  utils.py               # Utility functions
├── 🤖 groq_client.py          # Groq API client
├── 📄 document_processor.py   # Document processing
├── 🔍 vector_store.py         # Vector store management
├── 🧠 rag_system.py           # Core RAG system
├── 🎨 ui_components.py        # Streamlit UI components
├── 🐳 Dockerfile             # Docker configuration
├── 🐳 docker-compose.yml     # Multi-service setup
├── 📦 requirements.txt        # Python dependencies
├── ⚙️  .env.example           # Environment template
└── 📖 README.md              # This file
```

---

## ⚙️ Configuration

All settings are configured through environment variables in your `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | **Required**: Your Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model to use |
| `OLLAMA_MODEL` | `nomic-embed-text` | Embedding model |
| `CHUNK_SIZE` | `1000` | Document chunk size |
| `CHUNK_OVERLAP` | `200` | Chunk overlap size |
| `HINDI_THRESHOLD` | `0.3` | Hindi detection threshold |

---

## 🆘 Troubleshooting

### Common Issues

**🔴 "Cannot connect to Docker"**
- Make sure Docker Desktop is running
- Look for Docker whale icon in system tray
- Try restarting Docker Desktop

**🔴 "API key not configured"**
- Check your `.env` file has the correct API key
- Make sure no extra spaces around the key
- Verify the key starts with `gsk_`

**🔴 "Ollama not ready"**
- Wait 2-3 minutes for first-time model download (274MB)
- Check logs: `docker-compose logs ollama`
- Ensure port 11434 is not blocked

**🔴 "Port already in use"**
- Stop existing containers: `docker-compose down`
- Check what's using the port: `lsof -i :8501` (Mac/Linux)
- Change ports in `docker-compose.yml` if needed

**🔴 "Build failed"**
- Clear Docker cache: `docker system prune -a`
- Rebuild: `docker-compose build --no-cache`

### Getting Help

1. **Check existing issues**: [GitHub Issues](https://github.com/yourusername/rag-chatbot/issues)
2. **Create a new issue** with:
   - Error message
   - Steps to reproduce
   - Output of `docker-compose logs`
   - Your OS and Docker version

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📈 Roadmap

- [ ] Support for more document types (DOCX, PPTX)
- [ ] Additional language support (Spanish, French)
- [ ] API endpoints for integration
- [ ] User authentication system
- [ ] Document management interface
- [ ] Performance analytics dashboard

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for lightning-fast LLM inference
- [Ollama](https://ollama.ai/) for local embeddings
- [Streamlit](https://streamlit.io/) for the beautiful UI
- [LangChain](https://langchain.com/) for RAG components
- [Chroma](https://www.trychroma.com/) for vector storage

---

## 📧 Support

If you have issues, please:

1. **Check the troubleshooting section** above
2. **Search existing issues** in the repository
3. **Create a new issue** with detailed information:
   - Error message
   - Output of `docker-compose logs`
   - Your operating system
   - Steps to reproduce

---

**Made with ❤️ for the multilingual AI community**

⭐ **If you find this project helpful, please star it on GitHub!**

---

Enjoy chatting with your documents! 🎉