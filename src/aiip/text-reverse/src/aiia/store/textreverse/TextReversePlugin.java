package aiia.store.textreverse;

import aiia.plugin.common.PluginSupport;
import com.aiia.app.plugins.engine.AiiaPlugin;
import com.aiia.app.plugins.engine.PluginManifest;
import com.aiia.app.plugins.engine.PluginPermission;
import com.aiia.app.plugins.engine.PluginTool;
import java.util.Collections;
import java.util.List;
import kotlin.coroutines.Continuation;
import kotlinx.serialization.json.JsonObject;

public final class TextReversePlugin implements AiiaPlugin {
    private static final PluginManifest MANIFEST = new PluginManifest(
            "store.aiia.aiip.text-reverse",
            "Text Reverse",
            "1.0.0",
            "aiia.store.textreverse.TextReversePlugin",
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
                "reverse",
                "Reverse text without changing Unicode content",
                PluginSupport.schema()
        ));
    }

    @Override
    public Object call(String name, JsonObject arguments, Continuation<? super String> continuation) {
        if (!"reverse".equals(name)) return "error: unknown tool " + name;
        return PluginSupport.execute("reverse", name, arguments);
    }
}
