package fi.dy.masa.litematica.schematic.ai;

import net.minecraft.block.BlockState;
import net.minecraft.registry.Registries;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Vec3i;
import fi.dy.masa.litematica.schematic.LitematicaSchematic;
import fi.dy.masa.litematica.schematic.container.LitematicaBlockStateContainer;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

public class OpenAISchematicDSLReverser {

    /**
     * Reverses a LitematicaSchematic back into AI DSL script.
     * This is useful for debugging and comparing generated outputs.
     */
    public static String reverse(LitematicaSchematic schematic) {
        StringBuilder dsl = new StringBuilder();
        Map<BlockState, Character> palette = new HashMap<>();
        char nextChar = 'A';
        
        // 1. Build Palette
        dsl.append("palette\n");
        
        // We iterate through all containers to collect all used BlockStates
        for (String regionName : schematic.getAreaPositions().keySet()) {
            LitematicaBlockStateContainer container = schematic.getSubRegionContainer(regionName);
            if (container == null) continue;
            
            Vec3i size = container.getSize();
            for (int y = 0; y < size.getY(); y++) {
                for (int z = 0; z < size.getZ(); z++) {
                    for (int x = 0; x < size.getX(); x++) {
                        BlockState state = container.get(x, y, z);
                        if (!state.isAir() && !palette.containsKey(state)) {
                            palette.put(state, nextChar++);
                            String id = Registries.BLOCK.getId(state.getBlock()).toString();
                            dsl.append(palette.get(state)).append(" = ").append(id).append("\n");
                            
                            // Simple overflow protection for char palette
                            if (nextChar > 'Z' && nextChar < 'a') nextChar = 'a';
                            if (nextChar > 'z') nextChar = '!'; // fallback to symbols
                        }
                    }
                }
            }
        }
        dsl.append("end_palette\n\n");

        // 2. Generate Commands (currently using set for simplicity, or layer_y if preferred)
        for (String regionName : schematic.getAreaPositions().keySet()) {
            LitematicaBlockStateContainer container = schematic.getSubRegionContainer(regionName);
            BlockPos regionPos = schematic.getSubRegionPosition(regionName);
            if (container == null || regionPos == null) continue;
            
            dsl.append("# Region: ").append(regionName).append("\n");
            
            Vec3i size = container.getSize();
            for (int y = 0; y < size.getY(); y++) {
                dsl.append("layer_y ").append(regionPos.getY() + y).append(" ").append(regionPos.getX()).append(" ").append(regionPos.getZ()).append("\n");
                
                for (int z = 0; z < size.getZ(); z++) {
                    StringBuilder row = new StringBuilder();
                    for (int x = 0; x < size.getX(); x++) {
                        BlockState state = container.get(x, y, z);
                        if (state.isAir()) {
                            row.append(".");
                        } else {
                            row.append(palette.get(state));
                        }
                    }
                    dsl.append(row).append("\n");
                }
                dsl.append("end_layer\n");
            }
        }

        return dsl.toString();
    }
}
