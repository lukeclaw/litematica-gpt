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
import fi.dy.masa.litematica.config.Configs;

public class OpenAISchematicDSLParser {

    public static Map<BlockPos, BlockState> parse(String script) {
        return parse(script, null);
    }

    private static boolean isWithinBounds(int x, int y, int z, int[] bounds) {
        if (bounds == null) return true;
        int minX = Math.min(bounds[0], bounds[3]);
        int maxX = Math.max(bounds[0], bounds[3]);
        int minY = Math.min(bounds[1], bounds[4]);
        int maxY = Math.max(bounds[1], bounds[4]);
        int minZ = Math.min(bounds[2], bounds[5]);
        int maxZ = Math.max(bounds[2], bounds[5]);
        return x >= minX && x <= maxX && y >= minY && y <= maxY && z >= minZ && z <= maxZ;
    }

    public static Map<BlockPos, BlockState> parse(String script, int[] bounds) {
        return parse(script, bounds, null);
    }

    public static Map<BlockPos, BlockState> parse(String script, int[] bounds, BlockPos originOffset) {
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
        
        int offX = originOffset != null ? originOffset.getX() : 0;
        int offY = originOffset != null ? originOffset.getY() : 0;
        int offZ = originOffset != null ? originOffset.getZ() : 0;

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
                    BlockState state = parseState(stateStr, palette);
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
                    int worldX = x + layerOffsetX + offX;
                    int worldY = currentLayerY + offY;
                    int worldZ = layerZ + layerOffsetZ + offZ;
                    if (c != '.' && palette.containsKey(c)) {
                        if (isWithinBounds(worldX, worldY, worldZ, bounds)) {
                            blocks.put(new BlockPos(worldX, worldY, worldZ), palette.get(c));
                        }
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
                    int x = Integer.parseInt(tokens[1]) + offX;
                    int y = Integer.parseInt(tokens[2]) + offY;
                    int z = Integer.parseInt(tokens[3]) + offZ;
                    BlockState state = parseState(tokens[4], palette);
                    if (isWithinBounds(x, y, z, bounds)) {
                        blocks.put(new BlockPos(x, y, z), state);
                    }
                } else if (cmd.equals("fill")) {
                    int x1 = Integer.parseInt(tokens[1]) + offX;
                    int y1 = Integer.parseInt(tokens[2]) + offY;
                    int z1 = Integer.parseInt(tokens[3]) + offZ;
                    int x2 = Integer.parseInt(tokens[4]) + offX;
                    int y2 = Integer.parseInt(tokens[5]) + offY;
                    int z2 = Integer.parseInt(tokens[6]) + offZ;
                    BlockState state = parseState(tokens[7], palette);
                    
                    int minX = Math.min(x1, x2), maxX = Math.max(x1, x2);
                    int minY = Math.min(y1, y2), maxY = Math.max(y1, y2);
                    int minZ = Math.min(z1, z2), maxZ = Math.max(z1, z2);
                    
                    for (int x = minX; x <= maxX; x++) {
                        for (int y = minY; y <= maxY; y++) {
                            for (int z = minZ; z <= maxZ; z++) {
                                if (isWithinBounds(x, y, z, bounds)) {
                                    blocks.put(new BlockPos(x, y, z), state);
                                }
                            }
                        }
                    }
                } else if (cmd.equals("box")) {
                    int x1 = Integer.parseInt(tokens[1]) + offX;
                    int y1 = Integer.parseInt(tokens[2]) + offY;
                    int z1 = Integer.parseInt(tokens[3]) + offZ;
                    int x2 = Integer.parseInt(tokens[4]) + offX;
                    int y2 = Integer.parseInt(tokens[5]) + offY;
                    int z2 = Integer.parseInt(tokens[6]) + offZ;
                    BlockState state = parseState(tokens[7], palette);
                    
                    int minX = Math.min(x1, x2), maxX = Math.max(x1, x2);
                    int minY = Math.min(y1, y2), maxY = Math.max(y1, y2);
                    int minZ = Math.min(z1, z2), maxZ = Math.max(z1, z2);
                    
                    for (int x = minX; x <= maxX; x++) {
                        for (int y = minY; y <= maxY; y++) {
                            for (int z = minZ; z <= maxZ; z++) {
                                if (x == minX || x == maxX || y == minY || y == maxY || z == minZ || z == maxZ) {
                                    if (isWithinBounds(x, y, z, bounds)) {
                                        blocks.put(new BlockPos(x, y, z), state);
                                    }
                                }
                            }
                        }
                    }
                } else if (cmd.equals("carve")) {
                    int x1 = Integer.parseInt(tokens[1]) + offX;
                    int y1 = Integer.parseInt(tokens[2]) + offY;
                    int z1 = Integer.parseInt(tokens[3]) + offZ;
                    int x2 = Integer.parseInt(tokens[4]) + offX;
                    int y2 = Integer.parseInt(tokens[5]) + offY;
                    int z2 = Integer.parseInt(tokens[6]) + offZ;
                    BlockState air = Blocks.AIR.getDefaultState();
                    
                    int minX = Math.min(x1, x2), maxX = Math.max(x1, x2);
                    int minY = Math.min(y1, y2), maxY = Math.max(y1, y2);
                    int minZ = Math.min(z1, z2), maxZ = Math.max(z1, z2);
                    
                    for (int x = minX; x <= maxX; x++) {
                        for (int y = minY; y <= maxY; y++) {
                            for (int z = minZ; z <= maxZ; z++) {
                                if (isWithinBounds(x, y, z, bounds)) {
                                    blocks.put(new BlockPos(x, y, z), air);
                                }
                            }
                        }
                    }
                } else if (cmd.equals("cursor_move")) {
                    cursorX += Integer.parseInt(tokens[1]);
                    cursorY += Integer.parseInt(tokens[2]);
                    cursorZ += Integer.parseInt(tokens[3]);
                } else if (cmd.equals("cursor_set")) {
                    int wx = cursorX + offX;
                    int wy = cursorY + offY;
                    int wz = cursorZ + offZ;
                    if (isWithinBounds(wx, wy, wz, bounds)) {
                        blocks.put(new BlockPos(wx, wy, wz), parseState(tokens[1], palette));
                    }
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

    private static BlockState parseState(String str, Map<Character, BlockState> palette) {
        if (str.length() == 1 && palette.containsKey(str.charAt(0))) {
            return palette.get(str.charAt(0));
        }

        // AI often adds 's' to block IDs incorrectly (e.g., quartz_blocks)
        if (str.endsWith("_blocks") && !str.contains("minecraft:quartz_blocks")) {
            str = str.substring(0, str.length() - 1);
        }
        if (str.equals("minecraft:quartz_blocks")) {
            str = "minecraft:quartz_block";
        }

        try {
            return Registries.BLOCK.get(Identifier.of(str)).getDefaultState();
        } catch (Exception e) {
            try {
                return Registries.BLOCK.get(Identifier.of("minecraft", str)).getDefaultState();
            } catch (Exception ex) {
                String fallbackStr = Configs.Generic.AI_FALLBACK_BLOCK.getStringValue();
                try {
                    return Registries.BLOCK.get(Identifier.of(fallbackStr)).getDefaultState();
                } catch (Exception ex2) {
                    return Blocks.STONE.getDefaultState();
                }
            }
        }
    }
}
