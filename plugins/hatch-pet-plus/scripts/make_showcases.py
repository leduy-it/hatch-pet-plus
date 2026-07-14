#!/usr/bin/env python3
"""The repo-level showcases. Regenerates every one, from the atlases.

    examples/showcase-all-idle.gif    every pet idling
    examples/showcase-lanes.gif       every pet playing each lane in turn
    examples/showcase-hover.gif       every pet's `jumping` — what you see most
    examples/showcase-evolution.gif   every evolving pet transforming
    pets/<name>/demo.gif              one pet, all nine lanes side by side

Reads stage one of an evolving pet, so it appears alongside the others.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path.home() / "Desktop/hatch-pet-plus"
CELL_W, CELL_H = 192, 208
PAD = 6
BG = (250, 251, 252, 255)

LANES = ["idle", "waving", "jumping", "running-right", "running-left",
         "running", "waiting", "review", "failed"]
COUNTS = {"idle": 6, "running-right": 8, "running-left": 8, "waving": 4, "jumping": 5,
          "failed": 8, "waiting": 6, "running": 6, "review": 6}
ROW = {l: i for i, l in enumerate(
    ["idle", "running-right", "running-left", "waving", "jumping",
     "failed", "waiting", "running", "review"])}


def sheet_of(pet: Path) -> Path | None:
    for name in ("spritesheet.webp", "stage-1.webp"):
        if (pet / name).is_file():
            return pet / name
    return None


def lane_frames(sheet: Path, lane: str) -> list[Image.Image]:
    a = Image.open(sheet).convert("RGBA")
    r = ROW[lane]
    out = []
    for c in range(COUNTS[lane]):   # not all 8: the surplus cell duplicates the first
        cell = a.crop((c * CELL_W, r * CELL_H, (c + 1) * CELL_W, (r + 1) * CELL_H))
        if cell.getbbox() is not None:
            out.append(cell)
    return out


def save(frames, path, duration=140):
    if not frames:
        return
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=255) for f in frames]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=duration,
                loop=0, disposal=2)


def strip(clips: list[list[Image.Image]], label: str | None = None,
          scale: float = 1.0) -> list[Image.Image]:
    """Lay clips side by side and play them in step."""
    w, h = int(CELL_W * scale), int(CELL_H * scale)
    n = max(len(c) for c in clips)
    head = 26 if label else 0
    out = []
    for i in range(n):
        canvas = Image.new("RGBA", (len(clips) * w + PAD * (len(clips) + 1), h + PAD * 2 + head), BG)
        if label:
            d = ImageDraw.Draw(canvas)
            d.text((PAD + 2, 6), label, fill=(90, 98, 112, 255))
        for j, c in enumerate(clips):
            f = c[i % len(c)]
            if scale != 1.0:
                f = f.resize((w, h), Image.LANCZOS)
            canvas.alpha_composite(f, (PAD + j * (w + PAD), PAD + head))
        out.append(canvas)
    return out


def main() -> None:
    pets = sorted(p for p in (REPO / "pets").iterdir() if p.is_dir() and sheet_of(p))
    sheets = {p.name: sheet_of(p) for p in pets}
    ex = REPO / "examples"
    print(f"{len(pets)} pets: {', '.join(p.name for p in pets)}\n")

    # per-pet: all nine lanes side by side
    for p in pets:
        clips = [lane_frames(sheets[p.name], l) for l in LANES]
        clips = [c for c in clips if c]
        if clips:
            save(strip(clips), p / "demo.gif")
    print(f"  pets/*/demo.gif                ({len(pets)} pets, 9 lanes each)")

    scale = 0.62   # 14 pets at full size is 2700px wide

    # every pet idling
    save(strip([lane_frames(sheets[p.name], "idle") for p in pets], scale=scale),
         ex / "showcase-all-idle.gif", duration=200)
    print(f"  examples/showcase-all-idle.gif ({len(pets)} pets)")

    # every pet's hover animation — the one users see most
    save(strip([lane_frames(sheets[p.name], "jumping") for p in pets], scale=scale),
         ex / "showcase-hover.gif", duration=150)
    print(f"  examples/showcase-hover.gif    ({len(pets)} pets, `jumping`)")

    # every pet through every lane, labelled
    frames, timing = [], []
    for lane in LANES:
        seg = strip([lane_frames(sheets[p.name], lane) for p in pets], label=lane, scale=scale)
        # One loop per lane, played slowly. Two loops read better but doubled the file to
        # 5.5MB, which is not a reasonable thing to put at the top of a README.
        frames += seg
        timing += [190] * len(seg)
        timing[-1] = 650                          # beat before the next lane
    save(frames, ex / "showcase-lanes.gif")
    Image.open(ex / "showcase-lanes.gif")
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=255) for f in frames]
    pal[0].save(ex / "showcase-lanes.gif", save_all=True, append_images=pal[1:],
                duration=timing, loop=0, disposal=2)
    print(f"  examples/showcase-lanes.gif    ({len(pets)} pets x {len(LANES)} lanes, {len(frames)} frames)")


if __name__ == "__main__":
    main()
