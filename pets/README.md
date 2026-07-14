# 14 ready-to-install Codex pets

Every pet here is **complete and validated** — a full 8×11 v2 atlas with all 9 animation lanes
and 16 look directions. Each has its own page with lane-by-lane detail.

<p align="center">
  <img src="../examples/showcase-lanes.gif" width="960" alt="every pet, every lane">
</p>

<p align="center">
  <em>all 14 pets, playing each of the nine lanes in turn</em>
</p>

---

## The pets

| | pet | style | |
|---|---|---|---|
| <img src="blip/hero.gif" width="64"> | **[Blip](blip/)** | `flat-vector` |  |
| <img src="bot-3d-toy/hero.gif" width="64"> | **[Sprocket Toy](bot-3d-toy/)** | `3d-toy` |  |
| <img src="bot-clay/hero.gif" width="64"> | **[Sprocket Clay](bot-clay/)** | `clay` |  |
| <img src="bot-flat-vector/hero.gif" width="64"> | **[Sprocket Vector](bot-flat-vector/)** | `flat-vector` |  |
| <img src="bot-pixel/hero.gif" width="64"> | **[Sprocket Pixel](bot-pixel/)** | `pixel` |  |
| <img src="bot-plush/hero.gif" width="64"> | **[Sprocket Plush](bot-plush/)** | `plush` |  |
| <img src="bot-sticker/hero.gif" width="64"> | **[Sprocket Sticker](bot-sticker/)** | `sticker` |  |
| <img src="bunny/hero.gif" width="64"> | **[Bunny](bunny/)** | `pixel` |  |
| <img src="inko/hero.gif" width="64"> | **[Inko](inko/)** | `painterly` |  |
| <img src="kiln/hero.gif" width="64"> | **[Kiln](kiln/)** | `clay` |  |
| <img src="mossback/hero.gif" width="64"> | **[Mossback](mossback/)** | `plush` |  |
| <img src="nimbus/hero.gif" width="64"> | **[Nimbus](nimbus/)** | `3d-toy` |  |
| <img src="pip/hero.gif" width="64"> | **[Pip](pip/)** | `sticker` |  |
| <img src="volt/hero.gif" width="64"> | **[Volt](volt/)** | `3d-toy` | **evolves** — Volt → Anodane |

```bash
./install.sh --pet <name>     # one
./install.sh --pet            # all of them
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
├── README.md          lane-by-lane detail, measured from the atlas
├── pet.json           installable manifest (spriteVersionNumber: 2)
├── spritesheet.webp   8x11 atlas, 1536x2288, transparent
├── base.png           the canonical art all 88 drawings were generated against
├── hero.gif           a large idle loop
├── demo.gif           all 9 lanes side by side
├── contact-sheet.png  all 11 rows, cell by cell
├── validation.json    the validator's report
└── previews/*.gif     one animated GIF per lane
```

---

## Evolving pets

Some pets have **two forms**, and ship one complete atlas *per stage*:

<p align="center">
  <img src="../examples/showcase-evolution.gif" width="420" alt="evolving">
</p>

```
pets/<name>/
├── pet.json              declares `stages` + `attributes`
├── stage-1.webp          the form it hatches as
├── stage-2.webp          the form it becomes at Lv 10
├── evolution.gif         the transformation, animated
└── previews/stage-1/*.gif  /  previews/stage-2/*.gif
```

`spritesheetPath` still points at stage one, so **Codex loads an evolving pet and shows its
first form** — it knows nothing about stages and does not need to. To actually *see* one evolve
you need a host that tracks your coding and reads `stages`, like
[evolvepet](https://github.com/leduy-it/evolvepet).

Format and build guide: **[../docs/EVOLUTION.md](../docs/EVOLUTION.md)**.

