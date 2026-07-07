#!/bin/bash

# FIX 1: Install the missing tool BEFORE doing anything else
echo "Installing zstd..."
apt-get update && apt-get install -y zstd

# FIX 2: Install Ollama
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# FIX 3: Ensure the data directory exists BEFORE running Python
mkdir -p data

# FIX 4: Start Ollama properly
echo "Starting Ollama..."
ollama serve > ollama.log 2>&1 &
sleep 15

# FIX 5: Pull the model
echo "Pulling Llama 3.2..."
ollama pull llama3.2:3b

# FIX 6: Install your requirements
pip install -r requirements.txt

# FIX 7: Run the main program
python main.py
