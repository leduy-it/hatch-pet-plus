---
description: Create a custom animated Codex pet — any mascot, any style, from reference art or just a concept
---

Create a custom animated Codex pet using the bundled `hatch-pet` skill.

The user's request: $ARGUMENTS

## First, work out what you're building

**The mascot.** Anything: a creature, an object, a plant, an abstract shape, a company mascot. It does not need to be an animal. If the user gives only a brand or product name, run brand discovery first and derive a mascot-safe concept from it.

**The style.** Pick a preset, or infer one with `auto`:

| preset | look |
| --- | --- |
| `pixel` | chunky retro sprite, limited flat palette |
| `plush` | felt / soft toy, stitched seams, fabric weave |
| `clay` | claymation, thumbprints, matte earthenware |
| `sticker` | die-cut vinyl, bold white border, glossy |
| `flat-vector` | clean geometric shapes, flat fills, no texture |
| `3d-toy` | glossy moulded vinyl, studio highlights |
| `painterly` | brushstrokes, pigment, expressive edges |
| `brand-inspired` | derived from a company's visual system |
| `auto` | infer from the prompt/references (default) |

Non-pixel styles are first-class. Do not default to pixel art.

**The input.** Two supported paths, both first-class:

- **With reference art** — pass each image via `--reference`. The style and identity are anchored to the references. Best when the user has existing character art.
- **From a concept only** — no images at all. Put the description in `--pet-notes` and let the base generation invent the character. Everything downstream is then anchored to that approved base.

## Then build it

Follow `skills/hatch-pet/SKILL.md`. The things that are easy to get wrong:

1. **Generate the base first, then STOP and get it approved.** All 9 animation rows are generated against the canonical base — a bad base poisons every row. Do not fan out until the user has approved it. If the user is iterating on taste, generate 3–4 *distinct* variants at once and let them pick; re-rolling one guess at a time does not converge.

2. **Image generation needs a host with an image tool.** Codex has built-in `image_gen`. Claude Code does not — from there, delegate to Codex:

   ```bash
   codex exec --skip-git-repo-check - < prompt.txt
   ```

   Do **not** pass `--profile`: it is rejected on codex-cli ≥ 0.139 and still exits 0 while doing nothing.

3. **Never spawn subagents for image jobs in headless `codex exec`.** The worker call returns `completed` but no image ever arrives and the parent hangs forever. Call `image_gen` inline. For parallelism, run one `codex exec` process per row, each writing only its own PNG — never let concurrent processes touch the shared manifest.

4. **Verify the file exists on disk.** A model will happily print `OUT=<path>` without ever calling `image_gen`. Check the artifact, never the report.

5. **Despill before extracting.** Chroma keying uses a hard threshold with no despill, so soft edges keep the key colour and halo the sprite. Softer styles are worse: measured green edge contamination on a fresh base — `flat-vector` 9%, `clay` 11%, `sticker` 15%, `3d-toy` 16%, `plush` 17%, `painterly` 19%. Despilling (clamp green to `max(r,b)` on kept pixels, at the extractor's threshold of **96**) takes every one of them to **0%**.

6. **Gaze direction comes from the head, not the eyes.** Pupil shifts are invisible at sprite scale (measured under 2px). Turn the head into a three-quarter view for left/right; tilt it so the pet's aiming feature (muzzle, beak, visor, eye, lens — whatever the pet has) rides high for up and drops low for down. Verify numerically per cell.

7. **Measure, don't eyeball.** Check per-frame size consistency, chroma contamination, and gaze monotonicity with scripts. Contact sheets look convincing right up until you measure them.

See `docs/LESSONS.md` for the full write-up.
