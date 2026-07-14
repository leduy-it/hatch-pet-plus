#!/usr/bin/env python3
"""The look directions — the one thing the repo never actually showed.

Rows 9 and 10 of the atlas are 16 head poses, one every 22.5°, and they are what
makes the pet track your cursor. Until now they existed only as still cells on a
contact sheet, so the single most alive thing a pet does was invisible.

    pets/<name>/previews/look.gif    the head sweeping a full circle
    pets/<name>/look-strip.png       all 16 directions, laid out as a clock
    examples/showcase-look.gif       every pet sweeping together

Row 9  = 000, 022.5, 045, 067.5, 090, 112.5, 135, 157.5   (up -> screen-right -> down)
Row 10 = 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5   (down -> screen-left -> up)
So cells 0..15 in order ARE a full clockwise sweep.
"""
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path.home() / "Desktop/hatch-pet-plus"
CELL_W, CELL_H = 192, 208
LOOK_ROWS = (9, 10)
BG = (250, 251, 252, 255)


def sheet_of(pet: Path) -> Path | None:
    for n in ("spritesheet.webp", "stage-1.webp"):
        if (pet / n).is_file():
            return pet / n
    return None


def look_cells(sheet: Path) -> list[Image.Image]:
    """All 16 directions, in clockwise order starting from straight up."""
    a = Image.open(sheet).convert("RGBA")
    out = []
    for r in LOOK_ROWS:
        for c in range(8):
            cell = a.crop((c * CELL_W, r * CELL_H, (c + 1) * CELL_W, (r + 1) * CELL_H))
            if cell.getbbox() is not None:
                out.append(cell)
    return out


def on_bg(img, scale=1.0):
    w, h = int(CELL_W * scale), int(CELL_H * scale)
    if scale != 1.0:
        img = img.resize((w, h), Image.LANCZOS)
    base = Image.new("RGBA", (w, h), BG)
    base.alpha_composite(img)
    return base


def save(frames, path, duration=110):
    if not frames:
        return
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=255) for f in frames]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=duration,
                loop=0, disposal=2)


def sweep(cells: list[Image.Image]) -> list[Image.Image]:
    """A full circle, then back the other way — so the eye reads it as tracking
    rather than snapping round."""
    order = list(range(len(cells))) + list(range(len(cells) - 2, 0, -1))
    return [on_bg(cells[i]) for i in order]


def strip16(cells: list[Image.Image], path: Path) -> None:
    """All 16 directions at once, 8 per row, with their angles."""
    pad, head = 6, 18
    cols = 8
    rows = (len(cells) + cols - 1) // cols
    w = cols * CELL_W + pad * (cols + 1)
    h = rows * (CELL_H + head) + pad * (rows + 1)
    canvas = Image.new("RGBA", (w, h), BG)
    d = ImageDraw.Draw(canvas)
    for i, c in enumerate(cells):
        x = pad + (i % cols) * (CELL_W + pad)
        y = pad + (i // cols) * (CELL_H + head + pad)
        d.text((x + 2, y), f"{i * 22.5:g}°", fill=(120, 128, 142, 255))
        canvas.alpha_composite(c, (x, y + head))
    canvas.convert("RGB").save(path)


def main() -> None:
    pets = sorted(p for p in (REPO / "pets").iterdir() if p.is_dir() and sheet_of(p))
    done = []
    for p in pets:
        cells = look_cells(sheet_of(p))
        if len(cells) < 16:
            print(f"  {p.name}: only {len(cells)}/16 look cells — skipped")
            continue
        prev = p / ("previews/stage-1" if (p / "stage-1.webp").is_file() else "previews")
        prev.mkdir(parents=True, exist_ok=True)
        save(sweep(cells), prev / "look.gif")
        strip16(cells, p / "look-strip.png")
        done.append(p.name)
    print(f"  pets/*/previews/look.gif + look-strip.png   ({len(done)} pets)")

    # every pet sweeping together
    scale = 0.62
    allcells = {p.name: look_cells(sheet_of(p)) for p in pets if len(look_cells(sheet_of(p))) >= 16}
    names = sorted(allcells)
    order = list(range(16)) + list(range(14, 0, -1))
    pad = 6
    w = int(CELL_W * scale)
    h = int(CELL_H * scale)
    frames = []
    for i in order:
        canvas = Image.new("RGBA", (len(names) * w + pad * (len(names) + 1), h + pad * 2), BG)
        for j, n in enumerate(names):
            canvas.alpha_composite(on_bg(allcells[n][i], scale), (pad + j * (w + pad), pad))
        frames.append(canvas)
    save(frames, REPO / "examples/showcase-look.gif", duration=110)
    print(f"  examples/showcase-look.gif                  ({len(names)} pets, 16 directions)")


if __name__ == "__main__":
    main()
