import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

def test_llama_compiler(prompt_text):
    model_path = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
    adapter_path = "specialized_skills/dsl_compiler_llama8b" 

    print(f"Loading Llama 3.1 8B with DSL Compiler adapters...")
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
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
    
    full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    print(f"Generating DSL (God Mode Checkpoint 500)...\n" + "="*20)
    
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
    # The EXACT rationale from the training set
    sample_plan = """Listen closely, Student. Before we place a single block, we must see the structure in our mind's eye. We are building a 2D pixel art representation of a Minion. I will guide you through the spatial rationale so you can bridge the gap between raw coordinates and architectural intent.

1. Footprint Analysis
I will establish a bounding box with the dimensions X=2 (Depth), Z=12 (Width), and Y=19 (Height). This is not a fully 3D hollow or solid building; it is a vertical, solid pixel art canvas. The structure is primarily flat—exactly 1 block thick along the X=0 axis. However, I will make the very bottom layer (Y=0) 2 blocks deep (X=0 and X=1) to create a tiered, extruded base. This gives the flat artwork a stable physical stand so it does not look paper-thin where it meets the ground.

2. Material Strategy
I will use a highly restricted, stylized palette to bring this pixel art to life:
- White Wool (B): This is my primary canvas. I will use it for the Minion's body, overalls, and the whites of its eyes. Wool provides a clean, matte texture that is perfect for flat pixel art.
- Stone (C): I will use Stone exclusively for the Minion's goggles. The grey, solid, slightly rugged texture of stone perfectly mimics the thick metallic frames of the goggles, creating a visual contrast against the soft wool.
- Oak Leaves (A): I will use these only at the bottom corners of the build. They act as small decorative bushes or ground anchors, framing the piece and giving it a connection to the earth.

3. Construction Sequence
I will build this from the ground up, layer by layer, keeping the 2D profile in mind.

At Y=0, I will lay down the foundation and the stand. I will place Oak Leaves at the far left (Z=0) and far right (Z=11) edges. In the center (Z=4 and Z=7), I will place White Wool for the Minion's feet. I will extend this entire layer to be 2 blocks deep (X=0 and X=1) to ensure the structure has a sturdy base.

At Y=1, I will transition to a strictly 1-block depth (X=0) for the rest of the build. I will build the ankles using White Wool directly above the feet.

At Y=2 and Y=3, I will begin forming the lower body and overalls. I will expand the White Wool outward, growing the width from 4 blocks to 6 blocks to create the curved bottom of the Minion.

From Y=4 to Y=11, I will construct the main cylindrical torso. I will rapidly expand the width to 8 blocks, then 10 blocks, until I hit the maximum width of 12 blocks between Y=6 and Y=9. This forms the fat, pill-like shape of the character. At Y=10 and Y=11, I will slightly taper the sides back to 10 blocks wide to define the upper head area.

From Y=12 to Y=15, I will construct the focal point of the art: the goggles and eyes. 
- At Y=12, I will lay a horizontal line of Stone to form the thick lower rim of the goggles, flanked by White Wool for the sides of the head.
- At Y=13 and Y=14, I will build the lenses. I will use Stone for the outer frames and the center bridge. I will fill the negative space inside these frames with White Wool to represent the large, wide-open eyes.
- At Y=15, I will cap the goggles with another horizontal line of Stone for the upper rim.

At Y=16 and Y=17, I will build the top of the head. I will use White Wool and aggressively taper the width down to 8 blocks, and finally to 4 blocks at the very top. This creates the smooth, iconic dome shape of the Minion's head.

At Y=18, I will leave the layer completely empty (Air). This acts as the spatial ceiling of our bounding box, confirming the structure is complete. 

By following this logic, I ensure that every coordinate serves a visual purpose, turning a grid of letters into a recognizable, standing piece of art."""
    test_llama_compiler(sample_plan)
