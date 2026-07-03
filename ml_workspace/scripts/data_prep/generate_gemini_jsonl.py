import json
import os
import sys

def generate_gemini_jsonl(file_list_path, src_dir, output_path):
    if not os.path.exists(file_list_path):
        print(f"Error: {file_list_path} not found")
        return

    with open(file_list_path, 'r') as f:
        filenames = [line.strip() for line in f.readlines()]

    system_text = "You are an expert Minecraft Architect. Output raw DSL script to generate the requested schematic."

    with open(output_path, 'w', encoding='utf-8') as out:
        for fname in filenames:
            file_path = os.path.join(src_dir, fname)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as dsl_file:
                    dsl_content = dsl_file.read()
                
                prompt = fname.replace('.txt', '').split(' - ', 1)[-1]
                
                example = {
                    "system_instruction": {
                        "parts": [{"text": system_text}]
                    },
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": f"Build a {prompt}"}]
                        },
                        {
                            "role": "model",
                            "parts": [{"text": dsl_content}]
                        }
                    ]
                }
                out.write(json.dumps(example) + '\n')

    print(f"Successfully generated {output_path} with {len(filenames)} examples.")

if __name__ == "__main__":
    # Generate Training Set
    generate_gemini_jsonl("dataset/poc_files.txt", "dataset/dsl_10kb", "dataset/poc_train_gemini.jsonl")
    # Generate Validation Set
    generate_gemini_jsonl("dataset/poc_validation_files.txt", "dataset/dsl_10kb", "dataset/poc_validate_gemini.jsonl")
