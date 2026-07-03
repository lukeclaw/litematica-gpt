import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
import os

def test_comparison(prompt_text):
    model_path = "mlx-community/gemma-4-e4b-it-4bit"
    adapter_path = "specialized_skills/gemma4_think_compiler_lora"
    
    # 1. Test Base Model
    print("\n" + "="*50)
    print("TESTING BASE MODEL (No Training)")
    print("="*50)
    
    model_base, tokenizer_base = load(model_path)
    
    system_prompt = (
        "ROLE: You are the Lead Litematica DSL Architect. Your mission is to construct Minecraft architectural plans "
        "and compile them into syntactically perfect Litematica DSL code that matches the Java Parser specification.\n\n"
        "COORDINATE SYSTEM:\n"
        "- X: Width, Y: Height (Start at 0), Z: Depth.\n\n"
        "TECHNICAL SPECIFICATION:\n"
        "1. PALETTE: 'palette' ... 'end_palette'. Map 1-char keys to block IDs: 'A = minecraft:stone'. '.' is air.\n"
        "2. GRID LAYERS: 'layer_y Y OffsetX OffsetZ'. Every subsequent line is a row of Z-depth. End with 'end_layer'.\n"
        "3. COMMANDS: 'set X Y Z BLOCK', 'fill X1 Y1 Z1 X2 Y2 Z2 BLOCK', 'box', 'carve'.\n\n"
        "CONSTRAINTS:\n"
        "- You MUST output a <think> block first, detailing the Footprint, Materials, and Layer-by-Layer sequence.\n"
        "- Immediately after the </think> tag, output the raw DSL code. No other conversational text."
    )
    
    messages = [
        {"role": "user", "content": f"{system_prompt}\n\nBuild the {prompt_text}."}
    ]
    full_prompt = tokenizer_base.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    sampler = make_sampler(temp=0.1)
    generate(model_base, tokenizer_base, prompt=full_prompt, max_tokens=1000, verbose=True, sampler=sampler)

    # 2. Test Adapter Model (Checkpoint 100)
    print("\n" + "="*50)
    print("TESTING ADAPTER MODEL (100 Iterations)")
    print("="*50)
    
    # Load with adapter
    model_adapter, tokenizer_adapter = load(model_path, adapter_path=adapter_path)
    
    # Use the same prompt
    full_prompt_adapter = tokenizer_adapter.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    generate(model_adapter, tokenizer_adapter, prompt=full_prompt_adapter, max_tokens=1000, verbose=True, sampler=sampler)

if __name__ == "__main__":
    test_comparison("Small Stone Tower")
