import json
import os
import random
from transformers import AutoTokenizer

def get_rich_system_prompt():
    return (
        "You are an expert Minecraft Architect using 'Litematica DSL'.\n"
        "1. palette/end_palette defines blocks.\n"
        "2. layer_y defines horizontal grid slices.\n"
        "3. fill/set commands for large volumes.\n"
        "Goal: Output a COMPLETE, structurally sound schematic."
    )

def prepare_mlx_data():
    input_file = "dataset/full_train_sparse.jsonl"
    output_dir = "mlx_data_gemma4_distributed"
    os.makedirs(output_dir, exist_ok=True)
    
    # Distributed power allows us to handle 4096 tokens!
    MAX_TOKENS = 4096 

    print("Loading Gemma 4 tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("google/gemma-4-e4b")

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    samples = []
    for line in lines:
        try:
            data = json.loads(line)
            user_msg = next(m["content"] for m in data["messages"] if m["role"] == "user")
            assistant_msg = next(m["content"] for m in data["messages"] if m["role"] == "assistant")
            
            # Proper Gemma 4 Chat Format
            chat_sample = {
                "messages": [
                    {"role": "system", "content": get_rich_system_prompt()},
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": assistant_msg}
                ]
            }
            
            # Check length for memory safety
            text = f"<|turn|>system\n{get_rich_system_prompt()}<turn|>\n<|turn|>user\n{user_msg}<turn|>\n<|turn|>model\n{assistant_msg}<turn|>\n"
            if len(tokenizer.encode(text)) <= MAX_TOKENS:
                samples.append(chat_sample)
        except Exception: continue

    print(f"Dataset ready: {len(samples)} complete structures.")
    random.seed(3407)
    random.shuffle(samples)

    with open(os.path.join(output_dir, "train.jsonl"), 'w') as f:
        for s in samples[:-20]: f.write(json.dumps(s) + '\n')
    with open(os.path.join(output_dir, "valid.jsonl"), 'w') as f:
        for s in samples[-20:]: f.write(json.dumps(s) + '\n')

if __name__ == "__main__":
    prepare_mlx_data()
