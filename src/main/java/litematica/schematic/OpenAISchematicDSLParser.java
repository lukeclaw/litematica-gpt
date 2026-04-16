package litematica.schematic;

import malilib.util.position.BlockPos;
import malilib.util.world.BlockState;

import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class OpenAISchematicDSLParser {

    public static Map<BlockPos, BlockState> parse(String script, int dataVersion) {
        Map<BlockPos, BlockState> blocks = new HashMap<>();
        Map<Character, BlockState> palette = new HashMap<>();
        
        Scanner scanner = new Scanner(script);
        int cursorX = 0, cursorY = 0, cursorZ = 0;
        
        boolean inPalette = false;
        boolean inLayer = false;
        int currentLayerY = 0;
        int layerZ = 0;
        
        while (scanner.hasNextLine()) {
            String line = scanner.nextLine().trim();
            if (line.isEmpty() || line.startsWith("//") || line.startsWith("```")) continue;
            
            if (inPalette) {
                if (line.equalsIgnoreCase("end_palette")) {
                    inPalette = false;
                } else if (line.contains("=")) {
                    String[] parts = line.split("=");
                    char c = parts[0].trim().charAt(0);
                    String blockId = parts[1].trim();
                    palette.put(c, BlockState.of(blockId, dataVersion));
                }
                continue;
            }
            
            if (inLayer) {
                if (line.equalsIgnoreCase("end_layer")) {
                    inLayer = false;
                } else {
                    for (int x = 0; x < line.length(); x++) {
                        char c = line.charAt(x);
                        if (c == ' ' || c == '.') continue;
                        if (palette.containsKey(c)) {
                            blocks.put(new BlockPos(x, currentLayerY, layerZ), palette.get(c));
                        }
                    }
                    layerZ++;
                }
                continue;
            }

            String[] tokens = line.split("\\s+");
            String cmd = tokens[0].toLowerCase();
            
            try {
                if (cmd.equals("palette")) {
                    inPalette = true;
                } else if (cmd.equals("layer_y")) {
                    inLayer = true;
                    currentLayerY = Integer.parseInt(tokens[1]);
                    layerZ = 0;
                } else if (cmd.equals("set")) {
                    int x = Integer.parseInt(tokens[1]);
                    int y = Integer.parseInt(tokens[2]);
                    int z = Integer.parseInt(tokens[3]);
                    blocks.put(new BlockPos(x, y, z), BlockState.of(tokens[4], dataVersion));
                } else if (cmd.equals("fill")) {
                    int x1 = Integer.parseInt(tokens[1]);
                    int y1 = Integer.parseInt(tokens[2]);
                    int z1 = Integer.parseInt(tokens[3]);
                    int x2 = Integer.parseInt(tokens[4]);
                    int y2 = Integer.parseInt(tokens[5]);
                    int z2 = Integer.parseInt(tokens[6]);
                    BlockState state = BlockState.of(tokens[7], dataVersion);
                    
                    int minX = Math.min(x1, x2), maxX = Math.max(x1, x2);
                    int minY = Math.min(y1, y2), maxY = Math.max(y1, y2);
                    int minZ = Math.min(z1, z2), maxZ = Math.max(z1, z2);
                    
                    for (int x = minX; x <= maxX; x++) {
                        for (int y = minY; y <= maxY; y++) {
                            for (int z = minZ; z <= maxZ; z++) {
                                blocks.put(new BlockPos(x, y, z), state);
                            }
                        }
                    }
                } else if (cmd.equals("box")) {
                    int x1 = Integer.parseInt(tokens[1]);
                    int y1 = Integer.parseInt(tokens[2]);
                    int z1 = Integer.parseInt(tokens[3]);
                    int x2 = Integer.parseInt(tokens[4]);
                    int y2 = Integer.parseInt(tokens[5]);
                    int z2 = Integer.parseInt(tokens[6]);
                    BlockState state = BlockState.of(tokens[7], dataVersion);
                    
                    int minX = Math.min(x1, x2), maxX = Math.max(x1, x2);
                    int minY = Math.min(y1, y2), maxY = Math.max(y1, y2);
                    int minZ = Math.min(z1, z2), maxZ = Math.max(z1, z2);
                    
                    for (int x = minX; x <= maxX; x++) {
                        for (int y = minY; y <= maxY; y++) {
                            for (int z = minZ; z <= maxZ; z++) {
                                if (x == minX || x == maxX || y == minY || y == maxY || z == minZ || z == maxZ) {
                                    blocks.put(new BlockPos(x, y, z), state);
                                }
                            }
                        }
                    }
                } else if (cmd.equals("carve")) {
                    int x1 = Integer.parseInt(tokens[1]);
                    int y1 = Integer.parseInt(tokens[2]);
                    int z1 = Integer.parseInt(tokens[3]);
                    int x2 = Integer.parseInt(tokens[4]);
                    int y2 = Integer.parseInt(tokens[5]);
                    int z2 = Integer.parseInt(tokens[6]);
                    BlockState air = BlockState.of("minecraft:air", dataVersion);
                    
                    int minX = Math.min(x1, x2), maxX = Math.max(x1, x2);
                    int minY = Math.min(y1, y2), maxY = Math.max(y1, y2);
                    int minZ = Math.min(z1, z2), maxZ = Math.max(z1, z2);
                    
                    for (int x = minX; x <= maxX; x++) {
                        for (int y = minY; y <= maxY; y++) {
                            for (int z = minZ; z <= maxZ; z++) {
                                blocks.put(new BlockPos(x, y, z), air);
                            }
                        }
                    }
                } else if (cmd.equals("cursor_move")) {
                    cursorX += Integer.parseInt(tokens[1]);
                    cursorY += Integer.parseInt(tokens[2]);
                    cursorZ += Integer.parseInt(tokens[3]);
                } else if (cmd.equals("cursor_set")) {
                    blocks.put(new BlockPos(cursorX, cursorY, cursorZ), BlockState.of(tokens[1], dataVersion));
                }
            } catch (Exception e) {
                System.out.println("Failed to parse DSL line: " + line);
            }
        }
        
        scanner.close();
        return blocks;
    }
}
