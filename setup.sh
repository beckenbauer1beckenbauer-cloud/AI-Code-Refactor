#!/bin/bash
echo "🚀 Initializing System Dependencies & Ollama..."

# 1. Install required extraction tools
apt-get update -qq && apt-get install -y zstd -qq

# 2. Kill any stale Ollama processes running in corrupted directories
pkill -f "ollama serve" || true
pkill -f "llama-server" || true

# 3. Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama binary..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 4. Start Ollama explicitly anchored at System Root (/)
echo "🔄 Starting Ollama background server anchored at system root..."
cd /
nohup ollama serve > /tmp/ollama.log 2>&1 &

# 5. Wait for server health response
echo "⏳ Waiting for Ollama engine..."
until curl -s http://127.0.0.1:11434/api/version > /dev/null; do
    sleep 2
done

echo "✅ Ollama system daemon is active!"
