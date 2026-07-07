import json
import time
import logging
from src.engine import refactor_code_with_ollama

logger = logging.getLogger(__name__)

def refactor_and_validate(name, code):
    """Refactors code with a self-healing validation loop."""
    refactored_data = refactor_code_with_ollama(name, code)
    
    # 1. FIX: Check if the returned data is actually a dictionary/valid
    if not isinstance(refactored_data, dict):
        logger.warning(f"Engine failed to return valid JSON for {name}")
        return code, "Engine failed"

    # 2. FIX: Safely get the code string, defaulting to original if missing
    new_code = refactored_data.get("refactored_code")
    if not isinstance(new_code, str):
        logger.warning(f"Engine returned invalid code format for {name}")
        return code, "Format error"
    
    # 3. Self-Healing: Check if the AI returned valid Python syntax
    try:
        compile(new_code, '<string>', 'exec')
        return new_code, "verified"
    except (SyntaxError, TypeError) as e:
        logger.warning(f"Syntax error in {name}. Attempting fix...")
        fix_prompt = f"The following code has a syntax error: {str(e)}. Fix it:\n{new_code}"
        
        fix_data = refactor_code_with_ollama(name, fix_prompt)
        
        if isinstance(fix_data, dict) and isinstance(fix_data.get("refactored_code"), str):
            return fix_data.get("refactored_code"), "fixed"

        def process_dataset(functions_list, output_file):
    """Processes a list of functions and saves them to a file."""
    validated_dataset = []
    
    for name, code in functions_list:
        logger.info(f"Processing: {name}...")
        final_code, status = refactor_and_validate(name, code)
        
        validated_dataset.append({
            "function": name,
            "refactored_code": final_code,
            "status": status
        })
        
        # Incremental save
        with open(output_file, "w") as f:
            json.dump(validated_dataset, f, indent=4)
        
        time.sleep(2) # Prevent server overload
            
    return validated_dataset
        
        return new_code, "unfixed_error"
