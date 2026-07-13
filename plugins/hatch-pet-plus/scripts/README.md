# Hardening scripts

These fix real defects the stock pipeline does not catch. `validate_atlas` reported
`ok: true, 0 errors` on pets that were visibly broken — see `docs/LESSONS.md`.

| script | fixes |
| --- | --- |
| `pick_key.py` | choose the chroma key **furthest from the pet's own palette** (the auto-picker gave a blue pet a magenta key) |
| `normalize_bg.py` | detect each strip's **actual** background and force it onto the declared key — the model ignores the colour you ask for |
| `despill.py` | universal despill; handles **2-channel keys** like magenta (single-channel clamping left a violet fringe on 50% of edges) |
| `despill_strips.py` / `despill_atlas.py` | apply it before extraction and on the final atlas |
| `extract_slots.py` | deterministic slot slicing — the stock extractor silently emits **empty frames** when adjacent poses touch |
| `normalize_lane_scale.py` | stop the pet **halving in size on hover** (jump-arc bbox shrinks the sprite) |
| `pad_look_row.py` | recentre look-row poses so the assembler accepts them |
| `verify_pet.py` | independent QA gate — geometry, baked-in background, chroma lean across **all** keys, cross-lane scale, lane population |

Run `verify_pet.py <pet-dir> <chroma-hex>` on any pet. It exits non-zero on failure.
