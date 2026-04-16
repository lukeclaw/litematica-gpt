package fi.dy.masa.litematica.schematic.ai;

import fi.dy.masa.litematica.config.Configs;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.concurrent.CompletableFuture;

public class OpenAIIntegration {

    private static final String API_URL = "https://api.openai.com/v1/chat/completions";

    public static CompletableFuture<String> generateSchematic(String prompt, String previousDecompiledCode) {
        String apiKey = Configs.Generic.OPENAI_API_KEY.getStringValue();
        if (apiKey == null || apiKey.isEmpty()) {
            return CompletableFuture.failedFuture(new IllegalStateException("API Key is not configured!"));
        }

        JsonObject payload = new JsonObject();
        payload.addProperty("model", "gpt-4o");
        
        JsonArray messages = new JsonArray();
        
        JsonObject systemMessage = new JsonObject();
        systemMessage.addProperty("role", "system");
        systemMessage.addProperty("content", "You are an AI that generates Minecraft schematics using a strict DSL format. The DSL grammar ONLY supports these literal commands:\n" +
                "1) palette\\n[char] = [minecraft_id]\\nend_palette\\n\n" +
                "2) layer_y [number]\\n(ascii map of characters)\\nend_layer\\n\n" +
                "   **CRITICAL: Use '.' (dot) to represent empty space/air in ascii maps.**\n" +
                "   **CRITICAL: Build upwards in 3D grid coordinates. You must stack multiple layer_y slices to build 3D objects.**\n" +
                "3) set [x] [y] [z] [minecraft_id]\n" +
                "4) fill [x1] [y1] [z1] [x2] [y2] [z2] [minecraft_id]\n" +
                "5) box [x1] [y1] [z1] [x2] [y2] [z2] [minecraft_id]\n" +
                "6) carve [x1] [y1] [z1] [x2] [y2] [z2]\n" +
                "NEVER output 'size', 'slice', or anything else. Output only raw plaintext DSL script. Do not use markdown backticks.");
        messages.add(systemMessage);
        
        JsonObject userMessage = new JsonObject();
        userMessage.addProperty("role", "user");
        String finalPrompt = "User Prompt: " + prompt;
        if (previousDecompiledCode != null && !previousDecompiledCode.isEmpty()) {
            finalPrompt += "\n\nExisting Schematic DSL (Please edit this to fulfill the prompt):\n" + previousDecompiledCode;
        }
        userMessage.addProperty("content", finalPrompt);
        messages.add(userMessage);

        payload.add("messages", messages);

        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(API_URL))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + apiKey)
                .POST(HttpRequest.BodyPublishers.ofString(payload.toString()))
                .build();

        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(response -> {
                    if (response.statusCode() != 200) {
                        throw new RuntimeException("API returned status code " + response.statusCode() + ": " + response.body());
                    }
                    JsonObject json = JsonParser.parseString(response.body()).getAsJsonObject();
                    return json.getAsJsonArray("choices").get(0).getAsJsonObject().getAsJsonObject("message").get("content").getAsString();
                });
    }
}
