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

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh

# Expose port
EXPOSE 8501

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the application
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]