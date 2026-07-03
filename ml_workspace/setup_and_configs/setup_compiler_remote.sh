#!/bin/bash
set -e
sudo ldconfig /usr/lib64-nvidia
pip install unsloth trl peft accelerate bitsandbytes
echo "Starting Compiler training..."
nohup python3 train_unsloth_gemma4_compiler.py > training_compiler.log 2>&1 &
