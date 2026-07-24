#!/bin/bash
echo "🚀 Installing Ollama Engine..."

# 1. Install missing extraction dependencies
apt-get update -qq && apt-get install -y zstd -qq

# 2. Install Ollama engine binary
if ! command -v ollama &> /dev/null; then
    echo "📦 Downloading and installing Ollama system binary..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 3. Start background server from stable directory
echo "🔄 Starting Ollama background daemon..."
cd /content || cd /tmp
ollama serve > /dev/null 2>&1 &

# 4. Wait for engine health check
echo "⏳ Waiting for Ollama engine to initialize..."
until curl -s http://127.0.0.1:11434/api/version > /dev/null; do
    sleep 2
done

echo "✅ Ollama Engine is running and ready!"
