package fi.dy.masa.litematica.schematic.ai;

import fi.dy.masa.litematica.data.DataManager;
import fi.dy.masa.litematica.schematic.LitematicaSchematic;
import fi.dy.masa.litematica.schematic.container.LitematicaBlockStateContainer;

import fi.dy.masa.litematica.selection.AreaSelection;
import net.minecraft.block.BlockState;
import net.minecraft.util.math.BlockPos;

import java.io.File;
import java.util.Map;

public class OpenAISchematicBuilder {

    public static boolean buildAndSave(String name, Map<BlockPos, BlockState> blocks) {
        if (blocks.isEmpty()) return false;

        System.out.println("Building schematic from " + blocks.size() + " AI instruction blocks...");
        
        int minX = Integer.MAX_VALUE, minY = Integer.MAX_VALUE, minZ = Integer.MAX_VALUE;
        int maxX = Integer.MIN_VALUE, maxY = Integer.MIN_VALUE, maxZ = Integer.MIN_VALUE;

        for (BlockPos pos : blocks.keySet()) {
            if (pos.getX() < minX) minX = pos.getX();
            if (pos.getY() < minY) minY = pos.getY();
            if (pos.getZ() < minZ) minZ = pos.getZ();
            if (pos.getX() > maxX) maxX = pos.getX();
            if (pos.getY() > maxY) maxY = pos.getY();
            if (pos.getZ() > maxZ) maxZ = pos.getZ();
        }

        BlockPos origin = new BlockPos(minX, minY, minZ);
        BlockPos sizePos = new BlockPos(maxX - minX + 1, maxY - minY + 1, maxZ - minZ + 1);

        AreaSelection areaSelection = new AreaSelection();
        areaSelection.setName(name);
        areaSelection.setExplicitOrigin(origin);
        String regionName = areaSelection.createNewSubRegionBox(origin, "AI-Region");
        fi.dy.masa.litematica.selection.Box box = areaSelection.getSubRegionBox(regionName);
        if (box != null) {
            box.setPos2(origin.add(sizePos).add(-1, -1, -1));
        }

        LitematicaSchematic schematic = LitematicaSchematic.createEmptySchematic(areaSelection, "OpenAI Generator");
        if (schematic == null) return false;

        LitematicaBlockStateContainer container = schematic.getSubRegionContainer("AI-Region");
        if (container == null) return false;

        for (Map.Entry<BlockPos, BlockState> entry : blocks.entrySet()) {
            BlockPos pos = entry.getKey();
            int x = pos.getX() - minX;
            int y = pos.getY() - minY;
            int z = pos.getZ() - minZ;
            container.set(x, y, z, entry.getValue());
        }

        File schematicsDir = DataManager.getSchematicsBaseDirectory();
        
        // Ensure that name ends with .litematic
        String fileName = name.endsWith(".litematic") ? name : name + ".litematic";
        
        return schematic.writeToFile(schematicsDir, fileName, true);
    }
}
