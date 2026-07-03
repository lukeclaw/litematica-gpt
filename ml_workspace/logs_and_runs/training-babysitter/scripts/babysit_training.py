import sys
import time
import subprocess

def run_ssh(ip, port, key, command):
    ssh_cmd = f"ssh -o StrictHostKeyChecking=no -i {key} -p {port} ubuntu@{ip} \"{command}\""
    try:
        return subprocess.check_output(ssh_cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.output.decode('utf-8')}"

def babysit(name, ip, port, key, log_file, script_file):
    print(f"[{name}] Starting babysitter...")
    
    while True:
        # 1. Check if training is running
        ps_check = run_ssh(ip, port, key, f"ps aux | grep {script_file} | grep -v grep")
        
        if not ps_check or "ERROR" in ps_check:
            print(f"[{name}] ⚠️  Training NOT detected. Checking setup logs...")
            last_log = run_ssh(ip, port, key, f"tail -n 10 {log_file}")
            
            # AUTO-FIX: Filename mismatch
            if "can't open file" in last_log and "train_unsloth_god.py" in last_log:
                print(f"[{name}] 🔧 Auto-fixing filename mismatch...")
                run_ssh(ip, port, key, f"sed -i 's/train_unsloth_god.py/{script_file}/g' setup.sh && nohup bash setup.sh > {log_file} 2>&1 &")
            else:
                print(f"[{name}] Current Log: {last_log}")
        else:
            # 2. Training is active, get metrics
            print(f"[{name}] ✅ Training is ACTIVE. Polling metrics...")
            metrics = run_ssh(ip, port, key, f"tail -n 20 {log_file}")
            print(f"[{name}] Metrics:\n{metrics}")
            
        print(f"[{name}] Sleeping for 2 minutes...")
        time.sleep(120)

if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("Usage: python3 babysit.py <name> <ip> <port> <key> <log_file> <script_file>")
        sys.exit(1)
        
    babysit(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
