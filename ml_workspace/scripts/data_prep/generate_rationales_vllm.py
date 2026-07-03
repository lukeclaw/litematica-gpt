import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- CONFIGURATION ---
VLLM_SERVER_URL = "http://localhost:8000/v1/chat/completions"
MODEL_NAME = "AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored-BF16" 
SRC_DIR = "dataset/dsl_10kb"
RATIONALE_FILE = "synthetic_rationales_h100.jsonl"
MAX_WORKERS = 10 # Optimized for H100 with 8-bit quantization and 128k context

MASTER_INSTRUCTIONS = """PROJECT MISSION: We are training a 'Student AI' to become a Minecraft Architect. 
The student model is smart with language but struggles with 3D coordinate math. 
Your role is the 'Master Teacher'.

INPUT: I will provide you with a raw Litematica DSL script (Litematica Format).

TASK: Reverse-engineer the code and write a 'Spatial Rationale'. This rationale must act 
as a mental bridge between the building's name and the raw coordinates.

YOUR MONOLOGUE MUST COVER:
1. Footprint Analysis: What are the X, Y, Z dimensions? Is it hollow, solid, or tiered?
2. Material Strategy: Explain the block choices. Why Stone for the base? Why Glass here?
3. Construction Sequence: Walk through the layers (Y=0, Y=1...) and explain the logical 
   purpose of each section (e.g., 'At Y=4, I am starting the roof overhang to provide shade').
4. Logic: Use ACTIVE VOICE ('I will', 'I should').

GOAL: If the Student AI reads your thinking process, it should be able to 'visualize' the 
building perfectly before it ever looks at the raw code.

IMPORTANT: Output ONLY plain text within the <Thinking> tags. Do NOT use tools or write code."""

def get_processed_names():
    processed = set()
    if os.path.exists(RATIONALE_FILE):
        with open(RATIONALE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    processed.add(data["name"])
                except: continue
    return processed

def generate_rationale(filename):
    building_name = filename.split(" - ")[-1].replace(".txt", "")
    file_path = os.path.join(SRC_DIR, filename)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            dsl_content = f.read()

        prompt = (
            f"STRUCTURE NAME: '{building_name}'\n"
            f"REFERENCE DSL CODE:\n{dsl_content}\n\n"
            f"OUTPUT FORMAT:\n<Thinking> [Your detailed spatial rationale] </Thinking>"
        )

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": MASTER_INSTRUCTIONS},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4096
        }

        response = requests.post(VLLM_SERVER_URL, json=payload, timeout=600)
        response.raise_for_status()
        
        result = response.json()
        text = result['choices'][0]['message']['content']
        
        if "<Thinking>" in text:
            thinking = text.split("<Thinking>")[1].split("</Thinking>")[0].strip()
            return building_name, thinking
        else:
            return building_name, text.strip()

    except Exception as e:
        print(f"   [ERROR] {building_name}: {e}")
        return building_name, None

def main():
    if not os.path.exists(SRC_DIR):
        print(f"Error: {SRC_DIR} not found. Please unzip your DSL files into this directory.")
        return

    processed_names = get_processed_names()
    all_files = sorted([f for f in os.listdir(SRC_DIR) if f.endswith('.txt')])
    remaining_files = [f for f in all_files if f.split(" - ")[-1].replace(".txt", "") not in processed_names]

    print(f"Detected {len(processed_names)} existing rationales.")
    print(f"Processing {len(remaining_files)} NEW structures with {MAX_WORKERS} workers...")

    with open(RATIONALE_FILE, 'a', encoding='utf-8') as out_f:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_file = {executor.submit(generate_rationale, f): f for f in remaining_files}
            for future in as_completed(future_to_file):
                name, rationale = future.result()
                if rationale:
                    out_f.write(json.dumps({"name": name, "rationale": rationale}) + "\n")
                    out_f.flush()
                    print(f"   [SAVED] {name}")

if __name__ == "__main__":
    main()
