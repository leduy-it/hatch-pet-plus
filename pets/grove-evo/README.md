# Pip

> Pip — a sprout that grows, as you do, from a seedling into a mossy grove-creature.

<p align="center">
  <img src="hero.gif" width="240" alt="Pip idling">
</p>

| | |
|---|---|
| **style** | `auto` |
| **atlas** | 8 × 11 cells of 192×208 — `1536×2288`, `spriteVersionNumber: 2` |
| **chroma key** | `#00FF00` (keyed to transparency, then despilled) |
| **evolves** | **Pip** (Lv 0) → **Mossback** (Lv 12) |
| **type** | `leaf` |

## Evolution

<p align="center">
  <img src="evolution.gif" width="240" alt="evolving">
</p>

| stage | reached at | stats |
|---|---|---|
| **Pip** | Lv 0 | HP 40 · ATK 34 · DEF 42 · SPD 40 |
| **Mossback** | Lv 12 | HP 68 · ATK 52 · DEF 74 · SPD 44 |

Each stage is a **complete 8×11 atlas** — see [docs/EVOLUTION.md](../../docs/EVOLUTION.md).

## Every animation, and what plays it

| | lane | plays when | frames | sprite height |
|---|---|---|---|---|
| <img src="previews/stage-1/idle.gif" width="76"> | `idle` | Codex is idle <br><sub>the default resting loop</sub> | 6 | 162px |
| <img src="previews/stage-1/running-right.gif" width="76"> | `running-right` | **you drag it right** <br><sub>travels right with a walking cadence</sub> | 8 | 162px |
| <img src="previews/stage-1/running-left.gif" width="76"> | `running-left` | **you drag it left** <br><sub>the mirror of running-right</sub> | 8 | 162px |
| <img src="previews/stage-1/waving.gif" width="76"> | `waving` | greeting <br><sub>a friendly wave</sub> | 4 | 162px |
| <img src="previews/stage-1/jumping.gif" width="76"> | `jumping` | **you hover it** <br><sub>a small joyful hop — the most-seen animation</sub> | 5 | 156px |
| <img src="previews/stage-1/failed.gif" width="76"> | `failed` | Codex failed or was cancelled <br><sub>deflated, disappointed</sub> | 8 | 162px |
| <img src="previews/stage-1/waiting.gif" width="76"> | `waiting` | Codex is blocked on you <br><sub>an expectant, asking pose</sub> | 6 | 162px |
| <img src="previews/stage-1/running.gif" width="76"> | `running` | Codex is working / thinking <br><sub>focused effort — *not* foot-running</sub> | 6 | 162px |
| <img src="previews/stage-1/review.gif" width="76"> | `review` | Codex is reviewing output <br><sub>leaning in, inspecting</sub> | 6 | 162px |

Rows 9 and 10 are the **16 look directions**: as you move your cursor, the pet's head turns to follow it, in 22.5° steps.

The pet is drawn the **same size in every lane** (spread 4%), so it does not visibly resize when you hover or drag it.

## All 11 rows

<p align="center">
  <img src="contact-sheet-1.png" width="640" alt="contact sheet">
</p>

## Composed from existing pets

This evolution line reuses atlases that already ship in this repo — **no new art was generated**. Each stage is one of the finished, QA-passed pets:

- **Pip** — `stage-1.webp`
- **Mossback** — `stage-2.webp`

## Install

```bash
./install.sh --pet grove-evo
```

Then **Codex Settings → Appearance / Pets**, and `/pet` to wake it.

