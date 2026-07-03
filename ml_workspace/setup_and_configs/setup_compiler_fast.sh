#!/bin/bash
set -e
echo "Optimizing CUDA..."
sudo ldconfig /usr/lib64-nvidia
echo "Installing final logic layers..."
pip install --user unsloth trl peft accelerate bitsandbytes xformers
echo "Starting Pure Compiler Training (2,000 Steps)..."
nohup python3 train_unsloth_gemma4_compiler.py > training_compiler.log 2>&1 &
echo "Deployment successful. Monitoring training_compiler.log."
