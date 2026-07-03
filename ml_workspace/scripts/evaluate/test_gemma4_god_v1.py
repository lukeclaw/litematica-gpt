import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
import os

def test_god_mode_v1(prompt_text):
    model_path = "mlx-community/gemma-4-e4b-it-4bit"
    adapter_path = "specialized_skills/gemma4_think_compiler_lora"
    
    print(f"Loading Gemma 4 God Mode (Checkpoint 100)...")
    model, tokenizer = load(model_path, adapter_path=adapter_path)
    
    # Using the EXACT Prescriptive System Prompt from the training set
    system_prompt = (
        "<|think|> ROLE: You are the Lead Litematica DSL Architect. "
        "MISSION: Construct a step-by-step spatial rationale followed by syntactically perfect Litematica DSL code.\n\n"
        "SPATIAL RATIONALE STRUCTURE (Inside <|channel|>thought):\n"
        "1. **FOOTPRINT ANALYSIS**: Define the bounding box (X, Y, Z). Describe the structure's overall shape and orientation.\n"
        "2. **MATERIAL STRATEGY**: List every block type and assign it a unique 1-character key (A, B, C...). Explain the choice for each material.\n"
        "3. **CONSTRUCTION SEQUENCE**: Walk through the build layer-by-layer (Y=0, Y=1...). Explain the logic of where blocks are placed."
    )
    
    user_content = f"{system_prompt}\n\nBuild the {prompt_text}."
    
    messages = [{"role": "user", "content": user_content}]
    full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    print(f"--- GENERATED OUTPUT (GOD MODE V1) ---")
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
    # Test with a classic build from the training set
    test_god_mode_v1("Small Stone Tower")
