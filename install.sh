#!/usr/bin/env bash
# Local install for the hatch-pet-plus plugin (Codex + Claude Code) and the Bunny pet.
#
#   ./install.sh              install plugin into both hosts (whichever are present)
#   ./install.sh --pet        also install the Bunny pet into ~/.codex/pets/
#   ./install.sh --codex      Codex only
#   ./install.sh --claude     Claude Code only
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_SRC="$REPO_DIR/plugins/hatch-pet-plus"
PLUGIN_NAME="hatch-pet-plus"

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"

DO_CODEX=1; DO_CLAUDE=1; DO_PET=0
for a in "$@"; do
  case "$a" in
    --codex)  DO_CLAUDE=0 ;;
    --claude) DO_CODEX=0 ;;
    --pet)    DO_PET=1 ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
  esac
done

say() { printf '  %s\n' "$1"; }

# ---------------------------------------------------------------- Codex
if [ "$DO_CODEX" = 1 ] && [ -d "$CODEX_HOME" ]; then
  echo "Codex"
  dest="$CODEX_HOME/plugins/$PLUGIN_NAME"
  mkdir -p "$dest"
  cp -R "$PLUGIN_SRC/." "$dest/"
  say "plugin -> $dest"

  # register in the personal marketplace
  mkt="$HOME/.agents/plugins/marketplace.json"
  mkdir -p "$(dirname "$mkt")"
  if [ ! -f "$mkt" ]; then
    cat > "$mkt" <<'EOF'
{
  "name": "personal",
  "interface": { "displayName": "Personal Plugins" },
  "plugins": []
}
EOF
    say "created $mkt"
  fi
  if command -v jq >/dev/null 2>&1; then
    tmp="$(mktemp)"
    jq --arg n "$PLUGIN_NAME" --arg p "$CODEX_HOME/plugins/$PLUGIN_NAME" '
      .plugins |= (map(select(.name != $n)) + [{
        name: $n,
        source: { source: "local", path: $p },
        policy: { installation: "AVAILABLE" },
        category: "Creative"
      }])' "$mkt" > "$tmp" && mv "$tmp" "$mkt"
    say "registered in $mkt"
  else
    say "jq not found — add the entry to $mkt manually"
  fi
else
  [ "$DO_CODEX" = 1 ] && say "Codex not found at $CODEX_HOME — skipped"
fi

# ---------------------------------------------------------- Claude Code
if [ "$DO_CLAUDE" = 1 ] && [ -d "$CLAUDE_HOME" ]; then
  echo "Claude Code"
  say "run this inside Claude Code:"
  say "    /plugin marketplace add $REPO_DIR"
  say "    /plugin install $PLUGIN_NAME@leduy-pets"
  say "(or from GitHub: /plugin marketplace add leduy-it/codex-pet-bunny)"
else
  [ "$DO_CLAUDE" = 1 ] && say "Claude Code not found at $CLAUDE_HOME — skipped"
fi

# ------------------------------------------------------------------ pet
if [ "$DO_PET" = 1 ]; then
  echo "Bunny pet"
  petdir="$CODEX_HOME/pets/bunny"
  mkdir -p "$petdir"
  cp "$REPO_DIR/pets/bunny/pet.json" "$REPO_DIR/pets/bunny/spritesheet.webp" "$petdir/"
  say "pet -> $petdir"
  say "enable it: Codex Settings -> Appearance / Pets -> Bunny   (then /pet)"
fi

echo
echo "Done."
