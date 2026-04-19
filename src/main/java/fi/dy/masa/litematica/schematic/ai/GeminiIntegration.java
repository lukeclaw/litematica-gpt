package fi.dy.masa.litematica.schematic.ai;

import fi.dy.masa.litematica.config.Configs;
import fi.dy.masa.litematica.Litematica;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.concurrent.CompletableFuture;

public class GeminiIntegration {

    public static CompletableFuture<String> generateContent(String prompt, String systemInstruction) {
        String apiKey = Configs.Generic.GEMINI_API_KEY.getStringValue();
        String projectId = Configs.Generic.GEMINI_PROJECT_ID.getStringValue();
        String location = Configs.Generic.GEMINI_LOCATION.getStringValue();
        String modelId = Configs.Generic.GEMINI_MODEL_ID.getStringValue();

        if (apiKey.isEmpty() || projectId.isEmpty()) {
            return CompletableFuture.failedFuture(new IllegalStateException("Gemini API Key and Project ID must be configured for Vertex AI!"));
        }

        // Vertex AI URL format
        // Standard models: publishers/google/models/{modelId}
        // Tuned models: tunedModels/{modelId}
        String modelPath = modelId.startsWith("tunedModels/") ? modelId : "publishers/google/models/" + modelId;
        
        String url = String.format("https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/%s:generateContent",
                location, projectId, location, modelPath);

        JsonObject payload = new JsonObject();
        
        // System instruction
        if (systemInstruction != null && !systemInstruction.isEmpty()) {
            JsonObject si = new JsonObject();
            JsonArray siParts = new JsonArray();
            JsonObject siText = new JsonObject();
            siText.addProperty("text", systemInstruction);
            siParts.add(siText);
            si.add("parts", siParts);
            payload.add("system_instruction", si);
        }

        // Contents
        JsonArray contents = new JsonArray();
        JsonObject userContent = new JsonObject();
        userContent.addProperty("role", "user");
        JsonArray userParts = new JsonArray();
        JsonObject userText = new JsonObject();
        userText.addProperty("text", prompt);
        userParts.add(userText);
        userContent.add("parts", userParts);
        contents.add(userContent);
        payload.add("contents", contents);

        // Generation Config
        JsonObject genConfig = new JsonObject();
        genConfig.addProperty("maxOutputTokens", 8192);
        genConfig.addProperty("temperature", 0.2);
        payload.add("generation_config", genConfig);

        Litematica.logger.info("Sending API Request to Gemini (Vertex AI): {}", modelId);

        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + apiKey)
                .POST(HttpRequest.BodyPublishers.ofString(payload.toString()))
                .build();

        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(response -> {
                    if (response.statusCode() != 200) {
                        Litematica.logger.error("Gemini API Error: HTTP {} - {}", response.statusCode(), response.body());
                        throw new RuntimeException("Gemini API returned status code " + response.statusCode() + ": " + response.body());
                    }
                    
                    try {
                        JsonObject json = JsonParser.parseString(response.body()).getAsJsonObject();
                        // Gemini response structure: candidates[0].content.parts[0].text
                        return json.getAsJsonArray("candidates").get(0).getAsJsonObject()
                                .getAsJsonObject("content").getAsJsonArray("parts").get(0).getAsJsonObject()
                                .get("text").getAsString();
                    } catch (Exception e) {
                        Litematica.logger.error("Failed to parse Gemini response", e);
                        throw new RuntimeException("Failed to parse Gemini response: " + e.getMessage());
                    }
                });
    }
}
