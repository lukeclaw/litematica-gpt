# ThunderCompute Bundling & Deployment Guide

This document provides comprehensive information about bundling and deploying training scripts to ThunderCompute GPU instances for Litematica-GPT model training.

## Overview

The project uses ThunderCompute RTX A6000 instances for training Gemma 4 models with specialized LoRA adapters for compiler and planner agents. Training is bundled into self-contained zip archives that can be deployed to remote instances.

## Training Bundles

### Available Bundles (in `ml_workspace/data/archives/`)

| Bundle | Purpose | Size | Contents |
|--------|---------|------|----------|
| `compiler_training_bundle.zip` | Compiler agent training | ~6.3MB | train.jsonl, valid.jsonl, train_mlx_gemma4.py, setup.sh |
| `planner_training_bundle.zip` | Planner agent training | ~3.5MB | train.jsonl, valid.jsonl, train_mlx_gemma4_planner.py, setup.sh |
| `god_training_bundle.zip` | "God Mode" comprehensive training | ~5.0MB | Training data + comprehensive setup |
| `compiler_v2.zip` | Version 2 compiler training | ~6.3MB | Updated compiler training |
| `planner_v2.zip` | Version 2 planner training | ~3.5MB | Updated planner training |
| `litematica.zip` | Complete Litematica dataset | ~3.5GB | Full dataset archive |

### Bundle Contents Structure

Each training bundle contains:
- **Training Data**: `train.jsonl` (training samples), `valid.jsonl` (validation samples)
- **Training Script**: Model-specific training script (e.g., `train_mlx_gemma4_compiler.py`)
- **Setup Script**: Environment configuration (`setup.sh`)

## Setup Scripts

### Remote Setup Scripts

#### 1. Compiler Setup
**File**: `setup_compiler_remote.sh`
```bash
#!/bin/bash
set -e
sudo ldconfig /usr/lib64-nvidia
pip install unsloth trl peft accelerate bitsandbytes
echo "Starting Compiler training..."
nohup python3 train_unsloth_gemma4_compiler.py > training_compiler.log 2>&1 &
```

#### 2. Planner Setup  
**File**: `setup_planner_remote.sh`
```bash
#!/bin/bash
set -e
sudo ldconfig /usr/lib64-nvidia
pip install unsloth trl peft accelerate bitsandbytes
echo "Starting Planner training..."
nohup python3 train_unsloth_gemma4_planner.py > training_planner.log 2>&1 &
```

#### 3. Fast Compiler Setup
**File**: `setup_compiler_fast.sh`
```bash
#!/bin/bash
set -e
echo "Optimizing CUDA..."
sudo ldconfig /usr/lib64-nvidia
echo "Installing final logic layers..."
pip install --user unsloth trl peft accelerate bitsandbytes xformers
echo "Starting Pure Compiler Training (2,000 Steps)..."
nohup python3 train_unsloth_gemma4_compiler.py > training_compiler.log 2>&1 &
echo "Deployment successful. Monitoring training_compiler.log."
```

#### 4. Comprehensive "God Mode" Setup
**File**: `setup.sh`
```bash
#!/bin/bash
set -e

echo "Updating system..."
sudo apt-get update -y
sudo apt-get install -y python3.10-venv python3.10-dev tmux zip unzip

echo "Cleaning up old venv..."
rm -rf god_venv
python3.10 -m venv god_venv

echo "Upgrading pip in venv..."
./god_venv/bin/python3 -m pip install --upgrade pip setuptools wheel

echo "Installing Torch 2.5.1 + CUDA 12.1..."
./god_venv/bin/python3 -m pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121

echo "Installing Unsloth (Stable Release)..."
./god_venv/bin/python3 -m pip install unsloth

echo "Installing essentials..."
./god_venv/bin/python3 -m pip install trl peft accelerate bitsandbytes

echo "Final sanity check..."
./god_venv/bin/python3 -c "from unsloth import FastLanguageModel; print('Environment is God Mode Ready.')"

echo "Starting God Mode training..."
./god_venv/bin/python3 train_unsloth_god.py
```

## Deployment Workflows

### Standard Deployment Process

