package aiia.store.jsonsummary;

import aiia.plugin.common.PluginSupport;
import com.aiia.app.plugins.engine.AiiaPlugin;
import com.aiia.app.plugins.engine.PluginManifest;
import com.aiia.app.plugins.engine.PluginPermission;
import com.aiia.app.plugins.engine.PluginTool;
import java.util.Collections;
import java.util.List;
import kotlin.coroutines.Continuation;
import kotlinx.serialization.json.JsonObject;

public final class JsonSummaryPlugin implements AiiaPlugin {
    private static final PluginManifest MANIFEST = new PluginManifest(
            "store.aiia.aiip.json-summary",
            "JSON Summary",
            "1.0.0",
            "aiia.store.jsonsummary.JsonSummaryPlugin",
            Collections.singletonList(new PluginPermission("tool-call", "Run the trusted local tool")),
            1
    );

    @Override
    public PluginManifest getManifest() {
        return MANIFEST;
    }

    @Override
    public List<PluginTool> tools() {
        return Collections.singletonList(new PluginTool(
                "json_summary",
                "Summarize a JSON document without uploading it",
                PluginSupport.schema()
        ));
    }

    @Override
    public Object call(String name, JsonObject arguments, Continuation<? super String> continuation) {
        if (!"json_summary".equals(name)) return "error: unknown tool " + name;
        return PluginSupport.execute("json_summary", name, arguments);
    }
}
