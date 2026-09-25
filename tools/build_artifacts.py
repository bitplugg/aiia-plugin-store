from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
RELEASES = ROOT / "releases"
CATALOG = ROOT / "catalog"


def run(args: list[str], cwd: Path = ROOT) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def zip_write(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(128 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_jar(name: str) -> Path:
    external = Path(os.environ["AIIA_PLUGIN_LIB_DIR"]) / name if os.environ.get("AIIA_PLUGIN_LIB_DIR") else None
    if external and external.is_file():
        return external
    candidates = sorted(Path.home().glob(f".gradle/caches/modules-2/files-2.1/**/{name}"))
    if not candidates:
        raise RuntimeError(f"Gradle jar not found: {name}")
    return candidates[-1]


def dependency_jars() -> list[Path]:
    return [
        find_jar("kotlin-stdlib-2.0.20.jar"),
        find_jar("kotlinx-serialization-core-jvm-1.7.3.jar"),
        find_jar("kotlinx-serialization-json-jvm-1.7.3.jar"),
    ]


def main() -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    if RELEASES.exists():
        shutil.rmtree(RELEASES)
    CATALOG.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True)

    android_home = Path(os.environ.get("ANDROID_HOME", Path.home() / "Android/Sdk"))
    android_jar = android_home / "platforms/android-35/android.jar"
    d8 = android_home / "build-tools/35.0.0/d8"
    if not android_jar.is_file() or not d8.is_file():
        raise RuntimeError("Android SDK 35 and build-tools 35.0.0 are required")

    deps = dependency_jars()
    dep_cp = ":".join(str(path) for path in deps)
    api_classes = BUILD / "api-classes"
    api_jar = BUILD / "api-stub.jar"
    common_classes = BUILD / "common-classes"
    api_classes.mkdir()
    common_classes.mkdir()

    api_sources = list((ROOT / "tools/api-stub/src").rglob("*.java"))
    run([
        "javac", "--release", "17", "-cp", dep_cp,
        "-d", str(api_classes), *map(str, api_sources)
    ])
    run(["jar", "cf", str(api_jar), "-C", str(api_classes), "."])

    common_sources = list((ROOT / "tools/common/src").rglob("*.java"))
    run([
        "javac", "--release", "17", "-cp", f"{api_jar}:{dep_cp}",
        "-d", str(common_classes), *map(str, common_sources)
    ])

    metadata_files = sorted(ROOT.glob("src/*/*/plugin.json"))
    entries = []
    for metadata_path in metadata_files:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        plugin_dir = metadata_path.parent
        source_files = list((plugin_dir / "src").rglob("*.java"))
        work = BUILD / "work" / metadata["format"] / metadata["slug"]
        classes = work / "classes"
        dex_dir = work / "dex"
        classes.mkdir(parents=True)
        dex_dir.mkdir(parents=True)
        run([
            "javac", "--release", "17",
            "-cp", f"{api_jar}:{common_classes}:{dep_cp}",
            "-d", str(classes), *map(str, source_files)
        ])
        jar = work / "plugin.jar"
        run(["jar", "cf", str(jar), "-C", str(classes), ".", "-C", str(common_classes), "."])
        d8_command = [str(d8), "--min-api", "29", "--lib", str(android_jar)]
        for dependency in deps:
            d8_command.extend(["--lib", str(dependency)])
        d8_command.extend(["--output", str(dex_dir), str(jar)])
        run(d8_command)
        dex = dex_dir / "classes.dex"
        if not dex.is_file():
            raise RuntimeError(f"D8 did not create {dex}")
        manifest = {
            "id": metadata["id"],
            "name": metadata["name"],
            "version": metadata["version"],
            "entryClass": metadata["entryClass"],
            "permissions": [{"name": metadata["permission"], "description": "Run this local tool after confirmation"}],
            "apiVersion": 1,
            "schemaVersion": 1,
            "minApiVersion": 1,
            "maxApiVersion": 1,
        }
        manifest_hash = None
        if metadata["format"] == "aiip":
            target_dir = RELEASES / "aiip"
            target_dir.mkdir(parents=True, exist_ok=True)
            target = target_dir / f"{metadata['slug']}.aiip"
            with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                zip_write(archive, "manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
                zip_write(archive, "plugin.dex", dex.read_bytes())
                zip_write(archive, "assets/README.txt", (metadata["description"] + "\n").encode("utf-8"))
            artifact = f"releases/aiip/{target.name}"
        else:
            target_dir = RELEASES / "dex"
            target_dir.mkdir(parents=True, exist_ok=True)
            target = target_dir / f"{metadata['slug']}.dex"
            shutil.copy2(dex, target)
            sidecar = target_dir / f"{metadata['slug']}.manifest.json"
            sidecar.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            manifest_hash = file_sha256(sidecar)
            artifact = f"releases/dex/{target.name}"
        entries.append({
            "id": metadata["id"],
            "slug": metadata["slug"],
            "format": metadata["format"],
            "name": metadata["name"],
            "version": metadata["version"],
            "description": metadata["description"],
            "tool": metadata["operation"],
            "entryClass": metadata["entryClass"],
            "artifact": artifact,
            "sha256": file_sha256(target),
            "sizeBytes": target.stat().st_size,
            "signerSha256": [],
            "manifestSha256": manifest_hash,
            "manifest": f"releases/{metadata['format']}/{metadata['slug']}.manifest.json" if metadata["format"] == "dex" else None,
            "source": str(plugin_dir.relative_to(ROOT)),
        })

    catalog = {
        "schema": 1,
        "project": "AIIA Plugin Store",
        "repository": "https://github.com/bitplugg/aiia-plugin-store",
        "updated": "2026-09-25",
        "plugins": entries,
    }
    (CATALOG / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (CATALOG / "aiip.json").write_text(json.dumps([x for x in entries if x["format"] == "aiip"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (CATALOG / "dex.json").write_text(json.dumps([x for x in entries if x["format"] == "dex"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(entries)} artifacts: {sum(x['format'] == 'aiip' for x in entries)} aiip, {sum(x['format'] == 'dex' for x in entries)} dex")


if __name__ == "__main__":
    main()
