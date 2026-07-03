import re
import sys
import json

def parse_hf_log(log_text):
    """
    Parses HuggingFace/Unsloth log output for metrics.
    Example line: {'loss': '0.5814', 'grad_norm': '0.5218', 'learning_rate': '9.274e-05', 'epoch': '1.129'}
    """
    metrics = []
    # Find JSON-like dicts in the text
    matches = re.findall(r"\{'loss': '[\d.]+',.*'epoch': '[\d.]+'\}", log_text)
    for match in matches:
        # Convert single quotes to double quotes for JSON parsing
        try:
            valid_json = match.replace("'", '"')
            metrics.append(json.loads(valid_json))
        except:
            continue
    
    # Find progress bar info
    # Example: 10%|█ | 600/6000 [38:17<5:38:12, 3.76s/it]
    prog_match = re.search(r"(\d+)%\|.*\| (\d+)/(\d+) \[(.*?)<(\d+:\d+:\d+), (.*?)s/it\]", log_text)
    
    progress = {}
    if prog_match:
        progress = {
            "percent": prog_match.group(1),
            "step": prog_match.group(2),
            "total_steps": prog_match.group(3),
            "elapsed": prog_match.group(4),
            "eta": prog_match.group(5),
            "speed": prog_match.group(6)
        }
        
    return metrics, progress

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse_logs.py <log_file_path>")
        sys.exit(1)
        
    with open(sys.argv[1], 'r') as f:
        content = f.read()
        
    metrics, progress = parse_hf_log(content)
    
    if progress:
        print(f"--- PROGRESS ---")
        print(f"Step: {progress['step']}/{progress['total_steps']} ({progress['percent']}%)")
        print(f"Speed: {progress['speed']}s/it | ETA: {progress['eta']}")
        
    if metrics:
        latest = metrics[-1]
        print(f"\n--- LATEST METRICS ---")
        print(f"Loss: {latest['loss']}")
        print(f"Epoch: {latest['epoch']}")
        print(f"LR: {latest['learning_rate']}")
    else:
        print("\nNo metric logs found yet.")
