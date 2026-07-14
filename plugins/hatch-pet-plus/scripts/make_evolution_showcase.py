#!/usr/bin/env python3
"""Every evolving pet transforming, side by side, in step.

    make_evolution_showcase.py                 -> examples/showcase-evolution.gif
                                                  examples/showcase-evolution.png

Finds every pet in pets/ that has a stage-2 sheet. Reuses the single-pet effect so
the showcase and the per-pet GIF can never drift apart.
"""
import os
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_evolution_gif import (  # noqa: E402
    BG_CALM, BG_FLASH, CELL_W, CELL_H, FLASH_HOLD, FLASH_IN, FLASH_MS, FLASH_OUT,
    FRAME_MS, HOLD_CYCLES, idle_frames, whiten,
)

REPO = Path.home() / "Desktop/hatch-pet-plus"
PAD = 10


def timeline(a: list, b: list) -> list:
    """(frame, whiteness, ms) for one pet — identical shape for every pet, so the
    columns stay in step no matter how many idle frames each one has."""
    out = []
    for i in range(HOLD_CYCLES * 6):
        out.append((a[i % len(a)], 0.0, FRAME_MS))
    for i in range(FLASH_IN):
        out.append((a[i % len(a)], (i + 1) / FLASH_IN, FLASH_MS))
    for _ in range(FLASH_HOLD):
        out.append((a[0], 1.0, FLASH_MS))
    for _ in range(FLASH_HOLD):
        out.append((b[0], 1.0, FLASH_MS))
    for i in range(FLASH_OUT):
        out.append((b[i % len(b)], 1.0 - (i + 1) / FLASH_OUT, FLASH_MS))
    for i in range(HOLD_CYCLES * 6):
        out.append((b[i % len(b)], 0.0, FRAME_MS))
    return out


def main() -> None:
    pets = sorted(p for p in (REPO / "pets").iterdir()
                  if (p / "stage-2.webp").is_file() and (p / "stage-1.webp").is_file())
    if not pets:
        raise SystemExit("make_evolution_showcase: no evolving pets built yet")

    tls = [timeline(idle_frames(p / "stage-1.webp"), idle_frames(p / "stage-2.webp")) for p in pets]
    n = min(len(t) for t in tls)

    w = len(pets) * CELL_W + PAD * (len(pets) + 1)
    h = CELL_H + PAD * 2
    frames, timing = [], []
    for i in range(n):
        t = tls[0][i][1]  # every pet shares the timeline, so one whiteness drives the backdrop
        bg = tuple(int(c + (f - c) * t) for c, f in zip(BG_CALM, BG_FLASH))
        canvas = Image.new("RGBA", (w, h), bg)
        for j, tl in enumerate(tls):
            frame, white, _ = tl[i]
            canvas.alpha_composite(whiten(frame, white), (PAD + j * (CELL_W + PAD), PAD))
        frames.append(canvas)
        timing.append(tls[0][i][2])

    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=255) for f in frames]
    out = REPO / "examples"
    pal[0].save(out / "showcase-evolution.gif", save_all=True, append_images=pal[1:],
                duration=timing, loop=0, disposal=2)

    # a static before/after, one row per pet
    chart_gap = 56
    cw = CELL_W * 2 + chart_gap + PAD * 2
    ch = len(pets) * (CELL_H + PAD) + PAD
    chart = Image.new("RGBA", (cw, ch), BG_CALM)
    for j, p in enumerate(pets):
        y = PAD + j * (CELL_H + PAD)
        a = idle_frames(p / "stage-1.webp")[0]
        b = idle_frames(p / "stage-2.webp")[0]
        chart.alpha_composite(a, (PAD, y))
        chart.alpha_composite(b, (PAD + CELL_W + chart_gap, y))
        ax, ay = PAD + CELL_W + chart_gap // 2, y + CELL_H // 2
        chart.alpha_composite(Image.new("RGBA", (chart_gap - 16, 3), (150, 158, 168, 255)),
                              (ax - (chart_gap - 16) // 2, ay))
    chart.convert("RGB").save(out / "showcase-evolution.png")

    print(f"showcase-evolution.gif  ({len(pets)} evolving pets: {', '.join(p.name for p in pets)}, "
          f"{len(frames)} frames)")


if __name__ == "__main__":
    main()
