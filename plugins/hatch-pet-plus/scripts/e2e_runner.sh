#!/bin/zsh
# End-to-end pet build for one mascot, from an already-approved base sprite.
#   e2e_runner.sh <key> <display-name> <style-preset> <identity-sentence>
#
# Generates: 8 rows -> mirror -> cardinals -> look row 9 -> look row 10
#            -> despill -> extract -> atlas(8x11) -> validate -> contact sheet -> per-lane GIFs -> package
set -u

KEY="$1"; NAME="$2"; STYLE="$3"; IDENT="$4"
BASE_SRC="$5"

SKILL=~/.codex/skills/hatch-pet/scripts
RUN=$HOME/.codex/pet-runs/$KEY
SP=/private/tmp/claude-501/-Users-duyle/dd5d1313-7ca6-4b02-9fc6-5b2843e4b18c/scratchpad/pet
mkdir -p "$SP/prompts/e2e/$KEY" "$SP/logs/e2e" "$SP/results/e2e"

log () { print -r -- "[$KEY] $1" }

# ---------- 0. pick a chroma key far from THIS pet's palette ----------
# prepare_pet_run's auto-pick gave Blip MAGENTA — but Blip is blue with a violet outline,
# so the key sat next to the sprite's own colours and the spill could not be separated.
cp "$BASE_SRC" "/tmp/${KEY}_base.png"
CHROMA=$(python3 "$SP/pick_key.py" "/tmp/${KEY}_base.png" --rewrite)
log "chroma key: $CHROMA (base bg recoloured to match)"

# ---------- 1. scaffold the run, install the approved base ----------
python3 "$SKILL/prepare_pet_run.py" \
  --chroma-key "$CHROMA" \
  --pet-name "$NAME" --pet-id "$KEY" --display-name "$NAME" \
  --description "$NAME — a $STYLE Codex pet." \
  --output-dir "$RUN" \
  --pet-notes "$IDENT" \
  --style-preset "$STYLE" \
  --force > /dev/null 2>&1 || { log "scaffold FAILED"; exit 1; }

mkdir -p "$RUN/decoded" "$RUN/references"
cp "/tmp/${KEY}_base.png" "$RUN/decoded/base.png"
cp "/tmp/${KEY}_base.png" "$RUN/references/canonical-base.png"
AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
TMP=$(mktemp); jq --arg at "$AT" '(.jobs[]|select(.id=="base")) += {status:"complete", completed_at:$at}' \
  "$RUN/imagegen-jobs.json" > "$TMP" && mv "$TMP" "$RUN/imagegen-jobs.json"
log "scaffolded"

# ---------- 2. the 8 standard rows, in parallel processes ----------
STATES=(idle running-right waving jumping failed waiting running review)

typeset -A ACTION
ACTION[idle]='State IDLE: a calm, low-distraction resting loop — gentle breathing/bobbing, a small blink or equivalent, a tiny idle flourish. Every frame must differ, but keep it quiet. No walking, no gestures, no new props.'
ACTION[running-right]='State RUNNING-RIGHT (plays when the user DRAGS the pet to the RIGHT): the pet faces RIGHT and travels RIGHT with a visibly alternating locomotion cadence across the 8 frames. No speed lines, no dust, no motion trails.'
ACTION[waving]='State WAVING: a friendly greeting gesture — clear start, raised gesture, return. Convey it through limb/body pose only. NO wave marks, arcs, lines, sparkles or floating symbols.'
ACTION[jumping]='State JUMPING (plays on HOVER — the most-seen animation, make it charming): a small, bouncy, joyful hop — anticipation crouch, lift-off, airborne peak with a delighted expression, descent, settle.

CRITICAL — KEEP THE HOP SMALL. The pet must rise by AT MOST about 15% of its own body height. A big leap is WRONG.
Reason: the strip is cropped to its content and scaled into a fixed 192x208 cell. A tall jump arc makes the crop taller, which SHRINKS the pet when it is fitted into the cell — the pet then visibly halves in size the moment the user hovers it. Measured on a previous run: the pet came out 129px tall here versus 197px in idle, a 35% shrink.

