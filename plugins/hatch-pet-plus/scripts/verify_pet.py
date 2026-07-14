#!/usr/bin/env python3
"""Independent QA for a packaged pet. Catches what validate_atlas does NOT.

validate_atlas reported ok=true / 0 errors on a pet whose sprite had a solid MAGENTA rectangle
baked into it — because it only checks contamination by the DECLARED chroma key, and the model
had drawn that strip on a different colour entirely. These checks are the backstop.

  1. atlas geometry            1536x2288, 8x11, RGBA
  2. baked-in background       the border ring of each used cell must be transparent
  3. chroma lean               no pixel leaning toward ANY chroma key not in the pet's palette
  4. cross-lane scale          the pet must not resize between animations
  5. duplicate lanes           two animations must never be the same footage
  6. lane population           every lane has its expected frame count

An evolving pet has one atlas PER STAGE, and every stage is a pet in its own right — so each is
put through all six checks. A stage that fails must not ship: an evolution the user cannot reach
until level 10 is exactly the kind of defect that never gets noticed before release.

usage: verify_pet.py <pet-dir> <declared-chroma-hex>
"""
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from despill import residual

CELL_W, CELL_H = 192, 208
COLS = 8
LANES = ['idle', 'running-right', 'running-left', 'waving', 'jumping', 'failed',
         'waiting', 'running', 'review', 'look-9', 'look-10']
# The frames each lane is REQUIRED to have (check 6). The atlas is 8 columns wide and
# the surplus cells are not always empty — a lane's last cell is often a loop-closing
# duplicate of its first. So the pixel checks below sweep all COLS: a baked-in
# background or a chroma halo sitting in column 6 is just as broken, and scanning only
# COUNTS[r] columns would never look at it.
COUNTS = [6, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8]
ALL_KEYS = {'#00FF00': (0, 255, 0), '#FF00FF': (255, 0, 255),
            '#00FFFF': (0, 255, 255), '#FFFF00': (255, 255, 0)}

# How close a pixel must be to a key colour to count as "that key".
#
# This check exists to catch a BAKED-IN BACKGROUND — which is flat, opaque, and the
# EXACT key colour. It is not a check on the pet's palette. The radius used to be 90,
# which is wide enough to swallow real artwork: Volt's butter-yellow body sits 89.8
# from pure yellow, so the gate failed a perfectly good pet for "17.9% of its pixels
# are a baked-in background" — the pixels in question being the creature itself.
#
# At 40, no pet's art is near any key (measured across every pet built so far) except
# blip's genuinely bright yellow antenna, which is what `palette_keys` whitelists. A
# real baked background is at distance 0 and is still caught.
KEY_RADIUS = 40


def palette_keys(pet_dir: str, name: str) -> set:
    """Chroma colours that legitimately appear in this pet's own art.

    Blip has a bright yellow antenna. That is art, not a baked-in background, and an
    earlier version of this check failed the pet for it.
    """
    roots = [
        # The pet's own approved base art, kept by the run. Authoritative, and the only
        # source that exists for a stage build outside the repo — Volt is butter-yellow,
        # so without it the yellow chroma key looks like a baked-in background.
        os.path.expanduser(f'~/.codex/pet-runs/{name}/references/canonical-base.png'),
        f'{pet_dir}/../../assets/mascots/{name}/base.png',
        f'{pet_dir}/../../assets/robots/{name}/base.png',
        f'{pet_dir}/../../examples/elemental/{name}.png',
    ]
    base = next((p for p in roots if os.path.exists(p)), None)
    if base is None:
        return set()

    b = np.array(Image.open(base).convert('RGB')).astype(int)
    sprite_px = b[np.abs(b - b[3, 3]).sum(2) > 90]   # anything that is not the corner background
    if not len(sprite_px):
        return set()
    return {
        hexv for hexv, kk in ALL_KEYS.items()
        if (np.sqrt(((sprite_px - np.array(kk)) ** 2).sum(1)) < KEY_RADIUS).mean() > 0.005
    }


