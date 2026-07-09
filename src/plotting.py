import json
import matplotlib.pyplot as plt

# 1. Load the dataset we just created
with open("final_dataset.json", "r") as f:
    dataset = json.load(f)

# 2. Extract metrics (length of code in characters)
names = [entry['function'] for entry in dataset]
orig_lengths = [len(entry['original_code']) for entry in dataset]
refactored_lengths = [len(entry['refactored_code'] or '') for entry in dataset] # Handle None values

# 3. Create the plot
plt.figure(figsize=(12, 6))
bar_width = 0.35
index = range(len(names))

plt.bar(index, orig_lengths, bar_width, label='Original Code Length', color='gray')
plt.bar([i + bar_width for i in index], refactored_lengths, bar_width, label='Refactored Code Length', color='blue')

plt.xlabel('Functions')
plt.ylabel('Character Count')
plt.title('Code Expansion Analysis: Original vs Refactored')
plt.xticks([i + bar_width/2 for i in index], names, rotation=45, ha='right')
plt.legend()
plt.tight_layout()

# 4. Save and Show
plt.savefig("refactoring_analysis.png")
plt.show()
