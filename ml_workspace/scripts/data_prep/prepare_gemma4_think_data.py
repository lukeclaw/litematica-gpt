import json
import os
import random
from transformers import AutoTokenizer

def get_gemma4_system_prompt():
    return (
        "<|think|> ROLE: You are the Lead Litematica DSL Architect. "
        "MISSION: Construct a step-by-step spatial rationale followed by syntactically perfect Litematica DSL code.\n\n"
        "SPATIAL RATIONALE STRUCTURE (Inside <|channel|>thought):\n"
        "1. **FOOTPRINT ANALYSIS**: Define the bounding box (X, Y, Z). Describe the structure's overall shape and orientation.\n"
        "2. **MATERIAL STRATEGY**: List every block type and assign it a unique 1-character key (A, B, C...). Explain the choice for each material.\n"
        "3. **CONSTRUCTION SEQUENCE**: Walk through the build layer-by-layer (Y=0, Y=1...). Explain the logic of where blocks are placed.\n\n"
        "TECHNICAL SPECIFICATION:\n"
        "1. PALETTE: 'palette' ... 'end_palette'. Map 1-char keys to block IDs.\n"
        "2. GRID LAYERS: 'layer_y Y OffsetX OffsetZ'. Every line is a row of Z-depth. End with 'end_layer'.\n\n"
        "CONSTRAINTS:\n"
        "- The <|think|> token enables your internal reasoning expert.\n"
        "- You MUST provide the structured rationale above inside the native thought channel (<|channel|>thought).\n"
        "- Immediately after the <channel|> tag, output the raw DSL code. No other conversational text."
    )

def prepare_gemma_thinking_data():
    rationale_file = "dataset/synthetic_rationales.jsonl"
    dsl_dir = "dataset/dsl_10kb"
    output_dir = "mlx_gemma4_think_data" 
    os.makedirs(output_dir, exist_ok=True)
    
    # Gemma 4 E4B context window limit for safe local MLX training on 24GB
    MAX_TOKENS = 2048

    print("Loading Gemma tokenizer...")
    try:
        tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-9b-it") # Gemma family uses identical tokenizers
    except Exception:
        print("Using fallback Llama tokenizer for length estimation (similar ratios).")
        tokenizer = AutoTokenizer.from_pretrained("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")

    print("Mapping DSL files...")
    dsl_map = {f.split(" - ")[-1].replace(".txt", ""): f for f in os.listdir(dsl_dir) if f.endswith(".txt")}

    samples = []
    skipped = 0
    print(f"Aggregating all {len(dsl_map)} potential rationales into <think> blocks...")
    
    with open(rationale_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                name = data["name"]
                rationale = data["rationale"]
                
                if name in dsl_map:
                    with open(os.path.join(dsl_dir, dsl_map[name]), 'r', encoding='utf-8') as code_f:
                        dsl_code = code_f.read()
                    
                    # The Pure Compiler Format (Dual Expert)
                    user_prompt = f"{get_gemma4_system_prompt()}\n\nArchitect's Plan:\n{rationale}"
                    assistant_response = f"{dsl_code}"
                    
                    full_text = f"{user_prompt}\n{assistant_response}"
                    
                    if len(tokenizer.encode(full_text)) <= MAX_TOKENS:
                        samples.append({
                            "messages": [
                                {"role": "user", "content": user_content},
                                {"role": "model", "content": assistant_response}
                            ]
                        })
                    else:
                        skipped += 1
            except Exception as e:
                continue

    print(f"Gemma 4 Thinking Dataset: {len(samples)} end-to-end blueprints.")
    print(f"Skipped {skipped} for exceeding 2048 tokens.")
    random.seed(3407)
    random.shuffle(samples)

    # Exactly 10 for validation
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
    prepare_gemma_thinking_data()
