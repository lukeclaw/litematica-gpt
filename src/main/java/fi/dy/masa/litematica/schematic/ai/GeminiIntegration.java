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

    public static CompletableFuture<String> generateContent(String prompt, String systemInstruction, String modelId) {
        String apiKey = Configs.Generic.GEMINI_API_KEY.getStringValue().trim();
        String projectId = Configs.Generic.GEMINI_PROJECT_ID.getStringValue().trim();
        String location = Configs.Generic.GEMINI_LOCATION.getStringValue().trim();
        modelId = modelId.trim();

        if (apiKey.isEmpty() || (projectId.isEmpty() && !modelId.startsWith("projects/"))) {
            return CompletableFuture.failedFuture(new IllegalStateException("Gemini Bearer Token and Project ID must be configured for Vertex AI!"));
        }

        // Vertex AI URL format
        // Standard models: publishers/google/models/{modelId}
        // Tuned models: tunedModels/{modelId} OR models/{modelId}
        String modelPath;
        if (modelId.startsWith("tunedModels/") || modelId.startsWith("projects/") || modelId.startsWith("models/")) {
            modelPath = modelId;
        } else if (modelId.matches("\\d+")) {
            // Vertex AI Model Registry path
            modelPath = "models/" + modelId;
        } else {
            modelPath = "publishers/google/models/" + modelId;
        }

        String url;
        if (modelPath.startsWith("projects/")) {
            url = String.format("https://%s-aiplatform.googleapis.com/v1/%s:generateContent", 
                    location, modelPath);
        } else {
            url = String.format("https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/%s:generateContent",
                    location, projectId, location, modelPath);
        }

        // VERBOSE LOGGING - Check this in your Minecraft Console!
        Litematica.logger.info(">>> GEMINI REQUEST URL: {}", url);

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
                        Litematica.logger.error("Gemini API Error: HTTP {} - URL: {} - Response: {}", response.statusCode(), url, response.body());
                        throw new RuntimeException("Gemini API returned status code " + response.statusCode() + ": " + response.body());
                    }
                    
                    try {
                        JsonObject json = JsonParser.parseString(response.body()).getAsJsonObject();
                        // Gemini response structure: candidates[0].content.parts[0].text
                        return json.getAsJsonArray("candidates").get(0).getAsJsonObject()
                                .getAsJsonObject("content").getAsJsonArray("parts").get(0).getAsJsonObject()
                                .get("text").getAsString();
                    } catch (Exception e) {
                        Litematica.logger.error("Failed to parse Gemini response. Body: {}", response.body(), e);
                        throw new RuntimeException("Failed to parse Gemini response: " + e.getMessage());
                    }
                });
    }
}
