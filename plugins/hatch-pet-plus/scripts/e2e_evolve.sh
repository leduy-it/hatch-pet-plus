#!/bin/zsh
# Build ONE evolving pet, end to end, from a spec file.
#
#   e2e_evolve.sh <spec.json>
#
# Codex has no notion of "the same pet, one level up" — a stage is a whole 8x11
# atlas. So each stage is built by the ordinary hardened pipeline as if it were
# its own pet, and the two builds are merged into a single pet directory whose
# pet.json declares `stages`.
#
#   stage 1  base art (given)          -> e2e_runner -> e2e_stage2 -> pets/<id>-s1
#   stage 2  base art (GENERATED from
#            stage 1 + the evolution
#            prompt in the spec)       -> e2e_runner -> e2e_stage2 -> pets/<id>-s2
#   merge    -> pets/<id>/{pet.json, stage-1.webp, stage-2.webp, evolution.gif}
set -u

SPEC="$1"
SP=/private/tmp/claude-501/-Users-duyle/dd5d1313-7ca6-4b02-9fc6-5b2843e4b18c/scratchpad/pet
REPO=$HOME/Desktop/hatch-pet-plus
mkdir -p "$SP/logs/evolve" "$SP/prompts/evolve" "$SP/results/evolve"

ID=$(jq -r '.id'       "$SPEC")
STYLE=$(jq -r '.style' "$SPEC")
BASE=$(jq -r '.base'   "$SPEC")
IDENT1=$(jq -r '.identity' "$SPEC")
N1=$(jq -r '.stages[0].name' "$SPEC")
N2=$(jq -r '.stages[1].name' "$SPEC")
PROMPT2=$(jq -r '.stages[1].imagePrompt' "$SPEC")
ANCHORS=$(jq -r '.stages[1].identityAnchors | join("; ")' "$SPEC")

log () { print -r -- "[evolve:$ID] $1" }

# Stage builds are scaffolding — they live outside the repo so pets/ only ever
# contains finished pets.
B1="$SP/builds/$ID-s1"
B2="$SP/builds/$ID-s2"
mkdir -p "$SP/builds"

# The sentinel must be the LAST artefact written, not the first. stage-2.webp lands
# before pet.json and long before evolution.gif, so using it would let a run that
# crashed midway report EVOLVE_DONE on the next attempt.
if [[ -f "$REPO/pets/$ID/evolution.gif" ]]; then
  log "already built — nothing to do"
  echo "$ID EVOLVE_DONE verify=cached"
  exit 0
fi

# ---------- stage 1 ----------
if [[ -f "$B1/spritesheet.webp" ]]; then
  log "stage 1 already built — skipping"
else
  log "stage 1: $N1"
  zsh "$SP/e2e_runner.sh" "$ID-s1" "$N1" "$STYLE" "$IDENT1" "$BASE" \
    >> "$SP/logs/evolve/$ID.log" 2>&1 || { log "stage 1 rows FAILED"; exit 2; }
  PET_OUT_DIR="$B1" zsh "$SP/e2e_stage2.sh" "$ID-s1" "$N1" "$IDENT1" \
    >> "$SP/logs/evolve/$ID.log" 2>&1 || { log "stage 1 atlas FAILED"; exit 2; }
fi

# ---------- the evolved base art ----------
BASE2="$SP/bases/$ID-s2.png"
mkdir -p "$SP/bases"
if [[ ! -f "$BASE2" ]]; then
  log "generating the evolved base: $N1 -> $N2"
  cat > "$SP/prompts/evolve/$ID-base2.txt" <<EOF
Generate exactly ONE image: the canonical base sprite for "$N2", the EVOLVED form of the pet "$N1".

## Attach this to the image_gen call
$BASE   — "$N1", the form it evolves FROM. This is the identity to carry forward.

## The evolution
$PROMPT2

## Identity that MUST survive the evolution
$ANCHORS
It must still be recognisably the SAME creature, one form later — not a different species.

## Style
Match the attached base exactly: same rendering style ($STYLE), same material language, same lighting,
same level of finish. Only the CREATURE changes, never the art style.

## This is an evolution, NOT a resize
A scaled-up copy of the attached sprite is a FAILURE. The change must be visible in SILHOUETTE and in
CHARACTER — new structure, gear, materials or an ignited effect that is part of the body.

