package fi.dy.masa.litematica.schematic.ai;

import net.minecraft.block.BlockState;
import net.minecraft.util.math.BlockPos;

import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import fi.dy.masa.litematica.config.Configs;

public class HighEffortAIWorkflow {

    public static final HighEffortAIWorkflow INSTANCE = new HighEffortAIWorkflow();

    public enum State { IDLE, PLANNING, GENERATING, PAUSED }

    private State state = State.IDLE;
    private String originalPrompt;
    private String schemName;
    private JsonArray partsPlan = null;
    private int currentPartIndex = 0;
    
    private Map<BlockPos, BlockState> generatedBlocks = new ConcurrentHashMap<>();
    private CompletableFuture<HttpResponse<String>> activeFuture = null;
    
    private IProgressCallback callback;

    public interface IProgressCallback {
        void onProgress(String statusMessage);
        void onComplete(boolean success, String message);
    }

    public void start(String prompt, String schemName, IProgressCallback callback) {
        this.originalPrompt = prompt;
        this.schemName = schemName;
        this.callback = callback;
        this.generatedBlocks.clear();
        this.currentPartIndex = 0;
        this.partsPlan = null;
        
        this.state = State.PLANNING;
        callback.onProgress("Generating Master Plan... Please Wait.");
        
        String plannerPrompt = "You are an expert Minecraft Architect. Semantically break down the following request into primitive geometric components.\n" +
                               "You MUST output raw JSON format with a 'parts' array. Limit to max 5 parts.\n" +
                               "Example:\n{\n \"parts\": [\n  {\"name\": \"Left Leg\", \"bounds\": [0,0,0, 2,5,2], \"instructions\": \"make it out of oak logs\"}\n ]\n}\n\nRequest: " + prompt;

        this.activeFuture = sendApiRequest(plannerPrompt, "gpt-4o", null);
        this.activeFuture.thenAccept(response -> {
            if (this.state != State.PLANNING) return; // aborted
            if (response.statusCode() != 200) {
                fail("API Error during Planning: " + response.statusCode());
                return;
            }
            try {
                JsonObject json = JsonParser.parseString(response.body()).getAsJsonObject();
                String content = json.getAsJsonArray("choices").get(0).getAsJsonObject().getAsJsonObject("message").get("content").getAsString();
                
                // Strip markdown backticks if outputted
                content = content.replaceAll("```json|```", "").trim();
                
                JsonObject planJson = JsonParser.parseString(content).getAsJsonObject();
                this.partsPlan = planJson.getAsJsonArray("parts");
                
                this.state = State.GENERATING;
                processNextPart();
                
            } catch (Exception e) {
                fail("Failed to parse AI Plan JSON: " + e.getMessage());
            }
        }).exceptionally(e -> {
            if (this.state == State.PLANNING) fail("Planning Exception: " + e.getMessage());
            return null;
        });
    }

