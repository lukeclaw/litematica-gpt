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

    public static CompletableFuture<String> generateRaw(String prompt, String systemInstruction) {
        return generateRaw(prompt, systemInstruction, null);
    }

    public static CompletableFuture<String> generateRaw(String prompt, String systemInstruction, String modelId) {
        String apiKey = Configs.Generic.OPENAI_API_KEY.getStringValue();
        if (apiKey == null || apiKey.isEmpty()) {
            return CompletableFuture.failedFuture(new IllegalStateException("OpenAI API Key is not configured!"));
        }

        String targetModelId = (modelId != null && !modelId.isEmpty()) ? modelId : Configs.Generic.OPENAI_WORKER_MODEL_ID.getStringValue();
        JsonObject payload = new JsonObject();
        payload.addProperty("model", targetModelId);
        
        JsonArray messages = new JsonArray();
        
        if (systemInstruction != null && !systemInstruction.isEmpty()) {
            JsonObject systemMessage = new JsonObject();
            systemMessage.addProperty("role", "system");
            systemMessage.addProperty("content", systemInstruction);
            messages.add(systemMessage);
        }
        
        JsonObject userMessage = new JsonObject();
        userMessage.addProperty("role", "user");
        userMessage.addProperty("content", prompt);
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
                        throw new RuntimeException("OpenAI API Error: " + response.statusCode() + " - " + response.body());
                    }
                    JsonObject json = JsonParser.parseString(response.body()).getAsJsonObject();
                    return json.getAsJsonArray("choices").get(0).getAsJsonObject().getAsJsonObject("message").get("content").getAsString();
                });
    }

    public static CompletableFuture<String> generateSchematic(String prompt, String previousDecompiledCode) {
        String systemInstruction = "You are an AI that generates Minecraft schematics using a strict DSL format. The DSL grammar ONLY supports these literal commands:\n" +
                "1) palette\\n[char] = [minecraft_id]\\nend_palette\\n\n" +
                "2) layer_y [number]\\n(ascii map of characters)\\nend_layer\\n\n" +
                "   **CRITICAL: Use '.' (dot) to represent empty space/air in ascii maps.**\n" +
                "   **CRITICAL: Build upwards in 3D grid coordinates. You must stack multiple layer_y slices to build 3D objects.**\n" +
                "3) set [x] [y] [z] [minecraft_id]\n" +
                "4) fill [x1] [y1] [z1] [x2] [y2] [z2] [minecraft_id]\n" +
                "5) box [x1] [y1] [z1] [x2] [y2] [z2] [minecraft_id]\n" +
                "6) carve [x1] [y1] [z1] [x2] [y2] [z2]\n" +
                "NEVER output 'size', 'slice', or anything else. Output only raw plaintext DSL script. Do not use markdown backticks.";
        
        String finalPrompt = "User Prompt: " + prompt;
        if (previousDecompiledCode != null && !previousDecompiledCode.isEmpty()) {
            finalPrompt += "\n\nExisting Schematic DSL (Please edit this to fulfill the prompt):\n" + previousDecompiledCode;
        }

        return AIIntegration.generate(finalPrompt, systemInstruction);
    }
}
