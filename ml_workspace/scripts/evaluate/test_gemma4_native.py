import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
import os

def test_prescriptive_thinking(prompt_text):
    model_path = "mlx-community/gemma-4-e4b-it-4bit"
    
    print(f"Loading Base Gemma 4 E4B to test PRESCRIPTIVE thinking...")
    model, tokenizer = load(model_path)
    
    # The new Three-Pillar Prescriptive Prompt
    system_prompt = (
        "<|think|> ROLE: You are the Lead Litematica DSL Architect. "
        "MISSION: Construct a step-by-step spatial rationale followed by syntactically perfect Litematica DSL code.\n\n"
        "SPATIAL RATIONALE STRUCTURE (Inside <|channel|>thought):\n"
        "1. **FOOTPRINT ANALYSIS**: Define the bounding box (X, Y, Z). Describe the structure's overall shape and orientation.\n"
        "2. **MATERIAL STRATEGY**: List every block type and assign it a unique 1-character key (A, B, C...). Explain the choice for each material.\n"
        "3. **CONSTRUCTION SEQUENCE**: Walk through the build layer-by-layer (Y=0, Y=1...). Explain the logic of where blocks are placed."
    )
    
    messages = [
        {"role": "user", "content": f"{system_prompt}\n\nBuild the {prompt_text}."}
    ]
    
    full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    print(f"--- GENERATED DSL (PRESCRIPTIVE GOD MODE) ---")
    sampler = make_sampler(temp=0.1)
    
    generate(
        model, 
        tokenizer, 
        prompt=full_prompt, 
        max_tokens=2000, 
        verbose=True, 
        sampler=sampler
    )

if __name__ == "__main__":
    test_prescriptive_thinking("Small Stone Tower")
