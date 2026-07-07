import json
import time
import logging
from src.engine import refactor_code_with_ollama

logger = logging.getLogger(__name__)

def refactor_and_validate(name, code):
    """Refactors code with a self-healing validation loop."""
    refactored_data = refactor_code_with_ollama(name, code)
    
    if refactored_data is None:
        logger.warning(f"Engine failed for {name}, skipping.")
        return code, "Engine failed"

    new_code = refactored_data.get("refactored_code", code)
    
    # Self-Healing: Check if the AI returned valid Python syntax
    try:
        compile(new_code, '<string>', 'exec')
        return new_code, "verified"
    except SyntaxError as e:
        logger.warning(f"Syntax error in {name}. Attempting fix...")
        fix_prompt = f"The following code has a syntax error: {str(e)}. Fix it:\n{new_code}"
        fix_data = refactor_code_with_ollama(name, fix_prompt)
        
        if fix_data:
            return fix_data.get("refactored_code", new_code), "fixed"
        return new_code, "unfixed_error"

def process_dataset(functions_list, output_file):
    """Processes functions and saves them incrementally."""
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
