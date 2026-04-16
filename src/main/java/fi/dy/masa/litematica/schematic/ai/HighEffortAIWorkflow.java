package fi.dy.masa.litematica.schematic.ai;

import net.minecraft.block.BlockState;
import net.minecraft.util.math.BlockPos;

import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicInteger;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import fi.dy.masa.litematica.config.Configs;
import fi.dy.masa.litematica.Litematica;

public class HighEffortAIWorkflow {

    public static final HighEffortAIWorkflow INSTANCE = new HighEffortAIWorkflow();

    public enum State { IDLE, PLANNING, GENERATING, PAUSED }

    private static final int MAX_CONCURRENT_REQUESTS = 5;

    private State state = State.IDLE;
    private String originalPrompt;
    private String schemName;
    private JsonObject globalPalette = null;
    private JsonArray partsPlan = null;
    private AtomicInteger nextPartIndex = new AtomicInteger(0);
    private AtomicInteger completedPartsCount = new AtomicInteger(0);
    
    private Map<BlockPos, BlockState> generatedBlocks = new ConcurrentHashMap<>();
    private List<CompletableFuture<HttpResponse<String>>> activeFutures = new CopyOnWriteArrayList<>();
    
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
        this.nextPartIndex.set(0);
        this.completedPartsCount.set(0);
        this.globalPalette = null;
        this.partsPlan = null;
        this.activeFutures.clear();
        
        this.state = State.PLANNING;
        Litematica.logger.info("Starting High-Effort AI Workflow for: '{}' (File: {})", prompt, schemName);
        callback.onProgress("Generating Master Plan... Please Wait.");
        
        String plannerPrompt = "You are an expert Minecraft Architect. Semantically break down the following request into primitive geometric components.\n" +
                               "You MUST output raw JSON format with a 'global_palette' object (mapping conceptual materials to specific minecraft_ids) and a 'parts' array. Break it down into as many logical parts as necessary for high detail.\n" +
                               "Consistency is CRITICAL. Define a shared 'global_palette' for the entire project so all sub-agents use identical blocks for the same features.\n" +
                               "If parts physically intersect (like a leg joining a torso), explicitly define identical 'connections' interface coordinates in *both* intersecting parts so they fuse properly.\n" +
                               "Example:\n{\n \"global_palette\": {\"wall_material\": \"minecraft:stone_bricks\", \"accent\": \"minecraft:polished_andesite\"},\n \"parts\": [\n  {\"name\": \"Left Leg\", \"bounds\": [0,0,0, 4,5,4], \"instructions\": \"make it out of oak logs\", \"connections\": [{\"name\": \"torso_socket\", \"coord\": \"[2,5,2]\"}]},\n  {\"name\": \"Torso\", \"bounds\": [0,5,0, 6,10,6], \"instructions\": \"Build torso\", \"connections\": [{\"name\": \"torso_socket\", \"coord\": \"[2,5,2]\"}]}\n ]\n}\n\nRequest: " + prompt;

        CompletableFuture<HttpResponse<String>> plannerFuture = sendApiRequest(plannerPrompt, "gpt-5.4-mini", null);
        this.activeFutures.add(plannerFuture);
        
