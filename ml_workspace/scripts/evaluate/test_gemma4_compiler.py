import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
import os

def test_pure_compiler(rationale_text):
    model_path = "mlx-community/gemma-4-e4b-it-4bit"
    adapter_path = "specialized_skills/gemma4_compiler_lora"
    
    print(f"Loading Gemma 4 Pure Compiler (Latest Checkpoint)...")
    model, tokenizer = load(model_path, adapter_path=adapter_path)
    
    # EXACT Pure Compiler System Prompt
    system_prompt = (
        "ROLE: You are the Lead Litematica DSL Architect. Your mission is to compile architectural plans "
        "into syntactically perfect Litematica DSL code that matches the Java Parser specification.\n\n"
        "COORDINATE SYSTEM:\n"
        "- X: Width, Y: Height (Start at 0), Z: Depth.\n\n"
        "TECHNICAL SPECIFICATION:\n"
        "1. PALETTE: 'palette' ... 'end_palette'. Map 1-char keys to block IDs.\n"
        "2. GRID LAYERS: 'layer_y Y OffsetX OffsetZ'. Every line is a row of Z-depth. End with 'end_layer'.\n\n"
        "CONSTRAINTS:\n"
        "- Output raw code only. No conversational filler."
    )
    
    user_content = f"Architect's Plan:\n{rationale_text}"
    
    messages = [{"role": "user", "content": f"{system_prompt}\n\n{user_content}"}]
    full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    print(f"--- GENERATED PURE DSL ---")
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
    # Test with a precise rationale
    sample_rationale = (
        "I am building a 3x3 stone tower, 3 blocks high.\n"
        "1. FOOTPRINT: 3x3 base (X=0 to 2, Z=0 to 2).\n"
        "2. MATERIALS: A = minecraft:stone, . = minecraft:air.\n"
        "3. SEQUENCE: Y=0 is solid Stone. Y=1 is hollow with air at (1,1). Y=2 is solid Stone."
    )
    test_pure_compiler(sample_rationale)