def verify_sheet(path: str, chroma: str, legit: set, label: str) -> list:
    K = np.array([int(chroma[1:3], 16), int(chroma[3:5], 16), int(chroma[5:7], 16)])
    im = Image.open(path).convert('RGBA')
    a = np.array(im).astype(int)
    rgb, al = a[:, :, :3], a[:, :, 3]
    fails = []

    # 1. geometry
    if im.size != (1536, 2288):
        fails.append(f'atlas is {im.size[0]}x{im.size[1]}, expected 1536x2288')

    # 2. baked-in background: the 2px border ring of a used cell must be (almost) transparent
    worst_ring, worst_cell = 0.0, ''
    for r in range(11):
        for c in range(COLS):
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

    # 3. chroma lean — the declared key, then EVERY other key.
    #    (Mossback declared cyan; the model drew two strips on MAGENTA. That magenta background got
    #     baked in as an opaque block and passed every check that only looked for cyan.)
    vis = al > 0
    lean = residual(rgb, K, vis)
    if lean > 1.0:
        fails.append(f'{lean:.1f}% of sprite pixels still lean toward the declared key {chroma}')

    for hexv, kk in ALL_KEYS.items():
        if hexv in legit:
            continue
        d = np.sqrt(((rgb - np.array(kk)) ** 2).sum(2))
        pct = (vis & (d < KEY_RADIUS)).sum() / max(vis.sum(), 1) * 100
        if pct > 0.5:
            fails.append(f'{pct:.1f}% of sprite pixels are the chroma colour {hexv} '
                         f"(not in this pet's palette) — a background has been baked in")

    # 4. cross-lane scale — the extractor fits each row to its OWN bbox, so a tall jump arc
    #    shrinks the pet and it visibly halves in size the moment the user hovers it.
    #    Measured over the frames the host actually PLAYS (COUNTS), not the whole row: a
    #    lane's surplus cell is a loop-closing duplicate of its first frame, and folding it
    #    into the median skews the comparison without describing anything the user sees.
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

    # 5. DUPLICATE LANES — two animations must never be the same footage.
    #    Parallel codex processes share ~/.codex/generated_images/, so one can copy ANOTHER's
    #    output. It happened three times and nothing caught it: kiln's `waving` was byte-identical
    #    to `review`, bot-plush's `failed` to `jumping`, mossback's `failed` to `waiting`.
    by_hash = {}
    for r in range(9):
        frames = [a[r*CELL_H:(r+1)*CELL_H, c*CELL_W:(c+1)*CELL_W].tobytes()
                  for c in range(COLS)]
        by_hash.setdefault(hashlib.md5(b''.join(frames)).hexdigest(), []).append(LANES[r])
    for group in by_hash.values():
        if len(group) > 1:
            fails.append(f'lanes {" and ".join(group)} are IDENTICAL — a parallel run copied '
                         f"another process's image")

    # 6. lane population
    for r, (lane, n) in enumerate(zip(LANES, COUNTS)):
        used = sum(1 for c in range(n)
                   if (al[r*CELL_H:(r+1)*CELL_H, c*CELL_W:(c+1)*CELL_W] > 0).sum() > 50)
        if used < n:
            fails.append(f'lane {lane}: only {used}/{n} frames populated')

    status = 'PASS' if not fails else 'FAIL'
    print(f'{label:22s} {status}  key={chroma} lean={lean:.1f}% ring={worst_ring:.0f}% spread={spread:.0f}%')
    for f in fails:
        print(f'    - {f}')
    return fails


def main() -> None:
    pet_dir, chroma = sys.argv[1], sys.argv[2]
    name = os.path.basename(pet_dir.rstrip('/'))
    legit = palette_keys(pet_dir, name)

    # An evolving pet has one atlas per stage. Verify every one of them.
    manifest = os.path.join(pet_dir, 'pet.json')
    sheets = []
    if os.path.exists(manifest):
        pet = json.load(open(manifest))
        for i, st in enumerate(pet.get('stages') or [], start=1):
            sheets.append((os.path.join(pet_dir, st['spritesheetPath']),
                           f'{name}/{st.get("name", f"stage-{i}")}'))
    if not sheets:
        sheets = [(os.path.join(pet_dir, 'spritesheet.webp'), name)]

    fails = 0
    for path, label in sheets:
        if not os.path.exists(path):
            print(f'{label:22s} FAIL  missing sheet {path}')
            fails += 1
            continue
        fails += bool(verify_sheet(path, chroma, legit, label))

    sys.exit(0 if not fails else 1)


if __name__ == '__main__':
    main()
