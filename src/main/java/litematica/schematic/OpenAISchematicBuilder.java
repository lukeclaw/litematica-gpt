package litematica.schematic;

import litematica.schematic.container.ArrayBlockContainer;
import malilib.util.position.BlockPos;
import malilib.util.position.Vec3i;
import malilib.util.world.BlockState;

import java.util.Map;
import java.util.HashMap;
import com.google.common.collect.ImmutableMap;

public class OpenAISchematicBuilder {

    public static LitematicaSchematic buildFromBlockMap(String name, Map<BlockPos, BlockState> blockMap) {
        if (blockMap == null || blockMap.isEmpty()) {
            return null;
        }

        int minX = Integer.MAX_VALUE;
        int minY = Integer.MAX_VALUE;
        int minZ = Integer.MAX_VALUE;
        int maxX = Integer.MIN_VALUE;
        int maxY = Integer.MIN_VALUE;
        int maxZ = Integer.MIN_VALUE;

        for (BlockPos pos : blockMap.keySet()) {
            minX = Math.min(minX, pos.getX());
            minY = Math.min(minY, pos.getY());
            minZ = Math.min(minZ, pos.getZ());
            maxX = Math.max(maxX, pos.getX());
            maxY = Math.max(maxY, pos.getY());
            maxZ = Math.max(maxZ, pos.getZ());
        }

        int sizeX = maxX - minX + 1;
        int sizeY = maxY - minY + 1;
        int sizeZ = maxZ - minZ + 1;
        Vec3i size = new Vec3i(sizeX, sizeY, sizeZ);

        ArrayBlockContainer container = (ArrayBlockContainer) LitematicaSchematic.createDefaultBlockContainer(size);

        for (Map.Entry<BlockPos, BlockState> entry : blockMap.entrySet()) {
            BlockPos pos = entry.getKey();
            int localX = pos.getX() - minX;
            int localY = pos.getY() - minY;
            int localZ = pos.getZ() - minZ;
            container.setBlockState(localX, localY, localZ, entry.getValue());
        }

        BlockPos regionPos = new BlockPos(0, 0, 0);
        SchematicRegion region = new SchematicRegion(regionPos, size, container, new HashMap<>(), new HashMap<>(), new java.util.ArrayList<>(), LitematicaSchematic.CURRENT_MINECRAFT_DATA_VERSION);
        
        String regionName = name.replaceAll("[^a-zA-Z0-9_-]", "_");
        if(regionName.isEmpty()) regionName = "OpenAI_Region";
        ImmutableMap<String, SchematicRegion> regions = ImmutableMap.of(regionName, region);
        
        return (LitematicaSchematic) LitematicaSchematic.fromRegions(regions).orElse(null);
    }
}