So: convey the jump mostly through SQUASH AND STRETCH and pose (crouch, stretch upward, tuck legs, land and squash) and only a SMALL amount of actual vertical travel. The pet must be drawn at the SAME SIZE as in the attached idle strip in every frame, and the overall vertical span of the whole strip must stay close to the pet own height.'
ACTION[failed]='State FAILED: a sad, deflated, disappointed reaction — drooping, slumping, downcast. Readable but not noisy. No red X, no floating symbols, no detached smoke or stars.'
ACTION[waiting]='State WAITING (Codex is blocked on the user): an expectant asking pose — looking up at the user, attentive, politely requesting input. Clearly DIFFERENT from ordinary idle and from review.'
ACTION[running]='State RUNNING (Codex is WORKING/THINKING — this is NOT foot-running): focused effort, concentrating, processing, scanning. NO jogging, NO sprinting, NO strides, NO directional travel, NO speed lines.'
ACTION[review]='State REVIEW: a focused, inspecting, thinking loop — leaning in, narrowed/blinking eyes, a thoughtful pose. NO magnifying glass, NO papers, NO new props.'

for S in $STATES; do
  cat > "$SP/prompts/e2e/$KEY/$S.txt" <<EOF
Generate exactly ONE image: the "$S" animation row strip for the Codex pet "$NAME".
Do NOT generate any other row. Do NOT run scripts. Do NOT edit imagegen-jobs.json. Do NOT build an atlas. Do NOT package.

## Read this row's prompt for the exact frame count and layout
$RUN/prompts/rows/$S.md

## Attach BOTH of these to the image_gen call
$RUN/references/canonical-base.png            — THE canonical identity. Match it exactly.
$RUN/references/layout-guides/$S.png          — layout guide (frame count/spacing ONLY; never copy its boxes, borders, marks or colours)

## Identity — IDENTICAL in every frame, only the POSE changes
$IDENT
Preserve the exact style, palette, materials, proportions, face and silhouette of the canonical base.

## This row's action
${ACTION[$S]}

## Style: $STYLE
Match the canonical base's style exactly.

## CONSTANT SCALE
The pet must be drawn at EXACTLY the same size in every frame of the strip. Do not zoom or scale between frames. Inconsistent frame size makes the animation pop and is a FAILURE.

## Background and edges
- Perfectly flat, uniform, pure $CHROMA chroma-key background.
- CLEAN, DEFINITE outer silhouette. No wispy strands, no translucent fuzz, no motion blur, no glow.
- NO chroma-colour tint, rim-light or bounce light on the pet.
- No ground shadows, no scenery, no text, no detached effects.
- Each pose sits fully inside its own frame slot, complete and unclipped.

