#!/bin/bash

# 1. Install Ollama
# Install zstd dependency
!sudo apt-get update && sudo apt-get install -y zstd

# Install Ollama
!curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama in the background
import subprocess
import time

# Start the server process
process = subprocess.Popen(['ollama', 'serve'])
time.sleep(5) # Wait for the server to warm up

# Pull a lightweight but powerful model (Llama 3.2 3B is great for Colab)
!ollama pull llama3.2:3b

# 2. Start Ollama in the background
echo "Starting Ollama..."
ollama serve &
sleep 5

# 3. Pull the required model
echo "Pulling Llama 3.2..."
ollama pull llama3.2:3b

# 4. Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 5. Run the project
echo "Starting the Auto-Refactor Tool..."
python main.py
