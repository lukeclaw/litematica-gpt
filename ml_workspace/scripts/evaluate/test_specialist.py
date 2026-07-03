import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

def test_dsl_specialist(plan_text):
    model_path = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
    adapter_path = "specialized_skills/dsl_compiler_llama8b" 

    print(f"Loading Rank-128 DSL Compiler Specialist...")
    model, tokenizer = load(model_path, adapter_path=adapter_path)

    system_prompt = (
        "ROLE: You are the Lead Litematica DSL Architect. Your mission is to compile architectural plans "
        "into syntactically perfect Litematica DSL code that matches the Java Parser specification.\n\n"
        "TECHNICAL SPECIFICATION:\n"
        "1. PALETTE: 'palette' ... 'end_palette'. Map 1-char keys to block IDs: 'A = minecraft:stone'. '.' is air.\n"
        "2. GRID LAYERS: 'layer_y Y OffsetX OffsetZ'. Every subsequent line is a row of Z-depth. End with 'end_layer'.\n"
        "3. COMMANDS: 'set X Y Z BLOCK', 'fill X1 Y1 Z1 X2 Y2 Z2 BLOCK', 'box', 'carve'.\n\n"
        "CONSTRAINTS: No conversational filler. Output raw code only."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Architect's Plan:\n{plan_text}"}
    ]
    
    full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    # FORCED START: We put the model in the middle of a palette
    primed_prompt = full_prompt + "palette\nA = minecraft:stone\n"

    print(f"Testing the model with a 'Forced Start'...\n" + "="*20)
    print("palette\nA = minecraft:stone")
    
    sampler = make_sampler(temp=0.0)
    
    generate(
        model, 
        tokenizer, 
        prompt=primed_prompt, 
        max_tokens=1000, 
        verbose=True,
        sampler=sampler
    )

if __name__ == "__main__":
    test_plan = (
        "I will construct a Small Stone Vault using the following plan.\n"
        "1. **Palette**: I will define stone ('A'), a chest ('B'), and air ('.').\n"
        "2. **Foundation**: I will create a solid 5x5 stone foundation at Y=0.\n"
        "3. **Interior**: I will place a single chest at the center (2,1,2).\n"
        "4. **Walls**: I will raise stone walls 3 blocks high at the perimeter."
    )
    test_dsl_specialist(test_plan)
