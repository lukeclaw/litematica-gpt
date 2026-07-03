import json
import os
import random

def prepare_mlx_distill_data():
    input_file = "dataset/synthetic_train_rationalized.jsonl"
    output_dir = "mlx_distill_full"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    samples = [json.loads(line) for line in lines]
    print(f"Loaded {len(samples)} samples from {input_file}")
    
    random.seed(3407)
    random.shuffle(samples)

    # 95/5 split
    split_idx = int(len(samples) * 0.95)
    train_samples = samples[:split_idx]
    valid_samples = samples[split_idx:]

    def write_jsonl(data, filename):
        path = os.path.join(output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')
        print(f"Wrote {len(data)} to {path}")

    write_jsonl(train_samples, "train.jsonl")
    write_jsonl(valid_samples, "valid.jsonl")
    write_jsonl(valid_samples, "test.jsonl")

if __name__ == "__main__":
    prepare_mlx_distill_data()
