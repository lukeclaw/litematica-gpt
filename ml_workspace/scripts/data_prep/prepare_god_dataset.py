import json
import os
import random
from transformers import AutoTokenizer

def get_specialist_prompt():
    return (
        "ROLE: You are the Lead Litematica DSL Architect. Your mission is to compile architectural plans "
        "into syntactically perfect Litematica DSL code that matches the Java Parser specification.\n\n"
        "COORDINATE SYSTEM:\n"
        "- X: Width, Y: Height (Start at 0), Z: Depth.\n\n"
        "TECHNICAL SPECIFICATION:\n"
        "1. PALETTE: 'palette' ... 'end_palette'. Map 1-char keys to block IDs: 'A = minecraft:stone'. '.' is air.\n"
        "2. GRID LAYERS: 'layer_y Y OffsetX OffsetZ'. Every subsequent line is a row of Z-depth. End with 'end_layer'.\n"
        "3. COMMANDS: 'set X Y Z BLOCK', 'fill X1 Y1 Z1 X2 Y2 Z2 BLOCK', 'box', 'carve'.\n\n"
        "CONSTRAINTS: No conversational filler. Output raw code only."
    )

def prepare_god_dataset():
    rationale_file = "dataset/synthetic_rationales.jsonl"
    dsl_dir = "dataset/dsl_10kb"
    output_dir = "mlx_compiler_data_v7" 
    os.makedirs(output_dir, exist_ok=True)
    
    MAX_TOKENS = 8192 # GOD MODE

    print("Loading tokenizer...")
    # Using the local venv path for tokenizer if possible, or downloading
    tokenizer = AutoTokenizer.from_pretrained("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")

    print("Mapping DSL files...")
    dsl_map = {f.split(" - ")[-1].replace(".txt", ""): f for f in os.listdir(dsl_dir) if f.endswith(".txt")}

    samples = []
    print(f"Aggregating all {len(dsl_map)} potential rationales...")
    
    with open(rationale_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                name = data["name"]
                rationale = data["rationale"]
                
                if name in dsl_map:
                    with open(os.path.join(dsl_dir, dsl_map[name]), 'r', encoding='utf-8') as code_f:
                        dsl_code = code_f.read()
                    
                    full_text = f"system\n{get_specialist_prompt()}\nuser\nArchitect's Plan:\n{rationale}\nassistant\n{dsl_code}"
                    # Check if it fits in God Mode window
                    if len(tokenizer.encode(full_text)) <= MAX_TOKENS:
                        samples.append({
                            "messages": [
                                {"role": "system", "content": get_specialist_prompt()},
                                {"role": "user", "content": f"Architect's Plan:\n{rationale}"},
                                {"role": "assistant", "content": dsl_code}
                            ]
                        })
            except: continue

    print(f"God Mode Dataset: {len(samples)} high-depth blueprints.")
    random.seed(3407)
    random.shuffle(samples)

    # Keep a tiny validation set
    train_samples = samples[:-10]
    valid_samples = samples[-10:]

    def write_jsonl(data, filename):
        path = os.path.join(output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')
        print(f"Wrote {len(data)} to {path}")
            
    write_jsonl(train_samples, "train.jsonl")
    write_jsonl(valid_samples, "valid.jsonl")

if __name__ == "__main__":
    prepare_god_dataset()
