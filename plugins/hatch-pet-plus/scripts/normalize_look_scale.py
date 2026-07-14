#!/usr/bin/env python3
"""Stop the pet changing size as you move your cursor.

    normalize_look_scale.py <atlas.webp> [...]

Rows 0-8 (the animations) are scale-normalised at build time by
`normalize_lane_scale.py`. Rows 9-10 — the 16 look directions — never were: they are
pasted into the atlas straight from the generated strips, and the model does not draw
the creature at a consistent size across sixteen head angles.

Measured on the shipped pets, the sprite's area varies by 7-29% across the look row.
Since the look row is what tracks your cursor, the pet visibly swells and shrinks as
you move the mouse. Volt was the worst: 29%.

WHY AREA, NOT HEIGHT
Bounding-box height cannot tell pose from scale — a pet looking straight down really is
shorter than one looking up, and forcing every cell to the same height would squash the
poses. Pixel area is far less sensitive to head angle, so `sqrt(area)` is used as the
scale estimate and the pose is left alone.

Each look cell is rescaled to the common scale, re-centred horizontally, and re-planted
on a common baseline (the feet stay put — that is what makes it read as a head turn
rather than the whole pet bobbing). The look row as a whole is then matched to the
idle lane, so the pet does not jump size when it stops animating and starts looking.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

CELL_W, CELL_H = 192, 208
LOOK_ROWS = (9, 10)
IDLE_ROW = 0
IDLE_FRAMES = 6
ALPHA_FLOOR = 24     # LANCZOS rings faint alpha across the cell; below this it is noise
MAX_CORRECTION = 1.6  # refuse to invent a pet that was never drawn


def cell_of(a: np.ndarray, r: int, c: int) -> np.ndarray:
    return a[r * CELL_H:(r + 1) * CELL_H, c * CELL_W:(c + 1) * CELL_W]


def measure(cell: np.ndarray):
    """(scale estimate, bbox) — None if the cell is empty."""
    m = cell[:, :, 3] > 0
    n = int(m.sum())
    if n < 50:
        return None
    ys, xs = np.where(m)
    return float(np.sqrt(n)), (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))


def rescale(cell: np.ndarray, factor: float, baseline: int) -> np.ndarray:
    """Scale the sprite about its own baseline, centred in the cell."""
    m = measure(cell)
    if m is None or abs(factor - 1.0) < 0.01:
        return cell
    _s, (x0, y0, x1, y1) = m

    sprite = Image.fromarray(cell[y0:y1 + 1, x0:x1 + 1].astype(np.uint8), "RGBA")
    w = max(1, int(round(sprite.width * factor)))
    h = max(1, int(round(sprite.height * factor)))
    sprite = sprite.resize((w, h), Image.LANCZOS)

    out = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    x = (CELL_W - w) // 2
    y = baseline - h
    if y < 0:                       # taller than the cell: sit it at the top, do not clip the feet
        y = 0
    out.alpha_composite(sprite, (max(0, x), max(0, y)))

    arr = np.array(out).astype(int)
    arr[arr[:, :, 3] < ALPHA_FLOOR] = 0     # kill the ringing
    return arr


def normalize(path: Path) -> str:
    a = np.array(Image.open(path).convert("RGBA")).astype(int)

    idle = [measure(cell_of(a, IDLE_ROW, c)) for c in range(IDLE_FRAMES)]
    idle = [m for m in idle if m]
    if not idle:
        return f"{path.name}: no idle lane — skipped"
    idle_scale = float(np.median([m[0] for m in idle]))
    # the feet: where the idle sprite actually stands
    idle_baseline = int(np.median([m[1][3] for m in idle]))

    looks = {}
    for r in LOOK_ROWS:
        for c in range(8):
            m = measure(cell_of(a, r, c))
            if m:
                looks[(r, c)] = m
    if len(looks) < 8:
        return f"{path.name}: only {len(looks)} look cells — skipped"

    before = [m[0] for m in looks.values()]
    spread_before = (max(before) - min(before)) / max(before) * 100

    # Match the look row to the idle lane as a whole, then flatten the jitter within it.
    for (r, c), (scale, _bbox) in looks.items():
        factor = idle_scale / scale
        factor = min(max(factor, 1 / MAX_CORRECTION), MAX_CORRECTION)
        a[r * CELL_H:(r + 1) * CELL_H, c * CELL_W:(c + 1) * CELL_W] = \
            rescale(cell_of(a, r, c), factor, idle_baseline)

    after = []
    for r in LOOK_ROWS:
        for c in range(8):
            m = measure(cell_of(a, r, c))
            if m:
                after.append(m[0])
    spread_after = (max(after) - min(after)) / max(after) * 100

    out = np.clip(a, 0, 255).astype(np.uint8)
    out[out[:, :, 3] == 0] = 0          # transparent pixels must carry no RGB residue
    Image.fromarray(out, "RGBA").save(path, lossless=True, exact=True)

    return f"{path.parent.name:16s} look-row scale spread {spread_before:4.0f}% -> {spread_after:3.0f}%"


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(" ", normalize(Path(p)))
