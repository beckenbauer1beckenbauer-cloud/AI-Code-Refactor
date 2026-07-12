import json
import sys

# Load the shared engine state
with open("engine_state.json", "r") as f:
    engine_state = json.load(f)

# Use the unified refactor function we built in Code 2
def refactor_and_validate(name, code):
    """
    Refactors code and performs a syntax check. 
    If invalid, attempts a one-time self-healing fix using the selected engine.
    """
    # 1. Attempt Refactoring
    print(f"⚙️ Refactoring: {name}...")
    refactored_data = refactor_code_with_engine(name, code)

    if not refactored_data or not isinstance(refactored_data.get("refactored_code"), str):
        print(f"⚠️ Engine failed to return valid code for {name}.")
        return code, "Engine failed"

    new_code = refactored_data["refactored_code"]

    # 2. Validation Loop
    try:
        compile(new_code, '<string>', 'exec')
        return new_code, "verified"
    except SyntaxError as e:
        print(f"⚠️ Syntax Error in {name}. Triggering SELF-HEALING...")
        
        # Self-Healing Prompt
        fix_prompt = f"The following code has a syntax error: {str(e)}. Provide the corrected code in JSON format:\n{new_code}"
        
        # RE-TRY: Ask the engine to fix its own mistake
        fix_data = refactor_code_with_engine(name, fix_prompt)
        
        if fix_data and isinstance(fix_data.get("refactored_code"), str):
            fixed_code = fix_data["refactored_code"]
            try:
                compile(fixed_code, '<string>', 'exec')
                print(f"✅ Self-healing successful for {name}.")
                return fixed_code, "fixed"
            except:
                print(f"❌ Self-healing failed for {name}.")
                return new_code, "unfixed_error"
        
        return new_code, "unfixed_error"

# --- Main loop ---
def run_self_healing_pipeline(functions_list, output_file="final_dataset_validated.json"):
    validated_dataset = []
    for name, code in functions_list:
        final_code, status = refactor_and_validate(name, code)
        validated_dataset.append({"function": name, "refactored_code": final_code, "status": status})
        with open(output_file, "w") as f: json.dump(validated_dataset, f, indent=4)
    print(f"✅ Pipeline finished. Saved to {output_file}")

if __name__ == "__main__":
    run_self_healing_pipeline(functions_to_refactor)
