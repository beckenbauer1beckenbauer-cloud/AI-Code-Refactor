import json
import time
import re
from engine import refactor_code

def sanitize_code_string(code_data, fallback_code):
    """
    Ensures that the code returned from the model is strictly a clean string.
    Removes markdown backticks (```python) and prevents TypeErrors in compile().
    """
    if not isinstance(code_data, str):
        if isinstance(code_data, dict):
            code_data = code_data.get("refactored_code", fallback_code)
        else:
            code_data = str(code_data) if code_data else fallback_code

    # Strip markdown block formatting if present
    code_data = re.sub(r"^```python\s*", "", code_data, flags=re.MULTILINE)
    code_data = re.sub(r"^```\s*", "", code_data, flags=re.MULTILINE)
    return code_data.strip()

def refactor_and_validate(name, code, model_name):
    """
    Refactors a single function, validates syntax with compile(),
    and triggers a self-healing retry if an error occurs.
    """
    # 1. Attempt initial refactoring
    refactored_data = refactor_code(name, code, model_name=model_name)

    if not refactored_data or not isinstance(refactored_data, dict):
        print(f"⚠️ Engine failed for function '{name}', skipping refactoring.")
        return code, "Engine failed"

    # Extract and clean code string
    new_code = sanitize_code_string(refactored_data.get("refactored_code", code), fallback_code=code)

    # 2. Syntax Validation & Self-Healing Loop
    try:
        # Check if the code compiles cleanly
        compile(new_code, '<string>', 'exec')
        return new_code, "verified"
    except (SyntaxError, TypeError) as e:
        print(f"⚠️ Syntax/Type Error detected in '{name}'. Initiating AI Self-Healing loop...")
        
        # Build self-healing repair prompt
        fix_prompt = (
            f"The following refactored Python function has a syntax error: {str(e)}.\n"
            f"Fix the error and return ONLY valid Python code inside the JSON key 'refactored_code':\n\n{new_code}"
        )

        # 3. Retry model call to fix the syntax error
        fix_data = refactor_code(name, fix_prompt, model_name=model_name)
        if fix_data and isinstance(fix_data, dict):
            fixed_code = sanitize_code_string(fix_data.get("refactored_code", new_code), fallback_code=new_code)
            try:
                compile(fixed_code, '<string>', 'exec')
                print(f"✅ Self-healing succeeded for '{name}'.")
                return fixed_code, "fixed"
            except Exception:
                print(f"❌ Self-healing attempt failed for '{name}'. Using original code as fallback.")
                return code, "unfixed_error"
                
        return code, "unfixed_error"

def run_self_healing_pipeline(functions_list, model_name, output_file="final_dataset_validated.json"):
    """
    Loops through all extracted functions, refactors, validates syntax,
    and writes out the validated dataset without losing original_code keys.
    """
    validated_dataset = []

    for name, code in functions_list:
        print(f"⚙️ Processing: {name}...")

        final_code, status = refactor_and_validate(name, code, model_name=model_name)

        # Save both original and refactored versions to ensure plotting works
        validated_dataset.append({
            "function_name": name,
            "original_code": code,
            "refactored_code": final_code,
            "status": status
        })

        # Save incrementally after each function
        with open(output_file, "w") as f:
            json.dump(validated_dataset, f, indent=4)

        time.sleep(1)

    print(f"✅ Pipeline finished. Validated dataset saved to '{output_file}'.")
