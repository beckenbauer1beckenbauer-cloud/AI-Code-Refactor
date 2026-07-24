#!/bin/bash
echo "🚀 Initializing Environment and Ollama..."

# 1. Install Ollama if not present
if ! command -v ollama &> /dev/null
then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 2. Start Ollama service in the background
echo "🔄 Starting Ollama server..."
ollama serve > /dev/null 2>&1 &

# 3. Wait until server is reachable
echo "⏳ Waiting for Ollama server to respond..."
until curl -s http://127.0.0.1:11434/api/version > /dev/null; do
    sleep 2
done
echo "✅ Ollama is active!"

# 4. Pull default models
echo "📥 Pre-pulling default models..."
ollama pull qwen2.5:7b

echo "🎉 Setup complete!"
