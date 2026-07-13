import json
import matplotlib.pyplot as plt
import numpy as np
from engine import refactor_code_with_engine

def generate_analytics_report(metrics_old, metrics_new):
    """
    Generates a professional report using the selected engine.
    """
    prompt = f"""
    You are a Senior Python Software Quality Analyst.
    Analyze the following metrics comparing a Legacy Python Codebase to its Refactored version.
    
    Metrics:
    - Legacy Avg Docstring Length: {metrics_old['avg_docstring_len']} chars
    - Refactored Avg Docstring Length: {metrics_new['avg_docstring_len']} chars
    - Legacy Functions with Type Hints: {metrics_old['type_hint_pct']}%
    - Refactored Functions with Type Hints: {metrics_new['type_hint_pct']}%

    Generate a professional summary.
    """
    
    result = refactor_code_with_engine("Analytics_Report", prompt)
    if result and isinstance(result, dict):
        return result.get("explanation", "Report generation failed.")
    return "Error generating report."

def run_comparative_analytics(old_file="final_dataset.json", new_file="final_dataset_validated.json"):
    print("📊 Starting Comparative Analytics...")

    try:
        with open(old_file, "r") as f: old_data = json.load(f)
        with open(new_file, "r") as f: new_data = json.load(f)

        def calculate_metrics(dataset):
            total_funcs = len(dataset)
            if total_funcs == 0: return {'avg_docstring_len': 0, 'type_hint_pct': 0}
            total_doc_len = 0
            funcs_with_hints = 0
            for entry in dataset:
                # Handle dictionary or tuple/list based on your structure
                explanation = entry.get('explanation', '') if isinstance(entry, dict) else ""
                total_doc_len += len(str(explanation))
                code = str(entry.get('refactored_code', ''))
                if '->' in code or (':' in code and '=' not in code and 'def' in code):
                    funcs_with_hints += 1
            return {
                'avg_docstring_len': round(total_doc_len / total_funcs, 2),
                'type_hint_pct': round((funcs_with_hints / total_funcs) * 100, 2)
            }

        metrics_old = calculate_metrics(old_data)
        metrics_new = calculate_metrics(new_data)

        # --- PLOTTING LOGIC ---
        labels = ['Docstring Length', 'Type Hint %']
        legacy = [metrics_old['avg_docstring_len'], metrics_old['type_hint_pct']]
        refactored = [metrics_new['avg_docstring_len'], metrics_new['type_hint_pct']]

        x = np.arange(len(labels))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - width/2, legacy, width, label='Legacy', color='salmon')
        ax.bar(x + width/2, refactored, width, label='Refactored', color='skyblue')

        ax.set_ylabel('Scores')
        ax.set_title('Legacy vs Refactored Codebase Quality')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        plt.savefig('refactoring_analysis.png')
        print("✅ Analysis saved to 'refactoring_analysis.png'.")
        
        print("\n🤖 Generating AI Quality Report...")
        report = generate_analytics_report(metrics_old, metrics_new)
        print("\n" + "="*40 + "\n🐍 SENIOR ANALYST REPORT 🐍\n" + "="*40 + "\n")
        print(report)

    except FileNotFoundError as e:
        print(f"⚠️ Error: Ensure both JSON files exist. {e}")

if __name__ == "__main__":
    run_comparative_analytics()
