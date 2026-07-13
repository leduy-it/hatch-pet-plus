# Lessons from building custom Codex pets

Everything that went wrong, with the measurements. Written so the next person doesn't repeat it.

---

## 0. A model will claim success without doing the work

Generating six mascots in parallel, **three of them printed their `OUT=<path>` line, burned ~23k
tokens, and never called `image_gen` at all.** No file. No error. Exit 0.

They were simply obeying the "print exactly this" instruction and skipping the work.

**Fix — make the prompt force proof of the artifact:**

> A previous run printed the OUT= line WITHOUT ever calling image_gen and WITHOUT writing the file.
> That is a FAILURE. You MUST: (1) call image_gen, (2) copy the result to the path,
> (3) run `ls -la <path>` to prove it exists, (4) only then print the final block, including the
> real byte size from that ls.

With that added, the next batch came back **6/6** instead of 3/6.

**The general rule, which bit us three separate ways in this project:** verify the artifact on disk.
Never trust an exit code, a "done" message, or a returned path.

---

## 0b. `validate_atlas` passes pets that are visibly broken

This is the single most important thing in this document.

Across 13 pets, the official validator reported **`ok: true, 0 errors`** on sprites that had:

- a **solid magenta rectangle baked into them** (the model ignored the requested chroma colour)
- a **violet fringe on 50% of every silhouette edge**
- a pet that **halved in size the moment you hovered it**

None of these were caught. The contact sheets looked fine. The preview GIFs looked fine. Every check
was green.

They were only found by **measuring pixels**:

| defect | the measurement that caught it |
| --- | --- |
| baked-in background | % of sprite pixels near *any* chroma key, cross-checked against the pet's own palette |
| chroma fringe | % of silhouette-edge pixels leaning toward the key colour |
| hover shrink | median sprite height per lane, compared across lanes |
| gaze not encoded | muzzle/aiming-feature offset per look cell |
| frame popping | bounding-box height spread within a lane |

`validate_atlas` checks geometry and contamination **by the declared key**. That is a narrow slice of
what can go wrong. Write your own checks, and make packaging depend on them.

---

## 0c. The model ignores the chroma colour you asked for

Mossback's run declared `#00FFFF` (cyan). The model drew `idle` and `running-left` on **magenta**
anyway. The extractor keyed out cyan, so the magenta background survived as an **opaque rectangle**
inside the sprite.

**Never trust the declared key.** Detect each strip's *actual* background from its corner pixels and
force it onto the declared key before extraction:

```python
corners = np.array([a[3,3], a[3,w-4], a[h-4,3], a[h-4,w-4]])
bg = np.median(corners, axis=0)          # the REAL background
if np.abs(bg - KEY).sum() > 40:
    a[np.linalg.norm(a - bg, axis=2) <= 110] = KEY   # force it
```

Related: **pick a key that is far from the pet's palette.** `prepare_pet_run` assigned Blip magenta —
but Blip is blue with a violet outline, so the key sat right on top of the sprite's own colours and
the spill could not be separated from the art. Compute the key from the base art instead:

| pet | palette | key chosen |
| --- | --- | --- |
| Blip | blue / violet | green |
| Mossback, Pip, Kiln | greens, earth | cyan |
| Sprocket (robots) | slate-blue, amber | magenta |

---

## 1. `codex exec --profile` silently does nothing (codex-cli ≥ 0.139)

**Symptom:** the run "succeeds" instantly. Exit code 0. Empty result file. Zero work done.

**Cause:** profiles were deprecated. If `config.toml` still contains `[profiles.deep]`, passing `--profile deep` is rejected:

```
Error loading config.toml: --profile `deep` cannot be used while
/Users/you/.codex/config.toml contains legacy `profile = "deep"` or
`[profiles.deep]` config; move those settings into
/Users/you/.codex/deep.config.toml and remove the legacy profile
selector/table.
```

**The dangerous part:** it exits **0**. Any orchestrator that checks `$?` believes it worked.

