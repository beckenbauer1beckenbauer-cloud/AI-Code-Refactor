import json
import matplotlib.pyplot as plt
import requests
import numpy as np

# --- Helper Function: Call Ollama for Report ---
def generate_analytics_report(metrics_old, metrics_new):
    """
    Sends metrics to Ollama to generate a comparative professional report.
    """
    url = "http://localhost:11434/api/generate"

    prompt = f"""
    You are a Senior Python Software Quality Analyst.
    Analyze the following metrics comparing a Legacy Python Codebase to its Refactored version (using AI).
    Focus on improvements in documentation (Docstrings) and type hinting.

    Metrics (Average values per function):
    - Legacy Average Docstring Length: {metrics_old['avg_docstring_len']} chars
    - Refactored Average Docstring Length: {metrics_new['avg_docstring_len']} chars (Improvement: {metrics_new['avg_docstring_len'] - metrics_old['avg_docstring_len']} chars)
    - Legacy Functions with Type Hints: {metrics_old['type_hint_pct']}%
    - Refactored Functions with Type Hints: {metrics_new['type_hint_pct']}% (Improvement: +{metrics_new['type_hint_pct'] - metrics_old['type_hint_pct']}%)

    Generate a brief, well-organized professional report (bullet points) summarizing the quality improvements.
    """

    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()['response']
        else:
            return "Error generating report from Ollama."
    except Exception as e:
        return f"Analytics report generation failed: {e}"

# --- Main Analytics Logic ---
def run_comparative_analytics(old_file="final_dataset.json", new_file="final_dataset_validated.json"):
    print("📊 Starting Comparative Analytics...")

    try:
        # Load both datasets
        with open(old_file, "r") as f:
            old_data = json.load(f)
        with open(new_file, "r") as f:
            new_data = json.load(f)

        # Function to calculate metrics
        def calculate_metrics(dataset):
            total_funcs = len(dataset)
            if total_funcs == 0:
                return {'avg_docstring_len': 0, 'type_hint_pct': 0}

            total_doc_len = 0
            funcs_with_hints = 0

            for entry in dataset:
                # Assuming docstring is in 'explanation' or part of 'refactored_code'
                # We'll check 'explanation' length for simplicity as a proxy for doc quality
                docstring = entry.get('explanation', '')
                total_doc_len += len(docstring)

                # Check for type hint markers (e.g., '->', ': ') in refactored code
                # Ensure 'code' is always a string
                refactored_code_content = entry.get('refactored_code')
                if not isinstance(refactored_code_content, str):
                    code = ''
                else:
                    code = refactored_code_content

                if '->' in code or (':' in code and '=' not in code and 'def' in code):
                    funcs_with_hints += 1

            return {
                'avg_docstring_len': round(total_doc_len / total_funcs, 2),
                'type_hint_pct': round((funcs_with_hints / total_funcs) * 100, 2)
            }

        metrics_old = calculate_metrics(old_data)
        metrics_new = calculate_metrics(new_data)

        # --- Visualization (Plotting) ---
        labels = ['Avg Docstring Length (Chars)', 'Functions with Type Hints (%)']
        legacy_vals = [metrics_old['avg_docstring_len'], metrics_old['type_hint_pct']]
        refactored_vals = [metrics_new['avg_docstring_len'], metrics_new['type_hint_pct']]

        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots(figsize=(10, 6))
        rects1 = ax.bar(x - width/2, legacy_vals, width, label='Legacy Code', color='gray')
        rects2 = ax.bar(x + width/2, refactored_vals, width, label='Refactored (Self-Healed)', color='green')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Scores')
        ax.set_title('Quality Improvement: Legacy vs Self-Healed Refactoring')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylim(0, max(max(legacy_vals), max(refactored_vals)) * 1.2) # Add headroom
        ax.legend()

        def autolabel(rects):
            """Attach a text label above each bar in *rects*, displaying its height."""
            for rect in rects:
                height = rect.get_height()
                ax.annotate('{}'.format(height),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')

        autolabel(rects1)
        autolabel(rects2)

        fig.tight_layout()
        plt.savefig("comparative_analysis.png")
        plt.show()
        print("✅ Comparative plot generated: comparative_analysis.png")

        # --- AI Reporting ---
        print("\n🤖 Generating AI Quality Report...")
        report = generate_analytics_report(metrics_old, metrics_new)
        print("\n" + "="*40)
        print("🐍 SENIOR ANALYST REPORT 🐍")
        print("="*40)
        print(report)
        print("="*40)

    except FileNotFoundError as e:
        print(f"⚠️ Error: One or both files not found. Please ensure both JSON files exist. {e}")

# Run the comparative analytics
run_comparative_analytics()
