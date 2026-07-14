#!/bin/zsh
# Stage 2: look directions -> 8x11 atlas -> despill -> validate -> contact sheet -> per-lane GIFs -> package
#   e2e_stage2.sh <key> <display-name> <identity-sentence>
set -u
KEY="$1"; NAME="$2"; IDENT="$3"

SKILL=~/.codex/skills/hatch-pet/scripts
RUN=$HOME/.codex/pet-runs/$KEY
SP=/private/tmp/claude-501/-Users-duyle/dd5d1313-7ca6-4b02-9fc6-5b2843e4b18c/scratchpad/pet
REPO=$HOME/Desktop/hatch-pet-plus
# An evolving pet builds each stage as its own pet, then merges them. Those stage
# builds are scaffolding, not artefacts, so they must be able to land outside the
# repo's pets/ directory.
OUT=${PET_OUT_DIR:-$REPO/pets/$KEY}
mkdir -p "$SP/prompts/e2e/$KEY" "$OUT/previews" "$RUN/qa" "$RUN/final"
CHROMA=$(jq -r '.chroma_key.hex' "$RUN/pet_request.json")
log () { print -r -- "[$KEY] $1" }

# ---------- look mechanics plan (learned the hard way: HEAD, not pupils) ----------
cat > "$RUN/qa/look-mechanics.md" <<EOF
# $NAME — Look Mechanics

Gaze is carried by the HEAD, not by moving the pupils. Pupil shifts are invisible at sprite scale
(measured under 2px). Use whatever aiming feature this pet actually has — muzzle, nose, visor, eye,
lens, beak, antenna, front face.

- HORIZONTAL: the head/front TURNS into a three-quarter view. The aiming feature swings clearly to
  that side of head centre. The far side narrows; the near side widens.
- UP: the head TILTS BACK — the aiming feature RIDES HIGH on the face, chin/underside shows.
- DOWN: the head TILTS FORWARD — the aiming feature DROPS LOW, more of the top/crown shows.
- Diagonals combine the two.
- The BODY, FEET and BASELINE stay planted and identical in every cell.
EOF

GAZE="Gaze is carried by the HEAD, NOT by the pupils — pupil movement is invisible at this size.
HORIZONTAL: the head/front TURNS into a three-quarter view; the pet's aiming feature (muzzle, nose, visor, eye, lens, beak — whatever it has) swings CLEARLY to that side of head centre.
UP: the head TILTS BACK, the aiming feature RIDES HIGH on the face.
DOWN: the head TILTS FORWARD, the aiming feature DROPS LOW, more of the crown shows.
Diagonals combine both. Do NOT rotate/skew the whole sprite. BODY, FEET and BASELINE stay planted and identical in every cell."

COMMON="## Identity — IDENTICAL in every cell
$IDENT
Match the canonical base's style, palette, materials, proportions and silhouette exactly.

## Background and edges
- Perfectly flat, uniform, pure $CHROMA chroma-key background, generous padding.
- CLEAN, DEFINITE silhouette. No wispy strands, no fuzz, no blur, no glow.
- NO chroma-colour tint or rim-light on the pet.
- No shadows, scenery, text, labels, degree marks, arrows, guide marks, or detached effects.
- SAME SCALE and SAME BASELINE in every cell. No zooming.

