---
description: Create a custom animated Codex pet from art, a reference image, or just a concept
---

Create a custom animated Codex pet using the bundled `hatch-pet` skill.

The user's request: $ARGUMENTS

Follow `skills/hatch-pet/SKILL.md` exactly. Key points that are easy to get wrong:

1. **Generate the base first, then STOP and get it approved.** Every animation row is generated against the canonical base — a bad base poisons all 9 rows. Do not fan out until the user has seen and approved the base.

2. **Image generation must run in the host that has an image tool.** In Codex this is the built-in `image_gen`. If you are running in Claude Code (which has no image generation), delegate the generation steps to Codex:

   ```bash
   codex exec --skip-git-repo-check - < prompt.txt
   ```

   Do **not** pass `--profile` — it is rejected on codex-cli >= 0.139 and still exits 0 while doing nothing.

3. **Never spawn subagents for image jobs in headless `codex exec`** — the worker call returns `completed` but no image ever arrives and the parent hangs forever. Call `image_gen` inline, one row at a time. For parallelism, run one `codex exec` process per row and let each write only its own PNG (never the shared manifest).

4. **Despill before extracting.** Chroma keying uses a hard threshold with no despill, so soft edges keep the key colour and halo the sprite. Use `scripts/despill_chroma_edges.py`, and match the extractor's `--key-threshold` (default 96).

5. **Gaze direction comes from the head, not the pupils.** Pupil shifts are invisible at sprite scale (measured: <2px). Turn the head into a three-quarter view for left/right; tilt it so the muzzle rides high/drops low for up/down. Verify numerically.

6. **Measure, don't eyeball.** Check per-frame size consistency, chroma contamination, and gaze monotonicity with scripts. Contact sheets look fine right up until you measure them.

See `docs/LESSONS.md` in this repo for the full write-up.
