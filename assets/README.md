# Mascot assets — free to use

Every mascot here was generated with the `hatch-pet-plus` plugin and is **free for anyone to use**
(see [LICENSE](./LICENSE) — CC0 / public domain).

Each mascot ships in two forms:

| file | what it is | use it for |
| --- | --- | --- |
| `base.png` | raw generation on a flat `#00FF00` chroma background | feeding back into the hatch-pet pipeline as a canonical base |
| `cutout.png` | despilled, transparent PNG | dropping straight into a game, a slide, a README, an app |

The `cutout.png` files have been **despilled** — no green fringe, verified at 0.0% chroma
contamination on the silhouette edge.

---

## Two showcases

### 1. Six original mascots, six styles

Different creatures, different styles — showing the range of subjects the pipeline handles.
None of these are animals-with-a-gimmick clichés, and none were built from reference art:
**they were all invented from a text concept alone.**

| mascot | style | concept |
| --- | --- | --- |
| **Mossback** | `plush` | a living cushion of forest floor, with stitched mushroom caps |
| **Nimbus** | `3d-toy` | a glossy vinyl cloud with a quiff |
| **Kiln** | `clay` | a pot-bellied terracotta jar-creature with a lid for a hat |
| **Blip** | `flat-vector` | a one-eyed jelly blob with an antenna |
| **Pip** | `sticker` | a die-cut sprout bursting out of its seed |
| **Inko** | `painterly` | a creature made of living ink, with a calligraphic tail |

### 2. Six elemental creatures, and what they evolve into

Six **original** creatures, each a first form with a designed second form. They were invented from a
text concept alone, and each design was reviewed for derivativeness before it was drawn — because
this art is CC0, it has to be genuinely ours to give away.

| creature | type | evolves into | what changes |
| --- | --- | --- | --- |
| **Volt** | electric | **Anodane** | plush fuzz cures to hard enamel; a copper grounding collar and a ceramic earthing spike |
| **Firetail** | fire | **Emberkiln** | a kiln-fired ceramic carapace — a furnace that holds its heat, not a lizard carrying a candle |
| **Dewel** | water | **Dewelm** | the droplet shell crystallises |
| **Sprig** | leaf | **Verdicoil** | the curled frond unfurls |
| **Cobble** | rock | **Cairnvault** | the geode in its chest cracks open |
| **Wisp** | ghost | **Tollwarden** | the hood becomes a cloak, the flame burns cold |

The full art direction for each — the transformation, the identity anchors that must survive it, the
image prompt, and the stats — is in [`specs/`](../specs/), also free to use.

> **On Pokémon.** These are deliberately *not* Pokémon, and we declined to generate any. Pokémon are
> Nintendo/Game Freak's intellectual property; we could not license someone else's characters CC0, and
> handing you art you cannot legally use would be worse than useless.

### 3. One robot, six styles

The *same* mascot concept — **Sprocket**, a small desk-companion robot — rendered in six different
style presets. This is the clearest demonstration that style is a dial you control, independent of
the character.

`pixel` · `plush` · `clay` · `flat-vector` · `3d-toy` · `sticker`

---

## How hard is each style to cut out?

The pipeline keys the pet off a flat green background into transparent sprite cells. **Soft styles
key badly.** Measured green contamination on the silhouette edge of a fresh base:

| style | green edge before despill | after despill |
| --- | --- | --- |
| `flat-vector` | 9.1% | **0.0%** |
| `clay` | 11.2% | **0.0%** |
| `sticker` | 15.0% | **0.0%** |
| `3d-toy` | 16.1% | **0.0%** |
| `plush` | 17.1% | **0.0%** |
| `painterly` | 19.2% | **0.0%** |

Hard geometric edges (`flat-vector`) key cleanest; wispy brush edges (`painterly`) are worst.
**Every style needs despilling** — none of them are clean out of the box. The despill pass fixes
all of them completely.

---

## Using an asset as a Codex pet

These are single base sprites, not full animated pets. To turn one into a real pet, feed it to the
plugin as the canonical base and let it generate the animation rows:

```
/hatch-pet build a pet from assets/mascots/mossback/base.png
```
