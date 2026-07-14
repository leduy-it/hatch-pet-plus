#!/bin/zsh
# Build every evolving pet, in priority order, stopping before the Codex weekly
# quota is exhausted.
#
#   evolve_all.sh <quota-ceiling-percent> <spec.json>...
#
# One evolving pet is ~23 image generations (11 per stage, plus the evolved base),
# and that quota is the same allowance the user needs for their real work. So the
# ceiling is checked BEFORE each pet: if building the next one would likely cross
# it, the runner stops cleanly and says which pets it did not build. Silently
# truncating would read as "we made everything", which is exactly the failure we
# already shipped once.
set -u

CEILING="$1"; shift
SP=/private/tmp/claude-501/-Users-duyle/dd5d1313-7ca6-4b02-9fc6-5b2843e4b18c/scratchpad/pet
mkdir -p "$SP/logs/evolve"
SUMMARY="$SP/logs/evolve/SUMMARY.txt"
: > "$SUMMARY"

# What one evolving pet costs, as a percentage of the weekly window. Measured, not
# guessed: Volt's first stage moved the quota 50% -> 58% over 11 generations, so a
# two-stage pet (~23 generations) is ~15%.
#
# The gate RESERVES this before starting. Checking only the current reading would let
# a pet start at 74% against a 75% ceiling and finish at 89% — the ceiling would bound
# where we begin rather than where we end, which is not what a ceiling is for.
PET_COST_PCT=${PET_COST_PCT:-15}

BUILT=(); SKIPPED=(); FAILED=()

for SPEC in "$@"; do
  ID=$(jq -r '.id' "$SPEC")
  USED=$(python3 "$SP/quota.py")

  if [[ "$USED" != "-1" ]] && (( $(print -- "$USED + $PET_COST_PCT > $CEILING" | bc -l) )); then
    print -r -- "[quota] ${USED}% used + ~${PET_COST_PCT}% for this pet would pass the ${CEILING}% ceiling — STOPPING before $ID" | tee -a "$SUMMARY"
    SKIPPED+=("$ID")
    continue
  fi

  print -r -- "[quota] ${USED}% used (+~${PET_COST_PCT}% budgeted) — building $ID" | tee -a "$SUMMARY"
  if zsh "$SP/e2e_evolve.sh" "$SPEC" 2>&1 | tee -a "$SUMMARY" | grep -q EVOLVE_DONE; then
    BUILT+=("$ID")
  else
    FAILED+=("$ID")
  fi
done

{
  print -r -- ""
  print -r -- "==================== EVOLUTION BATCH ===================="
  print -r -- "built   (${#BUILT[@]}): ${BUILT[*]:-none}"
  print -r -- "failed  (${#FAILED[@]}): ${FAILED[*]:-none}"
  print -r -- "skipped (${#SKIPPED[@]}, quota ceiling ${CEILING}%): ${SKIPPED[*]:-none}"
  print -r -- "quota now: $(python3 "$SP/quota.py")%"
  print -r -- "========================================================"
} | tee -a "$SUMMARY"
