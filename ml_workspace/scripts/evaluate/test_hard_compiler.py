import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
import os

def test_hard_compiler(rationale_text):
    model_path = "mlx-community/gemma-4-e4b-it-4bit"
    adapter_path = "specialized_skills/gemma4_compiler_lora_v3"
    
    print(f"Loading Litematica God Mode (Checkpoint 500)...")
    model, tokenizer = load(model_path, adapter_path=adapter_path)
    
    system_prompt = (
        "ROLE: You are the Lead Litematica DSL Architect. Your mission is to compile architectural plans "
        "into syntactically perfect Litematica DSL code that matches the Java Parser specification.\n\n"
        "TECHNICAL SPECIFICATION:\n"
        "1. PALETTE: 'palette' ... 'end_palette'. Map 1-char keys to block IDs.\n"
        "2. GRID LAYERS: 'layer_y Y OffsetX OffsetZ'. Every line is a row of Z-depth. End with 'end_layer'.\n\n"
        "CONSTRAINTS:\n"
        "- Output raw code only. No conversational filler."
    )
    
    user_content = f"Architect's Plan:\n{rationale_text}"
    messages = [{"role": "user", "content": f"{system_prompt}\n\n{user_content}"}]
    full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    print(f"--- GENERATING PURE DSL (HARD TEST) ---")
    sampler = make_sampler(temp=0.1)
    
    generate(
        model, 
        tokenizer, 
        prompt=full_prompt, 
        max_tokens=3000, 
        verbose=True, 
        sampler=sampler
    )

if __name__ == "__main__":
    sample_rationale = (
        "I am building a 7x7 stone fountain with a central 3x3 pillar, 4 blocks high.\n"
        "1. FOOTPRINT: 7x7 base (X=0 to 6, Z=0 to 6).\n"
        "2. MATERIALS: A = minecraft:stone, B = minecraft:water, C = minecraft:quartz_block, . = minecraft:air.\n"
        "3. SEQUENCE:\n"
        "Y=0: Solid 7x7 Stone floor.\n"
        "Y=1: 7x7 Stone perimeter wall (1 block thick). Interior (5x5) is filled with Water. At the absolute center (3,3), place a single Quartz Block.\n"
        "Y=2: Same as Y=1, but the outer perimeter is now Air (hollow). Maintain the water and the central Quartz pillar.\n"
        "Y=3: Cap the central 3x3 area with Quartz Blocks to form the fountain head."
    )
    test_hard_compiler(sample_rationale)
