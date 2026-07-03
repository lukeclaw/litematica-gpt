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
