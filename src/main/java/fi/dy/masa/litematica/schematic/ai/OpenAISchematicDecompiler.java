package fi.dy.masa.litematica.schematic.ai;

import fi.dy.masa.litematica.schematic.container.LitematicaBlockStateContainer;
import net.minecraft.block.BlockState;
import net.minecraft.registry.Registries;
import net.minecraft.util.math.Vec3i;

import java.util.HashMap;
import java.util.Map;

public class OpenAISchematicDecompiler {

    private static final String CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+";

    public static String decompile(LitematicaBlockStateContainer container) {
        StringBuilder dsl = new StringBuilder();
        Vec3i size = container.getSize();
        
        Map<BlockState, Character> stateToChar = new HashMap<>();
        Map<Character, BlockState> charToState = new HashMap<>();
        
        int charIndex = 0;
        
        // Scan for all unique states
        for (int y = 0; y < size.getY(); y++) {
            for (int z = 0; z < size.getZ(); z++) {
                for (int x = 0; x < size.getX(); x++) {
                    BlockState state = container.get(x, y, z);
                    String stateStr = state.isAir() ? "minecraft:air" : Registries.BLOCK.getId(state.getBlock()).toString();
                    if (stateStr.equals("minecraft:air") || stateStr.isEmpty()) continue;
                    
                    if (!stateToChar.containsKey(state)) {
                        char c = charIndex < CHARS.length() ? CHARS.charAt(charIndex++) : '?';
                        stateToChar.put(state, c);
                        charToState.put(c, state);
                    }
                }
            }
        }
        
        dsl.append("palette\n");
        for (Map.Entry<Character, BlockState> entry : charToState.entrySet()) {
            dsl.append(entry.getKey()).append(" = ").append(Registries.BLOCK.getId(entry.getValue().getBlock()).toString()).append("\n");
        }
        dsl.append("end_palette\n\n");
        
        for (int y = 0; y < size.getY(); y++) {
            dsl.append("layer_y ").append(y).append("\n");
            for (int z = 0; z < size.getZ(); z++) {
                for (int x = 0; x < size.getX(); x++) {
                    BlockState state = container.get(x, y, z);
                    String stateStr = state.isAir() ? "minecraft:air" : Registries.BLOCK.getId(state.getBlock()).toString();
                    if (stateStr.equals("minecraft:air") || stateStr.isEmpty()) {
                        dsl.append(".");
                    } else {
                        dsl.append(stateToChar.get(state));
                    }
                }
                dsl.append("\n");
            }
            dsl.append("end_layer\n\n");
        }
        
        return dsl.toString();
    }
}
