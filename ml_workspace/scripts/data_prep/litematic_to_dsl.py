import nbtlib
import os
import sys
import math

def unpack_blockstates(block_states, bits_per_entry, total_blocks):
    """Unpacks bit-packed block states from Litematica's LongArray correctly."""
    unpacked = []
    mask = (1 << bits_per_entry) - 1
    
    for i in range(total_blocks):
        bit_start = i * bits_per_entry
        index_start = bit_start // 64
        offset_start = bit_start % 64
        
        index_end = (bit_start + bits_per_entry - 1) // 64
        
        if index_start == index_end:
            val = (block_states[index_start] >> offset_start) & mask
        else:
            # Spans across two longs
            bits_in_first = 64 - offset_start
            val = (block_states[index_start] >> offset_start)
            val |= (block_states[index_end] << bits_in_first)
            val &= mask
            
        unpacked.append(val)
        
    return unpacked

def convert_to_dsl(file_path):
    nbt_file = nbtlib.load(file_path)
    root = nbt_file
    
    # Litematica metadata
    metadata = root.get('Metadata', {})
    regions = root.get('Regions', {})
    
    dsl_output = []
    
    # Global Palette Collection
    global_palette_map = {} # block_id -> char
    char_code = 65 # Start with 'A'
    
    def get_char():
        nonlocal char_code
        c = chr(char_code)
        char_code += 1
        if char_code == 91: char_code = 97 # Skip to 'a'
        return c

    # Process each region
    for region_name, region in regions.items():
        size = region['Size']
        width, height, depth = size['x'], size['y'], size['z']
        palette = region['BlockStatePalette']
        block_states = region['BlockStates']
        
        # Calculate bits per entry
        bits_per_entry = max(2, math.ceil(math.log2(len(palette))))
        total_blocks = abs(width * height * depth)
        
        # nbtlib handles long arrays as list of ints, but they are signed
        # Convert to unsigned for bit manipulation
        unsigned_states = [(s + (1 << 64) if s < 0 else s) for s in block_states]
        
        # Unpack indices
        indices = unpack_blockstates(unsigned_states, bits_per_entry, total_blocks)
        
        # Build local region palette
        local_to_char = {}
        for i, entry in enumerate(palette):
            block_id = entry.get('Name', 'minecraft:air')
            if block_id not in global_palette_map:
                global_palette_map[block_id] = get_char()
            local_to_char[i] = global_palette_map[block_id]

        # Start DSL generation
        dsl_output.append(f"# Region: {region_name}")
        
        # Layer by Layer
        for y in range(abs(height)):
            dsl_output.append(f"layer_y {y} 0 0")
            for z in range(abs(depth)):
                row = ""
                for x in range(abs(width)):
                    # Litematica index calculation: (y * depth + z) * width + x
                    idx = (y * abs(depth) + z) * abs(width) + x
                    char = local_to_char[indices[idx]]
                    row += char if char != global_palette_map.get('minecraft:air') else "."
                dsl_output.append(row)
            dsl_output.append("end_layer")

    # Prepend Palette
    palette_header = ["palette"]
    for bid, char in global_palette_map.items():
        if bid != 'minecraft:air':
            palette_header.append(f"{char} = {bid}")
    palette_header.append(". = minecraft:air")
    palette_header.append("end_palette\n")
    
    return "\n".join(palette_header + dsl_output)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 litematic_to_dsl.py <file_or_dir>")
        sys.exit(1)
        
    path = sys.argv[1]
    if os.path.isfile(path):
        print(convert_to_dsl(path))
    elif os.path.isdir(path):
        for f in os.listdir(path):
            if f.endswith(".litematic"):
                print(f"Converting {f}...")
                dsl = convert_to_dsl(os.path.join(path, f))
                with open(os.path.join(path, f.replace(".litematic", ".txt")), "w") as out:
                    out.write(dsl)
