#!/usr/bin/env python3
"""Register separated alpha silhouettes at a shared scale and vertical origin."""
import argparse
import json
from pathlib import Path
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--frames', type=int, default=8)
parser.add_argument('--align-ground', action='store_true', help='Register grounded poses by their alpha baseline; never use for jumping clips')
args = parser.parse_args()
im = Image.open(args.source).convert('RGBA')
alpha = im.getchannel('A')
# Native-alpha cleanup once: discard only near-invisible generation residue.
alpha = alpha.point(lambda value: 0 if value < 8 else value)
im.putalpha(alpha)
runs = []
start = None
for x in range(im.width):
    occupied = alpha.crop((x, 0, x + 1, im.height)).getextrema()[1] > 32
    if occupied and start is None:
        start = x
    if not occupied and start is not None:
        runs.append((start, x))
        start = None
if start is not None:
    runs.append((start, im.width))
assert len(runs) == args.frames, f'Expected {args.frames} separated silhouettes; found {len(runs)}'
bounds = alpha.getbbox()
assert bounds
upper, lower = bounds[1], bounds[3]
scale = min(176 / max(end - begin + 8 for begin, end in runs), 188 / (lower - upper))
out = Image.new('RGBA', (192 * args.frames, 208))
frames = []
for i, (begin, end) in enumerate(runs):
    left = max(0, begin - 4)
    right = min(im.width, end + 4)
    frame_lower = lower
    if args.align_ground:
        local_bounds = alpha.crop((left, 0, right, im.height)).point(lambda v: 255 if v > 32 else 0).getbbox()
        frame_lower = local_bounds[3] + 2
    frame = im.crop((left, upper, right, frame_lower))
    frame = frame.resize((round(frame.width * scale), round(frame.height * scale)), Image.Resampling.LANCZOS)
    out.alpha_composite(frame, (192 * i + (192 - frame.width) // 2, 200 - frame.height))
    frames.append(out.crop((192 * i, 0, 192 * (i + 1), 208)))
args.output.parent.mkdir(parents=True, exist_ok=True)
out.save(args.output, lossless=True)
frames[0].save(args.output.with_suffix('.preview.gif'), save_all=True, append_images=frames[1:], duration=120, loop=0, disposal=2)
args.output.with_suffix('.registration.json').write_text(json.dumps({'source': str(args.source), 'runs': runs, 'sharedScale': scale, 'verticalBounds': [upper, lower], 'alignGround': args.align_ground}, indent=2) + '\n')
print(json.dumps({'output': str(args.output), 'size': out.size, 'frames': len(frames)}))
