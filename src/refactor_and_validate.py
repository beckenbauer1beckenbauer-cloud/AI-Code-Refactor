import json
import time

def refactor_and_validate(name, code):
    """
    Refactors code with bulletproof error handling.
    """
    # 1. Attempt Refactoring
    refactored_data = refactor_code_with_ollama(name, code)
    
    # If the engine failed to return data, treat it as an empty refactoring
    if refactored_data is None:
        print(f"⚠️ Engine failed for {name}, skipping refactoring.")
        return code, "Engine failed"

    new_code = refactored_data.get("refactored_code", code)
    
    # 2. Validate (Self-Healing Loop)
    try:
        compile(new_code, '<string>', 'exec')
        return new_code, "verified"
    except SyntaxError as e:
        print(f"⚠️ Syntax Error in {name}. Attempting fix...")
        fix_prompt = f"The following code has a syntax error: {str(e)}. Fix it:\n{new_code}"
        
        fix_data = refactor_code_with_ollama(name, fix_prompt)
        if fix_data:
            return fix_data.get("refactored_code", new_code), "fixed"
        return new_code, "unfixed_error"

def run_self_healing_pipeline(functions_list, output_file="final_dataset_validated.json"):
    validated_dataset = []
    
    for name, code in functions_list:
        print(f"⚙️ Processing: {name}...")
        
        # Use our robust refactor/validate function
        final_code, status = refactor_and_validate(name, code)
        
        validated_dataset.append({
            "function": name,
            "refactored_code": final_code,
            "status": status
        })
        
        # Incremental save
        with open(output_file, "w") as f:
            json.dump(validated_dataset, f, indent=4)
        
        # Small delay to prevent server overload
        time.sleep(2) 
            
    print(f"✅ Pipeline finished. Dataset saved to {output_file}")

# Run the pipeline
run_self_healing_pipeline(functions_to_refactor)
