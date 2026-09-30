#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
venv="$root/.motion-venv"
if [[ ! -x "$venv/bin/python" ]]; then
  python3 -m venv "$venv"
fi
"$venv/bin/python" -m pip -q install 'Pillow==11.1.0' >&2
"$venv/bin/python" -c 'from PIL import Image, features; assert features.check("webp"), "WebP support required"' >&2
printf '%s\n' "$venv/bin/python"
