import json
import os
import sys

def prepare_full_train(src_dir, output_path):
    if not os.path.exists(src_dir):
        print(f"Error: {src_dir} not found")
        return

    files = [f for f in os.listdir(src_dir) if f.endswith('.txt')]
    print(f"Found {len(files)} files in {src_dir}")

    samples = []
    for filename in files:
        # File name is like "10 - admin shoppe.txt"
        # We want "admin shoppe" as the prompt
        name_parts = filename.replace(".txt", "").split(" - ")
        if len(name_parts) > 1:
            prompt_name = name_parts[1]
        else:
            prompt_name = name_parts[0]

        file_path = os.path.join(src_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        sample = {
            "messages": [
                {"role": "system", "content": "You are an expert Minecraft Architect. Output raw DSL script to generate the requested schematic."},
                {"role": "user", "content": f"Build a {prompt_name}"},
                {"role": "assistant", "content": content}
            ]
        }
        samples.append(sample)

    with open(output_path, 'w', encoding='utf-8') as f:
        for sample in samples:
            f.write(json.dumps(sample) + '\n')

    print(f"Successfully generated {output_path} with {len(samples)} examples.")

if __name__ == "__main__":
    prepare_full_train("dataset/dsl_10kb", "dataset/full_train_sparse.jsonl")
