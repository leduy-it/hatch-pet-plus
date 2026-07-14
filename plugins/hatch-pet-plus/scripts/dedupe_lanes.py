#!/usr/bin/env python3
"""Detect lanes that are byte-identical to a sibling, and delete the duplicates so they regenerate.

THE BUG
  Parallel `codex exec` processes all write into the shared ~/.codex/generated_images/, so a process
  can copy ANOTHER process's output and report success with a byte count. It happened three times
  and shipped:
      kiln/waving.png      == kiln/review.png
      bot-plush/failed.png == bot-plush/jumping.png
      mossback/failed.png  == mossback/waiting.png
  Two different animations playing the exact same footage. Nothing caught it — not validate_atlas,
  not the contact sheet, not the preview GIFs.

usage: dedupe_lanes.py <run-dir> [--delete]
  without --delete: report only (exit 1 if duplicates found)
  with --delete:    remove the duplicate strips so the runner regenerates them
"""
import hashlib
import os
import sys
from collections import defaultdict

run = sys.argv[1]
delete = '--delete' in sys.argv

STATES = ['idle', 'running-right', 'running-left', 'waving', 'jumping', 'failed',
          'waiting', 'running', 'review', 'look-row-9', 'look-row-10']

# running-left is a legitimate deterministic mirror of running-right, but it is FLIPPED,
# so it should never be byte-identical to it. Everything here must be unique.
by_hash = defaultdict(list)
for st in STATES:
    p = f'{run}/decoded/{st}.png'
    if not os.path.exists(p):
        continue
    by_hash[hashlib.md5(open(p, 'rb').read()).hexdigest()].append(st)

dupes = {h: v for h, v in by_hash.items() if len(v) > 1}
if not dupes:
    print('  lanes all unique')
    sys.exit(0)

pet = os.path.basename(run.rstrip('/'))
for h, lanes in dupes.items():
    print(f'  {pet}: {" == ".join(lanes)}  <- a parallel run copied another process\'s image')
    if delete:
        # keep the first, drop the rest so they get regenerated
        for st in lanes[1:]:
            for f in (f'{run}/decoded/{st}.png', f'{run}/decoded-raw/{st}.png'):
                if os.path.exists(f):
                    os.remove(f)
            print(f'    deleted {st} — will regenerate')

sys.exit(1)
