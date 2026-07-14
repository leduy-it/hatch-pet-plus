#!/usr/bin/env python3
"""Cut a mascot out of its white background — without punching holes in the mascot.

    cutout_white.py <base.png> <cutout.png>

The mascots are generated on pure white. The naive cut — "make white transparent" —
would also erase a cream felt belly, a snow-white hare, the sugar crust on a gumdrop.
So instead of keying by colour, we flood-fill inwards from the four edges and remove
only the white that is CONNECTED to the border. Interior whites are part of the
creature and are kept.

The edge is then feathered by one pixel so the cutout does not have a hard aliased
rim, and any fully-transparent pixel is zeroed in RGB so a lossless WebP/PNG carries
no colour residue behind the alpha.
"""
import sys
from collections import deque

import numpy as np
from PIL import Image

WHITE_MIN = 236          # a pixel this bright on all channels is "background white"
FEATHER = 1


def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    im = Image.open(src).convert("RGBA")
    a = np.array(im)
    rgb = a[:, :, :3].astype(int)
    h, w = a.shape[:2]

    near_white = (rgb.min(axis=2) >= WHITE_MIN)

    # Flood-fill the background from every edge pixel that is near-white. Only white
    # reachable from the border is background; white walled inside the sprite is kept.
    bg = np.zeros((h, w), bool)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near_white[y, x]:
                dq.append((y, x)); bg[y, x] = True
    for y in range(h):
        for x in (0, w - 1):
            if near_white[y, x] and not bg[y, x]:
                dq.append((y, x)); bg[y, x] = True
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not bg[ny, nx] and near_white[ny, nx]:
                bg[ny, nx] = True
                dq.append((ny, nx))

    alpha = np.where(bg, 0, 255).astype(np.uint8)

    # Feather: one ring of edge pixels goes half-transparent so the rim is not aliased.
    if FEATHER:
        from PIL import ImageFilter
        soft = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(FEATHER))
        alpha = np.array(soft)

    out = a.copy()
    out[:, :, 3] = alpha
    out[alpha == 0, :3] = 0     # no RGB residue behind transparent pixels

    Image.fromarray(out, "RGBA").save(dst)

    kept = int((alpha > 0).sum())
    print(f"{src.split('/')[-1]:16s} -> cutout  ({kept * 100 // (h * w)}% opaque)")


if __name__ == "__main__":
    main()
