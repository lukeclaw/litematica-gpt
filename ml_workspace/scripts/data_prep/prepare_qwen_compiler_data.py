import json
import os
import random

def prepare_qwen_compiler_data():
    rationale_file = "./ml_workspace/data/raw/dataset/synthetic_rationales.jsonl"
    dsl_dir = "dataset/dsl_10kb"
    output_dir = "mlx_qwen_compiler_data"
    os.makedirs(output_dir, exist_ok=True)

    print("Mapping DSL files...")
    # Map building names to their actual DSL files
    dsl_map = {f.split(" - ")[-1].replace(".txt", ""): f for f in os.listdir(dsl_dir) if f.endswith('.txt')}

    samples = []
    print(f"Processing rationales from {rationale_file}...")
    
    with open(rationale_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                name = data["name"]
                rationale = data["rationale"]
                
                if name in dsl_map:
                    with open(os.path.join(dsl_dir, dsl_map[name]), 'r', encoding='utf-8') as code_f:
                        dsl_code = code_f.read()
                    
                    # Qwen 3.5 Chat Format
                    samples.append({
                        "messages": [
                            {"role": "system", "content": "You are the Lead Litematica DSL Architect. Compile the following plan into syntactically perfect Litematica DSL grid code."},
                            {"role": "user", "content": f"Architect's Plan for {name}:\n{rationale}"},
                            {"role": "assistant", "content": dsl_code}
                        ]
                    })
            except:
                continue

    print(f"Generated {len(samples)} examples for Qwen 3.5.")
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
    prepare_qwen_compiler_data()
