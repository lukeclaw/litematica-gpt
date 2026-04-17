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
    private JsonArray globalBounds = null;
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
        this.globalBounds = null;
        this.partsPlan = null;
        this.activeFutures.clear();
        
        this.state = State.PLANNING;
        Litematica.logger.info("Starting High-Effort AI Workflow for: '{}' (File: {})", prompt, schemName);
        callback.onProgress("Generating Master Plan... Please Wait.");
        
        String plannerPrompt = "You are an expert Minecraft Architect. Semantically break down the following request into primitive geometric components.\n" +
                               "You MUST output raw JSON format with a 'global_bounds' array [x1,y1,z1, x2,y2,z2], a 'global_palette' object, and a 'parts' array. Break it down into as many logical parts as necessary for high detail.\n" +
                               "CRITICAL: Prioritize 'Major Structural Assemblies' (e.g., Head, Torso, Limbs, Hull) over minor features. DO NOT separate tiny details like 'eyes' or 'buttons' into their own parts; instead, include them in the instructions of the larger parent assembly. Target exactly 4-8 high-quality parts.\n" +
                               "SYMMETRY & DUPLICATES: If there are multiple identical/symmetrical components (e.g., 4 identical legs, 2 identical wings), GROUP them into a single part that encompasses all their bounding boxes, and instruct the sub-agent to build ALL of them. Do NOT split identical parts into separate sub-agents.\n" +
                               "Consistency is CRITICAL. Define a shared 'global_palette' for the entire project so all sub-agents use identical blocks for the same features.\n" +
                               "If parts physically intersect (like a leg joining a torso), explicitly define identical 'connections' interface coordinates in *both* intersecting parts so they fuse properly.\n" +
                               "Example:\n{\n \"global_bounds\": [0,0,0, 10,20,10],\n \"global_palette\": {\"wall_material\": \"minecraft:stone_bricks\", \"accent\": \"minecraft:polished_andesite\"},\n \"parts\": [\n  {\"name\": \"Legs (All 4)\", \"bounds\": [0,0,0, 10,5,10], \"instructions\": \"Build 4 identical legs at the corners out of oak logs.\", \"connections\": [{\"name\": \"torso_socket\", \"coord\": \"[2,5,2], [8,5,2], [2,5,8], [8,5,8]\"}]},\n  {\"name\": \"Torso\", \"bounds\": [0,5,0, 10,15,10], \"instructions\": \"Build torso with detail\", \"connections\": [{\"name\": [\"torso_socket\", \"head_socket\"], \"coord\": [\"[2,5,2], [8,5,2], [2,5,8], [8,5,8]\", \"[5,15,5]\"]}]}\n ]\n}\n\nRequest: " + prompt;

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
                this.globalBounds = planJson.getAsJsonArray("global_bounds");
                this.partsPlan = planJson.getAsJsonArray("parts");
                
                Litematica.logger.info("Master Plan generated successfully with {} parts. Scale: {}.", this.partsPlan.size(), this.globalBounds);
                
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

    private int[] parseBounds(JsonArray arr) {
        if (arr.size() == 6) {
            int[] b = new int[6];
            for (int i = 0; i < 6; i++) b[i] = arr.get(i).getAsInt();
            return b;
        } else if (arr.size() == 2 && arr.get(0).isJsonArray() && arr.get(1).isJsonArray()) {
            JsonArray a1 = arr.get(0).getAsJsonArray();
            JsonArray a2 = arr.get(1).getAsJsonArray();
            return new int[] {
                a1.get(0).getAsInt(), a1.get(1).getAsInt(), a1.get(2).getAsInt(),
                a2.get(0).getAsInt(), a2.get(1).getAsInt(), a2.get(2).getAsInt()
            };
        }
        throw new IllegalStateException("Invalid bounds array size: " + arr.size());
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
        JsonArray boundsJson = part.getAsJsonArray("bounds");
        String instructions = part.get("instructions").getAsString();
        
        Litematica.logger.info("Dispatching Sub-Agent for Part {}/{}: '{}'", (index + 1), partsPlan.size(), partName);
        
        int[] b = parseBounds(boundsJson);
        int x1 = b[0], y1 = b[1], z1 = b[2], x2 = b[3], y2 = b[4], z2 = b[5];

        String connectionsText = "";
        if (part.has("connections") && part.get("connections").isJsonArray()) {
            JsonArray conns = part.getAsJsonArray("connections");
            if (conns.size() > 0) {
                connectionsText = "\nABSOLUTE PHYSICAL CONSTRAINT - Tie-in points: You MUST explicitly place physical blocks intersecting these exact coordinates. Failure to build blocks touching these tie-in coordinates will result in a disconnected structure. Interface points:\n";
                for (int i = 0; i < conns.size(); i++) {
                    JsonObject c = conns.get(i).getAsJsonObject();
                    if (c.has("name") && c.has("coord")) {
                        String nameStr = c.get("name").isJsonPrimitive() ? c.get("name").getAsString() : c.get("name").toString();
                        String coordStr = c.get("coord").isJsonPrimitive() ? c.get("coord").getAsString() : c.get("coord").toString();
                        connectionsText += "- " + nameStr + " at " + coordStr + " -> YOU MUST BRIDGE YOUR BLOCKS TO SMOOTHLY BLEND INTO THIS COORDINATE TO AVOID GAPS.\n";
                    }
                }
            }
        }
        
        String paletteText = "";
        if (this.globalPalette != null) {
            paletteText = "\nPROJECT GLOBAL PALETTE (Use these materials for project-wide consistency):\n" + this.globalPalette.toString() + "\n";
        }

        int width = Math.abs(x2 - x1) + 1;
        int height = Math.abs(y2 - y1) + 1;
        int depth = Math.abs(z2 - z1) + 1;

        String scaleText = "";
        if (this.globalBounds != null) {
            scaleText = "\nPROJECT SCALE CONTEXT: You are building a piece of a larger structure. The TOTAL build bounds are: " + this.globalBounds.toString() + ".\n" +
                        "Your specific part's bounds are ONLY: [" + x1 + "," + y1 + "," + z1 + "," + x2 + "," + y2 + "," + z2 + "].\n" +
                        "This means your part has dimensions: Width=" + width + ", Height=" + height + ", Depth=" + depth + ". Plan your geometry to fit EXACTLY within these dimensions.\n";
        }

        // Context about other parts
        String contextText = "\nCONTEXT - OTHER PARTS IN THIS BUILD:\n";
        for (int i = 0; i < partsPlan.size(); i++) {
            if (i == index) continue;
            JsonObject otherPart = partsPlan.get(i).getAsJsonObject();
            String otherName = otherPart.get("name").getAsString();
            String otherBounds = otherPart.get("bounds").toString();
            contextText += "- " + otherName + " " + otherBounds + "\n";
        }
        
        callback.onProgress("Generating: " + partName);

        String systemInstruction = "You are a sub-agent generating a Minecraft schematic part: '" + partName + "'.\n" +
            "Specific instructions: " + instructions + "\n" + scaleText + contextText + paletteText + connectionsText + "\n" +
            "The DSL grammar ONLY supports these literal commands:\n" +
            "1) palette\\n[char] = [minecraft_id]\\nend_palette\\n\n" +
            "2) layer_y [Y] [offsetX] [offsetZ]\\n(ascii map)\\nend_layer\\n\n" +
            "3) set [x] [y] [z] [minecraft_id]\n" +
            "4) fill [x1] [y1] [z1] [x2] [y2] [z2] [minecraft_id]\n" +
            "5) box [x1] [y1] [z1] [x2] [y2] [z2] [minecraft_id]\n" +
            "6) carve [x1] [y1] [z1] [x2] [y2] [z2]\n" +
            "HARD CONSTRAINT: You MUST NOT place any blocks outside your designated bounds. Your bounds are ABSOLUTE WORLD COORDINATES. Do not use relative coordinates. Any block placed outside your bounds will be physically clipped and deleted by the system.\n" +
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
                
                Map<BlockPos, BlockState> parsedPart = OpenAISchematicDSLParser.parse(script, b);
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
