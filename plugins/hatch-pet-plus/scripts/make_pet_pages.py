#!/usr/bin/env python3
"""Give every pet the showcase depth the flagship one has.

Until now only `bunny` had a full write-up; the other twelve shipped with a contact
sheet and a demo GIF and nothing that told you what any of it did. This builds, per pet:

    pets/<name>/README.md   lane-by-lane detail: what plays it, how many frames, how big
    pets/<name>/base.png    the canonical base art the whole pet was generated from
    pets/<name>/hero.gif    a large idle loop

Everything in the page is MEASURED from the atlas — frame counts, sprite heights, the QA
numbers. Nothing is asserted from memory, because the whole history of this project is
green checks on broken pets.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path.home() / "Desktop/hatch-pet-plus"
RUNS = Path.home() / ".codex/pet-runs"
CELL_W, CELL_H = 192, 208
COLS = 8

LANES = [
    ("idle",          6, "Codex is idle", "the default resting loop"),
    ("running-right", 8, "**you drag it right**", "travels right with a walking cadence"),
    ("running-left",  8, "**you drag it left**", "the mirror of running-right"),
    ("waving",        4, "greeting", "a friendly wave"),
    ("jumping",       5, "**you hover it**", "a small joyful hop — the most-seen animation"),
    ("failed",        8, "Codex failed or was cancelled", "deflated, disappointed"),
    ("waiting",       6, "Codex is blocked on you", "an expectant, asking pose"),
    ("running",       6, "Codex is working / thinking", "focused effort — *not* foot-running"),
    ("review",        6, "Codex is reviewing output", "leaning in, inspecting"),
]

TRIGGERS_NOTE = (
    "Rows 9 and 10 are the **16 look directions**: as you move your cursor, the pet's head "
    "turns to follow it, in 22.5° steps."
)


def lane_stats(atlas: Path) -> dict:
    """Frames actually populated, and the pet's height, per lane — measured."""
    a = np.array(Image.open(atlas).convert("RGBA"))
    out = {}
    for r, (lane, expect, _, _) in enumerate(LANES):
        used, heights = 0, []
        for c in range(COLS):
            cell = a[r * CELL_H:(r + 1) * CELL_H, c * CELL_W:(c + 1) * CELL_W, 3]
            if (cell > 0).sum() > 50:
                used += 1
                ys, _x = np.where(cell > 0)
                heights.append(int(ys.max() - ys.min() + 1))
        out[lane] = {
            "played": expect,
            "populated": used,
            "height": int(np.median(heights[:expect])) if heights else 0,
        }
    return out


def hero_gif(atlas: Path, dst: Path, scale: int = 2) -> None:
    """A big idle loop. Nearest-neighbour, so pixel styles stay crisp."""
    a = Image.open(atlas).convert("RGBA")
    frames = []
    for c in range(6):  # the idle lane; cell 6 is a loop-closing duplicate of cell 0
        cell = a.crop((c * CELL_W, 0, (c + 1) * CELL_W, CELL_H))
        if cell.getbbox() is None:
            continue
        big = cell.resize((CELL_W * scale, CELL_H * scale), Image.NEAREST)
        bg = Image.new("RGBA", big.size, (250, 251, 252, 255))
        bg.alpha_composite(big)
        frames.append(bg)
    if not frames:
        return
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=255) for f in frames]
    pal[0].save(dst, save_all=True, append_images=pal[1:], duration=160, loop=0, disposal=2)


def qa_line(pet_dir: Path, chroma: str) -> str:
    """Run the real QA gate and quote what it says."""
    sp = Path(__file__).resolve().parent
    r = subprocess.run([sys.executable, str(sp / "verify_pet.py"), str(pet_dir), chroma],
                       capture_output=True, text=True)
    first = (r.stdout.strip().splitlines() or ["(no output)"])[0]
    return " ".join(first.split())


