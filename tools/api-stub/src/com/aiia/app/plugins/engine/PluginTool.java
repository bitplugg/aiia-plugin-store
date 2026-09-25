package com.aiia.app.plugins.engine;

import kotlinx.serialization.json.JsonObject;

public final class PluginTool {
    private final String name;
    private final String description;
    private final JsonObject inputSchema;

    public PluginTool(String name, String description, JsonObject inputSchema) {
        this.name = name;
        this.description = description;
        this.inputSchema = inputSchema;
    }

    public String getName() {
        return name;
    }

    public String getDescription() {
        return description;
    }

    public JsonObject getInputSchema() {
        return inputSchema;
    }
}