1. **Instance Provisioning**
```bash
tnr create --mode prototyping --gpu a6000 --num-gpus 1 --vcpus 4 --template base --primary-disk 100 -y
```

2. **Bundle Creation**
```bash
# Compiler bundle
zip -j compiler_training_bundle.zip training_data/compiler/train.jsonl scripts/train/train_unsloth_gemma4_compiler.py setup_and_configs/setup.sh

# Planner bundle  
zip -j planner_training_bundle.zip training_data/planner/train.jsonl scripts/train/train_unsloth_gemma4_planner.py setup_and_configs/setup.sh
```

3. **Transfer to Instance**
```bash
tnr scp compiler_training_bundle.zip <INSTANCE_ID>:/home/ubuntu/
```

4. **Remote Execution**
```bash
tnr connect <INSTANCE_ID>
unzip compiler_training_bundle.zip
bash setup.sh
```

### Fast Deployment (for testing)

Use the pre-built bundles:
```bash
# Transfer pre-built bundle
tnr scp ml_workspace/data/archives/compiler_training_bundle.zip <INSTANCE_ID>:/home/ubuntu/

# Connect and deploy
tnr connect <INSTANCE_ID>
unzip compiler_training_bundle.zip
bash setup_compiler_fast.sh
```

## Training Scripts

### Key Training Files
- `train_unsloth_gemma4_compiler.py` - Compiler agent training
- `train_unsloth_gemma4_planner.py` - Planner agent training
- `train_unsloth_god.py` - Comprehensive "God Mode" training
- `train_mlx_gemma4.py` - MLX-optimized training for Apple Silicon
- `train_mlx_gemma4_planner.py` - MLX planner training

### Configuration Details

#### Model Configuration
- **Base Model**: `unsloth/meta-llama-3.1-8b-instruct-bnb-4bit`
- **Max Sequence Length**: 8192 tokens
- **LoRA Rank**: 128 (high capacity for spatial mapping)
- **LoRA Alpha**: 256
- **Learning Rate**: 2e-4
- **Max Steps**: 6000 (God Mode), 2000 (Fast)

#### Hardware Requirements
- **GPU**: RTX A6000 (48GB VRAM)
- **vCPUs**: 4
- **Storage**: 100GB primary disk
- **Mode**: Prototyping (auto-stops when idle)

## Monitoring & Logging

### Training Logs
- `training_compiler.log` - Compiler training progress
- `training_planner.log` - Planner training progress
- Logs are created in nohup background processes

### Monitoring Commands
```bash
# Check training progress
tail -f training_compiler.log

# Monitor GPU usage
nvidia-smi

# Check process status
ps aux | grep train
```

## Troubleshooting

### Common Issues

1. **CUDA Configuration**
```bash
sudo ldconfig /usr/lib64-nvidia
```

2. **Python Version Conflicts**
- Always use Python 3.10 virtual environment for stability
- Avoid Python 3.12 due to `torch.int1` compatibility issues

3. **Unsloth Installation**
- Use stable release: `pip install unsloth`
- Avoid git-edge versions to prevent regression patches

4. **Memory Issues**
- Monitor GPU memory with `nvidia-smi`
- Adjust batch size if encountering OOM errors

## File Locations

### Scripts
- Training scripts: `ml_workspace/scripts/train/`
- Setup scripts: `ml_workspace/setup_and_configs/`
- Utility scripts: `ml_workspace/scripts/utils/`

### Data
- Training bundles: `ml_workspace/data/archives/`
- Training data: `ml_workspace/data/`
- Models and adapters: `ml_workspace/models_and_adapters/`

### Logs
- Active runs: `ml_workspace/logs_and_runs/`
- Completed training logs are saved on the remote instance

## Quick Reference

### Bundle Creation
```bash
cd ml_workspace/data/archives
zip -r bundle_name.zip training_data/ scripts/train/train_*.py setup_and_configs/setup.sh
```

### Instance Management
```bash
# List instances
tnr list

# Connect to instance
tnr connect <ID>

# Transfer files
tnr scp <file.zip> <ID>:/home/ubuntu/

# Monitor instance
tnr monitor <ID>
```

This bundling system enables rapid deployment of specialized training environments for Litematica-GPT's compiler and planner agents on ThunderCompute infrastructure.