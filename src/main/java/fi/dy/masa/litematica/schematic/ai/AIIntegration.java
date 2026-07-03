package fi.dy.masa.litematica.schematic.ai;

import fi.dy.masa.litematica.config.Configs;
import fi.dy.masa.litematica.util.AIProvider;
import java.util.concurrent.CompletableFuture;

public class AIIntegration {

    public static CompletableFuture<String> generate(String prompt, String systemInstruction) {
        AIProvider provider = (AIProvider) Configs.Generic.AI_PROVIDER.getOptionListValue();
        String defaultModelId = (provider == AIProvider.GEMINI) 
                ? Configs.Generic.GEMINI_WORKER_MODEL_ID.getStringValue()
                : Configs.Generic.OPENAI_WORKER_MODEL_ID.getStringValue();
        return generate(prompt, systemInstruction, defaultModelId);
    }

    public static CompletableFuture<String> generate(String prompt, String systemInstruction, String modelId) {
        AIProvider provider = (AIProvider) Configs.Generic.AI_PROVIDER.getOptionListValue();

        if (provider == AIProvider.GEMINI) {
            String targetModelId = (modelId != null && !modelId.isEmpty()) ? modelId : Configs.Generic.GEMINI_WORKER_MODEL_ID.getStringValue();
            return GeminiIntegration.generateContent(prompt, systemInstruction, targetModelId);
        } else {
            // Default to OpenAI
            String targetModelId = (modelId != null && !modelId.isEmpty()) ? modelId : Configs.Generic.OPENAI_WORKER_MODEL_ID.getStringValue();
            return OpenAIIntegration.generateRaw(prompt, systemInstruction, targetModelId);
        }
    }
}
