# Blip

> Blip — a cheerful geometric blob of soft jelly shaped like a rounded teardrop, FLAT VECTOR style. ONE big friendly eye (clean circle with a crisp white highlight) and a tiny curved smile. A slim antenna rises from the top ending in a small glowing yellow square. Bright periwinkle-blue flat body with a confident dark outline. Two small rounded nub arms. Flat colour fills, no gradients, no texture, crisp geometric edges.

<p align="center">
  <img src="hero.gif" width="240" alt="Blip idling">
</p>

| | |
|---|---|
| **style** | `flat-vector` |
| **atlas** | 8 × 11 cells of 192×208 — `1536×2288`, `spriteVersionNumber: 2` |
| **chroma key** | `#00FF00` (keyed to transparency, then despilled) |

## Every animation, and what plays it

| | lane | plays when | frames | sprite height |
|---|---|---|---|---|
| <img src="previews/idle.gif" width="76"> | `idle` | Codex is idle <br><sub>the default resting loop</sub> | 6 | 162px |
| <img src="previews/running-right.gif" width="76"> | `running-right` | **you drag it right** <br><sub>travels right with a walking cadence</sub> | 8 | 161px |
| <img src="previews/running-left.gif" width="76"> | `running-left` | **you drag it left** <br><sub>the mirror of running-right</sub> | 8 | 161px |
| <img src="previews/waving.gif" width="76"> | `waving` | greeting <br><sub>a friendly wave</sub> | 4 | 162px |
| <img src="previews/jumping.gif" width="76"> | `jumping` | **you hover it** <br><sub>a small joyful hop — the most-seen animation</sub> | 5 | 161px |
| <img src="previews/failed.gif" width="76"> | `failed` | Codex failed or was cancelled <br><sub>deflated, disappointed</sub> | 8 | 162px |
| <img src="previews/waiting.gif" width="76"> | `waiting` | Codex is blocked on you <br><sub>an expectant, asking pose</sub> | 6 | 162px |
| <img src="previews/running.gif" width="76"> | `running` | Codex is working / thinking <br><sub>focused effort — *not* foot-running</sub> | 6 | 162px |
| <img src="previews/review.gif" width="76"> | `review` | Codex is reviewing output <br><sub>leaning in, inspecting</sub> | 6 | 162px |

Rows 9 and 10 are the **16 look directions**: as you move your cursor, the pet's head turns to follow it, in 22.5° steps.

The pet is drawn the **same size in every lane** (spread 1%), so it does not visibly resize when you hover or drag it.

## All 11 rows

<p align="center">
  <img src="contact-sheet.png" width="640" alt="contact sheet">
</p>

## QA

```
blip PASS key=#00FF00 lean=0.0% ring=13% spread=1%
```

`lean` = pixels still tinted by the chroma key · `ring` = background baked into the sprite · `spread` = how much the pet resizes between lanes. All must be near zero.

## The base art everything was generated from

<p align="center">
  <img src="base.png" width="260" alt="canonical base">
</p>

Every one of the 88 drawings in the atlas was generated against this single canonical reference, which is what keeps the identity stable across all of them.

## Install

```bash
./install.sh --pet blip
```

Then **Codex Settings → Appearance / Pets**, and `/pet` to wake it.

