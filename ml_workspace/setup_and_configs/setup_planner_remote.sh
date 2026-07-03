#!/bin/bash
set -e
sudo ldconfig /usr/lib64-nvidia
pip install unsloth trl peft accelerate bitsandbytes
echo "Starting Planner training..."
nohup python3 train_unsloth_gemma4_planner.py > training_planner.log 2>&1 &
