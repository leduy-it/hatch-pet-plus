#!/usr/bin/env python3
"""Independent QA for a packaged pet. Catches what validate_atlas does NOT.

validate_atlas reported ok=true / 0 errors on a pet whose sprite had a solid MAGENTA rectangle
baked into it — because it only checks contamination by the DECLARED chroma key, and the model
had drawn that strip on a different colour entirely. These checks are the backstop.

  1. atlas geometry            1536x2288, 8x11, RGBA
  2. baked-in background       the border ring of each used cell must be transparent
  3. chroma lean               no pixel leaning toward the declared key
  4. cross-lane scale          the pet must not resize between animations
  5. lane population           every lane has its expected frame count

usage: verify_pet.py <pet-dir> <declared-chroma-hex>
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from despill import residual

CELL_W, CELL_H = 192, 208
LANES = ['idle', 'running-right', 'running-left', 'waving', 'jumping', 'failed',
         'waiting', 'running', 'review', 'look-9', 'look-10']
COUNTS = [6, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8]

pet_dir, chroma = sys.argv[1], sys.argv[2]
name = os.path.basename(pet_dir.rstrip('/'))
K = np.array([int(chroma[1:3], 16), int(chroma[3:5], 16), int(chroma[5:7], 16)])

im = Image.open(f'{pet_dir}/spritesheet.webp').convert('RGBA')
a = np.array(im).astype(int)
rgb, al = a[:, :, :3], a[:, :, 3]
fails = []

# 1. geometry
if im.size != (1536, 2288):
    fails.append(f'atlas is {im.size[0]}x{im.size[1]}, expected 1536x2288')

# 2. baked-in background: the 2px border ring of a used cell must be (almost) transparent
worst_ring, worst_cell = 0.0, ''
for r in range(11):
    for c in range(COUNTS[r]):
        cell = al[r*CELL_H:(r+1)*CELL_H, c*CELL_W:(c+1)*CELL_W]
        if (cell > 0).sum() < 50:
            continue
        ring = np.concatenate([cell[:2].ravel(), cell[-2:].ravel(),
                               cell[:, :2].ravel(), cell[:, -2:].ravel()])
        opaque = (ring > 0).mean() * 100
        if opaque > worst_ring:
            worst_ring, worst_cell = opaque, f'{LANES[r]}[{c}]'
if worst_ring > 20:
    fails.append(f'background baked into sprite — {worst_cell} border ring is {worst_ring:.0f}% opaque')

# 3. chroma lean — check EVERY candidate key, not just the declared one.
#    (Mossback declared cyan; the model drew two strips on MAGENTA. The magenta background got
#     baked in as an opaque block and passed every check that only looked for cyan.)
vis = al > 0
lean = residual(rgb, K, vis)
if lean > 1.0:
    fails.append(f'{lean:.1f}% of sprite pixels still lean toward the declared key {chroma}')

ALL_KEYS = {'#00FF00': (0, 255, 0), '#FF00FF': (255, 0, 255),
            '#00FFFF': (0, 255, 255), '#FFFF00': (255, 255, 0)}

# A key colour is only suspicious if it is NOT part of the pet's own palette.
# (Blip legitimately has a bright yellow antenna — that is art, not a baked background.)
legit = set()
base = f'{pet_dir}/../../assets/mascots/{name}/base.png'
if not os.path.exists(base):
    base = f'{pet_dir}/../../assets/robots/{name}/base.png'
if os.path.exists(base):
    b = np.array(Image.open(base).convert('RGB')).astype(int)
    corner = b[3, 3]
    sprite_px = b[np.abs(b - corner).sum(2) > 90]
    for hexv, kk in ALL_KEYS.items():
        if len(sprite_px) and (np.sqrt(((sprite_px - np.array(kk)) ** 2).sum(1)) < 90).mean() > 0.005:
            legit.add(hexv)

for hexv, kk in ALL_KEYS.items():
    if hexv in legit:
        continue
    d = np.sqrt(((rgb - np.array(kk)) ** 2).sum(2))
    pct = (vis & (d < 90)).sum() / max(vis.sum(), 1) * 100
    if pct > 0.5:
        fails.append(f'{pct:.1f}% of sprite pixels are the chroma colour {hexv} '
                     f'(not in this pet\'s palette) — a background has been baked in')

# 4. cross-lane scale
meds = []
for r in range(9):
    hs = []
    for c in range(COUNTS[r]):
        cell = al[r*CELL_H:(r+1)*CELL_H, c*CELL_W:(c+1)*CELL_W]
        ys, _ = np.where(cell > 0)
        if len(ys):
            hs.append(ys.max() - ys.min() + 1)
    if hs:
        meds.append(float(np.median(hs)))
spread = (max(meds) - min(meds)) / max(meds) * 100 if meds else 0
if spread > 12:
    fails.append(f'pet resizes between animations — {spread:.0f}% lane spread')

# 5. lane population
for r, (lane, n) in enumerate(zip(LANES, COUNTS)):
    used = sum(1 for c in range(n)
               if (al[r*CELL_H:(r+1)*CELL_H, c*CELL_W:(c+1)*CELL_W] > 0).sum() > 50)
    if used < n:
        fails.append(f'lane {lane}: only {used}/{n} frames populated')

status = 'PASS' if not fails else 'FAIL'
print(f'{name:16s} {status}  key={chroma} lean={lean:.1f}% ring={worst_ring:.0f}% spread={spread:.0f}%')
for f in fails:
    print(f'    - {f}')
sys.exit(0 if not fails else 1)
