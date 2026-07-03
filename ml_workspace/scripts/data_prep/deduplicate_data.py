import json
import os

def deduplicate_jsonl(file_path):
    if not os.path.exists(file_path):
        return
    
    unique_samples = {}
    total_count = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            total_count += 1
            try:
                data = json.loads(line)
                # Use the user prompt as the key (assuming unique buildings)
                # messages[1] is the user prompt
                key = data["messages"][1]["content"]
                unique_samples[key] = line
            except: continue
            
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in unique_samples.values():
            f.write(line)
            
    print(f"Deduplication complete.")
    print(f"Original lines: {total_count}")
    print(f"Unique lines: {len(unique_samples)}")
    print(f"Removed: {total_count - len(unique_samples)}")

if __name__ == "__main__":
    deduplicate_jsonl("dataset/synthetic_train_rationalized.jsonl")
