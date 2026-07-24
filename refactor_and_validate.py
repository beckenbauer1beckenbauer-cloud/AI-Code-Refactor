import ast
import json
import time
from engine import refactor_code

def validate_python_syntax(code_str):
    """Checks if the refactored code compiles into valid Python AST."""
    try:
        ast.parse(code_str)
        return True, ""
    except SyntaxError as e:
        return False, str(e)

def run_self_healing_pipeline(functions_list, model_name="qwen2.5:7b", output_file="final_dataset_validated.json"):
    """Refactor functions and apply AI self-healing repairs on syntax errors."""
    print(f"\n🚀 Refactoring {len(functions_list)} functions using {model_name}...")
    validated_dataset = []

    for name, code in functions_list:
        print(f"⚙️ Processing: {name}...")
        result = refactor_code(name, code, model_name=model_name)

        if not result:
            print(f"⚠️ Engine failed for '{name}', skipping.")
            continue

        refactored = result.get("refactored_code", code)
        explanation = result.get("explanation", "")

        is_valid, err_msg = validate_python_syntax(refactored)
        status = "verified"

        if not is_valid:
            print(f"⚠️ Syntax Error in '{name}': {err_msg}. Triggering AI self-healing...")
            repair_prompt = f"Fix this Python syntax error:\n{err_msg}\n\nCode:\n{refactored}"
            repaired_res = refactor_code(name, repair_prompt, model_name=model_name)
            
            if repaired_res and "refactored_code" in repaired_res:
                refactored = repaired_res["refactored_code"]
                re_valid, _ = validate_python_syntax(refactored)
                status = "fixed" if re_valid else "failed_repair"
            else:
                status = "failed_repair"

        validated_dataset.append({
            "function_name": name,
            "original_code": code,
            "refactored_code": refactored,
            "explanation": explanation,
            "status": status
        })

        time.sleep(0.5)

    with open(output_file, "w") as f:
        json.dump(validated_dataset, f, indent=4)

    print(f"✅ Validated dataset saved to '{output_file}'.")
    return validated_dataset
