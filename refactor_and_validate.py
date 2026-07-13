import json
import sys
import os

# Import the refactor engine
from engine import refactor_code_with_engine

def refactor_and_validate(name, code):
    """
    Refactors code and performs a syntax check. 
    If invalid, attempts a one-time self-healing fix.
    If healing fails, falls back to the original code.
    """
    print(f"⚙️ Refactoring: {name}...")
    refactored_data = refactor_code_with_engine(name, code)

    # 1. Handle Engine Failure
    if not refactored_data or not isinstance(refactored_data.get("refactored_code"), str):
        print(f"⚠️ Engine failed for {name}. Keeping original code.")
        return code, "original"

    new_code = refactored_data["refactored_code"]

    # 2. Validation Loop
    try:
        compile(new_code, '<string>', 'exec')
        return new_code, "verified"
    except SyntaxError as e:
        print(f"⚠️ Syntax Error in {name}. Triggering SELF-HEALING...")
        
        # Self-Healing Prompt
        fix_prompt = f"The following code has a syntax error: {str(e)}. Provide ONLY the corrected code in the same JSON structure:\n{new_code}"
        
        fix_data = refactor_code_with_engine(name, fix_prompt)
        
        if fix_data and isinstance(fix_data.get("refactored_code"), str):
            fixed_code = fix_data["refactored_code"]
            try:
                compile(fixed_code, '<string>', 'exec')
                print(f"✅ Self-healing successful for {name}.")
                return fixed_code, "fixed"
            except SyntaxError:
                print(f"❌ Self-healing failed for {name}. Falling back to original.")
                return code, "original"
        
        return code, "original"

def run_self_healing_pipeline(functions_list, output_file="final_dataset_validated.json"):
    validated_dataset = []
    for entry in functions_list:
        # Handle cases where functions_list might be a list of tuples or list of dicts
        name = entry[0] if isinstance(entry, (tuple, list)) else entry['function']
        code = entry[1] if isinstance(entry, (tuple, list)) else entry['refactored_code']
        
        final_code, status = refactor_and_validate(name, code)
        validated_dataset.append({"function": name, "refactored_code": final_code, "status": status})
        
        # Save incrementally
        with open(output_file, "w") as f: 
            json.dump(validated_dataset, f, indent=4)
            
    print(f"\n✅ Pipeline finished. Saved to {output_file}")

if __name__ == "__main__":
    # Ensure data exists from the previous step
    if os.path.exists("final_dataset.json"):
        with open("final_dataset.json", "r") as f:
            functions_to_refactor = json.load(f)
        run_self_healing_pipeline(functions_to_refactor)
    else:
        print("❌ Error: 'final_dataset.json' not found. Please run processor.py first.")
