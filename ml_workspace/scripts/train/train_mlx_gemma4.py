import mlx.core as mx
import mlx.optimizers as opt
from mlx_lm.tuner import train, TrainingArgs
from mlx_lm.tuner.datasets import load_dataset, CacheDataset
from mlx_lm.tuner.utils import build_schedule, linear_to_lora_layers
from mlx_lm import load
import argparse
import os
from pathlib import Path
from types import SimpleNamespace

def run_training():
    """
    Executes an end-to-end LoRA fine-tune on Gemma 4 E4B using MLX.
    Full-throttle training for 24GB Mac (no concurrent game).
    """
    model_name = "mlx-community/gemma-4-e4b-it-4bit"
    data_dir = "mlx_gemma4_compiler_data"
    adapter_path = "specialized_skills/gemma4_compiler_lora"

    os.makedirs(adapter_path, exist_ok=True)
    print(f"Starting Gemma 4 E4B 'Pure Compiler' Training (FULL THROTTLE)...")
    
    # Auto-detect and set memory limits
    if mx.metal.is_available():
        max_mem = mx.device_info()["max_recommended_working_set_size"]
        mx.set_wired_limit(max_mem) 
        print(f"MLX Wired Memory set to max recommended: {max_mem / (1024**3):.2f} GB")

    model, tokenizer = load(model_name)
    
    if not tokenizer.chat_template:
        tokenizer.chat_template = "{% for message in messages %}{{'<start_of_turn>' + message['role'] + '\n' + message['content'] + '<end_of_turn>\n'}}{% end_for %}{% if add_generation_prompt %}{{'<start_of_turn>model\n'}}{% endif %}"

    print("Configuring High-Performance LoRA Adapter (Rank 128)...")
    lora_config = {
        "rank": 128,
        "alpha": 256,
        "dropout": 0.05,
        "scale": 2.0, 
        "keys": ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    }
    linear_to_lora_layers(model, num_layers=16, config=lora_config)

    training_args = TrainingArgs(
        batch_size=2,            
        iters=2000,
        val_batches=10,
        steps_per_report=1,
        steps_per_eval=100,
        steps_per_save=500,
        max_seq_length=8192,     
        adapter_file=str(Path(adapter_path) / "adapters.safetensors"),
        grad_checkpoint=True,
        grad_accumulation_steps=4,
    )

    dataset_args = SimpleNamespace(
        data=data_dir,
        train=True,
        valid=True,
        test=False,
        mask_prompt=True, # MASK THE RATIONALE INPUT
    )

    print("Loading Dataset (Filtered for high-quality examples)...")
    train_set, valid_set, _ = load_dataset(dataset_args, tokenizer)
    train_set = CacheDataset(train_set)
    valid_set = CacheDataset(valid_set)

    lr_schedule = build_schedule({
        "name": "linear_schedule",
        "arguments": [1e-4, 0.0, training_args.iters]
    })
    
    optimizer = opt.Adam(learning_rate=lr_schedule)

    print("Executing Full-Throttle MLX Training...")
    mx.eval(model.parameters())
    
    train(
        model=model,
        optimizer=optimizer,
        train_dataset=train_set,
        val_dataset=valid_set,
        args=training_args
    )

    print(f"Training Complete! Adapters saved to {adapter_path}")

if __name__ == "__main__":
    run_training()
