#!/usr/bin/env python3
"""Despill every decoded row strip, before frame extraction. usage: despill_strips.py <key> <chroma>"""
import os
import shutil
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from despill import despill, residual

pet, chroma = sys.argv[1], sys.argv[2]
run = os.path.expanduser(f'~/.codex/pet-runs/{pet}')
K = np.array([int(chroma[1:3], 16), int(chroma[3:5], 16), int(chroma[5:7], 16)])
T = 96.0                      # must match extract_strip_frames.py --key-threshold

STATES = ['idle', 'running-right', 'running-left', 'waving', 'jumping', 'failed',
          'waiting', 'running', 'review', 'look-row-9', 'look-row-10']

raw = f'{run}/decoded-raw'
os.makedirs(raw, exist_ok=True)

worst = 0.0
for st in STATES:
    p = f'{run}/decoded/{st}.png'
    b = f'{raw}/{st}.png'
    if not os.path.exists(p):
        continue
    if not os.path.exists(b):
        shutil.copy2(p, b)          # keep a pristine copy so this is re-runnable

    # read the CURRENT strip, not the pristine one — stage2 has already restored it from
    # decoded-raw and then normalised its background onto the declared key. Reading `raw`
    # here would silently throw that correction away.
    a = np.array(Image.open(p).convert('RGB')).astype(int)
    kept = np.sqrt(((a - K) ** 2).sum(2)) > T      # what the extractor will keep
    before = residual(a, K, kept)
    out = despill(a, K, kept)
    after = residual(out, K, kept)
    worst = max(worst, after)
    Image.fromarray(out.astype(np.uint8)).save(p)

print(f'  strips despilled (worst residual {worst:.1f}%)')
