import time
import os
import subprocess

# Instance Config (from previous tnr status)
IP = "64.247.206.198"
PLANNER_PORT = 32394
COMPILER_PORT = 32417
KEY_0 = "tnr_key_0"
KEY_1 = "tnr_key_1"

def get_status(port, key, log_file):
    try:
        cmd = f"ssh -o StrictHostKeyChecking=no -i {key} -p {port} ubuntu@{IP} 'tail -n 1 {log_file}'"
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8').strip()
        return result
    except:
        return "Waiting for connection..."

def monitor():
    print("\n" + "="*80)
    print("GOD MODE MISSION CONTROL - PARALLEL TRAINING")
    print("="*80)
    
    while True:
        planner_log = get_status(PLANNER_PORT, KEY_0, "setup_planner.log")
        compiler_log = get_status(COMPILER_PORT, KEY_1, "setup_compiler.log")
        
        os.system('clear')
        print("="*80)
        print(f"TIME: {time.strftime('%H:%M:%S')}")
        print("-"*80)
        print(f"PLANNER (Instance 0): {planner_log[:70]}...")
        print(f"COMPILER (Instance 1): {compiler_log[:70]}...")
        print("-"*80)
        print("Polling every 20 seconds... Press Ctrl+C to stop.")
        print("="*80)
        
        time.sleep(20)

if __name__ == "__main__":
    monitor()
