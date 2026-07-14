#!/usr/bin/env python3
"""Build an evolving pet by CHAINING atlases we already have — zero generation.

    assemble_evolution_line.py <line.json>

A stage-2 atlas is expensive (~11 image generations). But an evolution stage does not
have to be *new* art — it just has to be a full atlas. We already ship 14 of them. So
an evolving pet can point its stages at existing pets' sheets, and the app renders the
right form for the level with no art cost at all.

The line spec:
    {
      "id": "sprocket-evo",
      "displayName": "Sprocket",
      "type": "machine",
      "description": "...",
      "stages": [
        { "source": "bot-pixel",       "minLevel": 0,  "name": "Sprocket 8-bit",
          "attributes": {"type":"machine","hp":38,"atk":40,"def":36,"spd":44} },
        { "source": "bot-flat-vector",  "minLevel": 8,  "name": "Sprocket Vector", ... },
        { "source": "bot-3d-toy",       "minLevel": 20, "name": "Sprocket HD", ... }
      ]
    }

`source` names an existing pets/<source>/ directory; its atlas becomes this stage.
"""
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

REPO = Path.home() / "Desktop/hatch-pet-plus"
CELL_W, CELL_H = 192, 208
IDLE_COUNT = 6
BG_CALM = (250, 251, 252, 255)
BG_FLASH = (26, 30, 46, 255)
FRAME_MS, FLASH_MS = 120, 55


def source_sheet(key: str) -> Path:
    for name in ("spritesheet.webp", "stage-1.webp"):
        p = REPO / "pets" / key / name
        if p.is_file():
            return p
    raise SystemExit(f"assemble_evolution_line: no atlas for source pet '{key}'")


def idle_frames(sheet: Path) -> list[Image.Image]:
    a = Image.open(sheet).convert("RGBA")
    out = []
    for c in range(IDLE_COUNT):
        cell = a.crop((c * CELL_W, 0, (c + 1) * CELL_W, CELL_H))
        if cell.getbbox() is not None:
            out.append(cell)
    return out


def whiten(img: Image.Image, amount: float) -> Image.Image:
    if amount <= 0:
        return img
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, al = px[x, y]
            if al:
                px[x, y] = (int(r + (255 - r) * amount), int(g + (255 - g) * amount),
                            int(b + (255 - b) * amount), al)
    return out


def on_bg(img, t=0.0):
    bg = tuple(int(c + (f - c) * t) for c, f in zip(BG_CALM, BG_FLASH))
    base = Image.new("RGBA", img.size, bg)
    base.alpha_composite(img)
    return base


def evolution_media(out: Path, stage_sheets: list[Path]) -> None:
    """One GIF that walks the whole chain, and a static chart of every stage."""
    idles = [idle_frames(s) for s in stage_sheets]
    frames, timing = [], []

    def add(f, ms, t=0.0):
        frames.append(on_bg(whiten(f, t), t))
        timing.append(ms)

    for i, cur in enumerate(idles):
        for k in range(len(cur) * 2):        # hold this form idling
            add(cur[k % len(cur)], FRAME_MS)
        if i + 1 < len(idles):               # morph into the next
            nxt = idles[i + 1]
            for s in range(1, 7):
                add(cur[s % len(cur)], FLASH_MS, s / 6)
            for _ in range(2):
                add(cur[0], FLASH_MS, 1.0)
            for _ in range(2):
                add(nxt[0], FLASH_MS, 1.0)
            for s in range(1, 7):
                add(nxt[s % len(nxt)], FLASH_MS, 1 - s / 6)

    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=255) for f in frames]
    pal[0].save(out / "evolution.gif", save_all=True, append_images=pal[1:],
                duration=timing, loop=0, disposal=2)

    # static chart: stage 1 -> stage 2 -> ... with arrows
    pad, gap = 16, 46
    n = len(idles)
    w = n * CELL_W + (n - 1) * gap + pad * 2
    chart = Image.new("RGBA", (w, CELL_H + pad * 2), BG_CALM)
    for i, cur in enumerate(idles):
        x = pad + i * (CELL_W + gap)
        chart.alpha_composite(cur[0], (x, pad))
        if i + 1 < n:
            ay = pad + CELL_H // 2
            ax = x + CELL_W + gap // 2
            chart.alpha_composite(Image.new("RGBA", (gap - 14, 3), (150, 158, 168, 255)),
                                  (ax - (gap - 14) // 2, ay))
    chart.convert("RGB").save(out / "evolution.png")


def main() -> None:
    spec = json.loads(Path(sys.argv[1]).read_text())
    out = REPO / "pets" / spec["id"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "previews").mkdir(exist_ok=True)

    manifest_stages, sheets = [], []
    for n, st in enumerate(spec["stages"], start=1):
        src = source_sheet(st["source"])
        shutil.copy2(src, out / f"stage-{n}.webp")
        sheets.append(out / f"stage-{n}.webp")

        # bring the source pet's per-lane preview GIFs along, under this stage
        src_prev = src.parent / "previews"
        if src_prev.is_dir():
            dst_prev = out / "previews" / f"stage-{n}"
            if dst_prev.exists():
                shutil.rmtree(dst_prev)
            shutil.copytree(src_prev, dst_prev)

        entry = {"minLevel": st["minLevel"], "name": st["name"],
                 "spritesheetPath": f"stage-{n}.webp"}
        if st.get("attributes"):
            entry["attributes"] = st["attributes"]
        manifest_stages.append(entry)

    pet = {
        "id": spec["id"],
        "displayName": spec.get("displayName", spec["stages"][0]["name"]),
        "description": spec.get("description", ""),
        "spriteVersionNumber": 2,
        "spritesheetPath": "stage-1.webp",   # first form, so Codex still loads it
        "stages": manifest_stages,
    }
    if spec.get("type"):
        pet["type"] = spec["type"]
    # This pet is COMPOSED from existing pets' atlases, not new art. Showcases that
    # display distinct art skip it (its stages would duplicate other pets); the
    # evolution showcase features it.
    pet["composed"] = True
    (out / "pet.json").write_text(json.dumps(pet, indent=2, ensure_ascii=False) + "\n")

    # a contact sheet per stage, from the source
    from subprocess import run
    sk = Path.home() / ".codex/skills/hatch-pet/scripts/make_contact_sheet.py"
    if sk.is_file():
        for n, s in enumerate(sheets, start=1):
            run([sys.executable, str(sk), str(s), "--output", str(out / f"contact-sheet-{n}.png")],
                capture_output=True)

    evolution_media(out, sheets)

    chain = " -> ".join(f"{s['name']}(L{s['minLevel']})" for s in manifest_stages)
    print(f"{spec['id']}: {chain}")
    print(f"  {len(sheets)} stages, 0 images generated -> {out}")


if __name__ == "__main__":
    main()
