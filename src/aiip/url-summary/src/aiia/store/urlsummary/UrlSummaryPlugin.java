package aiia.store.urlsummary;

import aiia.plugin.common.PluginSupport;
import com.aiia.app.plugins.engine.AiiaPlugin;
import com.aiia.app.plugins.engine.PluginManifest;
import com.aiia.app.plugins.engine.PluginPermission;
import com.aiia.app.plugins.engine.PluginTool;
import java.util.Collections;
import java.util.List;
import kotlin.coroutines.Continuation;
import kotlinx.serialization.json.JsonObject;

public final class UrlSummaryPlugin implements AiiaPlugin {
    private static final PluginManifest MANIFEST = new PluginManifest(
            "store.aiia.aiip.url-summary",
            "URL Summary",
            "1.0.0",
            "aiia.store.urlsummary.UrlSummaryPlugin",
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
                "url_summary",
                "Inspect URL scheme, host, path and query",
                PluginSupport.schema()
        ));
    }

    @Override
    public Object call(String name, JsonObject arguments, Continuation<? super String> continuation) {
        if (!"url_summary".equals(name)) return "error: unknown tool " + name;
        return PluginSupport.execute("url_summary", name, arguments);
    }
}
