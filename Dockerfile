# Simple Dockerfile for RAG Chatbot
FROM python:3.11-slim

# Set working directory
WORKDIR /app


# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all application files
COPY . .

# Create directories
RUN mkdir -p chroma_db logs temp

# Expose port
EXPOSE 8501

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Start application with built-in wait for Ollama
CMD sh -c "\
    echo '🚀 Starting RAG Chatbot...' && \
    echo '⏳ Waiting for Ollama...' && \
    while ! curl -s http://ollama:11434/api/tags > /dev/null 2>&1; do \
        echo '   Waiting for Ollama to start...' && \
        sleep 5; \
    done && \
    echo '✅ Ollama is ready!' && \
    echo '📥 Downloading embedding model...' && \
    curl -X POST http://ollama:11434/api/pull \
        -H 'Content-Type: application/json' \
        -d '{\"name\":\"nomic-embed-text\"}' \
        --max-time 300 && \
    echo '✅ Model ready!' && \
    echo '🎉 Starting application...' && \
    streamlit run main.py --server.port=8501 --server.address=0.0.0.0"