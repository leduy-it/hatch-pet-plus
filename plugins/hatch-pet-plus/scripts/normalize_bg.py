#!/usr/bin/env python3
"""Force every decoded strip onto the DECLARED chroma key, whatever the model actually drew.

THE BUG
  Mossback's run declared #00FFFF (cyan). The model drew `idle` and `running-left` on MAGENTA
  anyway. The extractor keyed out cyan, so the magenta background stayed OPAQUE and was baked
  into the sprite as a solid rectangle.

  Nothing caught it. validate_atlas said ok=true / 0 errors, because it only checks for
  contamination by the DECLARED key — and magenta is not cyan. The contact sheet looked fine.

THE FIX
  Never trust the declared key. Detect each strip's ACTUAL background from its corners, and
  recolour it to the declared key. Then everything downstream is consistent no matter what the
  model did.

usage: normalize_bg.py <pet-key> <declared-chroma-hex>
"""
import os
import sys

import numpy as np
from PIL import Image

pet, chroma = sys.argv[1], sys.argv[2]
run = os.path.expanduser(f'~/.codex/pet-runs/{pet}')
KEY = np.array([int(chroma[1:3], 16), int(chroma[3:5], 16), int(chroma[5:7], 16)])

STATES = ['idle', 'running-right', 'running-left', 'waving', 'jumping', 'failed',
          'waiting', 'running', 'review', 'look-row-9', 'look-row-10']

fixed = []
for st in STATES:
    p = f'{run}/decoded/{st}.png'
    if not os.path.exists(p):
        continue
    a = np.array(Image.open(p).convert('RGB')).astype(int)
    h, w = a.shape[:2]

    # the real background = the dominant corner colour
    corners = np.array([a[3, 3], a[3, w - 4], a[h - 4, 3], a[h - 4, w - 4]])
    bg = np.median(corners, axis=0).astype(int)

    if np.abs(bg - KEY).sum() <= 40:
        continue                        # already on the declared key

    # recolour everything close to the ACTUAL background -> the declared key
    d = np.sqrt(((a - bg) ** 2).sum(2))
    mask = d <= 110
    out = a.copy()
    out[mask] = KEY
    Image.fromarray(out.astype(np.uint8)).save(p)
    fixed.append(f'{st} {tuple(bg)}')

if fixed:
    print(f'  background normalised -> {chroma}: ' + ', '.join(fixed))
else:
    print(f'  all strips already on {chroma}')
