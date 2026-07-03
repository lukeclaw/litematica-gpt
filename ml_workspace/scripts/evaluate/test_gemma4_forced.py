import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
import os

def test_forced_thinking(prompt_text):
    model_path = "mlx-community/gemma-4-e4b-it-4bit"
    adapter_path = "specialized_skills/gemma4_think_compiler_lora"
    
    print(f"Loading Model with Adapter (Step 100)...")
    model, tokenizer = load(model_path, adapter_path=adapter_path)
    
    system_prompt = (
        "ROLE: You are the Lead Litematica DSL Architect. Your mission is to construct Minecraft architectural plans "
        "and compile them into syntactically perfect Litematica DSL code that matches the Java Parser specification.\n\n"
        "TECHNICAL SPECIFICATION:\n"
        "1. PALETTE: 'palette' ... 'end_palette'. Map 1-char keys to block IDs.\n"
        "2. GRID LAYERS: 'layer_y Y OffsetX OffsetZ'.\n\n"
        "CONSTRAINTS:\n"
        "- You MUST output a <think> block first, detailing the Footprint, Materials, and Layer-by-Layer sequence."
    )
    
    # Gemma 4 Prompt Construction
    user_content = f"{system_prompt}\n\nBuild the {prompt_text}."
    
    # We manually build the prompt to "force" the assistant to start with <think>
    # This bypasses the base model's default <|channel|> logic
    full_prompt = (
        f"<start_of_turn>user\n{user_content}<end_of_turn>\n"
        f"<start_of_turn>model\n<think>\n" # This is the "Forced Thinking" flag
    )

    print(f"--- GENERATED DSL (FORCED THINKING) ---")
    sampler = make_sampler(temp=0.1)
    
    # Note: we use prompt=full_prompt directly, bypassing chat_template
    generate(
        model, 
        tokenizer, 
        prompt=full_prompt, 
        max_tokens=2000, 
        verbose=True, 
        sampler=sampler
    )

if __name__ == "__main__":
    test_forced_thinking("Small Stone Tower")
