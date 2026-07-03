import os
import sys

def parse_dense_dsl(content):
    lines = content.split('\n')
    palette = {}
    blocks = {} 
    in_palette = False
    in_layer = False
    current_y = 0
    layer_offset_x = 0
    layer_offset_z = 0
    layer_z = 0

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'): continue
        if line == 'palette': in_palette = True; continue
        if line == 'end_palette': in_palette = False; continue
        if line == 'end_layer': in_layer = False; continue
        if in_palette:
            if '=' in line:
                char, bid = line.split('=')
                palette[char.strip()] = bid.strip()
            continue
        if line.startswith('layer_y'):
            in_layer = True
            tokens = line.split()
            current_y = int(tokens[1])
            layer_offset_x = int(tokens[2]) if len(tokens) > 2 else 0
            layer_offset_z = int(tokens[3]) if len(tokens) > 3 else 0
            layer_z = 0
            continue
        if in_layer:
            for x, char in enumerate(line):
                if char != '.' and char in palette:
                    blocks[(x + layer_offset_x, current_y, layer_z + layer_offset_z)] = char
            layer_z += 1
    return palette, blocks

def convert_to_sparse(palette, blocks):
    output = ["palette"]
    for char, bid in palette.items():
        if bid != 'minecraft:air':
            output.append(f"{char} = {bid}")
    output.append("end_palette\n")
    sorted_keys = sorted(blocks.keys(), key=lambda k: (k[1], k[2], k[0]))
    processed = set()
    for x, y, z in sorted_keys:
        if (x, y, z) in processed: continue
        char = blocks[(x, y, z)]
        extend_x = 0
        while (x + extend_x + 1, y, z) in blocks and blocks[(x + extend_x + 1, y, z)] == char:
            extend_x += 1
        if extend_x > 0:
            output.append(f"fill {x} {y} {z} {x+extend_x} {y} {z} {char}")
            for ex in range(extend_x + 1):
                processed.add((x + ex, y, z))
        else:
            output.append(f"set {x} {y} {z} {char}")
            processed.add((x, y, z))
    return "\n".join(output)

if __name__ == '__main__':
    src_dir, dest_dir = 'dataset/dsl', 'dataset/dsl_sparse'
    files = [f for f in os.listdir(src_dir) if f.endswith('.txt')]
    for f in files:
        if os.path.exists(os.path.join(dest_dir, f)): continue
        try:
            print(f'Processing {f}...')
            with open(os.path.join(src_dir, f), 'r') as file:
                content = file.read()
            pal, blks = parse_dense_dsl(content)
            sparse_dsl = convert_to_sparse(pal, blks)
            with open(os.path.join(dest_dir, f), 'w') as file:
                file.write(sparse_dsl)
        except Exception as e:
            print(f'Error transforming {f}: {e}')
