#!/bin/bash
set -e

echo "--- 1. Updating System & Installing Dependencies ---"
sudo apt-get update && sudo apt-get install -y python3-pip python3-venv unzip screen

echo "--- 2. Setting up Python Virtual Environment ---"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install vllm requests

echo "--- 3. Unzipping DSL Data ---"
mkdir -p dataset/dsl_10kb
unzip -o dsl_under_128k_tokens.zip -d dataset/dsl_10kb

echo "--- 4. Instructions for Deployment ---"
echo "---------------------------------------------------------"
echo "SETUP COMPLETE."
echo ""
echo "TO START THE MODEL SERVER (Run in a separate 'screen' or tab):"
echo "source venv/bin/activate"
echo "vllm serve AEON-7/Qwen3.6-35B-A3B-Ultimate-Uncensored --quantization fp8 --max-model-len 128000"
echo ""
echo "TO START BATCH PROCESSING:"
echo "python3 generate_rationales_vllm.py"
echo "---------------------------------------------------------"
