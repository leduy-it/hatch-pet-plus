# 13 ready-to-install Codex pets

Every pet here is **complete and validated** — a full 8×11 v2 atlas with all 9 animation lanes and
16 look directions. Drop any of them into `~/.codex/pets/` and it just works.

<p align="center">
  <img src="../examples/showcase-all-idle.gif" width="960" alt="All 13 pets idling">
</p>

---

## Install any pet

```bash
cp -r pets/<name> ~/.codex/pets/
```

Then **Codex Settings → Appearance / Pets → pick it**, or set it directly:

```toml
[desktop]
selected-avatar-id = "<name>"
```

---

## What each pet ships with

```
pets/<name>/
├── pet.json           installable manifest (spriteVersionNumber: 2)
├── spritesheet.webp   8x11 atlas, 1536x2288, transparent
├── contact-sheet.png  all 11 rows, cell by cell
├── validation.json    the validator's report
├── demo.gif           all 9 lanes side by side
└── previews/*.gif     one animated GIF per lane
```

---

## The 9 animation lanes

Each lane is a separate animation. Some you trigger; some Codex triggers based on what the agent
is doing.

| # | lane | frames | what triggers it | what it shows |
| --- | --- | ---: | --- | --- |
| 0 | `idle` | 6 | default resting state | a calm breathing/bobbing loop with a blink — deliberately low-distraction |
| 1 | `running-right` | 8 | **you drag the pet right** | directional locomotion, alternating gait |
| 2 | `running-left` | 8 | **you drag the pet left** | the mirror of lane 1, frame order preserved |
| 3 | `waving` | 4 | greeting / attention | a raised-limb greeting — gesture only, no motion marks |
| 4 | `jumping` | 5 | **you hover the pet** | a small joyful hop: crouch → lift → peak → descent → settle |
| 5 | `failed` | 8 | Codex hit an error or was cancelled | a sad, deflated, drooping reaction |
| 6 | `waiting` | 6 | Codex is **blocked on your approval** | an expectant "asking" pose, looking up at you |
| 7 | `running` | 6 | Codex is **working / thinking** | focused effort — *not* foot-running |
| 8 | `review` | 6 | Codex is reviewing output | a focused, inspecting, thinking loop |
| 9–10 | look directions | 16 | **you move your cursor** | the pet's head tracks your pointer, 16 angles at 22.5° steps |

Lane 4 (`jumping`) is the one you see most, because it fires on hover.

**You cannot add a 12th lane.** The atlas is fixed at 8×11 and Codex maps the rows to fixed CSS
background positions. What you *can* change is what each lane *depicts* — a robot's `failed` can be
a shutdown sequence rather than a sad slump.

---

## The pets

### Creatures — one per style, all invented from a text concept (no reference art)

| pet | style | |
| --- | --- | --- |
| `mossback` | plush | a living cushion of forest floor, stitched mushroom caps |
| `nimbus` | 3d-toy | a glossy vinyl cloud with a quiff |
| `kiln` | clay | a terracotta jar-creature with a lid for a hat |
| `blip` | flat-vector | a one-eyed jelly blob with an antenna |
| `pip` | sticker | a die-cut sprout bursting out of its seed |
| `inko` | painterly | a creature of living ink with a calligraphic tail |
| `bunny` | pixel | a chibi blue bunny — the only one built **from reference art** |

### Sprocket — one robot, six styles

The *same* desk-companion robot rendered across six style presets, to show that style is a dial you
control independently of the character.

`bot-pixel` · `bot-plush` · `bot-clay` · `bot-flat-vector` · `bot-3d-toy` · `bot-sticker`

---

## Every pet passed independent QA

Not just `validate_atlas` — it reported `ok: true, 0 errors` on a pet that had a **solid magenta
rectangle baked into it**. These are the checks that actually caught things:

| check | why it exists |
| --- | --- |
| atlas geometry | 1536×2288, 8×11, RGBA |
| **baked-in background** | the model sometimes ignores the requested chroma colour entirely |
| **chroma lean (all keys)** | a stray background of *any* key colour, not just the declared one |
| **cross-lane scale** | the pet must not resize between animations (it was halving on hover) |
| lane population | every lane has its full frame count |

Result across all 13: **0.0% chroma lean, no baked backgrounds, ≤12% lane spread. 13 PASS, 0 FAIL.**

See [../docs/LESSONS.md](../docs/LESSONS.md) for how each of those bugs was found.
