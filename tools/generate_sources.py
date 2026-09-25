from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PLUGINS = [
    ("aiip", "text-upper", "Text Upper", "aiia.store.text", "TextUpperPlugin", "uppercase", "text", "Convert text to upper case"),
    ("aiip", "text-lower", "Text Lower", "aiia.store.text", "TextLowerPlugin", "lowercase", "text", "Convert text to lower case"),
    ("aiip", "text-reverse", "Text Reverse", "aiia.store.text", "TextReversePlugin", "reverse", "text", "Reverse text without changing Unicode content"),
    ("aiip", "word-count", "Word Count", "aiia.store.text", "WordCountPlugin", "word_count", "text", "Count words in plain text"),
    ("aiip", "json-summary", "JSON Summary", "aiia.store.data", "JsonSummaryPlugin", "json_summary", "text", "Summarize a JSON document without uploading it"),
    ("aiip", "base64-codec", "Base64 Codec", "aiia.store.data", "Base64CodecPlugin", "base64_encode", "text", "Encode UTF-8 text as Base64"),
    ("aiip", "hash-tool", "Hash Tool", "aiia.store.security", "HashToolPlugin", "sha256", "text", "Calculate a SHA-256 digest locally"),
    ("aiip", "url-summary", "URL Summary", "aiia.store.web", "UrlSummaryPlugin", "url_summary", "text", "Inspect URL scheme, host, path and query"),
    ("aiip", "datetime-tool", "Date Time", "aiia.store.time", "DateTimePlugin", "datetime", "text", "Convert Unix milliseconds to UTC ISO-8601"),
    ("aiip", "color-tool", "Color Tool", "aiia.store.design", "ColorToolPlugin", "color_hex", "text", "Convert a six-digit hex color to RGB"),
    ("dex", "length-converter", "Length Converter", "aiia.store.convert", "LengthConverterPlugin", "length", "value", "Convert common length units"),
    ("dex", "weight-converter", "Weight Converter", "aiia.store.convert", "WeightConverterPlugin", "weight", "value", "Convert common weight units"),
    ("dex", "temperature-converter", "Temperature Converter", "aiia.store.convert", "TemperatureConverterPlugin", "temperature", "value", "Convert Celsius and Fahrenheit"),
    ("dex", "number-stats", "Number Stats", "aiia.store.data", "NumberStatsPlugin", "number_stats", "text", "Calculate count, min, max and average"),
    ("dex", "password-generator", "Password Generator", "aiia.store.security", "PasswordGeneratorPlugin", "password_generate", "length", "Generate a local random password"),
    ("dex", "slugify", "Slugify", "aiia.store.text", "SlugifyPlugin", "slugify", "text", "Create a URL-safe ASCII slug"),
    ("dex", "markdown-cleaner", "Markdown Cleaner", "aiia.store.text", "MarkdownCleanerPlugin", "markdown_clean", "text", "Remove common Markdown decorations"),
    ("dex", "random-choice", "Random Choice", "aiia.store.text", "RandomChoicePlugin", "random_choice", "text", "Choose one pipe-separated option"),
    ("dex", "contact-mask", "Contact Mask", "aiia.store.security", "ContactMaskPlugin", "contact_mask", "text", "Mask an email or phone-like value"),
    ("dex", "text-profile", "Text Profile", "aiia.store.text", "TextProfilePlugin", "text_profile", "text", "Count letters, digits, spaces and characters"),
]

TEMPLATE = '''package {package};

import aiia.plugin.common.PluginSupport;
import com.aiia.app.plugins.engine.AiiaPlugin;
import com.aiia.app.plugins.engine.PluginManifest;
import com.aiia.app.plugins.engine.PluginPermission;
import com.aiia.app.plugins.engine.PluginTool;
import java.util.Collections;
import java.util.List;
import kotlin.coroutines.Continuation;
import kotlinx.serialization.json.JsonObject;

public final class {klass} implements AiiaPlugin {{
    private static final PluginManifest MANIFEST = new PluginManifest(
            "{id}",
            "{name}",
            "1.0.0",
            "{entry}",
            Collections.singletonList(new PluginPermission("tool-call", "Run the trusted local tool")),
            1
    );

    @Override
    public PluginManifest getManifest() {{
        return MANIFEST;
    }}

    @Override
    public List<PluginTool> tools() {{
        return Collections.singletonList(new PluginTool(
                "{tool}",
                "{description}",
                PluginSupport.schema()
        ));
    }}

    @Override
    public Object call(String name, JsonObject arguments, Continuation<? super String> continuation) {{
        if (!"{tool}".equals(name)) return "error: unknown tool " + name;
        return PluginSupport.execute("{operation}", name, arguments);
    }}
}}
'''


def package_name(value: str) -> str:
    return "aiia.store." + value.replace("-", "")


def main() -> None:
    for fmt, slug, name, package, klass, operation, argument, description in PLUGINS:
        java_package = package_name(slug.split("-")[0] if fmt == "dex" else package.split(".")[-1])
        if fmt == "aiip":
            java_package = "aiia.store." + slug.replace("-", "")
        source_dir = ROOT / "src" / fmt / slug / "src" / Path(*java_package.split("."))
        source_dir.mkdir(parents=True, exist_ok=True)
        source = TEMPLATE.format(
            package=java_package,
            klass=klass,
            id=f"store.aiia.{fmt}.{slug}",
            name=name,
            entry=f"{java_package}.{klass}",
            tool=operation,
            description=description,
            operation=operation,
        )
        (source_dir / f"{klass}.java").write_text(source, encoding="utf-8")
        plugin_dir = source_dir.parents[3]
        metadata = {
            "slug": slug,
            "format": fmt,
            "id": f"store.aiia.{fmt}.{slug}",
            "name": name,
            "version": "1.0.0",
            "description": description,
            "package": java_package,
            "class": klass,
            "entryClass": f"{java_package}.{klass}",
            "operation": operation,
            "argument": argument,
            "permission": "tool-call",
        }
        (plugin_dir / "plugin.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (plugin_dir / "README.md").write_text(
            f"# {name}\n\n{description}.\n\nInstall the `{fmt}/{slug}.{ 'aiip' if fmt == 'aiip' else 'dex' }` artifact from the repository releases directory.\n",
            encoding="utf-8",
        )
    print(f"generated {len(PLUGINS)} plugin sources")


if __name__ == "__main__":
    main()
