#!/bin/bash

# 1. Install Ollama
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

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
