#!/usr/bin/env python3
"""Make the pet the SAME SIZE in every animation lane, with headroom for the jump.

THE BUG
  extract_strip_frames fits each row to its own bounding box. The `jumping` row's bbox spans the
  whole jump ARC (pet + vertical travel), so scaling that taller bbox into the fixed 192x208 cell
  shrinks the PET. Measured: jumping 129px vs idle 197px — the pet visibly halves the instant the
  user hovers it. No prompt fixes this: the shrink happens after generation, inside the extractor.

WHY THE OBVIOUS FIX FAILS
  Just scaling `jumping` back up to idle's size pushes the airborne frames out of the top of the
  cell, where they get cropped. A 197px pet + travel simply does not fit in a 208px cell.

THE FIX
  Draw every lane at a common target height (~78% of the cell), anchored to a common baseline.
  That leaves real headroom, so the jump can travel without the pet changing size. Each frame's
  own vertical offset (the jump arc) is preserved, scaled by the same factor.

usage: normalize_lane_scale.py <frames-root> [target-fraction]
"""
import os
import sys

import numpy as np
from PIL import Image

CELL_W, CELL_H = 192, 208
TARGET_FRAC = 0.78          # pet occupies this much of the cell height -> ~46px headroom
BOTTOM_MARGIN = 6           # px between the pet's feet and the bottom of the cell


def box(im):
    a = np.array(im.convert('RGBA'))
    ys, xs = np.where(a[:, :, 3] > 0)
    if len(ys) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def lane_frames(root, lane):
    d = os.path.join(root, lane)
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith('.png'))


def main(root, frac=TARGET_FRAC):
    lanes = [d for d in sorted(os.listdir(root)) if os.path.isdir(os.path.join(root, d))]
    target_h = frac * CELL_H
    baseline_y = CELL_H - BOTTOM_MARGIN

    for lane in lanes:
        if lane.startswith('look'):
            continue                       # look rows are head-only; leave their framing alone

        frames = lane_frames(root, lane)
        boxes = {f: box(Image.open(f)) for f in frames}
        boxes = {f: b for f, b in boxes.items() if b}
        if not boxes:
            continue

        heights = [b[3] - b[1] + 1 for b in boxes.values()]
        bottoms = [b[3] for b in boxes.values()]
        h_med = float(np.median(heights))
        b_med = float(np.median(bottoms))
        if h_med <= 0:
            continue

        k = target_h / h_med

        for f, b in boxes.items():
            im = Image.open(f).convert('RGBA')
            sprite = im.crop((b[0], b[1], b[2] + 1, b[3] + 1))
            nw = max(1, int(round(sprite.width * k)))
            nh = max(1, int(round(sprite.height * k)))
            sprite = sprite.resize((nw, nh), Image.LANCZOS)

            # LANCZOS rings. Scaling UP (bot-pixel needed x2.25) sprays faint non-zero alpha
            # across the whole cell, which reads as "background baked in" — 65% opaque, 66%
            # border ring — even though it is invisible. Clamp the ringing away.
            sa = np.array(sprite)
            sa[:, :, 3] = np.where(sa[:, :, 3] < 24, 0, sa[:, :, 3])
            sa[sa[:, :, 3] == 0] = 0
            sprite = Image.fromarray(sa, 'RGBA')

            # keep this frame's offset from the lane's baseline (that IS the jump arc), scaled
            offset = (b[3] - b_med) * k
            bottom = int(round(baseline_y + offset))

            out = Image.new('RGBA', (CELL_W, CELL_H), (0, 0, 0, 0))
            x = (CELL_W - nw) // 2
            y = bottom - nh
            out.alpha_composite(sprite, (x, y))
            out.save(f)

        print(f'  {lane:15s} {h_med:5.1f}px -> {target_h:.0f}px  (x{k:.2f})')


if __name__ == '__main__':
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else TARGET_FRAC)
