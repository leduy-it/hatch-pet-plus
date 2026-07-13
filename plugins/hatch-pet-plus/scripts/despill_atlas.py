#!/usr/bin/env python3
"""Final atlas pass: universal despill + lossless WebP. usage: despill_atlas.py <key> <chroma>"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from despill import despill, residual

pet, chroma = sys.argv[1], sys.argv[2]
run = os.path.expanduser(f'~/.codex/pet-runs/{pet}')
p = f'{run}/final/spritesheet.png'
if not os.path.exists(p):
    raise SystemExit('  no atlas to finalise')

K = np.array([int(chroma[1:3], 16), int(chroma[3:5], 16), int(chroma[5:7], 16)])

a = np.array(Image.open(p).convert('RGBA')).astype(int)
rgb, al = a[:, :, :3], a[:, :, 3]
vis = al > 0

before = residual(rgb, K, vis)
rgb = despill(rgb, K, vis)
after = residual(rgb, K, vis)

a[:, :, :3] = rgb
a[al == 0] = 0                       # transparency invariant: no RGB residue under alpha=0

im = Image.fromarray(a.astype(np.uint8), 'RGBA')
im.save(p)
im.save(f'{run}/final/spritesheet.webp', lossless=True, exact=True)   # lossy would corrupt alpha RGB

print(f'  atlas {im.size[0]}x{im.size[1]}  key-lean {before:.1f}% -> {after:.1f}%')
