package fi.dy.masa.litematica.schematic.ai;

import net.minecraft.block.BlockState;
import net.minecraft.block.Blocks;
import net.minecraft.registry.Registries;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.BlockPos;

import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;
import fi.dy.masa.litematica.Litematica;

public class OpenAISchematicDSLParser {

    public static Map<BlockPos, BlockState> parse(String script) {
        Map<BlockPos, BlockState> blocks = new HashMap<>();
        Scanner scanner = new Scanner(script);
        
        boolean inPalette = false;
        boolean inLayer = false;
        int currentLayerY = 0;
        int layerZ = 0;
        int layerOffsetX = 0;
        int layerOffsetZ = 0;
        
        Map<Character, BlockState> palette = new HashMap<>();
        
        int cursorX = 0, cursorY = 0, cursorZ = 0;

        while (scanner.hasNextLine()) {
            String line = scanner.nextLine().trim();
            if (line.isEmpty()) continue;

            if (line.equals("end_palette")) {
                inPalette = false;
                continue;
            }
            if (line.equals("end_layer")) {
                inLayer = false;
                continue;
            }

            if (inPalette) {
                String[] parts = line.split("=");
                if (parts.length == 2) {
                    char c = parts[0].trim().charAt(0);
                    String stateStr = parts[1].trim();
                    BlockState state = parseState(stateStr);
                    if (state.isAir() && !stateStr.contains("air")) {
                        Litematica.logger.warn("DSL Parser: Palette character '{}' mapped to unknown block state: '{}'. Defaulting to AIR.", c, stateStr);
                    }
                    palette.put(c, state);
                }
                continue;
            }

            if (inLayer) {
                if (line.startsWith("layer_y")) continue; // the parser catches the first layer_y
                // Read row string
                for (int x = 0; x < line.length(); x++) {
                    char c = line.charAt(x);
                    if (c != '.' && palette.containsKey(c)) {
                        blocks.put(new BlockPos(x + layerOffsetX, currentLayerY, layerZ + layerOffsetZ), palette.get(c));
                    } else if (c != '.' && !palette.containsKey(c)) {
                        Litematica.logger.warn("DSL Parser: Unrecognized character '{}' in layer_y {} at x={}. No palette mapping found.", c, currentLayerY, x);
                    }
                }
                layerZ++;
                continue;
            }

            if (line.startsWith("#")) continue;

            String[] tokens = line.split("\\s+");
            if (tokens.length == 0) continue;
            String cmd = tokens[0].toLowerCase();
            
            try {
                if (cmd.equals("palette")) {
                    inPalette = true;
                } else if (cmd.equals("layer_y")) {
                    inLayer = true;
                    currentLayerY = Integer.parseInt(tokens[1]);
                    if (tokens.length >= 4) {
                        layerOffsetX = Integer.parseInt(tokens[2]);
                        layerOffsetZ = Integer.parseInt(tokens[3]);
                    } else {
                        layerOffsetX = 0;
                        layerOffsetZ = 0;
                    }
                    layerZ = 0;
                } else if (cmd.equals("set")) {
                    int x = Integer.parseInt(tokens[1]);
                    int y = Integer.parseInt(tokens[2]);
                    int z = Integer.parseInt(tokens[3]);
                    BlockState state = parseState(tokens[4]);
                    blocks.put(new BlockPos(x, y, z), state);
                } else if (cmd.equals("fill")) {
                    int x1 = Integer.parseInt(tokens[1]);
                    int y1 = Integer.parseInt(tokens[2]);
                    int z1 = Integer.parseInt(tokens[3]);
                    int x2 = Integer.parseInt(tokens[4]);
                    int y2 = Integer.parseInt(tokens[5]);
                    int z2 = Integer.parseInt(tokens[6]);
                    BlockState state = parseState(tokens[7]);
                    
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
                    BlockState state = parseState(tokens[7]);
                    
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
                    BlockState air = Blocks.AIR.getDefaultState();
                    
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
                    blocks.put(new BlockPos(cursorX, cursorY, cursorZ), parseState(tokens[1]));
                } else {
                    Litematica.logger.warn("DSL Parser: Unknown command '{}' in line: '{}'", cmd, line);
                }
            } catch (Exception e) {
                Litematica.logger.error("DSL Parser: Error parsing line: '{}'", line, e);
            }
        }
        
        scanner.close();
        return blocks;
    }

    private static BlockState parseState(String str) {
        try {
            return Registries.BLOCK.get(Identifier.of(str)).getDefaultState();
        } catch (Exception e) {
            try {
                return Registries.BLOCK.get(Identifier.of("minecraft", str)).getDefaultState();
            } catch (Exception ex) {
                return Blocks.AIR.getDefaultState();
            }
        }
    }
}
