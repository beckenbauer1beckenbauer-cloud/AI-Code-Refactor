import os
import sys
import json
import subprocess
import time
from engine import refactor_code_with_engine

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
    """Runs a script and loops if error, using the AI Agent to fix it."""
    for attempt in range(2):
        print(f"\n🚀 Executing: {script_name} (Attempt {attempt+1})")
        
        process = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
        
        if process.returncode == 0:
            print(f"✅ {script_name} success.")
            return True
        else:
            print(f"❌ Error in {script_name}:\n{process.stderr}")
            print("🤖 AI Agent: Analyzing and rewriting code...")
            
            with open(script_name, "r") as f: code = f.read()
            fix_prompt = f"The file '{script_name}' crashed with this error:\n{process.stderr}\n\nRewrite the code to fix this error. Keep the logic, just fix the crash. Output ONLY the corrected python code."
            
            fix = refactor_code_with_engine("HealingAgent", fix_prompt)
            
            if fix and 'refactored_code' in fix:
                with open(script_name, "w") as f: f.write(fix['refactored_code'])
                time.sleep(1)
            else:
                print("❌ AI Agent failed to fix the code.")
    return False

if __name__ == "__main__":
    setup_environment()
    
    # Pipeline sequence
    pipeline = ["extractor.py", "engine.py","processor.py", "plotting.py","refactor_and_validate.py","generate_analytics_report.py"]
    
    for step in pipeline:
        if os.path.exists(step):
            if not run_step_with_healing(step):
                print(f"🚨 Pipeline halted at {step}")
                break
        else:
            print(f"❌ File {step} missing!")
