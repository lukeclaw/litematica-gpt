import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 1. Configuration
PROJECT_ID = "project-04a53d5f-b875-4835-856"
LOCATION = "global" 
MODEL_NAME = "gemini-3.1-pro-preview" 
MAX_WORKERS = 10 
RATIONALE_FILE = "dataset/synthetic_rationales.jsonl"
# IGNORED: OLD_COMBINED_FILE = "dataset/synthetic_train_rationalized_OLD.jsonl"
SRC_DIR = "dataset/dsl_10kb"

vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(MODEL_NAME)
file_lock = threading.Lock()
shutdown_event = threading.Event()

def get_master_instructions():
    return (
        "PROJECT MISSION: We are training a 'Student AI' to become a Minecraft Architect. "
        "The student model is smart with language but struggles with 3D coordinate math. "
        "Your role is the 'Master Teacher'.\n\n"
        "INPUT: I will provide you with a raw Litematica DSL script (Litematica Format).\n\n"
        "TASK: Reverse-engineer the code and write a 'Spatial Rationale'. This rationale must act "
        "as a mental bridge between the building's name and the raw coordinates.\n\n"
        "YOUR MONOLOGUE MUST COVER:\n"
        "1. Footprint Analysis: What are the X, Y, Z dimensions? Is it hollow, solid, or tiered?\n"
        "2. Material Strategy: Explain the block choices. Why Stone for the base? Why Glass here?\n"
        "3. Construction Sequence: Walk through the layers (Y=0, Y=1...) and explain the logical "
        "purpose of each section (e.g., 'At Y=4, I am starting the roof overhang to provide shade').\n"
        "4. Logic: Use ACTIVE VOICE ('I will', 'I should').\n\n"
        "GOAL: If the Student AI reads your thinking process, it should be able to 'visualize' the "
        "building perfectly before it ever looks at the raw code.\n\n"
        "IMPORTANT: Output ONLY plain text within the <Thinking> tags. Do NOT use tools or write code."
    )

def get_processed_names():
    processed = set()
    # We ONLY check the new file now to ensure 100% Master Class quality
    if os.path.exists(RATIONALE_FILE):
        with open(RATIONALE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    processed.add(data["name"])
                except: continue
    return processed

def generate_rationale(filename):
    if shutdown_event.is_set():
        return None, None
    building_name = filename.split(" - ")[-1].replace(".txt", "")
    try:
        with open(os.path.join(SRC_DIR, filename), 'r', encoding='utf-8') as f:
            dsl_content = f.read()

        prompt = (
            f"{get_master_instructions()}\n\n"
            f"STRUCTURE NAME: '{building_name}'\n"
            f"REFERENCE DSL CODE:\n{dsl_content}\n\n"
            f"OUTPUT FORMAT:\n<Thinking> [Your detailed spatial rationale] </Thinking>"
        )

        response = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": 4096, "temperature": 0.3},
            safety_settings={
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        text = response.text
        if "<Thinking>" in text:
            thinking = text.split("<Thinking>")[1].split("</Thinking>")[0].strip()
            return building_name, thinking
        return building_name, None
    except Exception as e:
        if "429" in str(e):
            print(f"\n[!!!] QUOTA EXHAUSTED. Shutting down...")
            shutdown_event.set()
        else:
            print(f"   [ERROR] {building_name}: {e}")
        return building_name, None

def main():
    processed_names = get_processed_names()
    print(f"Detected {len(processed_names)} Master Class rationales.")

    all_files = sorted([f for f in os.listdir(SRC_DIR) if f.endswith('.txt')])
    remaining_files = [f for f in all_files if f.split(" - ")[-1].replace(".txt", "") not in processed_names]

    if not remaining_files:
        print("All rationales collected!")
        return

    print(f"Distilling {len(remaining_files)} NEW 'Master Class' rationales...")

    with open(RATIONALE_FILE, 'a', encoding='utf-8') as out_f:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_file = {executor.submit(generate_rationale, f): f for f in remaining_files}
            for future in as_completed(future_to_file):
                if shutdown_event.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                name, rationale = future.result()
                if rationale:
                    with file_lock:
                        out_f.write(json.dumps({"name": name, "rationale": rationale}) + "\n")
                        out_f.flush()
                        os.fsync(out_f.fileno())
                        print(f"   [SAVED] {name}")

if __name__ == "__main__":
    main()
