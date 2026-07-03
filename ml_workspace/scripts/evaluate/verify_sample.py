import nbtlib
import os

def count_blocks_in_dsl(dsl_path):
    with open(dsl_path, 'r') as f:
        lines = f.readlines()
    
    count = 0
    in_palette = False
    in_layer = False
    for line in lines:
        line = line.strip()
        if line == 'palette': in_palette = True; continue
        if line == 'end_palette': in_palette = False; continue
        if line == 'end_layer': in_layer = False; continue
        if in_palette or not line or line.startswith('#'): continue
        
        if line.startswith('set'):
            count += 1
        elif line.startswith('fill') or line.startswith('box'):
            parts = line.split()
            x1, y1, z1, x2, y2, z2 = map(int, parts[1:7])
            count += (abs(x2-x1)+1) * (abs(y2-y1)+1) * (abs(z2-z1)+1)
        elif not line.startswith('layer_y'):
            # It's a dense layer row
            count += len(line.replace('.', ''))
    return count

def count_blocks_in_schematic(schem_path):
    nbt = nbtlib.load(schem_path)
    if schem_path.endswith('.litematic'):
        # Litematics are complex to count perfectly without unpacking fully, 
        # but we can check if it loads.
        return "N/A (Litematic)"
    else:
        # Standard schematic
        blocks = nbt.get('Blocks', [])
        return sum(1 for b in blocks if b != 0)

samples = [
    ("343 - Cottage.txt", "343.schematic"),
    ("11292 - Prison Mine.txt", "11292.schematic"),
    ("17428 - Medieval House with Tower.txt", "17428.litematic")
]

for dsl_name, schem_name in samples:
    dsl_path = os.path.join("dataset/dsl_final", dsl_name)
    schem_path = os.path.join("/Users/josehugopineda/Downloads/Schematics", schem_name)
    
    if os.path.exists(dsl_path) and os.path.exists(schem_path):
        dsl_count = count_blocks_in_dsl(dsl_path)
        schem_count = count_blocks_in_schematic(schem_path)
        print(f"Sample: {dsl_name}")
        print(f"  DSL Blocks: {dsl_count}")
        print(f"  Orig Blocks: {schem_count}")
        print(f"  Match: {dsl_count == schem_count if isinstance(schem_count, int) else 'N/A'}")
