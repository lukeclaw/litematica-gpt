import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

def test_llama_compiler(prompt_text):
    model_path = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
    adapter_path = "specialized_skills/dsl_compiler_llama8b" 

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
    sample_plan = """Listen closely, Student. Before we place a single block, we must see the structure in our mind's eye. We are building a 2D pixel art representation of a Minion. I will guide you through the spatial rationale so you can bridge the gap between raw coordinates and architectural intent.

1. Footprint Analysis
I will establish a bounding box with the dimensions X=2 (Depth), Z=12 (Width), and Y=19 (Height). This is not a fully 3D hollow or solid building; it is a vertical, solid pixel art canvas. The structure is primarily flat—exactly 1 block thick along the X=0 axis. However, I will make the very bottom layer (Y=0) 2 blocks deep (X=0 and X=1) to create a tiered, extruded base. This gives the flat artwork a stable physical stand so it does not look paper-thin where it meets the ground.

2. Material Strategy
I will use a highly restricted, stylized palette to bring this pixel art to life:
- White Wool (B): This is my primary canvas. I will use it for the Minion's body, overalls, and the whites of its eyes.
- Stone (C): I will use Stone exclusively for the Minion's goggles.
- Oak Leaves (A): I will use these only at the bottom corners of the build.

3. Construction Sequence
I will build this from the ground up, layer by layer, keeping the 2D profile in mind.

At Y=0, I will lay down the foundation and the stand. I will place Oak Leaves at the far left (Z=0) and far right (Z=11) edges. In the center (Z=4 and Z=7), I will place White Wool for the Minion's feet. I will extend this entire layer to be 2 blocks deep (X=0 and X=1) to ensure the structure has a sturdy base.
"""
    test_llama_compiler(sample_plan)
