#!/bin/bash

echo "🚀 Starting RAG Chatbot..."

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama..."
while ! curl -s http://ollama:11434/api/tags > /dev/null; do
    echo "   Waiting for Ollama to start..."
    sleep 5
done
echo "✅ Ollama is ready!"

# Download the embedding model if it doesn't exist
echo "📥 Checking/downloading embedding model..."
curl -X POST http://ollama:11434/api/pull \
    -H "Content-Type: application/json" \
    -d '{"name":"nomic-embed-text"}' \
    --max-time 300

echo "✅ Model ready!"

# Create directories
mkdir -p /app/chroma_db /app/logs /app/temp

echo "🎉 Starting application..."
exec "$@"