#!/bin/bash
echo "🚀 Initializing Environment and Ollama..."

# 1. Install missing extraction tool (zstd)
apt-get update -qq && apt-get install -y zstd -qq

# 2. Install Ollama if missing
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 3. Start Ollama service in background from root directory
echo "🔄 Starting Ollama server..."
cd /content || cd /root
ollama serve > /dev/null 2>&1 &

# 4. Wait until server responds
echo "⏳ Waiting for Ollama server to respond..."
until curl -s http://127.0.0.1:11434/api/version > /dev/null; do
    sleep 2
done
echo "✅ Ollama is active!"

echo "🎉 Setup complete!"