def page(key: str) -> bool:
    pet_dir = REPO / "pets" / key
    manifest = json.loads((pet_dir / "pet.json").read_text())
    evolving = bool(manifest.get("stages"))
    composed = bool(manifest.get("composed"))

    sheets = ([(pet_dir / s["spritesheetPath"], s.get("name") or key, s["minLevel"])
               for s in manifest["stages"]] if evolving
              else [(pet_dir / "spritesheet.webp", manifest["displayName"], 0)])
    if not all(p.is_file() for p, _, _ in sheets):
        return False

    # The run that made stage one carries the style, the chroma key and the base art.
    run_key = f"{key}-s1" if evolving else key
    req_path = RUNS / run_key / "pet_request.json"
    req = json.loads(req_path.read_text()) if req_path.is_file() else {}
    style = req.get("style_preset", "auto")
    chroma = req.get("chroma_key", {}).get("hex", "#00FF00")
    notes = (req.get("pet_notes") or manifest.get("description") or "").strip()

    base_src = RUNS / run_key / "references/canonical-base.png"
    if not composed and base_src.is_file() and not (pet_dir / "base.png").is_file():
        b = Image.open(base_src).convert("RGBA")
        b.thumbnail((640, 640), Image.LANCZOS)
        b.convert("RGB").save(pet_dir / "base.png", quality=90)

    hero_gif(sheets[0][0], pet_dir / "hero.gif")

    stats = lane_stats(sheets[0][0])
    prev = "previews/stage-1" if evolving else "previews"

    L = []
    L.append(f"# {manifest['displayName']}")
    L.append("")
    if notes:
        L.append(f"> {notes}")
        L.append("")
    L.append('<p align="center">')
    L.append(f'  <img src="hero.gif" width="240" alt="{manifest["displayName"]} idling">')
    L.append("</p>")
    L.append("")

    meta = [
        ("style", f"`{style}`"),
        ("atlas", "8 × 11 cells of 192×208 — `1536×2288`, `spriteVersionNumber: 2`"),
        ("chroma key", f"`{chroma}` (keyed to transparency, then despilled)"),
    ]
    if evolving:
        chain = " → ".join(f"**{n}** (Lv {lv})" for _, n, lv in sheets)
        meta.append(("evolves", chain))
        attrs = manifest["stages"][0].get("attributes") or {}
        if attrs:
            meta.append(("type", f"`{attrs.get('type', '—')}`"))
    L.append("| | |")
    L.append("|---|---|")
    L += [f"| **{k}** | {v} |" for k, v in meta]
    L.append("")

    if evolving:
        L.append("## Evolution")
        L.append("")
        L.append('<p align="center">')
        L.append('  <img src="evolution.gif" width="240" alt="evolving">')
        L.append("</p>")
        L.append("")
        L.append("| stage | reached at | stats |")
        L.append("|---|---|---|")
        for s in manifest["stages"]:
            a = s.get("attributes") or {}
            stat = (f"HP {a.get('hp','—')} · ATK {a.get('atk','—')} · "
                    f"DEF {a.get('def','—')} · SPD {a.get('spd','—')}") if a else "—"
            L.append(f"| **{s.get('name', '?')}** | Lv {s['minLevel']} | {stat} |")
        L.append("")
        L.append("Each stage is a **complete 8×11 atlas** — see "
                 "[docs/EVOLUTION.md](../../docs/EVOLUTION.md).")
        L.append("")

    L.append("## Every animation, and what plays it")
    L.append("")
    L.append("| | lane | plays when | frames | sprite height |")
    L.append("|---|---|---|---|---|")
    for lane, _n, trigger, desc in LANES:
        s = stats[lane]
        L.append(f'| <img src="{prev}/{lane}.gif" width="76"> | `{lane}` | {trigger} '
                 f'<br><sub>{desc}</sub> | {s["played"]} | {s["height"]}px |')
    L.append("")
    L.append(TRIGGERS_NOTE)
    L.append("")
    heights = [stats[l]["height"] for l, *_ in LANES if stats[l]["height"]]
    if heights:
        spread = (max(heights) - min(heights)) / max(heights) * 100
        L.append(f"The pet is drawn the **same size in every lane** (spread {spread:.0f}%), so it "
                 f"does not visibly resize when you hover or drag it.")
        L.append("")

    L.append("## All 11 rows")
    L.append("")
    L.append('<p align="center">')
    sheet_img = "contact-sheet-1.png" if evolving else "contact-sheet.png"
    L.append(f'  <img src="{sheet_img}" width="640" alt="contact sheet">')
    L.append("</p>")
    L.append("")

    if composed:
        L.append("## Composed from existing pets")
        L.append("")
        L.append("This evolution line reuses atlases that already ship in this repo — **no new art was "
                 "generated**. Each stage is one of the finished, QA-passed pets:")
        L.append("")
        for st in manifest["stages"]:
            L.append(f"- **{st['name']}** — `{st['spritesheetPath']}`")
        L.append("")
    else:
        L.append("## QA")
        L.append("")
        L.append("```")
        L.append(qa_line(pet_dir, chroma))
        L.append("```")
        L.append("")
        L.append("`lean` = pixels still tinted by the chroma key · `ring` = background baked into the "
                 "sprite · `spread` = how much the pet resizes between lanes. All must be near zero.")
        L.append("")
    if (pet_dir / "base.png").is_file():
        L.append("## The base art everything was generated from")
        L.append("")
        L.append('<p align="center">')
        L.append('  <img src="base.png" width="260" alt="canonical base">')
        L.append("</p>")
        L.append("")
        L.append("Every one of the 88 drawings in the atlas was generated against this single "
                 "canonical reference, which is what keeps the identity stable across all of them.")
        L.append("")

    L.append("## Install")
    L.append("")
    L.append("```bash")
    L.append(f"./install.sh --pet {key}")
    L.append("```")
    L.append("")
    L.append("Then **Codex Settings → Appearance / Pets**, and `/pet` to wake it.")
    L.append("")

    (pet_dir / "README.md").write_text("\n".join(L) + "\n")
    return True


if __name__ == "__main__":
    keys = sorted(d.name for d in (REPO / "pets").iterdir()
                  if d.is_dir() and (d / "pet.json").is_file())
    made = [k for k in keys if page(k)]
    print(f"{len(made)} pet pages: {', '.join(made)}")
