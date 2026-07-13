#!/usr/bin/env python3
"""Give each look-row slot breathing room, so the atlas assembler will accept it.

THE BUG
  assemble_extended_atlas rejects a look row when the sprite has pixels near its final cell edge:
    "look direction 000 has 113 non-transparent pixels near its final cell edge — resynthesize"
  bot-pixel's robot was drawn with its ARMS TOUCHING the left and right edges of every slot
  (measured horizontal margin: 0px). Re-rolling the row did not help — the model keeps filling
  the slot width.

THE FIX
  Deterministically shrink and recentre the sprite inside each slot so it never reaches the edge.

usage: pad_look_row.py <strip.png> <chroma-hex> [max-fill]
"""
import sys

import numpy as np
from PIL import Image

path = sys.argv[1]
chroma = sys.argv[2]
MAX_FILL = float(sys.argv[3]) if len(sys.argv) > 3 else 0.78   # sprite may fill this much of a slot

K = np.array([int(chroma[1:3], 16), int(chroma[3:5], 16), int(chroma[5:7], 16)])

im = Image.open(path).convert('RGB')
a = np.array(im).astype(int)
h, w = a.shape[:2]
sw = w // 8

out = Image.new('RGB', (w, h), tuple(int(x) for x in K))
changed = []

for i in range(8):
    x0 = i * sw
    slot = im.crop((x0, 0, x0 + sw, h))
    sa = np.array(slot).astype(int)
    mask = np.sqrt(((sa - K) ** 2).sum(2)) > 96
    ys, xs = np.where(mask)
    if len(ys) == 0:
        continue

    sprite = slot.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    sw_px, sh_px = sprite.size

    k = min(MAX_FILL * sw / sw_px, MAX_FILL * h / sh_px, 1.0)
    if k < 0.999:
        sprite = sprite.resize((max(1, int(sw_px * k)), max(1, int(sh_px * k))), Image.LANCZOS)
        changed.append(f'{i+1}(x{k:.2f})')

    # recentre horizontally; keep the feet where they were (scaled)
    px = x0 + (sw - sprite.width) // 2
    baseline = ys.max()
    py = int(baseline * k) - sprite.height
    py = max(0, min(py, h - sprite.height))
    out.paste(sprite, (px, py))

out.save(path)
print(f"  padded {path.split('/')[-1]}: slots {', '.join(changed) if changed else '(none needed)'}")
