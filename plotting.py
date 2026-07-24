import json
import os
import matplotlib.pyplot as plt

def generate_plot(dataset_file="final_dataset_validated.json", library_name="target"):
    """Generates 2 distinct PNG charts specifically for the target library."""
    if not os.path.exists(dataset_file):
        print(f"⚠️ Dataset '{dataset_file}' not found.")
        return

    with open(dataset_file, "r") as f:
        data = json.load(f)

    if not data:
        return

    # Chart 1: Line Count Comparison
    names, orig_lines, refact_lines = [], [], []
    for item in data:
        name = item.get("function_name", "Unknown")
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
    plt.title(f"Code Line Count Comparison ({library_name})")
    plt.legend()
    plt.tight_layout()
    chart1_path = f"line_count_{library_name}.png"
    plt.savefig(chart1_path)
    plt.close()

    # Chart 2: Status Breakdown
    statuses = [item.get("status", "unknown") for item in data]
    verified = statuses.count("verified")
    fixed = statuses.count("fixed")
    failed = len(statuses) - verified - fixed

    plt.figure(figsize=(7, 5))
    colors = ["#2ecc71", "#3498db", "#e74c3c"]
    plt.bar(["Verified", "Self-Healed", "Failed"], [verified, fixed, failed], color=colors)
    plt.ylabel("Count")
    plt.title(f"Refactoring Status Distribution ({library_name})")
    plt.tight_layout()
    chart2_path = f"status_distribution_{library_name}.png"
    plt.savefig(chart2_path)
    plt.close()

    print(f"📊 Chart 1 saved: '{chart1_path}'")
    print(f"📊 Chart 2 saved: '{chart2_path}'")
