# Evolving pets

A pet can have more than one form. It hatches as its first form, and when it has levelled
up enough — because *you* coded enough — it transforms into the next one.

This document is the format. It is deliberately small, and deliberately optional: a pet
that says nothing about evolution behaves exactly as it always did.

---

## The format

An evolving pet declares `stages`. Each stage is a **complete spritesheet** unlocked at a
level.

```jsonc
{
  "id": "volt",
  "displayName": "Volt",
  "description": "Volt — an evolving electric-type Codex pet.",
  "spriteVersionNumber": 2,

  // Stage one, always. A host that has never heard of `stages` reads this field,
  // loads the pet's first form, and works exactly as before.
  "spritesheetPath": "stage-1.webp",

  "stages": [
    {
      "minLevel": 0,
      "name": "Volt",
      "spritesheetPath": "stage-1.webp",
      "attributes": { "type": "electric", "hp": 50, "atk": 58, "def": 46, "spd": 48 }
    },
    {
      "minLevel": 10,
      "name": "Anodane",
      "spritesheetPath": "stage-2.webp",
      "attributes": { "type": "electric", "hp": 68, "atk": 90, "def": 62, "spd": 65 }
    }
  ]
}
```

| field | meaning |
|---|---|
| `minLevel` | the level at which this form is reached. The first stage is `0`. |
| `name` | what the pet is called in this form. This is how you get *"Volt evolved into Anodane!"* |
| `spritesheetPath` | a full 8×11 atlas — **not** a variant, a patch, or a palette swap |
| `attributes` | optional. Battle-style stats, so a form is stronger as well as different. |

**The rule for a host:** pick the last stage whose `minLevel` the pet has reached, and render
*that* sheet. One line of logic.

### Backwards compatibility is the whole design

Every pet published before this — and every pet in the wild — has no `stages`. Such a pet gets
exactly one implicit stage, and nothing about it changes. `spritesheetPath` stays the source of
truth for the first form precisely so that Codex itself, which knows nothing about evolution,
still loads an evolving pet and shows its first form without complaint.

Nothing is required to opt in. Nothing breaks if it doesn't.

---

## Why every stage is a whole spritesheet

It would be tidier if a stage were a diff — "same pet, bigger, plus a collar". It cannot be.

A Codex pet is a fixed 8×11 atlas of 192×208 cells: nine animation lanes and sixteen look
directions, **88 drawings of the same creature**. There is no layer system, no attachment
points, no runtime compositing. The only thing a host can do is choose which sheet to read
cells out of.

So a second form is a second full atlas. That is what makes evolution expensive to *make*
(≈23 image generations per evolving pet) and free to *use* (one sheet swap).

---

## Evolution is not "the same pet, bigger"

The tempting shortcut is to scale the sprite up. Resist it — a bigger pet reads as the same
pet standing closer, not as a new form.

What actually sells a transformation is a change of **silhouette** and a change of
**character**, chosen for that specific creature:

| pet | first form | evolves into | what actually changes |
|---|---|---|---|
| **Volt** | a plump striped battery-creature | **Anodane** | its plush fuzz cures to hard enamel; it grows a copper grounding collar and a ceramic earthing spike where a tail-tip used to be |
| **Firetail** | a salamander with a flame on its tail | **Emberkiln** | a kiln-fired ceramic carapace grows over its back — it becomes a furnace that *holds* its heat, not a lizard carrying a candle |
| **Cobble** | a stone golem with a geode chest | **Cairnvault** | the geode opens |
| **Sprig** | a seedling with a curled frond | **Verdicoil** | the frond unfurls |
| **Dewel** | an amphibian under a droplet shell | **Dewelm** | the shell crystallises |
| **Wisp** | a lantern spirit under a cloth hood | **Tollwarden** | the hood becomes a cloak, the flame burns cold |

Gear. Materials. An ignition. A posture. *Then* size, if it helps.

The one hard constraint: it must still be recognisably **the same creature**. Each spec
records `identityAnchors` — the features that must survive — and the generator is told to
preserve them.

### Constraints the sprite pipeline imposes

These are not stylistic preferences. Breaking them produces a broken pet:

- **No detached parts.** No floating sparks, orbs, motes or particles. Anything not attached
  to the body is destroyed by the chroma-key extractor.
- **No wispy strands, hairs, smoke or fuzz.** They key out as fringe.
- **Nothing finer than ~4px** at sprite scale. It has to survive being drawn 88 times.
- **The art style never changes** between stages. Only the creature does.

