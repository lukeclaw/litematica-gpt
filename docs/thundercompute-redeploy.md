# Thunder Compute Training Redeployment Guide

This guide provides the optimized "God Mode" setup for training the Litematica DSL Specialist on Thunder Compute RTX A6000 instances.

## 1. Instance Provisioning
**Hardware:** RTX A6000 (48GB VRAM)
**Configuration:** Prototyping Mode, 4 vCPUs, 100GB Primary Disk.

```bash
tnr create --mode prototyping --gpu a6000 --num-gpus 1 --vcpus 4 --template base --primary-disk 100 -y
```

## 2. Environment Setup (Python 3.10 Virtual Env)
To avoid permission issues and version conflicts (specifically the `torch.int1` or `torch._inductor` errors seen with Python 3.12), always use a Python 3.10 virtual environment.

### Optimized `setup.sh`
```bash
#!/bin/bash
set -e

# System Deps
sudo apt-get update -y
sudo apt-get install -y python3.10-venv python3.10-dev tmux zip unzip

# Venv Initialization
rm -rf god_venv
python3.10 -m venv god_venv
./god_venv/bin/python3 -m pip install --upgrade pip setuptools wheel

# Stable AI Stack
# Torch 2.5.1 is currently the most stable for the Unsloth/Triton 3.x bridge
./god_venv/bin/python3 -m pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121

# Unsloth stable release (not git-edge to avoid regression patches)
./god_venv/bin/python3 -m pip install unsloth

# Supporting Libraries
./god_venv/bin/python3 -m pip install trl peft accelerate bitsandbytes
```

## 3. Dataset Configuration (v6 - God Mode)
- **Samples:** 3,165 rationalized blueprints.
- **Context Window:** 8,192 tokens (Crucial for complex structures like pipes/logos).
- **Format:** Llama 3.1 Instruct Chat Template.

Run `prepare_god_dataset.py` locally before bundling.

## 4. Training Hyperparameters
**Script:** `train_unsloth_god.py`
- **LoRA Rank (r):** 256 (High capacity to learn strict spatial mapping).
- **LoRA Alpha:** 512.
- **Target Modules:** All (q, k, v, o, gate, up, down).
- **Learning Rate:** 1e-4.
- **Max Steps:** 6000.
- **Batch Size:** 2 per device (with 4-8 gradient accumulation steps).

## 5. Execution Workflow
1. **Bundle:** `zip -j god_training_bundle.zip mlx_compiler_data_v6/train.jsonl train_unsloth_god.py setup.sh`
2. **Transfer:** `tnr scp god_training_bundle.zip <ID>:/home/ubuntu/`
3. **Connect:** `tnr connect <ID>`
4. **Deploy:** 
   ```bash
   unzip god_training_bundle.zip
   bash setup.sh
   # setup.sh ends by running the training script
   ```

## 6. Known Issues & Fixes
- **ModuleNotFoundError (torch/torchvision):** Usually caused by conflicting system packages. Solution: Wiping `god_venv` and using explicit `./god_venv/bin/python3 -m pip` calls.
- **AttributeError (torch.int1):** Occurs when Unsloth patches a bleeding-edge Torch version (like 2.10.0). Fix: Pin to `torch==2.5.1`.
- **unsloth_zoo metadata missing:** Occurs when installing from specific git branches. Fix: Use `pip install unsloth` stable release.
