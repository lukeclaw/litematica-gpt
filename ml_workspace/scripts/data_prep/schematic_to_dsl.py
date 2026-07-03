import nbtlib
import os
import sys
import math

# Mapping for common legacy numeric IDs to string IDs
LEGACY_MAPPING = {
    0: "minecraft:air", 1: "minecraft:stone", 2: "minecraft:grass_block", 3: "minecraft:dirt",
    4: "minecraft:cobblestone", 5: "minecraft:oak_planks", 7: "minecraft:bedrock",
    8: "minecraft:water", 9: "minecraft:water", 10: "minecraft:lava", 11: "minecraft:lava",
    12: "minecraft:sand", 13: "minecraft:gravel", 14: "minecraft:gold_ore", 15: "minecraft:iron_ore",
    16: "minecraft:coal_ore", 17: "minecraft:oak_log", 18: "minecraft:oak_leaves", 20: "minecraft:glass",
    35: "minecraft:white_wool", 41: "minecraft:gold_block", 42: "minecraft:iron_block",
    43: "minecraft:stone_slab", 44: "minecraft:stone_slab", 45: "minecraft:bricks",
    46: "minecraft:tnt", 47: "minecraft:bookshelf", 48: "minecraft:mossy_cobblestone",
    49: "minecraft:obsidian", 50: "minecraft:torch", 51: "minecraft:fire", 54: "minecraft:chest",
    56: "minecraft:diamond_ore", 57: "minecraft:diamond_block", 58: "minecraft:crafting_table",
    61: "minecraft:furnace", 95: "minecraft:white_stained_glass", 155: "minecraft:quartz_block"
}

def unpack_litematic(block_states, bits_per_entry, total_blocks):
    unpacked = []
    mask = (1 << bits_per_entry) - 1
    for i in range(total_blocks):
        bit_start = i * bits_per_entry
        idx_start, off_start = bit_start // 64, bit_start % 64
        idx_end = (bit_start + bits_per_entry - 1) // 64
        if idx_start == idx_end:
            val = (block_states[idx_start] >> off_start) & mask
        else:
            val = (block_states[idx_start] >> off_start) | (block_states[idx_end] << (64 - off_start))
            val &= mask
        unpacked.append(val)
    return unpacked

def convert_litematic(root):
    regions = root.get('Regions', {})
    dsl_output = []
    global_palette = {'minecraft:air': '.'}
    char_code = 65

    def get_char(bid):
        nonlocal char_code
        if bid in global_palette: return global_palette[bid]
        c = chr(char_code)
        char_code += 1
        if char_code == 91: char_code = 97
        global_palette[bid] = c
        return c

    for rname, region in regions.items():
        size = region['Size']
        w, h, d = abs(size['x']), abs(size['y']), abs(size['z'])
        palette = region['BlockStatePalette']
        unsigned_states = [(s + (1 << 64) if s < 0 else s) for s in region['BlockStates']]
        indices = unpack_litematic(unsigned_states, max(2, math.ceil(math.log2(len(palette)))), w*h*d)
        local_map = {i: get_char(entry.get('Name', 'minecraft:air')) for i, entry in enumerate(palette)}
        
        dsl_output.append(f"# Region: {rname}")
        for y in range(h):
            dsl_output.append(f"layer_y {y} 0 0")
            for z in range(d):
                dsl_output.append("".join(local_map[indices[(y*d+z)*w+x]] for x in range(w)))
            dsl_output.append("end_layer")
            
    header = ["palette"] + [f"{c} = {bid}" for bid, c in global_palette.items() if c != "."] + [". = minecraft:air", "end_palette"]
    return "\n".join(header + dsl_output)

def convert_schematic(root):
    w, h, d = int(root.get('Width', 0)), int(root.get('Height', 0)), int(root.get('Length', 0))
    blocks = root.get('Blocks')
    if blocks is None: raise ValueError("Blocks tag missing")
    
    dsl_output = []
    global_palette = {'minecraft:air': '.'}
    char_code = 65

    def get_char(bid):
        nonlocal char_code
        if bid in global_palette: return global_palette[bid]
        c = chr(char_code)
        char_code += 1
        if char_code == 91: char_code = 97
        global_palette[bid] = c
        return c

    for y in range(h):
        dsl_output.append(f"layer_y {y} 0 0")
        for z in range(d):
            row = ""
            for x in range(w):
                idx = (y * d + z) * w + x
                if idx >= len(blocks): break
                b_val = blocks[idx]
                if b_val < 0: b_val += 256
                row += get_char(LEGACY_MAPPING.get(b_val, "minecraft:stone"))
            dsl_output.append(row)
        dsl_output.append("end_layer")

    header = ["palette"] + [f"{c} = {bid}" for bid, c in global_palette.items() if c != "."] + [". = minecraft:air", "end_palette"]
    return "\n".join(header + dsl_output)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 schematic_to_dsl.py <input_dir> <output_dir>")
        sys.exit(1)
        
    input_dir, output_dir = sys.argv[1], sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)
    
    for f in os.listdir(input_dir):
        ext = os.path.splitext(f)[1]
        if ext in [".litematic", ".schematic"]:
            try:
                print(f"Converting {f}...")
                nbt = nbtlib.load(os.path.join(input_dir, f))
                dsl = convert_litematic(nbt) if ext == ".litematic" else convert_schematic(nbt)
                out_path = os.path.join(output_dir, f.replace(ext, ".txt"))
                with open(out_path, "w") as out:
                    out.write(dsl)
            except Exception as e:
                print(f"FAILED {f}: {e}")
