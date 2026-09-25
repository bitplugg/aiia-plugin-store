#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIB_DIR="${AIIA_PLUGIN_LIB_DIR:-$ROOT/.ci-libs}"
mkdir -p "$LIB_DIR"
BASE="https://repo.maven.apache.org/maven2"

fetch() {
  local path="$1"
  local name
  name="$(basename "$path")"
  if [[ -s "$LIB_DIR/$name" ]]; then
    return
  fi
  curl --fail --location --retry 3 --silent --show-error "$BASE/$path" -o "$LIB_DIR/$name"
}

fetch "org/jetbrains/kotlin/kotlin-stdlib/2.0.20/kotlin-stdlib-2.0.20.jar"
fetch "org/jetbrains/kotlinx/kotlinx-serialization-core-jvm/1.7.3/kotlinx-serialization-core-jvm-1.7.3.jar"
fetch "org/jetbrains/kotlinx/kotlinx-serialization-json-jvm/1.7.3/kotlinx-serialization-json-jvm-1.7.3.jar"
printf 'AIIA_PLUGIN_LIB_DIR=%s\n' "$LIB_DIR"
