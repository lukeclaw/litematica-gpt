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

    print(f"--- GENERATED DSL (Checkpoint 1500) ---")
    sampler = make_sampler(temp=0.1)
    generate(model, tokenizer, prompt=full_prompt, max_tokens=3000, verbose=True, sampler=sampler)

if __name__ == "__main__":
    sample_plan = """Footprint Analysis:
The structure occupies a 17x17 footprint (X=0 to 16, Z=0 to 16) and reaches a height of 23 blocks (Y=0 to 22). It is a tiered, mostly hollow build that combines organic shapes with industrial geometry. The lower section is a narrow, hollow shaft that flares out into a wider, hollow main cabin. A distinct, tall mechanical pillar runs up the northern edge (Z=1), featuring a massive horizontal crossbeam.

Material Strategy:
I will use a blend of natural and industrial materials to capture the "Mining Tree House" aesthetic. 
- Grass (A) and Dirt (B) will anchor the base to the landscape.
- Stone (C) and Cobblestone (D) will form the rugged, heavy foundation, the central mining shaft, and the roof. 
- Oak Planks (E) and Oak Logs (G) will provide the "tree house" warmth, used for the living floors and structural corner pillars.
- Quartz Blocks (F) will be used exclusively on the northern pillar and crossbeam. In this rustic context, the stark white quartz represents refined mechanical components, likely a mining crane or drill rig.
- Stone Slabs (I) will allow me to create a smooth, sloped roof over the main cabin.
- Torches (H) will provide essential lighting in the dark mining spaces.

Construction Sequence & Logic:

Layer Y=0: I will lay down a 17x17 circular earthen base. I will use dirt for the core and grass for the outer edges to naturally blend the structure into the ground.

Layer Y=1: I will build the primary foundation. I will use an outer ring of Stone, an inner ring of Cobblestone, and fill the core with Oak Planks. This creates a sturdy, reinforced floor for the mining shaft.

Layers Y=2 to Y=4: I will construct the lower "trunk" of the tree house. This is a hollow Cobblestone shaft (roughly 7x7) that acts as the main vertical support and access chute. I will mix in occasional Stone blocks to give the walls a weathered, textured look.

Layer Y=5: I will build a transition collar. I will use Stone and Cobblestone to flare the structure outward, creating a sturdy corbel to support the wider cabin above. I will also place the first blocks of the northern mechanical pillar at Z=1.

Layers Y=6 to Y=7: I will establish the main cabin. At Y=7, I will lay down an Oak Plank floor to serve as the primary living/working space. I will place Oak Logs at the corners to act as structural timber framing, and use Cobblestone for the walls. Meanwhile, I will continue building the Quartz and Stone mechanical pillar on the northern edge.

Layers Y=8 to Y=11: I will raise the walls of the main cabin. I will keep the center hollow for interior space. I will place Torches on the southern wall at Y=9 to illuminate the entrance area. The northern mechanical pillar continues to rise independently.

Layer Y=12: I will cap the main cabin with an Oak Plank ceiling. I will intentionally leave a small air gap on the eastern side to serve as a ladder hole or access hatch. 

Layer Y=13: I will construct a massive horizontal crossbeam at the northern edge (Z=1) spanning the entire width of the build (X=0 to 16). I will use a striking combination of Quartz, Stone, and Logs. This acts as the heavy arm of a mining crane or a structural suspension rig.

Layers Y=14 to Y=17: I will build the roof over the main cabin. I will use Stone and Stone Slabs to create a tiered, sloping roof that tapers inward to a peak at Y=17. This heavy stone roof protects the cabin from falling mining debris.

Layers Y=18 to Y=21: The main cabin is complete, but I will continue extending the northern Quartz and Stone pillar upward. This acts as the towering mast of the crane or an exhaust stack for the mining operations, capping it off with Stone at Y=21.

Layer Y=22: Finally, I will place four single Stone blocks at the absolute corners of the 17x17 grid (X=0/16, Z=0/16). These serve as aerial rigging anchors or bounding markers for the schematic's airspace."""
    test_llama_compiler(sample_plan)
