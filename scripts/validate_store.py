from __future__ import annotations

import json
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"aiip": 10, "dex": 10}


def fail(message: str) -> None:
    raise SystemExit(f"validation failed: {message}")


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as error:
        fail(f"{path}: {error}")


def validate_manifest(manifest: dict, expected_id: str, entry_class: str) -> None:
    required = {"id", "name", "version", "entryClass", "permissions", "apiVersion"}
    missing = required - set(manifest)
    if missing:
        fail(f"manifest {expected_id} missing {sorted(missing)}")
    if manifest["id"] != expected_id:
        fail(f"manifest id mismatch: {manifest['id']} != {expected_id}")
    if manifest["entryClass"] != entry_class:
        fail(f"manifest entry mismatch for {expected_id}")
    if not isinstance(manifest["permissions"], list):
        fail(f"permissions must be a list for {expected_id}")


def main() -> None:
    catalog = read_json(ROOT / "catalog/catalog.json")
    entries = catalog.get("plugins", [])
    counts = {fmt: sum(item.get("format") == fmt for item in entries) for fmt in EXPECTED}
    if counts != EXPECTED:
        fail(f"expected {EXPECTED}, got {counts}")
    ids = [item["id"] for item in entries]
    if len(ids) != len(set(ids)):
        fail("duplicate plugin ids")

    artifacts = []
    for item in entries:
        artifact = ROOT / item["artifact"]
        if not artifact.is_file():
            fail(f"missing artifact {item['artifact']}")
        artifacts.append(artifact)
        if item["format"] == "aiip":
            if artifact.suffix != ".aiip":
                fail(f"wrong aiip extension: {artifact}")
            with zipfile.ZipFile(artifact) as archive:
                names = set(archive.namelist())
                if not {"manifest.json", "plugin.dex"} <= names:
                    fail(f"{artifact} missing manifest.json/plugin.dex")
                if not any(name.startswith("assets/") for name in names):
                    fail(f"{artifact} has no assets")
                manifest = json.loads(archive.read("manifest.json"))
                validate_manifest(manifest, item["id"], item["entryClass"])
                plugin_dex = archive.read("plugin.dex")
        else:
            if artifact.suffix != ".dex":
                fail(f"wrong dex extension: {artifact}")
            sidecar = artifact.with_suffix(".manifest.json")
            if not sidecar.is_file():
                fail(f"missing sidecar {sidecar}")
            validate_manifest(read_json(sidecar), item["id"], item["entryClass"])
            plugin_dex = artifact.read_bytes()
        if not plugin_dex.startswith(b"dex\n"):
            fail(f"{artifact} is not a DEX file")

    source_count = len(list(ROOT.glob("src/*/*/plugin.json")))
    if source_count != 20:
        fail(f"expected 20 source manifests, got {source_count}")
    print(f"validated {len(entries)} plugins: 10 aiip + 10 dex")


if __name__ == "__main__":
    main()
