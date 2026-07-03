import json
import os
import random
from transformers import AutoTokenizer

def get_planner_system_prompt():
    return (
        "ROLE: You are the Lead Litematica DSL Architect. "
        "MISSION: Construct a step-by-step spatial rationale based on the provided building name.\n\n"
        "SPATIAL RATIONALE STRUCTURE:\n"
        "1. **FOOTPRINT ANALYSIS**: Define the bounding box (X, Y, Z). Describe the structure's overall shape and orientation.\n"
        "2. **MATERIAL STRATEGY**: List every block type and assign it a unique 1-character key (A, B, C...). Explain the choice for each material.\n"
        "3. **CONSTRUCTION SEQUENCE**: Walk through the build layer-by-layer (Y=0, Y=1...). Explain the logic of where blocks are placed."
    )

def prepare_gemma4_planner_data():
    input_file = "dataset/synthetic_rationales.jsonl"
    output_dir = "mlx_gemma4_planner_data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Gemma tokenizer for length check
    tokenizer = AutoTokenizer.from_pretrained("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")
    MAX_TOKENS = 2048

    print(f"Loading rationales from {input_file}...")
    samples = []
    skipped = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                name = data["name"]
                rationale = data["rationale"]
                
                # Input: Name
                # Output: Rationale
                user_content = f"{get_planner_system_prompt()}\n\nBuild the {name}."
                assistant_response = rationale
                
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

    print(f"Planner Dataset: {len(samples)} examples.")
    print(f"Skipped {skipped} for length.")
    
    random.seed(3407)
    random.shuffle(samples)

    # 10 for validation
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
    prepare_gemma4_planner_data()
