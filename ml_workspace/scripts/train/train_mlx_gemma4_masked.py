import mlx.core as mx
import mlx.optimizers as opt
from mlx_lm.tuner import train, TrainingArgs
from mlx_lm.tuner.datasets import load_dataset, CacheDataset
from mlx_lm.tuner.utils import build_schedule, linear_to_lora_layers
from mlx_lm import load
import os
from pathlib import Path
from types import SimpleNamespace
import json

def run_training():
    """
    Executes a Pure Compiler fine-tune on Gemma 4 E4B using MLX.
    Uses PROMPT MASKING to focus 100% of learning on the DSL syntax.
    """
    model_id = "mlx-community/gemma-4-e4b-it-4bit"
    data_dir = "mlx_gemma4_compiler_data"
    adapter_path = "specialized_skills/gemma4_compiler_masked_lora"

    os.makedirs(adapter_path, exist_ok=True)
    print(f"Starting Gemma 4 'Pure Compiler' (MASKED) Training...")

    # Auto-detect and set memory limits for 24GB Mac
    if mx.metal.is_available():
        max_mem = mx.device_info()["max_recommended_working_set_size"]
        mx.set_wired_limit(max_mem)
        print(f"Memory Limit: {max_mem / (1024**3):.2f} GB")

    model, tokenizer = load(model_id)

    # High-Rank LoRA for complex spatial precision
    lora_config = {
        "rank": 64,  # Lowered to 64 for local stability/generalization
        "alpha": 128,
        "dropout": 0.05,
        "scale": 2.0,
        "keys": ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    }
    linear_to_lora_layers(model, num_layers=16, config=lora_config)

    # Training Arguments
    args = TrainingArgs(
        batch_size=1,            # 1 for stability
        iters=2000,
        val_batches=10,
        steps_per_report=1,
        steps_per_eval=100,
        steps_per_save=100,      # Frequent saves to monitor progress
        max_seq_length=2048,     # Strict local window
        adapter_file=str(Path(adapter_path) / "adapters.safetensors"),
        grad_checkpoint=True,
        grad_accumulation_steps=8, # Effective Batch Size 8
    )

    # Dataset arguments with MASKING enabled
    dataset_args = SimpleNamespace(
        data=data_dir,
        train=True,
        valid=True,
        test=False,
        mask_prompt=True, # THIS IS THE KEY: Model only learns the DSL
    )

    print("Loading Dataset...")
    train_set, valid_set, _ = load_dataset(dataset_args, tokenizer)
    train_set = CacheDataset(train_set)
    valid_set = CacheDataset(valid_set)

    lr_schedule = build_schedule({
        "name": "linear_schedule",
        "arguments": [1e-4, 0.0, args.iters]
    })
    
    optimizer = opt.Adam(learning_rate=lr_schedule)

    print("Executing Masked Training...")
    mx.eval(model.parameters())
    
    train(
        model=model,
        optimizer=optimizer,
        train_dataset=train_set,
        val_dataset=valid_set,
        args=args
    )
    
    # Save the config manually
    config_data = {
        "model": model_id,
        "num_layers": 32,
        "lora_parameters": lora_config
    }
    with open(Path(adapter_path) / "adapter_config.json", "w") as f:
        json.dump(config_data, f, indent=4)

    print(f"Training Complete! Masked Adapters saved to {adapter_path}")

if __name__ == "__main__":
    run_training()
