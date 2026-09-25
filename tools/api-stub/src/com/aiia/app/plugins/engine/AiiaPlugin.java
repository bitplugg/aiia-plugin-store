package com.aiia.app.plugins.engine;

import kotlin.coroutines.Continuation;
import kotlinx.serialization.json.JsonObject;

public interface AiiaPlugin {
    PluginManifest getManifest();
    java.util.List<PluginTool> tools();
    Object call(String name, JsonObject arguments, Continuation<? super String> continuation);
}