**Fix:** drop `--profile` (the root config's defaults usually already match), or migrate the tables to `~/.codex/<name>.config.toml`.

**Rule:** verify artifacts on disk. Never trust an exit code.

---

## 2. Subagents deadlock in headless `codex exec`

The `hatch-pet` skill tells the agent to delegate each image to a "lightweight visual worker". That works interactively. In `codex exec` it **hangs forever**:

- parent spawns the worker via `collab_tool_call`
- the call returns `completed`
- **no image is ever produced**
- the parent blocks on a worker that will never report

**Fix:** instruct the agent explicitly:

> DO NOT SPAWN SUBAGENTS OR WORKERS. Call the built-in `image_gen` tool YOURSELF, inline, sequentially.

### Getting parallelism anyway

Run **one `codex exec` process per row**, concurrently, staggered ~10s to dodge rate limits.

**Critical:** each process must write **only its own PNG** and must be forbidden from touching `imagegen-jobs.json`. Concurrent JSON writes clobber each other. Update the manifest yourself, afterwards, once.

This cut 8 sequential rows (~15 min) down to ~4 min.

---

## 3. Chroma keying: fur, thresholds, and lossy WebP

Three separate bugs, all producing a green halo.

### 3a. Soft edges keep the key colour — and it depends on the STYLE

The extractor cuts on a hard colour-distance threshold with **no despill**. Semi-transparent edge pixels keep their green tint.

How bad this is depends entirely on the art style. Measured green contamination on the silhouette edge of a fresh base, one mascot per style:

| style | green edge | after despill |
| --- | --- | --- |
| `flat-vector` | 9.1% | **0.0%** |
| `clay` | 11.2% | **0.0%** |
| `sticker` | 15.0% | **0.0%** |
| `3d-toy` | 16.1% | **0.0%** |
| `plush` | 17.1% | **0.0%** |
| `painterly` | 19.2% | **0.0%** |
| *(3D fluffy fur)* | **34.7%** | **0.0%** |

Hard geometric edges key cleanest. Wispy brush edges and fur are worst. **No style is clean out of the box** — every one of them needs despilling, and despilling fixes every one of them completely.

**Fix — despill before extraction.** On sprite pixels, clamp green to `max(red, blue)`:

```python
cap   = np.maximum(rgb[:,:,0], rgb[:,:,2])
spill = sprite & (rgb[:,:,1] > cap)
rgb[:,:,1] = np.where(spill, cap, rgb[:,:,1])
```

The background stays pure `#00FF00`, so the extractor still keys it out — but nothing it *keeps* carries green any more.

> The upstream skill has since added `scripts/despill_chroma_edges.py` doing exactly this.

### 3b. Match the extractor's threshold exactly

`extract_strip_frames.py --key-threshold` defaults to **96**, not 120.

We despilled everything past distance 120, so pixels in the **96–120 band** — which the extractor *keeps* — were never cleaned. That produced **57 validation errors**.

Using 96 → **1 error**. Result: `~10% → 0.0%` contamination on every row.

### 3c. Write the final WebP lossless

PIL's default WebP encoder is **lossy** and corrupts RGB in fully-transparent pixels, which trips:

```
atlas has 264962 fully transparent pixels with non-zero RGB residue
```

**Fix:**

```python
img.save(path, lossless=True, exact=True)
```

Also zero the RGB of transparent pixels: `a[alpha == 0] = 0`.

---

## 4. Diffusion models cannot make true pixel art

They produce a **high-resolution painting that imitates pixels**: inconsistent block sizes, soft interior shading, anti-aliased edges.

Our final "pixel" sprite contains **61,734 distinct colours**. A real sprite of this kind has ~12. (The stock `gracies` pet: **12 colours, 7 KB**, every pixel placed deliberately.)

### Do not try to fix it by downscaling

We built a pixelizer: downscale to a 44×47 logical grid, snap to a 12-colour palette, nearest-neighbour upscale. It produced *true* pixel art — and it looked **worse** every time:

- averaging sprite pixels with the background → tan speckles round the silhouette
- re-stroking the outline → the thin wooden prop turned solid navy
- mode-based quantisation → one eye lost its highlight, the mouth became a grimace

**Why it can't work:** in real pixel art the eye highlight is *one pixel*, the mouth is *three*, the outline is *one*. Squashing a 1200px painting onto a 44px grid lands those on fractions of a pixel and mangles them. The information isn't there to recover.

**Accept the faux-pixel look, or hand-author the sprite.** There is no third option.

---

## 5. Gaze direction: move the head, not the eyes

The hardest part by far. Four failed attempts.

### What doesn't work: pupils

Prompting for "pupils shift toward the direction" produced, measured:

| attempt | 090 vs 270 separation |
| --- | --- |
| 1 | **0.9 px** |
| 2 | **−1.0 px** (backwards!) |

Measuring the pupil *inside the eye white* (the true gaze signal): **0.38 px vertical, 1.56 px horizontal.** Effectively zero. At sprite scale a pupil nudge is invisible, and the model won't commit to it.

### What works: the head

**Horizontal (screen-left / screen-right)** — turn the head into a **three-quarter view**:
- the muzzle, nose and teeth swing to that side of head centre
- the far cheek narrows; the far ear slips behind the head

**Vertical (up / down)** — **tilt** the head:
- **up:** chin lifts, the muzzle **rides high** on the face, eyes sit low, ears tilt back
- **down:** chin tucks, the muzzle **drops low**, more skull dome shows, ears tip forward

Result after switching strategy:

| axis | separation | verdict |
| --- | --- | --- |
| 090 vs 270 (muzzle dx) | **+7.7 px** | pass |
| 000 vs 180 (muzzle dy) | **+23.7 px** | pass |

### Verify the sweep numerically

A row of 8 look-poses must be **monotonic**. Ours wasn't, and it was invisible by eye:

```
slot   deg     muzzle dx
  1    000       +1.1
  3    045      +22.3   <- peaked here (wrong)
  5    090       +6.9   <- should be the MAXIMUM
  7    135      -20.4   <- swung LEFT (should still be right)
```

The head turned right, peaked early, then rotated back the wrong way. Measure `dx`/`dy` per cell and assert monotonicity — do not trust a glance at a contact sheet.

---

## 5b. The pet halved in size when you hovered it — and no prompt could fix it

`jumping` rendered at **129px** against **197px** for `idle`. Hover is the most-triggered animation,
so the pet visibly shrank by a third every time the cursor touched it.

**The cause is the extractor, not the model.** `extract_strip_frames` fits each row to its **own
bounding box**. The jumping row's bbox spans the whole jump *arc* — pet **plus** vertical travel —
so scaling that taller box into the fixed 192×208 cell shrinks the pet inside it.

No instruction like "draw it the same size as idle" can fix this: the shrink happens **after**
generation.

And you cannot simply scale `jumping` back up — the airborne frames then push out of the top of the
cell and get clipped. A 197px pet plus travel does not fit in a 208px cell. It is geometry.

**The fix is a deterministic post-extraction pass**: normalise every lane to a common sprite height
(~78% of the cell) anchored to a common baseline, preserving each frame's own vertical offset. That
leaves real headroom for the jump.

Result: **35% lane spread → 1%**.

> Watch out for LANCZOS. Scaling *up* (bot-pixel needed ×2.25) sprays faint non-zero alpha across the
> whole cell, which then reads as "background baked in" — 65% opaque, 66% border ring — even though
> it is invisible. Clamp alpha below ~24 to zero after resampling.

---

## 5c. The frame extractor silently produces empty frames

bot-pixel's six idle robots were drawn close together, so adjacent arms touched. `extract_strip_frames`
segments poses by **connected component** — so two robots fused into one, and the rest came out empty:

```
00.png  h=71  w=182   <- two robots merged
01.png  h=71  w=50
02.png  h=8   w=6     <- EMPTY
03.png  h=8   w=7     <- EMPTY
```

Both `--method auto` and `--method stable-slots` did this. The source strip was perfectly fine.

**Fix:** the poses are evenly spaced by construction, so slice the strip into N equal columns and fit
each to the cell with one shared scale and a common baseline. Deterministic, and immune to poses that
touch.

---

## 6. Measure everything

Almost every genuine defect was found by a script, not by looking:

| defect | how it was caught |
| --- | --- |
| frames different sizes → animation pops | bounding-box height spread per frame (13.7% on one row) |
| green halo | % of edge pixels where `g > r+25 and g > b+25` |
| gaze not encoded | muzzle/pupil centroid offset per cell |
| gaze sweep reversed | monotonicity check across the 8 slots |
| transparent-pixel RGB residue | the skill's own `validate_atlas.py` |

Contact sheets look convincing right up until you measure them. **Write the check.**

---

## 7. Iterate on the base, not the rows

Every row is generated against the canonical base. If the base is wrong, all 9 rows inherit it.

Generate the base, **stop**, get it approved, *then* fan out. We wasted several rounds building rows on a base that got rejected afterwards.

Corollary: when a design is being iterated on taste, don't guess one variant at a time. **Generate 4 distinct variants at once and let the human pick.** Blind re-rolling on adjectives ("fatter", "cuter", "chibi") does not converge.

---

## 8. Beware processes that outrun their brief

An earlier `codex exec` we thought we'd stopped kept following `SKILL.md` end-to-end, generated its own look rows, assembled an 8×11 atlas and **repackaged the installed pet** — while we were separately hand-building the same rows.

Its output was, embarrassingly, better than ours: correct left/right convention on both look rows.

Still: know what's writing to your output directory. Check file mtimes.
