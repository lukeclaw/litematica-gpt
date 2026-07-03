---
name: training-babysitter
description: Automates the monitoring and troubleshooting of remote training jobs. Dispatches background agents to poll logs every 120 seconds and auto-fix known environment issues. Use when parallel training jobs are active.
---

# Training Babysitter

This skill provides an autonomous monitoring system for active training jobs on Thunder Compute.

## Features
- **Auto-Fixing**: Detects and fixes common setup errors (like filename mismatches).
- **Metric Polling**: Retrieves latest loss, steps, and speed every 120 seconds.
- **Background Dispatch**: Designed to be run as an independent agent task.

## Workflow

### 1. Launch a Babysitter Agent
To monitor a deployment, run the included `babysit_training.py` script. 

**Parameters Required:**
- `name`: Identifier (e.g., "Planner")
- `ip`: Instance IP
- `port`: SSH Port
- `key`: Local path to private key
- `log_file`: Remote log file path
- `script_file`: Remote training script filename

### 2. Execution Pattern
```bash
python3 scripts/babysit_training.py <name> <ip> <port> <key> <log_file> <script_file>
```

### 3. Monitoring Output
The script will continuously output the latest training heartbeat until manually stopped.

## Dispatch Command
When multiple jobs are active, you can dispatch two independent monitor instances using `nohup` to run them in the background.
