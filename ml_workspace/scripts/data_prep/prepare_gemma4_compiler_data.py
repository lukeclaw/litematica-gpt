import json
import os
import random
from transformers import AutoTokenizer

def get_gemma4_system_prompt():
    return (
        "ROLE: You are the Lead Litematica DSL Architect. Your mission is to compile architectural plans "
        "into syntactically perfect Litematica DSL code that matches the Java Parser specification.\n\n"
        "COORDINATE SYSTEM:\n"
        "- X: Width, Y: Height (Start at 0), Z: Depth.\n\n"
        "TECHNICAL SPECIFICATION:\n"
        "1. PALETTE: 'palette' ... 'end_palette'. Map 1-char keys to block IDs.\n"
        "2. GRID LAYERS: 'layer_y Y OffsetX OffsetZ'. Every line is a row of Z-depth. End with 'end_layer'.\n\n"
        "CONSTRAINTS:\n"
        "- Output raw code only. No conversational filler."
    )

def prepare_compiler_only_data():
    rationale_file = "dataset/synthetic_rationales.jsonl"
    dsl_dir = "dataset/dsl_10kb"
    output_dir = "mlx_gemma4_compiler_data" 
    os.makedirs(output_dir, exist_ok=True)
    
    MAX_TOKENS = 8192

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")

    print("Mapping DSL files...")
    dsl_map = {f.split(" - ")[-1].replace(".txt", ""): f for f in os.listdir(dsl_dir) if f.endswith(".txt")}

    samples = []
    skipped = 0
    
    with open(rationale_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                name = data["name"]
                rationale = data["rationale"]
                
                if name in dsl_map:
                    with open(os.path.join(dsl_dir, dsl_map[name]), 'r', encoding='utf-8') as code_f:
                        dsl_code = code_f.read()
                    
                    # Dual Expert Format: Thinking is INPUT
                    user_content = f"{get_gemma4_system_prompt()}\n\nArchitect's Plan:\n{rationale}"
                    assistant_response = dsl_code
                    
                    full_text = f"user\n{user_content}\nassistant\n{assistant_response}"
                    
                    if len(tokenizer.encode(full_text)) <= MAX_TOKENS:
                        samples.append({
                            "messages": [
                                {"role": "user", "content": user_content},
                                {"role": "model", "content": assistant_response}
                            ]
                        })
                    else:
                        skipped += 1
            except:
                continue

    print(f"Compiler Dataset: {len(samples)} pure DSL blueprints.")
    print(f"Skipped {skipped} for exceeding {MAX_TOKENS} tokens.")
    random.seed(3407)
    random.shuffle(samples)

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
    prepare_compiler_only_data()
