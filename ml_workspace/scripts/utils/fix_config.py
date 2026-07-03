import json
import os

path = "specialized_skills/gemma4_compiler_lora/adapter_config.json"
with open(path, "r") as f:
    config = json.load(f)

# Calculating scale: alpha / rank
rank = config.get("r", 128)
alpha = config.get("lora_alpha", 256)
scale = alpha / rank

config["num_layers"] = 32
config["model"] = "mlx-community/gemma-4-e4b-it-4bit"
config["lora_parameters"] = {
    "rank": rank,
    "alpha": alpha,
    "dropout": config.get("lora_dropout", 0.0),
    "scale": scale
}

with open(path, "w") as f:
    json.dump(config, f, indent=4)

print(f"Fixed adapter_config.json with scale={scale}")
