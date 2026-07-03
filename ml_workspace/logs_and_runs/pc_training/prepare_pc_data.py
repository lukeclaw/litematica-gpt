import json
import os

def get_specialist_prompt():
    return (
        "ROLE: You are the Lead Litematica DSL Architect. Your mission is to compile architectural plans "
        "into syntactically perfect Litematica DSL code that matches the Java Parser specification.\n\n"
        "COORDINATE SYSTEM:\n"
        "- X: Width, Y: Height (Start at 0), Z: Depth.\n\n"
        "TECHNICAL SPECIFICATION:\n"
        "1. PALETTE: 'palette' ... 'end_palette'. Map 1-char keys to block IDs: 'A = minecraft:stone'. '.' is air.\n"
        "2. GRID LAYERS: 'layer_y Y OffsetX OffsetZ'. Every subsequent line is a row of Z-depth. "
        "Use single characters from your palette. End with 'end_layer'.\n"
        "3. COMMANDS (Format: X Y Z):\n"
        "   - 'set X Y Z BLOCK': Single block placement.\n"
        "   - 'fill X1 Y1 Z1 X2 Y2 Z2 BLOCK': Solid volume.\n"
        "   - 'box X1 Y1 Z1 X2 Y2 Z2 BLOCK': Hollow shell (6 faces only).\n"
        "   - 'carve X1 Y1 Z1 X2 Y2 Z2': Fill volume with air.\n"
        "4. CURSOR (Relative):\n"
        "   - 'cursor_move dX dY dZ': Move the build-tip.\n"
        "   - 'cursor_set BLOCK': Place at current build-tip.\n\n"
        "CONSTRAINTS:\n"
        "- Block IDs MUST use the 'minecraft:' prefix.\n"
        "- Do NOT use conversational filler. Output raw code only.\n"
        "- Use 'fill/box' for bulk and 'layer_y' for precision logic."
    )

def prepare_pc_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    rationale_file = os.path.join(base_dir, "data/rationales/synthetic_rationales.jsonl")
    dsl_dir = os.path.join(base_dir, "data/dsl")
    output_path = os.path.join(base_dir, "train.jsonl")

    print(f"Mapping DSL files from: {dsl_dir}")
    dsl_map = {}
    for filename in os.listdir(dsl_dir):
        if filename.endswith(".txt"):
            clean_name = filename.split(" - ")[-1].replace(".txt", "")
            dsl_map[clean_name] = filename

    samples = []
    print(f"Reading rationales from {rationale_file}...")
    with open(rationale_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                name = data["name"]
                rationale = data["rationale"]
                
                if name in dsl_map:
                    with open(os.path.join(dsl_dir, dsl_map[name]), 'r', encoding='utf-8') as code_f:
                        dsl_code = code_f.read()
                    
                    samples.append({
                        "messages": [
                            {"role": "system", "content": get_specialist_prompt()},
                            {"role": "user", "content": f"Architect's Plan:\n{rationale}"},
                            {"role": "assistant", "content": dsl_code}
                        ]
                    })
            except: continue

    print(f"Writing {len(samples)} Verified Architect samples to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        for s in samples:
            f.write(json.dumps(s) + '\n')

    print("--- VERIFIED DATA PREP COMPLETE ---")

if __name__ == "__main__":
    prepare_pc_data()
