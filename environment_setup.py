import subprocess
import os
import sys

def is_colab():
    """Detects if the code is running in a Google Colab environment."""
    return 'google.colab' in sys.modules

def run_command(command):
    """Executes a shell command based on the environment."""
    if is_colab():
        # In Colab, we use the '!' prefix via get_ipython or just shell exec
        from IPython import get_ipython
        get_ipython().system(command)
    else:
        # Locally, use subprocess
        subprocess.run(command, shell=True, check=True)

def setup_model(model_name):
    """Checks for model and pulls it if missing."""
    print(f"Checking for model: {model_name}...")
    try:
        # 'ollama list' returns a list of installed models
        # We check if the model name is in the output
        result = subprocess.check_output("ollama list", shell=True).decode()
        if model_name in result:
            print(f"✅ Model {model_name} is already installed.")
        else:
            print(f"📥 Pulling model {model_name}. This may take a while...")
            run_command(f"ollama pull {model_name}")
    except Exception as e:
        print(f"⚠️ Could not verify/pull model: {e}")