        plannerFuture.thenAccept(response -> {
            this.activeFutures.remove(plannerFuture);
            if (this.state != State.PLANNING) return; // aborted
            
            if (response.statusCode() != 200) {
                String errorMsg = "Planner API Error: HTTP " + response.statusCode() + " - " + response.body();
                Litematica.logger.error(errorMsg);
                fail(errorMsg);
                return;
            }
            
            try {
                JsonObject json = JsonParser.parseString(response.body()).getAsJsonObject();
                String content = json.getAsJsonArray("choices").get(0).getAsJsonObject().getAsJsonObject("message").get("content").getAsString();
                
                Litematica.logger.info("Planner API Response Body: \n{}", content);
                
                // Strip markdown backticks if outputted
                content = content.replaceAll("```json|```", "").trim();
                
                JsonObject planJson = JsonParser.parseString(content).getAsJsonObject();
                this.globalPalette = planJson.getAsJsonObject("global_palette");
                this.partsPlan = planJson.getAsJsonArray("parts");
                
                Litematica.logger.info("Master Plan generated successfully with {} parts and palette: {}.", this.partsPlan.size(), this.globalPalette);
                
                this.state = State.GENERATING;
                dispatchWorkers();
                
            } catch (Exception e) {
                Litematica.logger.error("Failed to parse AI Plan JSON.", e);
                fail("Failed to parse AI Plan JSON: " + e.getMessage());
            }
        }).exceptionally(e -> {
            this.activeFutures.remove(plannerFuture);
            if (this.state == State.PLANNING) {
                Litematica.logger.error("Planning Exception during API call.", e);
                fail("Planning Exception: " + e.getMessage());
            }
            return null;
        });
    }

    private synchronized void dispatchWorkers() {
        if (this.state != State.GENERATING) return;

        while (activeFutures.size() < MAX_CONCURRENT_REQUESTS) {
            int index = nextPartIndex.getAndIncrement();
            if (index >= partsPlan.size()) {
                break; // No more parts to start
            }
            startPart(index);
        }
    }

    private void startPart(int index) {
        JsonObject part = partsPlan.get(index).getAsJsonObject();
        String partName = part.get("name").getAsString();
        JsonArray bounds = part.getAsJsonArray("bounds");
        String instructions = part.get("instructions").getAsString();
        
        Litematica.logger.info("Dispatching Sub-Agent for Part {}/{}: '{}'", (index + 1), partsPlan.size(), partName);
        
        String connectionsText = "";
        if (part.has("connections") && part.get("connections").isJsonArray()) {
            JsonArray conns = part.getAsJsonArray("connections");
            if (conns.size() > 0) {
                connectionsText = "\nABSOLUTE PHYSICAL CONSTRAINT - Tie-in points: You MUST explicitly place physical blocks intersecting these exact coordinates. Failure to build blocks touching these tie-in coordinates will result in a disconnected structure. Interface points:\n";
                for (int i = 0; i < conns.size(); i++) {
                    JsonObject c = conns.get(i).getAsJsonObject();
                    if (c.has("name") && c.has("coord")) {
                        connectionsText += "- " + c.get("name").getAsString() + " at " + c.get("coord").getAsString() + "\n";
                    }
                }
            }
        }
        
        String paletteText = "";
        if (this.globalPalette != null) {
            paletteText = "\nPROJECT GLOBAL PALETTE (Use these materials for project-wide consistency):\n" + this.globalPalette.toString() + "\n";
        }
        
        int x1 = bounds.get(0).getAsInt();
        int y1 = bounds.get(1).getAsInt();
        int z1 = bounds.get(2).getAsInt();
        int x2 = bounds.get(3).getAsInt();
        int y2 = bounds.get(4).getAsInt();
        int z2 = bounds.get(5).getAsInt();

        callback.onProgress("Generating: " + partName);

        String systemInstruction = "You are a sub-agent generating a Minecraft schematic part: '" + partName + "'.\n" +
            "The bounds are: from ("+x1+","+y1+","+z1+") to ("+x2+","+y2+","+z2+").\n" +
            "Specific instructions: " + instructions + "\n" + paletteText + connectionsText + "\n" +
            "The DSL grammar ONLY supports these literal commands:\n" +
            "1) palette\\n[char] = [minecraft_id]\\nend_palette\\n\n" +
            "2) layer_y [Y] [offsetX] [offsetZ]\\n(ascii map)\\nend_layer\\n\n" +
            "3) set [x] [y] [z] [minecraft_id]\n" +
            "4) fill [x1] [y1] [z1] [x2] [y2] [z2] [minecraft_id]\n" +
            "5) box [x1] [y1] [z1] [x2] [y2] [z2] [minecraft_id]\n" +
            "6) carve [x1] [y1] [z1] [x2] [y2] [z2]\n" +
            "NEVER output 'size', 'slice', or markdown. Output raw plaintext script ONLY. Use `.` for explicit air.";

        CompletableFuture<HttpResponse<String>> future = sendApiRequest(originalPrompt, "gpt-5.4-mini", systemInstruction);
        this.activeFutures.add(future);

        future.thenAccept(response -> {
            this.activeFutures.remove(future);
            if (this.state != State.GENERATING) return; // Might be paused
            
            if (response.statusCode() != 200) {
                String errorMsg = "Sub-agent API Error for '" + partName + "': HTTP " + response.statusCode() + " - " + response.body();
                Litematica.logger.error(errorMsg);
                fail(errorMsg);
                return;
            }
            try {
                JsonObject json = JsonParser.parseString(response.body()).getAsJsonObject();
                String script = json.getAsJsonArray("choices").get(0).getAsJsonObject().getAsJsonObject("message").get("content").getAsString();
                
                Litematica.logger.info("Sub-agent Response for '{}':\n{}", partName, script);
                
                script = script.replaceAll("```(\\w+)?|```", "").trim();
                
                Map<BlockPos, BlockState> parsedPart = OpenAISchematicDSLParser.parse(script);
                this.generatedBlocks.putAll(parsedPart);
                
                int completed = completedPartsCount.incrementAndGet();
                Litematica.logger.info("Successfully parsed and integrated part '{}' ({}/{}).", partName, completed, partsPlan.size());
                callback.onProgress("Completed " + completed + "/" + partsPlan.size() + " parts.");
                
                if (completed >= partsPlan.size()) {
                    finishAndSave();
                } else {
                    dispatchWorkers();
                }
                
            } catch (Exception e) {
                Litematica.logger.error("Failed to parse DSL for part: '{}'", partName, e);
                fail("Failed to parse DSL for " + partName + ": " + e.getMessage());
            }
        }).exceptionally(e -> {
            this.activeFutures.remove(future);
            if (this.state == State.GENERATING) {
                Litematica.logger.error("Sub-agent exception for part: '{}'", partName, e);
                fail("Sub-agent Exception: " + e.getMessage());
            }
            return null;
        });
    }

    public void pause() {
        if (this.state == State.GENERATING || this.state == State.PLANNING) {
            this.state = State.PAUSED;
            Litematica.logger.info("AI Workflow PAUSED at part {}/{}", completedPartsCount.get(), (partsPlan == null ? "?" : partsPlan.size()));
            for (CompletableFuture<HttpResponse<String>> future : this.activeFutures) {
                future.cancel(true);
            }
            this.activeFutures.clear();
            callback.onProgress("PAUSED. (" + completedPartsCount.get() + "/" + (partsPlan == null ? "?" : partsPlan.size()) + " completed)");
        }
    }

    public void resume() {
        if (this.state == State.PAUSED) {
            Litematica.logger.info("AI Workflow RESUMED.");
            if (this.partsPlan == null) {
                this.start(originalPrompt, schemName, callback);
            } else {
                this.state = State.GENERATING;
                dispatchWorkers();
            }
        }
    }

    public void abort() {
        this.state = State.IDLE;
        Litematica.logger.info("AI Workflow ABORTED manually.");
        for (CompletableFuture<HttpResponse<String>> future : this.activeFutures) {
            future.cancel(true);
        }
        this.activeFutures.clear();
        callback.onComplete(false, "Aborted manually.");
    }

    private void finishAndSave() {
        Litematica.logger.info("All parts completed. Finalizing and saving schematic: '{}'", schemName);
        boolean result = OpenAISchematicBuilder.buildAndSave(schemName, generatedBlocks);
        this.state = State.IDLE;
        if (result) {
            Litematica.logger.info("Schematic '{}' saved successfully.", schemName);
            callback.onComplete(true, "Schematic built via High-Effort AI successfully!");
        } else {
            Litematica.logger.error("Failed to save the final compiled schematic: '{}'", schemName);
            callback.onComplete(false, "Failed to compile the final aggregated structure.");
        }
    }

    private void fail(String error) {
        this.state = State.IDLE;
        Litematica.logger.error("AI Workflow Failed: {}", error);
        callback.onComplete(false, error);
    }
    
    public State getState() {
        return this.state;
    }

    private CompletableFuture<HttpResponse<String>> sendApiRequest(String userText, String model, String systemOvr) {
        String apiKey = Configs.Generic.OPENAI_API_KEY.getStringValue();
        Litematica.logger.info("Sending API Request to OpenAI (Model: {})", model);
        
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
