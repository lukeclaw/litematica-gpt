import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

def test_llama_compiler_surgical(prompt_text):
    model_path = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
    adapter_path = "specialized_skills/dsl_compiler_llama8b" 

    print(f"Loading Llama 3.1 8B with DSL Compiler adapters...")
    model, tokenizer = load(model_path, adapter_path=adapter_path)

    # Using the EXACT system prompt from the training data
    system_prompt = "ROLE: You are the Lead Litematica DSL Architect. Your mission is to compile architectural plans into syntactically perfect Litematica DSL code that matches the Java Parser specification.\n\nCOORDINATE SYSTEM:\n- X: Width, Y: Height (Start at 0), Z: Depth.\n\nTECHNICAL SPECIFICATION:\n1. PALETTE: 'palette' ... 'end_palette'. Map 1-char keys to block IDs: 'A = minecraft:stone'. '.' is air.\n2. GRID LAYERS: 'layer_y Y OffsetX OffsetZ'. Every subsequent line is a row of Z-depth. End with 'end_layer'.\n3. COMMANDS: 'set X Y Z BLOCK', 'fill X1 Y1 Z1 X2 Y2 Z2 BLOCK', 'box', 'carve'.\n\nCONSTRAINTS: No conversational filler. Output raw code only."
    
    # Using the EXACT User prefix
    user_content = f"Architect's Plan:\n{prompt_text}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
    
    full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    print(f"Generating DSL (with repetition penalty)...")
    
    # Low temp + repetition penalty to prevent the ".." loop
    sampler = make_sampler(temp=0.1)
    
    generate(
        model, 
        tokenizer, 
        prompt=full_prompt, 
        max_tokens=500, # Short limit to catch loops early
        verbose=True,
        sampler=sampler,
        repetition_penalty=1.2,
        repetition_context_size=20
    )

if __name__ == "__main__":
    # Test with the simplest possible instruction
    sample_plan = "Build a 1x1x1 cube of Stone at the origin. Palette: A = minecraft:stone."
    test_llama_compiler_surgical(sample_plan)
