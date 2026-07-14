#!/bin/zsh
# Generate base art for a batch of original mascots, in parallel, quota-gated.
#
#   gen_mascots.sh <quota-ceiling> <spec.json>...
#
# One image each (~0.6% of the weekly Codex window). The ceiling is checked once up
# front against the whole batch, and each spec is skipped if the running quota has
# crossed it — so a batch cannot blow past the ceiling even if a reading drifts.
set -u

CEILING="$1"; shift
SP=/private/tmp/claude-501/-Users-duyle/dd5d1313-7ca6-4b02-9fc6-5b2843e4b18c/scratchpad/pet
OUT="$SP/mascot-bases"
mkdir -p "$OUT" "$SP/mascot-prompts" "$SP/mascot-logs"

gen () {
  local SPEC="$1"
  local KEY NAME STYLE PROMPT
  KEY=$(jq -r '.key' "$SPEC")
  NAME=$(jq -r '.name' "$SPEC")
  STYLE=$(jq -r '.style' "$SPEC")
  PROMPT=$(jq -r '.imagePrompt' "$SPEC")
  local DST="$OUT/$KEY.png"
  [[ -f "$DST" ]] && { print -r -- "[$KEY] already generated"; return 0; }

  cat > "$SP/mascot-prompts/$KEY.txt" <<EOF
Generate exactly ONE image: the canonical base sprite for an ORIGINAL mascot named "$NAME".

## The character
$PROMPT

## Style: $STYLE
Commit fully to this style. The material must be legible.

## This art is published CC0 — it must be entirely original
Do NOT reproduce or echo any existing character (Pokemon, Sanrio, Ghibli, Disney, Kirby,
Doraemon, or any other). One single connected creature.

## Sprite constraints — this becomes a sprite drawn 88 times
- ONE connected creature. NO detached floating parts, particles, sparks, orbs or motes.
- NO thin wispy strands, hair, smoke or fuzz (they key out as fringe).
- Nothing finer than ~4px at sprite scale. No text, no small symbols.
- CLEAN, DEFINITE outer silhouette. Full body, standing, facing the viewer, generous padding.

## Background
- Perfectly flat, uniform, pure white background. No shadow, no scenery, no ground plane.

## MANDATORY VERIFICATION
A model previously printed OUT= WITHOUT calling image_gen and WITHOUT writing a file. That is a
FAILURE. You MUST: (1) call image_gen, (2) copy the result to the exact path below, (3) run
\`ls -la <path>\` to prove it exists, (4) only then print the final block with the real byte size.

## Save to EXACTLY this path
$DST

## Rules
- DO NOT SPAWN SUBAGENTS. Call the built-in image_gen tool YOURSELF, inline.
- Built-in image_gen only. No CLI, no OPENAI_API_KEY. Do not post-process.

## Final output
OUT=$DST
SIZE_BYTES=<real byte size from ls>
EOF

  local try
  for try in 1 2 3; do
    [[ -f "$DST" ]] && break
    codex exec --skip-git-repo-check -m gpt-5.5 \
      --output-last-message "$SP/mascot-logs/$KEY.last.txt" \
      - < "$SP/mascot-prompts/$KEY.txt" > "$SP/mascot-logs/$KEY.out" 2>&1
  done
  [[ -f "$DST" ]] && print -r -- "[$KEY] OK" || print -r -- "[$KEY] FAILED after 3 tries"
}

USED=$(python3 "$SP/quota.py")
print -r -- "[quota] starting at ${USED}%, ceiling ${CEILING}%"

PIDS=()
for SPEC in "$@"; do
  USED=$(python3 "$SP/quota.py")
  if [[ "$USED" != "-1" ]] && (( $(print -- "$USED >= $CEILING" | bc -l) )); then
    print -r -- "[quota] ${USED}% >= ${CEILING}% — STOPPING, $(jq -r '.key' "$SPEC") and the rest not generated"
    break
  fi
  gen "$SPEC" &
  PIDS+=($!)
  sleep 8
done
wait

DONE=0; MISS=()
for SPEC in "$@"; do
  KEY=$(jq -r '.key' "$SPEC")
  [[ -f "$OUT/$KEY.png" ]] && DONE=$((DONE+1)) || MISS+=("$KEY")
done
print -r -- ""
print -r -- "==== ${DONE}/$# base sprites generated ===="
(( ${#MISS[@]} )) && print -r -- "missing: ${MISS[*]}"
print -r -- "quota now: $(python3 "$SP/quota.py")%"
