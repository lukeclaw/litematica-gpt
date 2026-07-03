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
    sample_plan = """As the Master Teacher, I will guide you through the spatial visualization of the 'Default Jungle Temple (Facing South)'. Before we look at a single coordinate, I want you to close your eyes and picture an ancient, overgrown ziggurat hidden deep within a jungle. 

Footprint Analysis:
I will build a tiered, pyramidal structure. The total bounding box is 12 blocks wide (X-axis), 15 blocks deep (Z-axis), and 14 blocks high (Y-axis, from 0 to 13). The structure is hollow, containing a maze of corridors and hidden rooms, but its exterior steps inward as it rises, creating three distinct tiers. Because it faces South, the entrance and main corridor alignment will be oriented along the Z-axis.

Material Strategy:
I will use a chaotic, randomized mix of Cobblestone and Mossy Cobblestone for 90% of the build. I should do this to simulate centuries of jungle overgrowth and weathering. 
I will use Stone blocks strategically. In a standard Jungle Temple, Stone is used to conceal or support the redstone mechanisms (like levers, sticky pistons, and dispensers). I will place Stone where the puzzle walls and trap corridors are located.\nI will use Chests as the focal points of the interior\u2014the ultimate reward for navigating the temple's traps. 

Construction Sequence:
At Y=0 (The Foundation): I will lay down a completely solid 12x15 foundation of mixed cobblestone and mossy cobblestone. I must do this to ground the temple into the jungle floor and prevent players from easily digging underneath the traps.

At Y=1 to Y=3 (The Trap Maze): I will build the thick outer walls of the first floor. Inside, I will carve out a hollow maze. At Y=1, I will place two Chests. I will place the first chest near the front (Z=3), hidden behind a wall of Stone that represents the lever puzzle. I will place the second chest at the far back (Z=10), at the end of a long hallway where the tripwire traps would normally be. I will use Stone blocks throughout these layers to map out the central dividing walls that house the hidden mechanisms.

At Y=4 (The First Ceiling): I will cap the first floor with a nearly solid layer of cobblestone variants. This layer serves a dual purpose: it is the ceiling that seals the dark trap rooms below, and the floor for the second tier above.

At Y=5 to Y=6 (The Second Tier): I will step the footprint inward. I will leave a 2-block margin of empty air on the left, right, front, and back. This creates the first visible "step" of our ziggurat. I will leave the center of this tier hollow to form the upper viewing room.

At Y=7 (The First Overhang): I will build a solid roof for the second tier, but I will extend it outward by one block in all directions. I should do this to create a distinct architectural lip or cornice, which adds depth and casts shadows on the walls below.

At Y=8 to Y=9 (The Third Tier): I will step the walls inward once again, creating an even smaller hollow room. I will leave small gaps in these walls to act as windows or arrow slits, allowing a player standing inside to look out over the jungle canopy.

At Y=10 (The Second Overhang): I will cap the third tier with another solid roof layer, once again overhanging the walls beneath it by one block to maintain the architectural theme.

At Y=11 to Y=12 (The Altar Tower): I will build the final, smallest tier. This is a compact, hollow 6x6 structure sitting in the dead center of the roof. It serves as the temple's peak.

At Y=13 (The Crown): I will place a sparse arrangement of blocks around the edges of the top tower. I will use these to form decorative crenellations and small pillars, completing the ancient, fortress-like silhouette of the temple against the sky."""
    test_llama_compiler(sample_plan)
