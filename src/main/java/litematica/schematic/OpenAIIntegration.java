package litematica.schematic;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class OpenAIIntegration {

    public static String generateSchematicScript(String prompt, String apiKey, String currentContext) throws Exception {
        URL url = new URL("https://api.openai.com/v1/chat/completions");
        HttpURLConnection con = (HttpURLConnection) url.openConnection();
        con.setRequestMethod("POST");
        con.setRequestProperty("Content-Type", "application/json");
        con.setRequestProperty("Authorization", "Bearer " + apiKey);
        con.setDoOutput(true);

        StringBuilder systemMessage = new StringBuilder();
        systemMessage.append("You are an expert Minecraft schematic generator. You write procedural generation scripts.\n");
        systemMessage.append("Available commands:\n");
        systemMessage.append("- box <x1> <y1> <z1> <x2> <y2> <z2> <minecraft:block> (hollow box)\n");
        systemMessage.append("- fill <x1> <y1> <z1> <x2> <y2> <z2> <minecraft:block> (solid fill)\n");
        systemMessage.append("- carve <x1> <y1> <z1> <x2> <y2> <z2> (replaces with air)\n");
        systemMessage.append("- set <x> <y> <z> <minecraft:block>\n");
        systemMessage.append("- cursor_move <dx> <dy> <dz>\n");
        systemMessage.append("- cursor_set <minecraft:block>\n");
        systemMessage.append("- palette\\n<char> = <minecraft:block>\\nend_palette\n");
        systemMessage.append("- layer_y <y>\\n<ascii characters>\\nend_layer\n");
        systemMessage.append("Only use these commands. Do not wrap code in markdown block, return raw text script only.");

        if (currentContext != null && !currentContext.isEmpty()) {
            systemMessage.append("\n\nThe user wants to edit an existing schematic. Here is the current schematic decompiled for you:\n");
            systemMessage.append(currentContext);
        }

        JsonObject systemMessageObj = new JsonObject();
        systemMessageObj.addProperty("role", "system");
        systemMessageObj.addProperty("content", systemMessage.toString());

        JsonObject userMessageObj = new JsonObject();
        userMessageObj.addProperty("role", "user");
        userMessageObj.addProperty("content", prompt);

        JsonArray messages = new JsonArray();
        messages.add(systemMessageObj);
        messages.add(userMessageObj);

        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("model", "gpt-4o-mini");
        requestBody.add("messages", messages);
        requestBody.addProperty("temperature", 0.0);

        try (OutputStream os = con.getOutputStream()) {
            byte[] input = requestBody.toString().getBytes(StandardCharsets.UTF_8);
            os.write(input, 0, input.length);
        }

        if (con.getResponseCode() != 200) {
            try (InputStreamReader reader = new InputStreamReader(con.getErrorStream(), StandardCharsets.UTF_8)) {
                JsonObject response = JsonParser.parseReader(reader).getAsJsonObject();
                throw new Exception("OpenAI API Error: " + response.toString());
            }
        }

        try (InputStreamReader reader = new InputStreamReader(con.getInputStream(), StandardCharsets.UTF_8)) {
            JsonObject response = JsonParser.parseReader(reader).getAsJsonObject();
            return response.getAsJsonArray("choices").get(0).getAsJsonObject()
                    .getAsJsonObject("message").get("content").getAsString();
        }
    }
}
