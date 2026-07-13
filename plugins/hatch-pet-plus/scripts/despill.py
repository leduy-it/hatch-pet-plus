#!/usr/bin/env python3
"""Universal chroma despill — works for ANY key colour, including 2-channel keys like magenta.

The bug this fixes: clamping only the key's single dominant channel works for green (#00FF00)
but NOT for magenta (#FF00FF), where BOTH red and blue are high. Clamping only red leaves blue
elevated, so the spill survives as a violet fringe.

Method: measure how far each pixel leans TOWARD the key, and pull it back along that axis.
  spill = min(pixel[c] - pixel[low])  over the key's HIGH channels
        (low = the mean of the key's LOW channels)
  then subtract `spill` from every HIGH channel.

For green (high=[G], low=[R,B]):    g -= max(0, g - max(r,b))   -> the classic green despill
For magenta (high=[R,B], low=[G]):  r,b -= max(0, min(r,b) - g) -> removes magenta without
                                     destroying a legitimately blue or red sprite.
"""
import numpy as np


def despill(rgb, key, kept):
    """rgb: HxWx3 int array. key: (r,g,b). kept: HxW bool — pixels the extractor will KEEP."""
    rgb = rgb.astype(int).copy()
    key = np.asarray(key, dtype=int)

    hi = [i for i in range(3) if key[i] >= 128]   # channels the key is strong in
    lo = [i for i in range(3) if key[i] < 128]
    if not hi or not lo:
        return rgb

    base = rgb[:, :, lo].max(axis=2)              # the "non-key" reference level
    lean = rgb[:, :, hi].min(axis=2) - base       # how far the pixel leans toward the key
    spill = np.clip(lean, 0, None)
    spill = np.where(kept, spill, 0)

    for c in hi:
        rgb[:, :, c] = np.clip(rgb[:, :, c] - spill, 0, 255)
    return rgb


def residual(rgb, key, mask):
    """% of masked pixels still leaning toward the key."""
    key = np.asarray(key, dtype=int)
    hi = [i for i in range(3) if key[i] >= 128]
    lo = [i for i in range(3) if key[i] < 128]
    if not hi or not lo or mask.sum() == 0:
        return 0.0
    px = rgb[mask].astype(int)
    lean = px[:, hi].min(axis=1) - px[:, lo].max(axis=1)
    return float((lean > 25).mean() * 100)
