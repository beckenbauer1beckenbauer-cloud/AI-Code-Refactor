def generate_analytics_report(metrics_old, metrics_new):
    """
    Generates a professional report using the selected engine.
    """
    prompt = f"""
    You are a Senior Python Software Quality Analyst.
    Analyze the following metrics comparing a Legacy Python Codebase to its Refactored version.
    Focus on improvements in documentation (Docstrings) and type hinting.

    Metrics (Average values per function):
    - Legacy Average Docstring Length: {metrics_old['avg_docstring_len']} chars
    - Refactored Average Docstring Length: {metrics_new['avg_docstring_len']} chars
    - Legacy Functions with Type Hints: {metrics_old['type_hint_pct']}%
    - Refactored Functions with Type Hints: {metrics_new['type_hint_pct']}%

    Generate a brief, well-organized professional report (bullet points) summarizing the quality improvements.
    """
    
    # We call our unified engine wrapper
    result = refactor_code_with_engine("Analytics_Report", prompt)
    
    if result and isinstance(result, dict):
        return result.get("explanation", "Report generation failed to return content.")
    return "Error generating report."

def run_comparative_analytics(old_file="final_dataset.json", new_file="final_dataset_validated.json"):
    print("📊 Starting Comparative Analytics...")

    try:
        with open(old_file, "r") as f:
            old_data = json.load(f)
        with open(new_file, "r") as f:
            new_data = json.load(f)

        def calculate_metrics(dataset):
            total_funcs = len(dataset)
            if total_funcs == 0: return {'avg_docstring_len': 0, 'type_hint_pct': 0}
            total_doc_len = 0
            funcs_with_hints = 0
            for entry in dataset:
                total_doc_len += len(str(entry.get('explanation', '')))
                code = str(entry.get('refactored_code', ''))
                if '->' in code or (':' in code and '=' not in code and 'def' in code):
                    funcs_with_hints += 1
            return {
                'avg_docstring_len': round(total_doc_len / total_funcs, 2),
                'type_hint_pct': round((funcs_with_hints / total_funcs) * 100, 2)
            }

        metrics_old = calculate_metrics(old_data)
        metrics_new = calculate_metrics(new_data)

        # Plotting code remains the same as your provided script...
        # (Assuming plt and np are available from your previous script contexts)
        
        print("\n🤖 Generating AI Quality Report...")
        report = generate_analytics_report(metrics_old, metrics_new)
        print("\n" + "="*40 + "\n🐍 SENIOR ANALYST REPORT 🐍\n" + "="*40 + "\n")
        print(report)

    except FileNotFoundError as e:
        print(f"⚠️ Error: Ensure both JSON files exist. {e}")

# Run the comparative analytics
run_comparative_analytics()
