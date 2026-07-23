import json
import os
import matplotlib.pyplot as plt

def generate_plot(dataset_file="final_dataset_validated.json", output_plot="refactoring_metrics.png"):
    """
    Generates line count comparison plot for original vs refactored functions.
    Handles flexible schema keys gracefully.
    """
    if not os.path.exists(dataset_file):
        print(f"⚠️ Cannot generate plot: '{dataset_file}' missing.")
        return

    with open(dataset_file, "r") as f:
        data = json.load(f)

    if not data:
        print("⚠️ Plotting skipped: Dataset is empty.")
        return

    names = []
    orig_lines = []
    refact_lines = []

    for item in data:
        # Flexible key extraction (handles 'function_name' vs 'function')
        name = item.get("function_name") or item.get("function") or "Unknown"
        orig_code = item.get("original_code", "")
        refact_code = item.get("refactored_code", "")

        names.append(name)
        orig_lines.append(len(orig_code.splitlines()))
        refact_lines.append(len(refact_code.splitlines()))

    plt.figure(figsize=(10, 5))
    x = range(len(names))
    plt.bar([i - 0.2 for i in x], orig_lines, width=0.4, label="Original Lines", align="center")
    plt.bar([i + 0.2 for i in x], refact_lines, width=0.4, label="Refactored Lines", align="center")
    
    plt.xticks(x, names, rotation=45, ha="right")
    plt.ylabel("Line Count")
    plt.title("Code Line Count Comparison (Original vs Refactored)")
    plt.legend()
    plt.tight_layout()

    plt.savefig(output_plot)
    plt.close()
    print(f"📊 Visualization graph saved to '{output_plot}'.")
