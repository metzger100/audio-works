#!/usr/bin/env bash
set -euo pipefail
LAB_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$LAB_DIR"
LAB_PYTHON="${MERIDIAN_PYTHON:-python3}"
mkdir -p tools/downloads tools/ngspice tools/cache
"$LAB_PYTHON" -m venv .venv
PIP_CACHE_DIR="$LAB_DIR/tools/cache/pip" .venv/bin/python -m pip install -r requirements.txt
if [[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]]; then
  while read -r checksum name; do
    if [[ ! -f "tools/downloads/$name" ]]; then
      curl -fL --retry 2 "https://geo.mirror.pkgbuild.com/extra/os/x86_64/$name" -o "tools/downloads/$name"
    fi
    printf '%s  %s\n' "$checksum" "tools/downloads/$name" | sha256sum -c -
    tar -xf "tools/downloads/$name" -C tools/ngspice
  done < tools/packages.sha256
else
  printf 'Use native ngspice 47 and set MERIDIAN_NGSPICE to its executable.\n'
fi
chmod +x run tools/ngspice-run
./run doctor
./run verify
