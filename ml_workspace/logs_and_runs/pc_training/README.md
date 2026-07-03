# Fast Training on PC (Nvidia 4070 Super)

This folder contains everything you need to fine-tune your Minecraft Architect model on your PC using **Unsloth**.

## Step 1: Prepare Data (On your Mac)
Run this in your project root on the Mac:
```bash
python pc_training/prepare_pc_data.py
```
This creates `pc_training/train.jsonl`.

## Step 2: Transfer Files to PC
Copy the entire `pc_training` folder to your PC.

## Step 3: Setup Environment (On PC)
On your PC (assuming Windows WSL2 or Linux), run:
```bash
# Create a new environment
conda create --name unsloth_env python=3.10 -y
conda activate unsloth_env

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Launch Training
```bash
python train_unsloth.py
```

## Step 5: Bring Weights back to Mac
1. Once training finishes, you will see a folder called `minecraft_compiler_adapter`.
2. Copy this folder back to your Mac into `specialized_skills/dsl_compiler_llama8b/`.
3. The Mac will immediately recognize the new, highly-accurate weights!
