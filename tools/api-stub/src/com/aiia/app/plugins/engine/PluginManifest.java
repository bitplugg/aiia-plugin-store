package com.aiia.app.plugins.engine;

import java.util.List;

public final class PluginManifest {
    private final String id;
    private final String name;
    private final String version;
    private final String entryClass;
    private final List<PluginPermission> permissions;
    private final int apiVersion;

    public PluginManifest(
            String id,
            String name,
            String version,
            String entryClass,
            List<PluginPermission> permissions,
            int apiVersion
    ) {
        this.id = id;
        this.name = name;
        this.version = version;
        this.entryClass = entryClass;
        this.permissions = permissions;
        this.apiVersion = apiVersion;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getVersion() {
        return version;
    }

    public String getEntryClass() {
        return entryClass;
    }

    public List<PluginPermission> getPermissions() {
        return permissions;
    }

    public int getApiVersion() {
        return apiVersion;
    }
}
