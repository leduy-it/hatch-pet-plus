# 🐰 Bunny — a custom Codex pet

A cute blue pixel bunny companion for the [Codex](https://openai.com/codex) desktop app, built with the `hatch-pet` skill.

<p align="center">
  <img src="examples/hero.gif" width="200" alt="Bunny idle animation">
</p>

<p align="center">
  <img src="examples/demo.gif" width="900" alt="Bunny animations: idle, waving, jumping, running, review, failed">
</p>

<p align="center">
  <em>idle · waving · jumping · running · review · failed</em>
</p>

This repo contains the finished pet, the (improved) `hatch-pet` skill used to make it, every intermediate artifact, and — most usefully — **an honest write-up of everything that went wrong**, so you don't hit the same walls.

---

## Install the pet

```bash
git clone https://github.com/<you>/codex-pet-bunny.git
mkdir -p ~/.codex/pets/bunny
cp codex-pet-bunny/pet/* ~/.codex/pets/bunny/
```

Then in Codex: **Settings → Appearance / Pets → Bunny**, and `/pet` to wake it.

Or set it directly in `~/.codex/config.toml`:

```toml
[desktop]
selected-avatar-id = "bunny"
```

---

## What the pet does

The atlas is an **8 × 11 grid** of `192×208` cells (`1536×2288`, `spriteVersionNumber: 2`).
Rows 0–8 are animation states; rows 9–10 are 16 look directions.

**You trigger these:**

| Action | Animation |
| --- | --- |
| **Hover** the pet | `jumping` |
| **Drag** it right | `running-right` |
| **Drag** it left | `running-left` |
| **Move your cursor** around | rows 9–10 — the bunny's head *follows your pointer* |
| Greeting | `waving` |

**Codex triggers these, based on what the agent is doing:**

| When Codex is… | Animation |
| --- | --- |
| idle | `idle` |
| working / thinking | `running` (not foot-running) |
| blocked on your approval | `waiting` |
| reviewing output | `review` |
| failed / cancelled | `failed` |

<p align="center">
  <img src="examples/contact-sheet.png" width="620" alt="Full contact sheet, all 11 rows">
</p>

---

## How it was built

1. **Reference art** → three 3D plush bunny images (`examples/bunny-0*.png`)
2. **Base sprite** → one canonical identity image, pixel-art style (`examples/canonical-base.png`)
3. **9 animation rows** → one `image_gen` call per row, each grounded on the canonical base + a layout guide
4. **`running-left`** → deterministically mirrored from `running-right` (frame order preserved)
5. **Look rows 9–10** → 4 cardinal anchors (up/right/down/left), then two 8-pose sweeps
6. **Despill → extract → atlas → validate → package**

Validation on the shipped atlas: **0 errors, 0 warnings** (`examples/validation.json`).

---

## 📌 Lessons learned (read this before you build your own)

Full write-up: **[docs/LESSONS.md](docs/LESSONS.md)**. The short version:

### 1. `codex exec --profile` is broken on codex-cli ≥ 0.139 — and it exits 0

```
Error loading config.toml: --profile `deep` cannot be used while config.toml
contains legacy `profile = "deep"` or `[profiles.deep]` config
```

It **still exits 0** and writes an empty `--output-last-message` file. A supervisor that trusts the exit code will think the run succeeded when nothing ran. **Verify artifacts on disk, never exit codes.**

### 2. Subagents deadlock in headless `codex exec`

The skill's "lightweight visual workers" pattern assumes an interactive session. In `codex exec`, the worker call returns `completed` but never delivers an image, and the parent blocks forever. **Call `image_gen` inline instead.**

For parallelism, run **one `codex exec` process per row** and have each write only its own PNG — never let concurrent processes touch `imagegen-jobs.json`, or they clobber each other's writes.

### 3. Fluffy fur leaves a green halo

Chroma-key extraction uses a hard distance threshold with no despill, so soft fur edges keep their green tint. Measured **34.7%** of edge pixels contaminated on a 3D fur render.

**Fix:** clamp green to `max(r, b)` on sprite pixels *before* extraction — and match the extractor's `--key-threshold` (default **96**, not 120, which cost us 57 validation errors). Result: **~10% → 0.0%**.

Also: write the final WebP **lossless** (`lossless=True, exact=True`). PIL's default lossy encoder corrupts RGB in fully-transparent pixels and trips the "transparent pixels with non-zero RGB residue" check.

### 4. Diffusion models don't make *true* pixel art

They paint a high-resolution image that *imitates* pixels — inconsistent block sizes, soft shading, tens of thousands of colours. Our "pixel" sprite has **61,734 distinct colours**, not the 12 a real sprite would have.

**Do not try to fix this by downscaling.** We tried; it destroys exactly what makes a sprite charming (a 1px eye highlight, a 3px mouth, a 1px outline all land on fractions of a pixel and get mangled). Accept the faux-pixel look, or hand-author real pixel art.

### 5. Gaze direction is the hardest part

Asking for **pupil shifts** does not work — measured pupil movement inside the eye was **0.38px vertically, 1.56px horizontally**. Invisible.

**What works:** move the *head*, not the eyes.
- **Left/right** → turn the head into a three-quarter view; the muzzle and nose swing to that side.
- **Up/down** → tilt the head; the muzzle *rides high* (up) or *drops low* (down).

Verify it numerically — measure the muzzle offset per cell. Don't trust your eyes on a 192px sprite.

### 6. Measure, don't eyeball

Nearly every real defect here was caught by a script, not by looking: size-popping between frames, chroma contamination, non-monotonic gaze sweeps, identity drift. Contact sheets look fine right up until you measure them.

---

## Repo layout

```
pet/         the installable pet (pet.json + spritesheet.webp)
skill/       the hatch-pet skill used to build it
examples/    reference art, canonical base, row strips, contact sheet, preview GIFs
docs/        the full lessons write-up
```

---

## Credits

Built with OpenAI's [`hatch-pet`](https://github.com/openai/skills/tree/main/skills/.curated/hatch-pet) skill (see `skill/LICENSE.txt`).
Pet art generated with Codex's built-in `image_gen`.
