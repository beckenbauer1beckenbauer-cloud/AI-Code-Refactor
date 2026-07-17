import json
import matplotlib.pyplot as plt
import numpy as np
from engine import refactor_code

def generate_analytics_report(metrics_old, metrics_new, model_name):
    """
    Sends metrics to the selected LLM to generate a comparative professional report.
    """
    prompt = f"""
    You are a Senior Python Software Quality Analyst.
    Analyze the following metrics comparing a Legacy Python Codebase to its Refactored version.
    
    Metrics:
    - Legacy Avg Docstring Length: {metrics_old['avg_docstring_len']}
    - Refactored Avg Docstring Length: {metrics_new['avg_docstring_len']}
    - Legacy Type Hint Coverage: {metrics_old['type_hint_pct']}%
    - Refactored Type Hint Coverage: {metrics_new['type_hint_pct']}%

    Generate a brief, professional summary of quality improvements.
    """

    # Use the shared engine instead of a hardcoded URL
    result = refactor_code("AnalyticsReport", prompt, model_name=model_name)
    
    if result:
        return result.get('refactored_code', "Report generation failed.")
    return "Error generating report from the engine."

def run_comparative_analytics(model_name, old_file="final_dataset.json", new_file="final_dataset_validated.json"):
    print("📊 Starting Comparative Analytics...")

    try:
        with open(old_file, "r") as f:
            old_data = json.load(f)
        with open(new_file, "r") as f:
            new_data = json.load(f)

        def calculate_metrics(dataset):
            total_funcs = len(dataset)
            if total_funcs == 0:
                return {'avg_docstring_len': 0, 'type_hint_pct': 0}

            total_doc_len = 0
            funcs_with_hints = 0
            for entry in dataset:
                docstring = entry.get('explanation', '')
                total_doc_len += len(docstring)
                code = entry.get('refactored_code', '')
                if '->' in code or (':' in code and '=' not in code and 'def' in code):
                    funcs_with_hints += 1
            return {
                'avg_docstring_len': round(total_doc_len / total_funcs, 2),
                'type_hint_pct': round((funcs_with_hints / total_funcs) * 100, 2)
            }

        metrics_old = calculate_metrics(old_data)
        metrics_new = calculate_metrics(new_data)

        # Plotting logic remains here (omitted for brevity, keep your original plot logic)
        # ... [Plotting code same as before] ...

        print("\n🤖 Generating AI Quality Report...")
        report = generate_analytics_report(metrics_old, metrics_new, model_name)
        print("\n" + "="*40 + "\n🐍 SENIOR ANALYST REPORT 🐍\n" + "="*40)
        print(report)

    except FileNotFoundError as e:
        print(f"⚠️ Error: {e}")
