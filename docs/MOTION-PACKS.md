# Companion motion extensions

Motion packs supplement the approved Codex v2 atlas. They never change `pet.json`,
`spriteVersionNumber`, the 8×11 grid, or the original 192×208 cells.

## Runtime

Run `scripts/bootstrap-motion-runtime.sh` from this repository. It creates an
isolated `.motion-venv` with Pillow 11.1.0. Use the printed interpreter for all
extraction, alpha checks, contact sheets and packing. No project Python environment
or image API key is required for deterministic processing.

## Layout

A published extension lives at `pets/<id>/motion/manifest.json`:

```json
{
  "version": 1,
  "petId": "inko",
  "cell": { "width": 192, "height": 208 },
  "clips": {
    "walk-se": {
      "file": "walk-se.webp",
      "frames": 8,
      "frameMs": 120,
      "loop": true,
      "direction": "se"
    }
  }
}
```

Each clip is a horizontal row of RGBA cells. Its dimensions must equal
`cell.width * frames` by `cell.height`. Every frame must contain visible artwork
and transparent margin on every edge. Paths are relative, local basenames only.

Directions describe the **body's travel direction**, not the original atlas gaze.
The eventual locomotion set is `n, ne, e, se, s, sw, w, nw`. Missing clips must fall
back to the original idle atlas, never a fabricated rotation of the whole bitmap.
Start/stop clips use four frames at 100 ms; walk loops use eight at 120 ms.
Additional named clips may cover rest, sleep, carry and celebrate.

## Acceptance

1. Attach an approved character reference to every generation job.
2. Generate one coherent strip per job with native alpha.
3. Preserve identity, scale, ground baseline and genuine gait across frames.
4. Extract and pack deterministically; do not redraw or tile a repeated pose.
5. Validate geometry and alpha with `scripts/validate-motion-pack.py`.
6. Independently inspect the contact sheet and animated preview for direction,
   identity drift, clipping and loop continuity before publishing the manifest.
7. Record generation prompt, selected source, QA verdict and source commit.

Drafts live in ignored `.motion-runs/`; unapproved art is not a published clip.
Portfolio consumers pin the source commit and SHA-256 of each delivered file.

## Delivered clips (September 2026)

Each pack supplies eight travel directions, one front-facing start/stop pair,
rest, sleep, carry and celebration. Turning samples actual directional poses along
the shortest arc. Start/stop are front-facing transitions; they are not eight
separately generated transition pairs. Inko's stop reverses its independently
approved gentle four-frame start. East/west and celebration are extracted from
existing approved atlas rows without changing frame content.

Generation prompts used original identity and neutral references, one strip per
job, constant scale/ground, native alpha and no background or symbols. New walking
rows requested eight grounded alternating steps in the named body direction;
rest/sleep requested seated/curled gentle breathing; carry requested a wood parcel
held in both paws. Detailed acceptance and rejected iterations are recorded under
`docs/qa/`. Only accepted packed assets are published under `pets/*/motion`.