## Sprite constraints — this art gets drawn 88 more times, identically
- ONE single connected creature. NO detached floating parts, particles, sparks, orbs or motes:
  anything not attached to the body is destroyed by the chroma-key extractor.
- NO thin wispy strands, hairs, smoke or fuzz — they key out as fringe.
- Nothing finer than about 4 pixels at sprite scale. No text, no small symbols.
- CLEAN, DEFINITE outer silhouette.
- Full body, standing, facing the viewer, complete and unclipped, generous padding.

## Background
- Perfectly flat, uniform, pure white background. No shadow, no scenery, no ground plane.

## MANDATORY VERIFICATION
A model previously printed the OUT= line WITHOUT calling image_gen and WITHOUT writing a file. That is
a FAILURE. You MUST: (1) call image_gen, (2) copy the result to the exact path below, (3) run
\`ls -la <path>\` to prove it exists, (4) only then print the final block with the real byte size.

## Save to EXACTLY this path
$BASE2

## Rules
- DO NOT SPAWN SUBAGENTS. Call the built-in image_gen tool YOURSELF, inline.
- Built-in image_gen only. No CLI, no OPENAI_API_KEY. Do not post-process.

## Final output
OUT=$BASE2
SIZE_BYTES=<real byte size from ls>
EOF

  for try in 1 2 3; do
    [[ -f "$BASE2" ]] && break
    codex exec --skip-git-repo-check -m gpt-5.5 \
      --output-last-message "$SP/results/evolve/$ID-base2.txt" \
      - < "$SP/prompts/evolve/$ID-base2.txt" >> "$SP/logs/evolve/$ID.log" 2>&1
  done
  [[ -f "$BASE2" ]] || { log "evolved base FAILED after 3 tries"; exit 3; }
fi
log "evolved base ready"

# ---------- stage 2 ----------
IDENT2="$N2 — the evolved form of $N1. $(jq -r '.stages[1].transformation' "$SPEC") Identity anchors carried over: $ANCHORS"
if [[ -f "$B2/spritesheet.webp" ]]; then
  log "stage 2 already built — skipping"
else
  log "stage 2: $N2"
  zsh "$SP/e2e_runner.sh" "$ID-s2" "$N2" "$STYLE" "$IDENT2" "$BASE2" \
    >> "$SP/logs/evolve/$ID.log" 2>&1 || { log "stage 2 rows FAILED"; exit 4; }
  PET_OUT_DIR="$B2" zsh "$SP/e2e_stage2.sh" "$ID-s2" "$N2" "$IDENT2" \
    >> "$SP/logs/evolve/$ID.log" 2>&1 || { log "stage 2 atlas FAILED"; exit 4; }
fi

# ---------- QA each stage BEFORE it is published ----------
# validate_atlas has passed pets with a magenta box baked in, a violet halo on half
# their edges, and two lanes playing identical footage. This is the gate that caught
# all three. A stage that fails it must not reach the repo.
CHROMA1=$(jq -r '.chroma_key.hex' "$HOME/.codex/pet-runs/$ID-s1/pet_request.json")
CHROMA2=$(jq -r '.chroma_key.hex' "$HOME/.codex/pet-runs/$ID-s2/pet_request.json")
FAIL=0
python3 "$SP/verify_pet.py" "$B1" "$CHROMA1" >> "$SP/logs/evolve/$ID.log" 2>&1 || FAIL=1
python3 "$SP/verify_pet.py" "$B2" "$CHROMA2" >> "$SP/logs/evolve/$ID.log" 2>&1 || FAIL=1
if (( FAIL )); then
  log "QA FAILED — refusing to publish. See $SP/logs/evolve/$ID.log"
  echo "$ID EVOLVE_FAIL verify=1"
  exit 7
fi

# ---------- merge into one evolving pet ----------
MERGE=$(mktemp)
jq --arg s1 "$B1" --arg s2 "$B2" \
  '{id, type, description, stages: [
      (.stages[0] + {buildDir: $s1}),
      (.stages[1] + {buildDir: $s2})
   ]}' "$SPEC" > "$MERGE"
python3 "$SP/merge_stages.py" "$REPO/pets/$ID" "$MERGE" || { log "merge FAILED"; exit 5; }
rm -f "$MERGE"

python3 "$SP/make_evolution_gif.py" "$REPO/pets/$ID" || { log "evolution gif FAILED"; exit 6; }

log "DONE  both stages QA-clean"
echo "$ID EVOLVE_DONE verify=0"
