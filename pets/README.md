# 14 ready-to-install Codex pets

Every pet here is **complete and validated** — a full 8×11 v2 atlas with all 9 animation lanes
and 16 look directions. Each has its own page with lane-by-lane detail.

<p align="center">
  <img src="../examples/showcase-lanes.gif" width="960" alt="every pet, every lane">
</p>

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

---

## Evolution lines — built from existing pets, zero new art

<p align="center">
  <img src="../examples/showcase-evolution.gif" width="620" alt="evolving pets">
</p>

A stage does not have to be *new* art — it just has to be a full atlas, and we already ship
14 of them. These pets **chain existing atlases as their stages**, so they evolve as you level
up without a single image being generated. Define your own in one small JSON file:
`scripts/assemble_evolution_line.py <line.json>`.

| | line | evolves |
|---|---|---|
| <img src="grove-evo/hero.gif" width="64"> | **[Pip](grove-evo/)** | Pip (Lv 0) → Mossback (Lv 12) |
| <img src="sprocket-evo/hero.gif" width="64"> | **[Sprocket](sprocket-evo/)** | Sprocket 8-bit (Lv 0) → Sprocket Vector (Lv 8) → Sprocket HD (Lv 20) |

---

## Install

```bash
./install.sh --pet <name>     # one
./install.sh --pet            # all of them
```

An evolving pet installs its first form into Codex (which cannot level pets up) and, if you have
[evolvepet](https://github.com/leduy-it/evolvepet), every stage into it. Format and build guide:
**[../docs/EVOLUTION.md](../docs/EVOLUTION.md)**.

