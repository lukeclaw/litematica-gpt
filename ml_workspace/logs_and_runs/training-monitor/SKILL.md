---
name: training-monitor
description: Monitors remote GPU training on Thunder Compute. Parses logs for loss, steps, and ETA. Use when training is active to provide progress reports and execute follow-up actions like downloading weights or terminating instances.
---

# Training Monitor

This skill provides a structured workflow for monitoring active machine learning training jobs on remote Thunder Compute instances.

## Workflow

### 1. Identify Context
- Determine the **Instance ID** (e.g., "0").
- Identify the **Log File** path (e.g., `setup_god_v7.log`).

### 2. Poll Training Progress
Use `mcp_thundercompute_run_command` to retrieve the latest log tail and parse it.

**Pattern:**
```bash
tail -n 100 <LOG_FILE>
```

**Metrics to Report:**
- **Step**: Current step / Total steps.
- **Percent**: Percentage of completion.
- **Speed**: s/it (seconds per iteration).
- **ETA**: Estimated time remaining.
- **Loss**: The most recent loss value.
- **Epoch**: Current epoch.

### 3. Check for Checkpoints
Check the `outputs/` directory for new `checkpoint-*` folders.

```bash
ls -d outputs/checkpoint-*
```

### 4. Interactive Reporting Loop
After providing a status report, you MUST ask the user if they want to:
- **Continue Monitoring**: Wait for the next interval.
- **Execute Action**: Perform a specific task (e.g., "Test Checkpoint 1000", "Terminate Instance").
- **Stop**: Exit the monitoring state.

## Follow-up Actions

### Test Checkpoint
1. Zip the adapter files on the remote instance.
2. Download to local machine.
3. Fix `adapter_config.json` if necessary.
4. Run validation scripts.

### Terminate Instance
1. Confirm with user.
2. Ensure any desired weights are downloaded first.
3. Call `mcp_thundercompute_delete_instance`.
