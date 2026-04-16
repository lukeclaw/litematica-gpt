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
        payload.addProperty("model", "gpt-4-turbo");
        
        JsonArray messages = new JsonArray();
        
        JsonObject systemMessage = new JsonObject();
        systemMessage.addProperty("role", "system");
        systemMessage.addProperty("content", "You are an AI that generates Minecraft schematics using a specific DSL format. The DSL has two primary usages: geometric logic (carve, fill, box, set) and ascii-slicing (palette mapped to layers). If you are editing an existing script, return ONLY the full DSL script format. No markdown blocks, just the text script. Limit it to max 64x64x64 grids.");
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
