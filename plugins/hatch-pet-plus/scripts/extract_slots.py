#!/usr/bin/env python3
"""Deterministic slot-based frame extraction — a fallback when the skill's extractor fails.

WHY
  extract_strip_frames segments poses by connected component. bot-pixel's robots are packed
  tightly enough that adjacent arms touch, so two robots fuse into one component and the rest
  come out EMPTY:
      00.png h=71 w=182 (two robots merged)   02.png h=17 w=9 (empty)   03.png (empty)
  Both --method auto and --method stable-slots produce this.

WHAT THIS DOES
  The poses are evenly spaced by construction (the layout guide enforces it), so just slice the
  strip into N equal columns, take the sprite in each, and fit it to the 192x208 cell with a
  shared scale and a common baseline — which is what stable-slots was meant to do anyway.

usage: extract_slots.py <run-dir> <chroma-hex>
"""
import json
import os
import sys

import numpy as np
from PIL import Image

CELL_W, CELL_H = 192, 208
TARGET_FRAC = 0.78
BOTTOM_MARGIN = 6

COUNTS = {'idle': 6, 'running-right': 8, 'running-left': 8, 'waving': 4, 'jumping': 5,
          'failed': 8, 'waiting': 6, 'running': 6, 'review': 6,
          'look-row-9': 8, 'look-row-10': 8}

run, chroma = sys.argv[1], sys.argv[2]
K = np.array([int(chroma[1:3], 16), int(chroma[3:5], 16), int(chroma[5:7], 16)])
out_root = f'{run}/frames'

manifest = {}
for state, n in COUNTS.items():
    p = f'{run}/decoded/{state}.png'
    if not os.path.exists(p):
        continue
    im = Image.open(p).convert('RGBA')
    a = np.array(im).astype(int)
    h, w = a.shape[:2]
    sw = w // n

    # first pass: find each slot's sprite box, and the shared scale + baseline
    boxes = []
    for i in range(n):
        sl = a[:, i*sw:(i+1)*sw, :3]
        mask = np.sqrt(((sl - K) ** 2).sum(2)) > 96
        ys, xs = np.where(mask)
        boxes.append(None if len(ys) == 0 else
                     (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))

    valid = [b for b in boxes if b]
    if not valid:
        continue
    hmax = max(b[3] - b[1] + 1 for b in valid)
    base = int(np.median([b[3] for b in valid]))
    k = (TARGET_FRAC * CELL_H) / hmax          # ONE scale for the whole row

    d = f'{out_root}/{state}'
    os.makedirs(d, exist_ok=True)
    for i, b in enumerate(boxes):
        cell = Image.new('RGBA', (CELL_W, CELL_H), (0, 0, 0, 0))
        if b:
            sprite = im.crop((i*sw + b[0], b[1], i*sw + b[2] + 1, b[3] + 1))
            # drop the chroma background inside the crop
            sa = np.array(sprite).astype(int)
            bgm = np.sqrt(((sa[:, :, :3] - K) ** 2).sum(2)) <= 96
            sa[bgm] = 0
            sprite = Image.fromarray(sa.astype(np.uint8), 'RGBA')

            nw = max(1, int(round(sprite.width * k)))
            nh = max(1, int(round(sprite.height * k)))
            sprite = sprite.resize((nw, nh), Image.LANCZOS)
            sa = np.array(sprite)
            sa[:, :, 3] = np.where(sa[:, :, 3] < 24, 0, sa[:, :, 3])   # kill LANCZOS ringing
            sa[sa[:, :, 3] == 0] = 0
            sprite = Image.fromarray(sa, 'RGBA')

            offset = (b[3] - base) * k                      # preserve this frame's jump offset
            bottom = int(round(CELL_H - BOTTOM_MARGIN + offset))
            cell.alpha_composite(sprite, ((CELL_W - nw) // 2, bottom - nh))
        cell.save(f'{d}/{i:02d}.png')

    manifest[state] = n
    filled = sum(1 for b in boxes if b)
    print(f'  {state:15s} {filled}/{n} slots  (shared scale x{k:.2f})')

os.makedirs(out_root, exist_ok=True)
json.dump({'states': manifest}, open(f'{out_root}/frames-manifest.json', 'w'), indent=2)
