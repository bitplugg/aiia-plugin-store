package aiia.store.text;

import aiia.plugin.common.PluginSupport;
import com.aiia.app.plugins.engine.AiiaPlugin;
import com.aiia.app.plugins.engine.PluginManifest;
import com.aiia.app.plugins.engine.PluginPermission;
import com.aiia.app.plugins.engine.PluginTool;
import java.util.Collections;
import java.util.List;
import kotlin.coroutines.Continuation;
import kotlinx.serialization.json.JsonObject;

public final class TextProfilePlugin implements AiiaPlugin {
    private static final PluginManifest MANIFEST = new PluginManifest(
            "store.aiia.dex.text-profile",
            "Text Profile",
            "1.0.0",
            "aiia.store.text.TextProfilePlugin",
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
                "text_profile",
                "Count letters, digits, spaces and characters",
                PluginSupport.schema()
        ));
    }

    @Override
    public Object call(String name, JsonObject arguments, Continuation<? super String> continuation) {
        if (!"text_profile".equals(name)) return "error: unknown tool " + name;
        return PluginSupport.execute("text_profile", name, arguments);
    }
}
