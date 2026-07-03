import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

def test_llama_compiler(prompt_text):
    model_path = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
    adapter_path = "specialized_skills/dsl_compiler_llama8b" 

    model, tokenizer = load(model_path, adapter_path=adapter_path)

    system_prompt = (
        "ROLE: You are the Lead Litematica DSL Architect. Your mission is to compile architectural plans "
        "into syntactically perfect Litematica DSL code that matches the Java Parser specification.\n\n"
        "COORDINATE SYSTEM:\n"
        "- X: Width, Y: Height (Start at 0), Z: Depth.\n\n"
        "TECHNICAL SPECIFICATION:\n"
        "1. PALETTE: 'palette' ... 'end_palette'. Map 1-char keys to block IDs: 'A = minecraft:stone'. '.' is air.\n"
        "2. GRID LAYERS: 'layer_y Y OffsetX OffsetZ'. Every subsequent line is a row of Z-depth. End with 'end_layer'.\n"
        "3. COMMANDS: 'set X Y Z BLOCK', 'fill X1 Y1 Z1 X2 Y2 Z2 BLOCK', 'box', 'carve'.\n\n"
        "CONSTRAINTS: No conversational filler. Output raw code only."
    )
    
    user_content = f"Architect's Plan:\n{prompt_text}"
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}]
    full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    print(f"--- GENERATED DSL (HYDROFLASK TEST) ---")
    sampler = make_sampler(temp=0.1)
    generate(model, tokenizer, prompt=full_prompt, max_tokens=3000, verbose=True, sampler=sampler)

if __name__ == "__main__":
    sample_plan = """PROJECT MISSION: SPATIAL RATIONALE
STRUCTURE: 'Hydroflask Replica'

1. FOOTPRINT ANALYSIS
I am building a vertical, cylindrical water bottle. The bounding box is 7x7x15 (X=0 to 6, Z=0 to 6, Y=0 to 14). The base is a 5x5 circle (rounded corners), which rises as a solid pillar before tapering into a narrow neck and capping with a lid and handle.

2. MATERIAL STRATEGY
- Cyan Wool (A): The primary powder-coated body of the flask.
- Stone (B): The metallic silver neck/rim.
- Obsidian (C): The black insulated lid.
- Iron Bars (D): The carry handle loop.

3. CONSTRUCTION SEQUENCE & LOGIC

Y=0 to Y=1 (The Reinforced Base):
I will lay down a solid 5x5 circular base using Cyan Wool (A). Corners will be Air (.) to create a rounded look.

Y=2 to Y=10 (The Main Body):
I will build a hollow 5x5 cylinder. The walls will be Cyan Wool (A), and the core (center 3x3) will be Air (.) to represent the vacuum insulation.

Y=11 (The Tapered Shoulder):
I will step the walls inward by 1 block on all sides, creating a 3x3 ring of Cyan Wool (A).

Y=12 (The Metallic Neck):
I will replace the material with Stone (B) to represent the stainless steel rim. I will maintain the 3x3 hollow ring.

Y=13 (The Insulated Lid):
I will place a solid 3x3 square of Obsidian (C) to seal the flask.

Y=14 (The Handle):
I will place a single Iron Bar (D) at the center (3,3) to act as the strap or carry loop."""
    test_llama_compiler(sample_plan)
