#!/bin/bash

# 0. Install zstd (Required for Ollama extraction)
echo "Installing zstd..."
apt-get update && apt-get install -y zstd

# 1. Install Ollama
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# 2. Start Ollama in the background
echo "Starting Ollama..."
ollama serve &
sleep 10 # Added a longer sleep to ensure server is fully ready

# 3. Pull the required model
echo "Pulling Llama 3.2..."
ollama pull llama3.2

# 4. Ensure data directory exists
mkdir -p data

# 5. Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 6. Run the project
echo "Starting the Auto-Refactor Tool..."
python main.py
