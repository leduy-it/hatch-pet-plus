#!/usr/bin/env python3
"""Render the evolution effect for an evolving pet.

    make_evolution_gif.py <pet-dir>

Produces, in <pet-dir>:
    evolution.gif     stage 1 idling -> white-out -> stage 2 idling, looping
    evolution.png     a static chart: stage 1  ->  stage 2

The white-out is the same effect the app plays when a pet crosses a stage
threshold: the sprite blows out to a flat silhouette, the sheet is swapped
underneath it, and the new form fades back in. Doing it as a silhouette is what
sells the change — the shape morphs while the colour is gone, so the eye reads
one creature becoming another rather than two pictures being cross-faded.
"""
import sys
from pathlib import Path

from PIL import Image, ImageSequence  # noqa: F401  (ImageSequence kept for parity with make_showcase)

CELL_W, CELL_H = 192, 208
IDLE_ROW = 0
# The idle lane the app actually plays is 6 frames (verify_pet.py COUNTS[0]). The
# atlas holds 8 columns and cell[6] is a loop-CLOSING duplicate of cell[0] — verified
# byte-identical on every shipped pet. Taking every non-empty cell would play frame 0
# twice per loop, a visible hitch in the idle we hold either side of the transformation.
IDLE_COUNT = 6

HOLD_CYCLES = 2       # idle loops before/after the transformation
FLASH_IN = 6          # frames blowing out to white
FLASH_HOLD = 2        # frames of pure white silhouette (the swap happens here)
FLASH_OUT = 6         # frames fading the new form back in
FRAME_MS = 110
FLASH_MS = 55         # the transformation runs faster than the idle


def idle_frames(sheet: Path) -> list[Image.Image]:
    """Row 0 of the atlas — the idle lane, without its loop-closing duplicate."""
    sheet_img = Image.open(sheet).convert("RGBA")
    frames = []
    for c in range(IDLE_COUNT):
        cell = sheet_img.crop(
            (c * CELL_W, IDLE_ROW * CELL_H, (c + 1) * CELL_W, (IDLE_ROW + 1) * CELL_H)
        )
        if cell.getbbox() is not None:  # tolerate a lane that is shorter still
            frames.append(cell)
    if not frames:
        raise SystemExit(f"make_evolution_gif: {sheet} has an empty idle lane")
    return frames


def whiten(img: Image.Image, amount: float) -> Image.Image:
    """Push the sprite toward a flat white silhouette. Alpha is untouched, so the
    shape stays exactly the sprite's own outline."""
    out = img.copy()
    px = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (
                    int(r + (255 - r) * amount),
                    int(g + (255 - g) * amount),
                    int(b + (255 - b) * amount),
                    a,
                )
    return out


BG_CALM = (250, 251, 252, 255)
BG_FLASH = (26, 30, 46, 255)   # the backdrop dims as the sprite blows out


def on_bg(img: Image.Image, t: float = 0.0) -> Image.Image:
    """Composite onto the backdrop. `t` is how far into the transformation we are:
    at t=1 the sprite is pure white, so the backdrop must be dark or the silhouette
    — the whole point of the effect, since that is where the shape changes —
    disappears into the page."""
    bg = tuple(int(c + (f - c) * t) for c, f in zip(BG_CALM, BG_FLASH))
    base = Image.new("RGBA", img.size, bg)
    base.alpha_composite(img)
    return base


def main() -> None:
    pet = Path(sys.argv[1])
    s1, s2 = pet / "stage-1.webp", pet / "stage-2.webp"
    for s in (s1, s2):
        if not s.is_file():
            raise SystemExit(f"make_evolution_gif: missing {s}")

    a, b = idle_frames(s1), idle_frames(s2)
    frames: list[Image.Image] = []
    timing: list[int] = []

    def add(f: Image.Image, ms: int, t: float = 0.0) -> None:
        frames.append(on_bg(whiten(f, t), t))
        timing.append(ms)

    for i in range(HOLD_CYCLES * len(a)):
        add(a[i % len(a)], FRAME_MS)

    # blow the old form out to white as the backdrop dims
    for i in range(FLASH_IN):
        add(a[i % len(a)], FLASH_MS, (i + 1) / FLASH_IN)

    # the swap, hidden inside the white-out: the silhouette itself changes, and it
    # is legible because the backdrop is now dark
    for _ in range(FLASH_HOLD):
        add(a[0], FLASH_MS, 1.0)
    for _ in range(FLASH_HOLD):
        add(b[0], FLASH_MS, 1.0)

    # bring the new form back up
    for i in range(FLASH_OUT):
        add(b[i % len(b)], FLASH_MS, 1.0 - (i + 1) / FLASH_OUT)

    for i in range(HOLD_CYCLES * len(b)):
        add(b[i % len(b)], FRAME_MS)

    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=255) for f in frames]
    pal[0].save(
        pet / "evolution.gif",
        save_all=True,
        append_images=pal[1:],
        duration=timing,
        loop=0,
        disposal=2,
    )

    # static chart: stage 1 -> stage 2
    pad, gap = 16, 56
    chart = Image.new("RGBA", (CELL_W * 2 + gap + pad * 2, CELL_H + pad * 2), (250, 251, 252, 255))
    chart.alpha_composite(a[0], (pad, pad))
    chart.alpha_composite(b[0], (pad + CELL_W + gap, pad))
    ax = pad + CELL_W + gap // 2
    ay = pad + CELL_H // 2
    arrow = Image.new("RGBA", (gap, 3), (150, 158, 168, 255))
    chart.alpha_composite(arrow, (ax - gap // 2, ay))
    for i in range(9):  # arrowhead
        head = Image.new("RGBA", (1, max(1, 9 - i)), (150, 158, 168, 255))
        chart.alpha_composite(head, (ax + gap // 2 - 10 + i, ay - (9 - i) // 2 + 1))
    chart.convert("RGB").save(pet / "evolution.png")

    print(f"{pet.name}: evolution.gif ({len(frames)} frames), evolution.png")


if __name__ == "__main__":
    main()
