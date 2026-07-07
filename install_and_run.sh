#!/bin/bash

# 1. Update and install necessary tools
echo "Installing dependencies..."
apt-get update && apt-get install -y zstd pciutils

# 2. Install Ollama
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# 3. Start Ollama in the background properly
echo "Starting Ollama server..."
ollama serve > ollama.log 2>&1 &
sleep 15  # Wait longer to ensure the server is ready

# 4. Pull the model
echo "Pulling Llama 3.2..."
ollama pull llama3.2:3b

# 5. Prepare data directory
mkdir -p data

# 6. Install Python dependencies
pip install -r requirements.txt

# 7. Run the project
echo "Starting the Auto-Refactor Tool..."
python main.py
