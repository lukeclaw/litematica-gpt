import subprocess
import re
import time
import sys
from datetime import datetime, timedelta

def run_training_with_eta(total_iters=6000):
    # Use sys.executable to ensure we use the same Python/venv as the caller
    cmd = [
        sys.executable, "-m", "mlx_lm", "lora",
        "--model", "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
        "--train",
        "--data", "mlx_compiler_data_v5",
        "--config", "lora_config.yaml",
        "--adapter-path", "specialized_skills/dsl_compiler_llama8b",
        "--iters", str(total_iters)
    ]

    print(f"--- Starting Training with Live ETA (Target: {total_iters} iters) ---")
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    for line in process.stdout:
        print(line, end="")
        
        # Look for the Iteration and Speed in the log
        match = re.search(r"Iter (\d+):.*It/sec ([\d.]+)", line)
        if match:
            current_iter = int(match.group(1))
            it_sec = float(match.group(2))
            
            if it_sec > 0:
                remaining_iters = total_iters - current_iter
                seconds_left = remaining_iters / it_sec
                eta_time = datetime.now() + timedelta(seconds=seconds_left)
                print(f"   >>> [ETA] {eta_time.strftime('%I:%M %p')} ({int(seconds_left // 60)}m remaining)")

    process.wait()
    print("--- Training Finished ---")

if __name__ == "__main__":
    run_training_with_eta(6000)
