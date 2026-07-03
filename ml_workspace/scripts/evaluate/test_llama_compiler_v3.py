import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

def test_llama_compiler(prompt_text):
    model_path = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
    adapter_path = "specialized_skills/gemma4_compiler_lora_v2" 

    print(f"Loading Llama 3.1 8B with DSL Compiler adapters...")
    model, tokenizer = load(model_path, adapter_path=adapter_path)

    system_prompt = (
        "ROLE: You are the Lead Litematica DSL Architect. Your mission is to compile architectural plans into syntactically perfect Litematica DSL code that matches the Java Parser specification.\n\n"
        "COORDINATE SYSTEM:\n"
        "- X: Width, Y: Height (Start at 0), Z: Depth.\n\n"
        "TECHNICAL SPECIFICATION:\n"
        "1. PALETTE: 'palette' ... 'end_palette'. Map 1-char keys to block IDs: 'A = minecraft:stone'. '.' is air.\n"
        "2. GRID LAYERS: 'layer_y Y OffsetX OffsetZ'. Every subsequent line is a row of Z-depth. End with 'end_layer'.\n"
        "3. COMMANDS: 'set X Y Z BLOCK', 'fill X1 Y1 Z1 X2 Y2 Z2 BLOCK', 'box', 'carve'.\n\n"
        "CONSTRAINTS: No conversational filler. Output raw code only."
    )
    
    user_content = f"Architect's Plan:\n{prompt_text}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
    
    full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    print(f"Generating DSL...\n" + "="*20)
    
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
    sample_plan = """PROJECT MISSION: SPATIAL RATIONALE
STRUCTURE: 'Cross Foundation'

1. FOOTPRINT ANALYSIS
A simple 3x3 foundation.

2. MATERIAL STRATEGY
- Stone (A)
- Air (.)

3. CONSTRUCTION SEQUENCE & LOGIC

Y=0:
I will place Stone (A) in a cross pattern. 
Stone at (1,0), (0,1), (1,1), (2,1), and (1,2).
All other blocks are Air (.).
"""
    test_llama_compiler(sample_plan)
