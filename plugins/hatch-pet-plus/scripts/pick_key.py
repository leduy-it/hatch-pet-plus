#!/usr/bin/env python3
"""Pick the chroma key furthest from a pet's actual palette, and recolour its base
background to that key so base art and row art agree.

Why: prepare_pet_run auto-picked MAGENTA for Blip — a blue pet with a violet outline.
The key sat right next to the sprite's own colours, so the spill couldn't be separated
from the art, leaving a violet fringe on 50% of edge pixels.

usage: pick_key.py <base.png>            -> prints the best key hex
       pick_key.py <base.png> --rewrite  -> also recolours the base bg to that key
"""
import sys
import numpy as np
from PIL import Image

CANDIDATES = {
    '#00FF00': (0, 255, 0),      # green
    '#FF00FF': (255, 0, 255),    # magenta
    '#00FFFF': (0, 255, 255),    # cyan
    '#FFFF00': (255, 255, 0),    # yellow
}


def sprite_mask(a):
    """Flood the flat background in from the corners."""
    h, w = a.shape[:2]
    corner = a[2, 2].astype(int)
    d = np.abs(a.astype(int) - corner).sum(2)
    return d > 90            # True = sprite


def pick(path):
    a = np.array(Image.open(path).convert('RGB'))
    m = sprite_mask(a)
    px = a[m].astype(int)
    if len(px) == 0:
        return '#00FF00', {}
    scores = {}
    for hexv, key in CANDIDATES.items():
        d = np.sqrt(((px - np.array(key)) ** 2).sum(1))
        # the worst case matters: how close does the CLOSEST sprite pixel get to the key?
        scores[hexv] = float(np.percentile(d, 1))
    best = max(scores, key=scores.get)
    return best, scores


def rewrite(path, hexv):
    a = np.array(Image.open(path).convert('RGB'))
    m = sprite_mask(a)
    key = CANDIDATES[hexv]
    out = a.copy()
    out[~m] = key
    Image.fromarray(out).save(path)


if __name__ == '__main__':
    p = sys.argv[1]
    best, scores = pick(p)
    if '--rewrite' in sys.argv:
        rewrite(p, best)
    if '--verbose' in sys.argv:
        for k, v in sorted(scores.items(), key=lambda x: -x[1]):
            print(f"  {k}  min-distance-to-sprite = {v:6.1f}{'   <- chosen' if k == best else ''}",
                  file=sys.stderr)
    print(best)