    private void processNextPart() {
        if (this.state != State.GENERATING) return;
        
        if (currentPartIndex >= partsPlan.size()) {
            // Done!
            finishAndSave();
            return;
        }

        JsonObject part = partsPlan.get(currentPartIndex).getAsJsonObject();
        String partName = part.get("name").getAsString();
        JsonArray bounds = part.getAsJsonArray("bounds");
        String instructions = part.get("instructions").getAsString();
        
        int x1 = bounds.get(0).getAsInt();
        int y1 = bounds.get(1).getAsInt();
        int z1 = bounds.get(2).getAsInt();
        int x2 = bounds.get(3).getAsInt();
        int y2 = bounds.get(4).getAsInt();
        int z2 = bounds.get(5).getAsInt();

        callback.onProgress("Generating " + (currentPartIndex + 1) + "/" + partsPlan.size() + ": " + partName);

        String systemInstruction = "You are a sub-agent generating a Minecraft schematic part: '" + partName + "'.\n" +
            "The bounds are: from ("+x1+","+y1+","+z1+") to ("+x2+","+y2+","+z2+").\n" +
            "Specific instructions: " + instructions + "\n\n" +
            "The DSL grammar ONLY supports these literal commands:\n" +
            "1) palette\\n[char] = [minecraft_id]\\nend_palette\\n\n" +
            "2) layer_y [Y] [offsetX] [offsetZ]\\n(ascii map)\\nend_layer\\n\n" +
            "3) set [x] [y] [z] [minecraft_id]\n" +
            "4) fill [x1] [y1] [z1] [x2] [y2] [z2] [minecraft_id]\n" +
            "5) box [x1] [y1] [z1] [x2] [y2] [z2] [minecraft_id]\n" +
            "6) carve [x1] [y1] [z1] [x2] [y2] [z2]\n" +
            "NEVER output 'size', 'slice', or markdown. Output raw plaintext script ONLY. Use `.` for explicit air.";

        this.activeFuture = sendApiRequest(originalPrompt, "gpt-4o", systemInstruction);
        this.activeFuture.thenAccept(response -> {
            if (this.state != State.GENERATING) return; // Might be paused
            
            if (response.statusCode() != 200) {
                fail("API Error making " + partName + ": " + response.statusCode());
                return;
            }
            try {
                JsonObject json = JsonParser.parseString(response.body()).getAsJsonObject();
                String script = json.getAsJsonArray("choices").get(0).getAsJsonObject().getAsJsonObject("message").get("content").getAsString();
                
                script = script.replaceAll("```(\\w+)?|```", "").trim();
                
                Map<BlockPos, BlockState> parsedPart = OpenAISchematicDSLParser.parse(script);
                this.generatedBlocks.putAll(parsedPart);
                
                currentPartIndex++;
                processNextPart();
                
            } catch (Exception e) {
                fail("Failed to parse DSL for " + partName + ": " + e.getMessage());
            }
        }).exceptionally(e -> {
            if (this.state == State.GENERATING) fail("Sub-agent Exception: " + e.getMessage());
            return null;
        });
    }

    public void pause() {
        if (this.state == State.GENERATING || this.state == State.PLANNING) {
            this.state = State.PAUSED;
            if (this.activeFuture != null) {
                this.activeFuture.cancel(true);
            }
            callback.onProgress("PAUSED. (" + currentPartIndex + "/" + (partsPlan == null ? "?" : partsPlan.size()) + " compiled)");
        }
    }

    public void resume() {
        if (this.state == State.PAUSED) {
            if (this.partsPlan == null) {
                this.start(originalPrompt, schemName, callback);
            } else {
                this.state = State.GENERATING;
                processNextPart();
            }
        }
    }

    public void abort() {
        this.state = State.IDLE;
        if (this.activeFuture != null) {
            this.activeFuture.cancel(true);
        }
        callback.onComplete(false, "Aborted manually.");
    }

    private void finishAndSave() {
        boolean result = OpenAISchematicBuilder.buildAndSave(schemName, generatedBlocks);
        this.state = State.IDLE;
        if (result) {
            callback.onComplete(true, "Schematic built via High-Effort AI successfully!");
        } else {
            callback.onComplete(false, "Failed to compile the final aggregated structure.");
        }
    }

    private void fail(String error) {
        this.state = State.IDLE;
        callback.onComplete(false, error);
    }
    
    public State getState() {
        return this.state;
    }

    private CompletableFuture<HttpResponse<String>> sendApiRequest(String userText, String model, String systemOvr) {
        String apiKey = Configs.Generic.OPENAI_API_KEY.getStringValue();
        JsonObject payload = new JsonObject();
        payload.addProperty("model", model);
        
        JsonArray messages = new JsonArray();
        if (systemOvr != null) {
            JsonObject sys = new JsonObject();
            sys.addProperty("role", "system");
            sys.addProperty("content", systemOvr);
            messages.add(sys);
        }
        
        JsonObject usr = new JsonObject();
        usr.addProperty("role", "user");
        usr.addProperty("content", userText);
        messages.add(usr);
        
        payload.add("messages", messages);

        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.openai.com/v1/chat/completions"))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + apiKey)
                .POST(HttpRequest.BodyPublishers.ofString(payload.toString()))
                .build();

        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString());
    }
}
