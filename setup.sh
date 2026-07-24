#!/bin/bash
echo "🚀 Initializing Environment and Ollama..."

# 1. Install missing extraction tool (zstd)
echo "📦 Installing system dependencies..."
apt-get update -qq && apt-get install -y zstd -qq

# 2. Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 3. Start Ollama service in background
echo "🔄 Starting Ollama server..."
ollama serve > /dev/null 2>&1 &

# 4. Wait until server is reachable
echo "⏳ Waiting for Ollama server to respond..."
until curl -s http://127.0.0.1:11434/api/version > /dev/null; do
    sleep 2
done
echo "✅ Ollama is active!"

# 5. Pull default model
echo "📥 Pre-pulling default model..."
ollama pull qwen2.5:7b

echo "🎉 Setup complete!"
