import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
import os

def test_novel_generalization():
    model_path = "mlx-community/gemma-4-e4b-it-4bit"
    adapter_path = "specialized_skills/gemma4_compiler_lora_v2"
    
    model, tokenizer = load(model_path, adapter_path=adapter_path)
    
    system_prompt = (
        "ROLE: You are the Lead Litematica DSL Architect. Your mission is to compile architectural plans "
        "into syntactically perfect Litematica DSL code.\n\n"
        "CONSTRAINTS: Output raw code only. No conversational filler."
    )
    
    # A COMPLETELY UNIQUE RATIONALE
    novel_rationale = (
        "I am building a 'Floating Cloud Palace'.\n"
        "1. FOOTPRINT: 5x5 circular platform (X=0 to 4, Z=0 to 4).\n"
        "2. MATERIALS: A = minecraft:white_wool, B = minecraft:gold_block, . = minecraft:air.\n"
        "3. SEQUENCE:\n"
        "Y=0: Circular White Wool platform (Corners are Air).\n"
        "Y=1: 3x3 Gold Block core in the center (X=1 to 3, Z=1 to 3).\n"
        "Y=2: A single Gold Block at the absolute center (2,2)."
    )
    
    user_content = f"Architect's Plan:\n{novel_rationale}"
    messages = [{"role": "user", "content": f"{system_prompt}\n\n{user_content}"}]
    full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    print(f"--- GENERATING NOVEL DSL (GENERALIZATION TEST) ---")
    sampler = make_sampler(temp=0.1)
    generate(model, tokenizer, prompt=full_prompt, max_tokens=1000, verbose=True, sampler=sampler)

if __name__ == "__main__":
    test_novel_generalization()
