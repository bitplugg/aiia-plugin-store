package com.aiia.app.plugins.engine;

public final class PluginPermission {
    private final String name;
    private final String description;

    public PluginPermission(String name, String description) {
        this.name = name;
        this.description = description;
    }

    public String getName() {
        return name;
    }

    public String getDescription() {
        return description;
    }
}
