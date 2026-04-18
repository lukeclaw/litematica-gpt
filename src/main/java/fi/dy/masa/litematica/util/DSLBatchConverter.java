package fi.dy.masa.litematica.util;

import fi.dy.masa.litematica.schematic.LitematicaSchematic;
import fi.dy.masa.litematica.schematic.ai.OpenAISchematicDSLReverser;
import java.io.File;
import java.nio.file.Files;
import java.nio.charset.StandardCharsets;

public class DSLBatchConverter {
    public static void main(String[] args) {
        if (args.length == 0) {
            System.err.println("Usage: DSLBatchConverter <directory_path>");
            return;
        }

        net.minecraft.SharedConstants.createGameVersion();
        net.minecraft.Bootstrap.initialize();

        File dir = new File(args[0]);
        if (!dir.exists() || !dir.isDirectory()) {
            System.err.println("Invalid directory: " + args[0]);
            return;
        }

        File[] files = dir.listFiles((d, name) -> name.endsWith(".litematic"));
        if (files == null || files.length == 0) {
            System.out.println("No .litematic files found in " + args[0]);
            return;
        }

        System.out.println("Processing " + files.length + " schematics...");

        for (File f : files) {
            try {
                System.out.print("Converting " + f.getName() + "... ");
                LitematicaSchematic schematic = LitematicaSchematic.createFromFile(f.getParentFile(), f.getName());
                if (schematic != null) {
                    String dsl = OpenAISchematicDSLReverser.reverse(schematic);
                    File outFile = new File(f.getParentFile(), f.getName().replace(".litematic", ".txt"));
                    Files.write(outFile.toPath(), dsl.getBytes(StandardCharsets.UTF_8));
                    System.out.println("DONE -> " + outFile.getName());
                } else {
                    System.out.println("FAILED (Parse Error)");
                }
            } catch (Exception e) {
                System.out.println("ERROR: " + e.getMessage());
            }
        }
        System.out.println("Batch conversion complete.");
    }
}
