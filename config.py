# config.py
# This file lets users easily change the AI provider and model

# Choose your provider: "ollama" or "openai"
PROVIDER = "ollama"

# Set your API Key (If using OpenAI, put your key here)
API_KEY = None

# Base URL for the AI service
BASE_URL = "http://localhost:11434/api/generate"

# The specific model to use
MODEL_NAME = "llama3.2:3b"
