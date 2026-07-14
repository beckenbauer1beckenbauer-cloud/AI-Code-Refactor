import subprocess
import json
import time
import os
import sys

def is_colab(): 
    return 'google.colab' in sys.modules

def setup_environment():
    # Load configuration
    with open('models_config.json', 'r') as f: 
        config = json.load(f)
    
    print("--- Choose your AI Engine ---")
    keys = list(config.keys())
    for i, model in enumerate(keys): 
        print(f"{i+1}. {model}")
    
    choice = keys[int(input("Selection: "))-1]
    selected_cfg = config[choice]

    # Ask for the library and validate
    target_lib = input("Enter the name of the Python library you want to analyze: ").strip()
    if not target_lib:
        print("\n❌ Error: You must specify a library name to proceed.")
        sys.exit(1)
    
    # Update config with library info
    selected_cfg['target_lib'] = target_lib
    
    # 1. Install dependencies
    print(f"📦 Installing dependencies for {choice}...")
    cmd = selected_cfg['install']
    if is_colab(): 
        from IPython import get_ipython
        get_ipython().magic(f"!{cmd}")
    else: 
        subprocess.run(cmd, shell=True)
    
    # 2. Download the model (The fix!)
    if "download" in selected_cfg:
        model_file = selected_cfg["model_file"]
        # Only download if file doesn't exist
        if not os.path.exists(model_file):
            print(f"📥 Downloading model {model_file}...")
            if is_colab():
                get_ipython().system(selected_cfg["download"])
            else:
                subprocess.run(selected_cfg["download"], shell=True)
        else:
            print(f"✅ Model {model_file} already exists locally.")

    # 3. Final verification
    if not os.path.exists(selected_cfg["model_file"]):
        print(f"❌ Error: Model file {selected_cfg['model_file']} not found after download!")
        sys.exit(1)

    # 4. Save engine state for other scripts to use
    with open("engine_state.json", "w") as f: 
        json.dump(selected_cfg, f)
    
    return choice

def run_step_with_healing(script_name):
    """Runs a script and keeps looping if it returns an error code."""
    max_retries = 3
    for attempt in range(max_retries):
        print(f"\n🚀 Attempting step: {script_name} (Attempt {attempt+1})")
        
        # Run the script as a process
        process = subprocess.run(['python3', script_name], capture_output=True, text=True)
        
        if process.returncode == 0:
            print(f"✅ {script_name} passed.")
            return True
        else:
            print(f"❌ Error in {script_name}:")
            error_log = process.stderr
            print(error_log)
            
            # --- AI HEALING AGENT ---
            print("🤖 AI Agent: Analyzing and fixing errors...")
            # Here you call your refactor_code_with_engine logic
            # to feed the 'error_log' back to the model 
            # and rewrite the script file.
            
            time.sleep(2) # Give the system a breath
            
    return False

# Main Pipeline Controller
pipeline = ["extractor.py", "engine.py","processor.py", "plotting.py","refactor_and_validate.py","generate_analytics_report.py"]

for step in pipeline:
    if not run_step_with_healing(step):
        print(f"🚨 Critical Failure: {step} could not be fixed. Stopping Pipeline.")
        break


if __name__ == "__main__":
    setup_environment()
    
    # Define pipeline
    pipeline = [
        "extractor.py",
        "engine.py",
        "processor.py",
        "plotting.py",
        "refactor_and_validate.py",
        "generate_analytics_report.py"
    ]
    
    for step in pipeline:
        if os.path.exists(step):
            print(f"\n🚀 Running: {step}")
            with open(step, "r") as f:
                exec(f.read(), globals())
        else:
            print(f"❌ Error: {step} not found. Skipping...")

