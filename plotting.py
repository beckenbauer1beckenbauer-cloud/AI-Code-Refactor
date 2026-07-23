import json
import os
import matplotlib.pyplot as plt

def generate_line_count_plot(dataset_file="final_dataset_validated.json", output_plot="line_count_comparison.png"):
    """
    Generates Chart 1: Line count comparison (Original vs Refactored).
    """
    if not os.path.exists(dataset_file):
        print(f"⚠️ Cannot generate line count plot: '{dataset_file}' missing.")
        return

    with open(dataset_file, "r") as f:
        data = json.load(f)

    if not data:
        print("⚠️ Line count plotting skipped: Dataset is empty.")
        return

    names = []
    orig_lines = []
    refact_lines = []

    for item in data:
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
    plt.title("Code Line Count Comparison")
    plt.legend()
    plt.tight_layout()

    plt.savefig(output_plot)
    plt.close()
    print(f"📊 Chart 1 saved: '{output_plot}'.")


def generate_status_plot(dataset_file="final_dataset_validated.json", output_plot="refactoring_status_distribution.png"):
    """
    Generates Chart 2: Status distribution (Verified vs Fixed vs Failed).
    """
    if not os.path.exists(dataset_file):
        print(f"⚠️ Cannot generate status plot: '{dataset_file}' missing.")
        return

    with open(dataset_file, "r") as f:
        data = json.load(f)

    if not data:
        return

    statuses = [item.get("status", "unknown") for item in data]
    verified = statuses.count("verified")
    fixed = statuses.count("fixed")
    failed = len(statuses) - verified - fixed

    labels = ["Verified (1st Try)", "Self-Healed (Fixed)", "Failed/Skipped"]
    counts = [verified, fixed, failed]

    plt.figure(figsize=(7, 5))
    colors = ["#2ecc71", "#3498db", "#e74c3c"]
    plt.bar(labels, counts, color=colors)
    plt.ylabel("Count")
    plt.title("Refactoring Status Distribution")
    plt.tight_layout()

    plt.savefig(output_plot)
    plt.close()
    print(f"📊 Chart 2 saved: '{output_plot}'.")


def generate_plot(dataset_file="final_dataset_validated.json"):
    """
    Helper function to trigger both plots at once.
    """
    generate_line_count_plot(dataset_file)
    generate_status_plot(dataset_file)
