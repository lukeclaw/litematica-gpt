// Standalone developer utility (not part of the mod build).
// Converts a .litematic file into the AI DSL format for debugging round-trips.
// Compile/run against the mod's classpath. See README.md.
import net.minecraft.nbt.NbtCompound;
import net.minecraft.nbt.NbtIo;
import net.minecraft.block.BlockState;
import net.minecraft.util.math.BlockPos;
import fi.dy.masa.litematica.schematic.LitematicaSchematic;
import fi.dy.masa.litematica.schematic.ai.OpenAISchematicDSLReverser;
import java.io.File;

public class DSLReverserTool {
    public static void main(String[] args) {
        net.minecraft.SharedConstants.createGameVersion();
        net.minecraft.Bootstrap.initialize();
        if (args.length == 0) {
            System.err.println("Usage: DSLReverserTool <path_to_litematic>");
            System.exit(1);
        }

        try {
            File file = new File(args[0]);
            if (!file.exists()) {
                System.err.println("File not found: " + args[0]);
                System.exit(1);
            }

            LitematicaSchematic schematic = LitematicaSchematic.createFromFile(file.getParentFile(), file.getName());
            
            if (schematic == null) {
                System.err.println("Failed to parse schematic.");
                System.exit(1);
            }

            String dsl = OpenAISchematicDSLReverser.reverse(schematic);
            System.out.println(dsl);
            
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
    }
}
