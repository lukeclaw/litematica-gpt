import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
import os
import json

def test_dual_expert_base(rationale_name):
    model_path = "mlx-community/gemma-4-e4b-it-4bit"
    
    print(f"Loading Base Gemma 4 E4B to test DUAL EXPERT approach...")
    model, tokenizer = load(model_path)
    
    # 1. Get a real rationale from the dataset
    rationale = ""
    with open('dataset/synthetic_rationales.jsonl', 'r') as f:
        for line in f:
            data = json.loads(line)
            if rationale_name in data['name']:
                rationale = data['rationale']
                break
    
    if not rationale:
        print(f"Could not find rationale for {rationale_name}")
        return

    # 2. Use the Llama "God Mode" System Prompt
    system_prompt = (
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
    
    user_content = f"Architect's Plan:\n{rationale}"
    
    messages = [
        {"role": "user", "content": f"{system_prompt}\n\n{user_content}"}
    ]
    
    full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    print(f"--- GENERATED DSL (DUAL EXPERT BASE MODEL) ---")
    sampler = make_sampler(temp=0.1)
    
    generate(
        model, 
        tokenizer, 
        prompt=full_prompt, 
        max_tokens=2048, 
        verbose=True, 
        sampler=sampler
    )

if __name__ == "__main__":
    # Test with the Minion rationale we found earlier
    test_dual_expert_base("Minion")
