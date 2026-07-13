import json
import sys

# Assume refactor_code_with_engine is imported from engine.py
# If not, add: from engine import refactor_code_with_engine

def refactor_and_validate(name, code):
    """
    Refactors code with a self-healing loop. 
    If all attempts fail, falls back to original code to ensure pipeline continuity.
    """
    # 1. Attempt Refactoring
    print(f"⚙️ Refactoring: {name}...")
    refactored_data = refactor_code_with_engine(name, code)

    # Validate output structure
    if not refactored_data or not isinstance(refactored_data.get("refactored_code"), str):
        print(f"⚠️ Engine failed. Falling back to original code for {name}.")
        return code, "original"

    new_code = refactored_data["refactored_code"]

    # 2. Syntax Validation
    try:
        compile(new_code, '<string>', 'exec')
        return new_code, "verified"
    except SyntaxError as e:
        print(f"⚠️ Syntax Error in {name}. Triggering SELF-HEALING...")
        
        # Self-Healing Prompt
        fix_prompt = f"The following code has a syntax error: {str(e)}. Provide ONLY the corrected code in JSON format:\n{new_code}"
        
        # RE-TRY: Ask the engine to fix its own mistake
        fix_data = refactor_code_with_engine(name, fix_prompt)
        
        if fix_data and isinstance(fix_data.get("refactored_code"), str):
            fixed_code = fix_data["refactored_code"]
            try:
                compile(fixed_code, '<string>', 'exec')
                print(f"✅ Self-healing successful for {name}.")
                return fixed_code, "fixed"
            except:
                print(f"❌ Self-healing failed for {name}. Using original.")
                return code, "original" # FALLBACK TO ORIGINAL
        
        return code, "original" # FALLBACK TO ORIGINAL

# --- Main loop ---
def run_self_healing_pipeline(functions_list, output_file="final_dataset_validated.json"):
    validated_dataset = []
    for name, code in functions_list:
        final_code, status = refactor_and_validate(name, code)
        validated_dataset.append({"function": name, "refactored_code": final_code, "status": status})
        
        # Save incrementally so you don't lose progress if it crashes later
        with open(output_file, "w") as f: 
            json.dump(validated_dataset, f, indent=4)
            
    print(f"\n✅ Pipeline finished. Dataset saved to {output_file}")

if __name__ == "__main__":
    # Ensure functions_to_refactor is available
    if 'functions_to_refactor' in globals():
        run_self_healing_pipeline(functions_to_refactor)
    else:
        print("❌ No 'functions_to_refactor' found. Did you run the previous steps?")
