import os
import sys
import json
import subprocess
import time
from engine import refactor_code_with_engine

def setup_environment():
    # 1. Load Model Config
    with open('models_config.json', 'r') as f: 
        config = json.load(f)
    
    # 2. Select Model
    print("--- Choose your AI Engine ---")
    keys = list(config.keys())
    for i, model in enumerate(keys): print(f"{i+1}. {model}")
    choice = keys[int(input("Selection: "))-1]
    selected_cfg = config[choice]
    
    # 3. Select Target Library
    target_lib = input("Enter the name of the Python library you want to analyze: ").strip()
    if not target_lib:
        print("\n❌ Error: You must specify a library name to proceed.")
        sys.exit(1)
    
    # Save selection to config
    selected_cfg['target_lib'] = target_lib
    
    # 4. Install & Download
    subprocess.run(selected_cfg['install'], shell=True)
    if "download" in selected_cfg and not os.path.exists(selected_cfg["model_file"]):
        print(f"📥 Downloading {selected_cfg['model_file']}...")
        subprocess.run(selected_cfg["download"], shell=True)
        
    # 5. Save State (Shared by all scripts)
    with open("engine_state.json", "w") as f: 
        json.dump(selected_cfg, f)
    
    print(f"✅ Environment Ready for '{target_lib}' using '{choice}'.")

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
    pipeline = ["extractor.py", "processor.py", "refactor_and_validate.py", "generate_analytics_report.py"]
    
    for step in pipeline:
        if os.path.exists(step):
            if not run_step_with_healing(step):
                print(f"🚨 Pipeline halted at {step}")
                break
        else:
            print(f"❌ File {step} missing!")