---

## Evolution lines — chaining existing pets, for free

An evolution stage does not have to be **new** art. It just has to be a full atlas — and this
repo already ships fourteen. So an evolving pet can point its stages at pets we already have,
and it evolves as you level up **without generating a single image**.

```bash
scripts/assemble_evolution_line.py line.json
```

```jsonc
{
  "id": "sprocket-evo",
  "displayName": "Sprocket",
  "type": "machine",
  "stages": [
    { "source": "bot-pixel",       "minLevel": 0,  "name": "Sprocket 8-bit" },
    { "source": "bot-flat-vector", "minLevel": 8,  "name": "Sprocket Vector" },
    { "source": "bot-3d-toy",      "minLevel": 20, "name": "Sprocket HD" }
  ]
}
```

`source` names an existing `pets/<source>/` directory; its atlas is copied in as that stage.
The shipped **Sprocket** line is the same desk robot re-rendering itself at rising fidelity —
pixel → vector → 3D — as you code. Full per-species art (a genuinely *different* creature at
stage two, like Volt → Anodane) is the richer path; a line is the cheap one, and often the more
charming, since the stages are already polished pets.

A line pet is marked `"composed": true` so the flat gallery skips it (its stages would duplicate
other pets) while the evolution showcase features it. Because its stages carry different original
chroma keys, QA each stage against its **source** pet's key, not one key for the whole pet.

## Building one

```bash
scripts/e2e_evolve.sh specs/volt.json
```

The spec carries the first form's base art, the evolution's image prompt, the identity
anchors, and the stats for both forms. The build:

1. builds **stage 1** through the ordinary pipeline (8 lanes → mirror → look rows → atlas),
2. **generates the evolved base art** from stage 1's base art plus the evolution prompt,
3. builds **stage 2** through the same pipeline,
4. runs `verify_pet.py` on **both** atlases — and refuses to publish if either fails,
5. merges them into one pet directory and renders the evolution effect.

Each stage is built as if it were its own pet, because to the pipeline it *is* one.

To build several, `evolve_all.sh <quota-ceiling> <spec>...` checks your Codex quota before
each pet and stops cleanly rather than spending your week's allowance on sprites. It reports
what it skipped — silently truncating would read as "we built everything".

### What lands

```
pets/volt/
  pet.json              stages + attributes
  stage-1.webp          full 8×11 atlas
  stage-2.webp          full 8×11 atlas
  contact-sheet-1.png   every cell of stage 1
  contact-sheet-2.png   every cell of stage 2
  validation-1.json     validator output, per stage
  validation-2.json
  evolution.gif         the transformation, animated
  evolution.png         stage 1 → stage 2, static
  previews/stage-1/*.gif   one GIF per animation lane
  previews/stage-2/*.gif
```

---

## The evolution effect

When a pet crosses a threshold, it should not simply *become* the new sheet between one frame
and the next.

`make_evolution_gif.py` renders the transition that sells it: the creature blows out to a flat
white silhouette while the backdrop dims, **the silhouette itself changes shape**, and the new
form fades back in.

The dimming backdrop is not decoration. At full white-out the sprite is pure white — on a light
background it would vanish at exactly the moment the shape changes, which is the moment the whole
effect exists to show. The backdrop darkens so the silhouette stays legible through the swap.

---

## Who reads this

**Codex** shows the first form and never evolves a pet — it has no notion of levels. Its manifest
parser is closed, so rather than bet that it ignores an unknown `stages` key, `install.sh` hands it
exactly the shape it has always been given: stage one, written out as a plain `spritesheet.webp`,
with `stages` stripped. Nothing to tolerate, nothing to break.

```bash
./install.sh --pet volt
#   ~/.codex/pets/volt/     stage 1, stages stripped   <- Codex
#   ~/.agentpet/pets/volt/  the whole pet              <- evolvepet, if installed
```

**[evolvepet](https://github.com/leduy-it/evolvepet)** is a desktop pet that watches your coding
agents and levels up as you work. It reads `stages` and renders the form you have actually reached.
(A fork of [ntd4996/agentpet](https://github.com/ntd4996/agentpet), whose XP and level system this
builds on. Upstream, a pet's stage only styled a rank badge — the artwork never changed. That gap
is what this format exists to close.)

**Anything else** — the rule is one line: the last stage whose `minLevel` you have reached.