## MANDATORY VERIFICATION
A model previously printed the OUT= line WITHOUT calling image_gen and WITHOUT writing a file. That is a FAILURE.
You MUST: (1) call image_gen, (2) copy the result to the exact path below, (3) run \`ls -la <path>\` to prove it exists, (4) only then print the final block with the real byte size.

## Save to EXACTLY this path
$RUN/decoded/$S.png

## Rules
- DO NOT SPAWN SUBAGENTS. Call the built-in image_gen tool YOURSELF, inline.
- Built-in image_gen only. No CLI, no OPENAI_API_KEY. Do not post-process.

## Final output
ROW=$S
OUT=$RUN/decoded/$S.png
SIZE_BYTES=<real byte size from ls>
EOF
done

cd "$HOME"

# idle FIRST — it becomes the SIZE REFERENCE for every other lane.
# (Blip's jumping row came out 104px tall vs 198px elsewhere: a 47% shrink on hover.)
for try in 1 2; do
  [[ -f "$RUN/decoded/idle.png" ]] && break
  codex exec --skip-git-repo-check -m gpt-5.5 --output-last-message "$SP/results/e2e/${KEY}_idle.txt" \
    - < "$SP/prompts/e2e/$KEY/idle.txt" > "$SP/logs/e2e/${KEY}_idle.out" 2>&1
done
[[ -f "$RUN/decoded/idle.png" ]] || { log "idle FAILED"; exit 2; }
log "idle done (now the scale reference)"

# every other lane attaches idle and must match its size
for S in ${STATES:1}; do
  perl -0pi -e "s|## Attach BOTH of these to the image_gen call|## Attach ALL of these to the image_gen call\n$RUN/decoded/idle.png   — THE SIZE REFERENCE. The pet must be drawn at EXACTLY this size. Do not draw it bigger or smaller than it is here.|" "$SP/prompts/e2e/$KEY/$S.txt"
  perl -0pi -e "s|## CONSTANT SCALE|## CONSTANT SCALE — MATCH THE ATTACHED IDLE STRIP\nThe pet must be the SAME SIZE as in the attached idle strip, in EVERY frame of this row. A previous run drew the jumping row at HALF the size of idle, which made the pet visibly shrink when hovered. That is a FAILURE.|" "$SP/prompts/e2e/$KEY/$S.txt"
done

for S in ${STATES:1}; do
  ( codex exec --skip-git-repo-check -m gpt-5.5 --output-last-message "$SP/results/e2e/${KEY}_$S.txt" \
      - < "$SP/prompts/e2e/$KEY/$S.txt" > "$SP/logs/e2e/${KEY}_$S.out" 2>&1 ) &
  sleep 7
done
wait

MISSING=()
for S in $STATES; do [[ -f "$RUN/decoded/$S.png" ]] || MISSING+=("$S"); done
# one retry pass for anything that silently produced nothing
if (( ${#MISSING[@]} )); then
  log "retrying: ${MISSING[*]}"
  for S in $MISSING; do
    codex exec --skip-git-repo-check -m gpt-5.5 --output-last-message "$SP/results/e2e/${KEY}_$S.txt" \
      - < "$SP/prompts/e2e/$KEY/$S.txt" > "$SP/logs/e2e/${KEY}_$S.out" 2>&1
  done
fi
for S in $STATES; do
  [[ -f "$RUN/decoded/$S.png" ]] || { log "ROW STILL MISSING: $S — aborting"; exit 2; }
done

# ---------- 2a. DEDUPE: parallel processes share ~/.codex/generated_images/, so one can copy
# another's output. It shipped three broken pets (kiln waving==review, bot-plush failed==jumping,
# mossback failed==waiting) — two animations playing identical footage. Regenerate SEQUENTIALLY.
for attempt in 1 2 3; do
  python3 "$SP/dedupe_lanes.py" "$RUN" --delete && break
  log "duplicate lanes found — regenerating sequentially (attempt $attempt)"
  for S in $STATES; do
    [[ -f "$RUN/decoded/$S.png" ]] && continue
    codex exec --skip-git-repo-check -m gpt-5.5 --output-last-message "$SP/results/e2e/${KEY}_$S.txt" \
      - < "$SP/prompts/e2e/$KEY/$S.txt" > "$SP/logs/e2e/${KEY}_$S.out" 2>&1
  done
done
python3 "$SP/dedupe_lanes.py" "$RUN" || { log "STILL duplicate lanes after 3 attempts — aborting"; exit 4; }

log "8 standard rows done (all unique)"

# ---------- 2b. sync the manifest (the row processes never touch it, to avoid a write race) ----------
AT2=$(date -u +%Y-%m-%dT%H:%M:%SZ)
for S in $STATES; do
  TMP=$(mktemp)
  jq --arg id "$S" --arg at "$AT2" --arg src "$RUN/decoded/$S.png" \
    '(.jobs[]|select(.id==$id)) += {status:"complete", source_path:$src, completed_at:$at}' \
    "$RUN/imagegen-jobs.json" > "$TMP" && mv "$TMP" "$RUN/imagegen-jobs.json"
done
log "manifest synced"

# ---------- 3. mirror running-left ----------
python3 "$SKILL/derive_running_left_from_running_right.py" --run-dir "$RUN" \
  --confirm-appropriate-mirror --decision-note "Symmetric pet, no side-specific prop; mirroring preserves identity." \
  > /dev/null 2>&1
[[ -f "$RUN/decoded/running-left.png" ]] || { log "mirror FAILED"; exit 3; }
log "running-left mirrored"

echo "$KEY OK_ROWS"
