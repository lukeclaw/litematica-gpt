import numpy as np
from safetensors import safe_open

with safe_open("adapters/adapters.safetensors", framework="numpy") as f:
    for key in f.keys()[:20]:
        weights = f.get_tensor(key)
        print(f"{key}: {weights.shape}, mean: {np.mean(weights):.6f}, std: {np.std(weights):.6f}")
