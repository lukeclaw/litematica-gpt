import json
import os
import shutil
import argparse
from pathlib import Path

def prepare_mlx_adapter(adapter_dir):
    """
    Converts an Unsloth-generated checkpoint into a production-ready MLX adapter.
    1. Renames adapter_model.safetensors -> adapters.safetensors
    2. Generates a valid MLX-compatible adapter_config.json
    """
    adapter_path = Path(adapter_dir)
    
    # 1. Rename Weights
    old_weights = adapter_path / "adapter_model.safetensors"
    new_weights = adapter_path / "adapters.safetensors"
    
    if old_weights.exists():
        print(f"Renaming {old_weights.name} -> {new_weights.name}")
        shutil.move(str(old_weights), str(new_weights))
    
    # 2. Fix Config
    config_path = adapter_path / "adapter_config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
            
        # Map Unsloth parameters to MLX schema
        rank = config.get("r", 128)
        alpha = config.get("lora_alpha", 256)
        scale = alpha / rank
        
        mlx_config = {
            "model": "mlx-community/gemma-4-e4b-it-4bit",
            "num_layers": 32,
            "lora_parameters": {
                "rank": rank,
                "alpha": alpha,
                "dropout": config.get("lora_dropout", 0.0),
                "scale": scale
            }
        }
        
        with open(config_path, "w") as f:
            json.dump(mlx_config, f, indent=4)
        print(f"Successfully converted {config_path.name} for MLX.")
    else:
        print(f"ERROR: {config_path} not found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="The directory containing the adapter weights")
    args = parser.parse_args()
    prepare_mlx_adapter(args.directory)
