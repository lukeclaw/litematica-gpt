package fi.dy.masa.litematica.util;

import fi.dy.masa.malilib.config.IConfigOptionListEntry;

public enum AIProvider implements IConfigOptionListEntry {
    OPENAI("OpenAI", "Use OpenAI's Chat Completions API"),
    GEMINI("Gemini (Vertex AI)", "Use Google Cloud Vertex AI Gemini API");

    private final String name;
    private final String comment;

    AIProvider(String name, String comment) {
        this.name = name;
        this.comment = comment;
    }

    @Override
    public String getStringValue() {
        return this.name();
    }

    @Override
    public String getDisplayName() {
        return this.name;
    }

    @Override
    public IConfigOptionListEntry cycleValue(boolean forward) {
        int id = this.ordinal();
        if (forward) {
            id++;
        } else {
            id--;
        }
        AIProvider[] values = AIProvider.values();
        if (id >= values.length) {
            id = 0;
        } else if (id < 0) {
            id = values.length - 1;
        }
        return values[id];
    }

    @Override
    public AIProvider fromString(String value) {
        for (AIProvider provider : AIProvider.values()) {
            if (provider.name().equalsIgnoreCase(value)) {
                return provider;
            }
        }
        return OPENAI;
    }
}
