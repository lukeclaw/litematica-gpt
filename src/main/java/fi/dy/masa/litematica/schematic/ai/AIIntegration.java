package fi.dy.masa.litematica.schematic.ai;

import fi.dy.masa.litematica.config.Configs;
import fi.dy.masa.litematica.util.AIProvider;
import java.util.concurrent.CompletableFuture;

public class AIIntegration {

    public static CompletableFuture<String> generate(String prompt, String systemInstruction) {
        AIProvider provider = (AIProvider) Configs.Generic.AI_PROVIDER.getOptionListValue();

        if (provider == AIProvider.GEMINI) {
            return GeminiIntegration.generateContent(prompt, systemInstruction);
        } else {
            // Default to OpenAI
            return OpenAIIntegration.generateRaw(prompt, systemInstruction);
        }
    }
}
