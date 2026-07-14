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

DO_CODEX=1; DO_CLAUDE=1; DO_PET=0; PET_NAME=""
prev=""
for a in "$@"; do
  case "$a" in
    --codex)  DO_CLAUDE=0 ;;
    --claude) DO_CODEX=0 ;;
    --pet)    DO_PET=1 ;;
    --list)   ls "$REPO_DIR/pets" 2>/dev/null | grep -v '\.md$' | sed 's/^/  /'; exit 0 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *)        [ "$prev" = "--pet" ] && PET_NAME="$a" ;;
  esac
  prev="$a"
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
  say "(or from GitHub: /plugin marketplace add leduy-it/hatch-pet-plus)"
else
  [ "$DO_CLAUDE" = 1 ] && say "Claude Code not found at $CLAUDE_HOME — skipped"
fi

# ------------------------------------------------------------------ pet
if [ "$DO_PET" = 1 ]; then
  pets="${PET_NAME:-$(ls "$REPO_DIR/pets" | grep -v '\.md$')}"
  echo "Pets"
  for p in $pets; do
    src="$REPO_DIR/pets/$p"
    if [ ! -f "$src/pet.json" ]; then say "no such pet: $p  (try ./install.sh --list)"; continue; fi

    # `|| true` is load-bearing: `ls` exits non-zero whenever one of the two patterns
    # does not match — which is ALWAYS, since a pet is either legacy or evolving, never
    # both — and `set -e` would abort the whole installer on the first pet.
    sheets=$(ls "$src"/spritesheet.webp "$src"/stage-*.webp 2>/dev/null || true)
    if [ -z "$sheets" ]; then say "$p has no spritesheet — skipped"; continue; fi

    # ---- Codex ----------------------------------------------------------------
    # Codex has never heard of `stages`, and its manifest parser is closed — so rather
    # than bet that it ignores an unknown key, hand it exactly the shape it has always
    # been given: stage one, under the plain `spritesheet.webp` name. Codex could never
    # show anything else; it does not level pets up.
    petdir="$CODEX_HOME/pets/$p"
    mkdir -p "$petdir"
    if [ -f "$src/stage-1.webp" ]; then
      cp "$src/stage-1.webp" "$petdir/spritesheet.webp"
      python3 - "$src/pet.json" "$petdir/pet.json" <<'PY'
import json, sys
pet = json.load(open(sys.argv[1]))
pet.pop("stages", None)
pet["spritesheetPath"] = "spritesheet.webp"
json.dump(pet, open(sys.argv[2], "w"), indent=2, ensure_ascii=False)
PY
    else
      cp "$src/pet.json" "$src/spritesheet.webp" "$petdir/"
    fi

    # ---- evolvepet ------------------------------------------------------------
    # A host that DOES understand stages gets the pet whole, so it can actually evolve.
    # https://github.com/leduy-it/evolvepet
    if [ -f "$src/stage-2.webp" ] && [ -d "$HOME/.agentpet" ]; then
      evodir="$HOME/.agentpet/pets/$p"
      mkdir -p "$evodir"
      cp "$src/pet.json" "$evodir/"
      # shellcheck disable=SC2086
      cp $sheets "$evodir/"
      say "$p -> $petdir (stage 1)  +  $evodir (evolving)"
    elif [ -f "$src/stage-2.webp" ]; then
      say "$p -> $petdir  (stage 1 — Codex cannot evolve a pet; install evolvepet for that)"
    else
      say "$p -> $petdir"
    fi
  done
  say ""
  say "enable one: Codex Settings -> Appearance / Pets   (then /pet)"
  say "or set it directly in ~/.codex/config.toml:  selected-avatar-id = \"<name>\""
fi

echo
echo "Done."
