package aiia.store.number;

import aiia.plugin.common.PluginSupport;
import com.aiia.app.plugins.engine.AiiaPlugin;
import com.aiia.app.plugins.engine.PluginManifest;
import com.aiia.app.plugins.engine.PluginPermission;
import com.aiia.app.plugins.engine.PluginTool;
import java.util.Collections;
import java.util.List;
import kotlin.coroutines.Continuation;
import kotlinx.serialization.json.JsonObject;

public final class NumberStatsPlugin implements AiiaPlugin {
    private static final PluginManifest MANIFEST = new PluginManifest(
            "store.aiia.dex.number-stats",
            "Number Stats",
            "1.0.0",
            "aiia.store.number.NumberStatsPlugin",
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
                "number_stats",
                "Calculate count, min, max and average",
                PluginSupport.schema()
        ));
    }

    @Override
    public Object call(String name, JsonObject arguments, Continuation<? super String> continuation) {
        if (!"number_stats".equals(name)) return "error: unknown tool " + name;
        return PluginSupport.execute("number_stats", name, arguments);
    }
}