## MANDATORY VERIFICATION
A model previously printed OUT= without calling image_gen and without writing a file. That is a FAILURE.
You MUST: (1) call image_gen, (2) copy to the exact path, (3) run \`ls -la <path>\` to prove it exists,
(4) only then print the final block with the real byte size.

## Rules
- DO NOT SPAWN SUBAGENTS. Call the built-in image_gen tool YOURSELF, inline.
- Built-in image_gen only. Do not post-process."

# ---------- cardinals ----------
cat > "$SP/prompts/e2e/$KEY/cardinals.txt" <<EOF
Generate ONE image: the four-cardinal look-anchor strip for the Codex pet "$NAME". Nothing else.

## Attach these to the image_gen call
$RUN/references/canonical-base.png
$RUN/references/layout-guides/look-cardinals.png
$RUN/qa/contact-sheet.png

## Draw FOUR full-body poses, left to right, in EXACTLY this order
slot 1 = 000 looking straight UP
slot 2 = 090 looking hard to the SCREEN-RIGHT (the right edge of the image)
slot 3 = 180 looking straight DOWN
slot 4 = 270 looking hard to the SCREEN-LEFT (the left edge of the image)

SCREEN-LEFT/RIGHT mean the VIEWER's edges, never the pet's own left/right.
Slots 2 and 4 must be OBVIOUS MIRROR-OPPOSITES, instantly tellable apart at a glance.
Slots 1 and 3 must be obviously different from each other and from a neutral front pose.

$GAZE

$COMMON

## Save to EXACTLY this path
$RUN/decoded/look-cardinals.png

## Final output
OUT=$RUN/decoded/look-cardinals.png
SIZE_BYTES=<real byte size from ls>
EOF

cd "$HOME"
for try in 1 2; do
  [[ -f "$RUN/decoded/look-cardinals.png" ]] && break
  codex exec --skip-git-repo-check -m gpt-5.5 --output-last-message "$SP/results/e2e/${KEY}_card.txt" \
    - < "$SP/prompts/e2e/$KEY/cardinals.txt" > "$SP/logs/e2e/${KEY}_card.out" 2>&1
done
[[ -f "$RUN/decoded/look-cardinals.png" ]] || { log "cardinals FAILED"; exit 2; }

python3 "$SKILL/extract_cardinal_anchors.py" --strip "$RUN/decoded/look-cardinals.png" \
  --output-dir "$RUN/decoded/look-anchors" --chroma-key "$CHROMA" \
  --json-out "$RUN/qa/cardinal-anchors.json" > /dev/null 2>&1
python3 "$SKILL/compose_cardinal_anchor_strip.py" --anchors-dir "$RUN/decoded/look-anchors" \
  --output "$RUN/decoded/look-anchors-approved.png" > /dev/null 2>&1
log "cardinals done"

# ---------- look rows 9 and 10 ----------
mk_look () {
  local ROW="$1" DEGS="$2" SWEEP="$3" EXTRA="$4"
  cat > "$SP/prompts/e2e/$KEY/look-row-$ROW.txt" <<EOF
Generate ONE image: look row $ROW for the Codex pet "$NAME". Nothing else.

## Attach these to the image_gen call
$RUN/decoded/look-anchors-approved.png   — THE APPROVED CARDINALS (000 up, 090 screen-right, 180 down, 270 screen-left). This defines what each direction MEANS. MOST IMPORTANT.
$RUN/references/canonical-base.png
$RUN/references/layout-guides/look-row-$ROW.png
$EXTRA

## Draw EIGHT full-body poses in ONE horizontal strip, left to right, at these gaze angles
$DEGS
(000 = UP / 12 o'clock, going CLOCKWISE.)

$SWEEP

This is ONE CONTINUOUS, SMOOTH, MONOTONIC sweep in even 22.5-degree steps. No slot may jump
backwards or repeat its neighbour. The direction must progress steadily across all 8 slots.

$GAZE

$COMMON

## Save to EXACTLY this path
$RUN/decoded/look-row-$ROW.png

## Final output
OUT=$RUN/decoded/look-row-$ROW.png
SIZE_BYTES=<real byte size from ls>
EOF
}

mk_look 9 \
"slot 1 = 000, slot 2 = 022.5, slot 3 = 045, slot 4 = 067.5, slot 5 = 090, slot 6 = 112.5, slot 7 = 135, slot 8 = 157.5" \
"The sweep runs from looking straight UP (slot 1), round through looking straight SCREEN-RIGHT (slot 5), to looking almost straight DOWN (slot 8). The head stays turned toward the SCREEN-RIGHT for the WHOLE row — slot 5 is the FURTHEST right, and slots 6-8 stay screen-right while progressively tipping DOWN. Slot 1 must match the 000 cardinal; slot 5 must match the 090 cardinal." \
""

mk_look 10 \
"slot 1 = 180, slot 2 = 202.5, slot 3 = 225, slot 4 = 247.5, slot 5 = 270, slot 6 = 292.5, slot 7 = 315, slot 8 = 337.5" \
"The sweep runs from looking straight DOWN (slot 1), round through looking straight SCREEN-LEFT (slot 5), back up to almost straight UP (slot 8). The head stays turned toward the SCREEN-LEFT for the WHOLE row — slot 5 is the FURTHEST left, and slots 6-8 stay screen-left while progressively tipping UP. Slot 1 must match the 180 cardinal; slot 5 must match the 270 cardinal." \
"$RUN/decoded/look-row-9.png   — completed row 9, for identity/scale/registration continuity"

for ROW in 9 10; do
  for try in 1 2; do
    [[ -f "$RUN/decoded/look-row-$ROW.png" ]] && break
    codex exec --skip-git-repo-check -m gpt-5.5 --output-last-message "$SP/results/e2e/${KEY}_look$ROW.txt" \
      - < "$SP/prompts/e2e/$KEY/look-row-$ROW.txt" > "$SP/logs/e2e/${KEY}_look$ROW.out" 2>&1
  done
  [[ -f "$RUN/decoded/look-row-$ROW.png" ]] || { log "look row $ROW FAILED"; exit 3; }
done
log "look rows done"

# ---------- despill + assemble + validate + QA + package ----------
# restore pristine strips so this stage is re-runnable
if [[ -d "$RUN/decoded-raw" ]]; then
  for f in "$RUN"/decoded-raw/*.png; do cp "$f" "$RUN/decoded/$(basename "$f")" 2>/dev/null; done
fi

# The model does NOT always obey the requested chroma colour. Mossback declared cyan and the
# model drew `idle` and `running-left` on MAGENTA — the extractor keyed out cyan, so the magenta
# background got baked into the sprite as an opaque rectangle. validate_atlas passed it (0 errors)
# because it only checks contamination by the DECLARED key. So: detect the ACTUAL background and
# force it onto the declared key before anything else touches the strips.
python3 "$SP/normalize_bg.py" "$KEY" "$CHROMA"

# The assembler rejects a look row if the sprite reaches its cell edge:
#   "look direction 000 has 113 non-transparent pixels near its final cell edge"
# bot-pixel's robot sat 48px from the left of its slot and flush against the right (R=0px) —
# off-centre, not oversized. Recentre and pad every look slot so nothing touches an edge.
for R in 9 10; do
  [[ -f "$RUN/decoded/look-row-$R.png" ]] && python3 "$SP/pad_look_row.py" "$RUN/decoded/look-row-$R.png" "$CHROMA"
done

python3 "$SP/despill_strips.py" "$KEY" "$CHROMA"

python3 "$SKILL/extract_strip_frames.py" --decoded-dir "$RUN/decoded" --output-dir "$RUN/frames" \
  --states all --method stable-slots > /dev/null 2>&1

# The extractor fits each row to its OWN bbox, so the jump arc shrinks the pet (129px vs 197px).
# Normalise every lane to one size, with headroom, so the pet does not resize between animations.
python3 "$SP/normalize_lane_scale.py" "$RUN/frames"

python3 "$SKILL/inspect_frames.py" --frames-root "$RUN/frames" --json-out "$RUN/qa/review.json" \
  --require-components --allow-stable-slots > /dev/null 2>&1

# base 8x9, then extend to 8x11 with the look rows
python3 "$SKILL/compose_atlas.py" --frames-root "$RUN/frames" \
  --output "$RUN/final/base-atlas.png" > /dev/null 2>&1
# --edge-pixel-threshold: a pixel-art robot with flat feet legitimately sits on the bottom cell
# edge, which trips the default check. We verify real clipping separately in verify_pet.py.
python3 "$SKILL/assemble_extended_atlas.py" --base-atlas "$RUN/final/base-atlas.png" \
  --look-row-9 "$RUN/decoded/look-row-9.png" --look-row-10 "$RUN/decoded/look-row-10.png" \
  --chroma-key "$CHROMA" --edge-margin 1 --edge-pixel-threshold 250 \
  --output "$RUN/final/spritesheet.png" --webp-output "$RUN/final/spritesheet.webp" > /dev/null 2>&1 \
  || python3 "$SKILL/assemble_extended_atlas.py" --base-atlas "$RUN/final/base-atlas.png" \
       --look-cells-dir "$RUN/frames" --output "$RUN/final/spritesheet.png" \
       --webp-output "$RUN/final/spritesheet.webp" > /dev/null 2>&1

# final atlas chroma pass — the SKILL's own despill is built for transparent sprite edges
python3 "$SKILL/despill_chroma_edges.py" "$RUN/final/spritesheet.png" \
  --output "$RUN/final/spritesheet.png" --chroma-key "$CHROMA" \
  --json-out "$RUN/qa/despill.json" > /dev/null 2>&1

# then our universal (multi-channel-safe) pass + lossless webp
python3 "$SP/despill_atlas.py" "$KEY" "$CHROMA"

python3 "$SKILL/validate_atlas.py" "$RUN/final/spritesheet.webp" \
  --json-out "$RUN/final/validation.json" > /dev/null 2>&1
OK=$(jq -r '.ok' "$RUN/final/validation.json" 2>/dev/null)
ERRS=$(jq -r '.errors|length' "$RUN/final/validation.json" 2>/dev/null)
log "validation ok=$OK errors=$ERRS"

python3 "$SKILL/make_contact_sheet.py" "$RUN/final/spritesheet.webp" \
  --output "$RUN/qa/contact-sheet.png" > /dev/null 2>&1
python3 "$SKILL/render_animation_previews.py" --frames-root "$RUN/frames" \
  --output-dir "$RUN/qa/previews" > /dev/null 2>&1

# ---------- publish into the repo ----------
mkdir -p "$OUT/previews"
cp "$RUN/final/spritesheet.webp" "$OUT/spritesheet.webp" 2>/dev/null
cp "$RUN/final/validation.json"  "$OUT/validation.json"  2>/dev/null
cp "$RUN/qa/contact-sheet.png"   "$OUT/contact-sheet.png" 2>/dev/null
cp "$RUN/qa/previews/"*.gif      "$OUT/previews/" 2>/dev/null
jq -n --arg id "$KEY" --arg n "$NAME" --arg d "$NAME — a Codex pet." \
  '{id:$id, displayName:$n, description:$d, spriteVersionNumber:2, spritesheetPath:"spritesheet.webp"}' \
  > "$OUT/pet.json"

# independent QA — validate_atlas passed a pet with a MAGENTA BOX baked into it (0 errors),
# because it only checks the DECLARED key. This is the backstop, and it is a PUBLISH GATE:
# a pet that fails it must not stay in the repo. Previously this only set an exit code that
# nothing read, so three pets shipped with two lanes playing identical footage while the
# build reported success.
python3 "$SP/verify_pet.py" "$OUT" "$CHROMA"
VERIFY=$?
if (( VERIFY )); then
  log "QA FAILED — withdrawing $OUT rather than publishing it"
  python3 -c 'import shutil,sys; shutil.rmtree(sys.argv[1], ignore_errors=True)' "$OUT"
  echo "$KEY FAIL ok=$OK errors=$ERRS verify=$VERIFY"
  exit 8
fi

log "PACKAGED -> $OUT"
echo "$KEY DONE ok=$OK errors=$ERRS verify=$VERIFY"
