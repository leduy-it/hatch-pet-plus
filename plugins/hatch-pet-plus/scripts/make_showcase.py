#!/usr/bin/env python3
"""Build the animated showcases for every completed pet.

Per pet:  pets/<key>/demo.gif        all 9 lanes side by side
Global :  examples/showcase-all-idle.gif   every pet idling, side by side
          examples/showcase-lanes.gif      one pet, every lane labelled
"""
from PIL import Image, ImageSequence
import os, glob, json

REPO = os.path.expanduser('~/Desktop/hatch-pet-plus')
PETS = f'{REPO}/pets'
EX   = f'{REPO}/examples'
W, H = 192, 208
LANES = ['idle','waving','jumping','running-right','running-left','running','waiting','review','failed']


def frames(path):
    return [f.convert('RGBA') for f in ImageSequence.Iterator(Image.open(path))]


def save_gif(fs, path, duration=140):
    if not fs:
        return
    pal = [f.convert('P', palette=Image.ADAPTIVE, colors=255) for f in fs]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=duration,
                loop=0, disposal=2, transparency=255)


def pet_demo(key):
    """All lanes of one pet, side by side."""
    prev = f'{PETS}/{key}/previews'
    strips, names = [], []
    for lane in LANES:
        p = f'{prev}/{lane}.gif'
        if os.path.exists(p):
            strips.append(frames(p)); names.append(lane)
    if not strips:
        return None
    n = max(len(s) for s in strips)
    pad = 6
    out_w = len(strips)*W + pad*(len(strips)+1)
    out_h = H + pad*2
    out = []
    for i in range(n):
        c = Image.new('RGBA', (out_w, out_h), (255,255,255,255))
        for j, s in enumerate(strips):
            c.alpha_composite(s[i % len(s)].resize((W,H), Image.NEAREST), (pad + j*(W+pad), pad))
        out.append(c)
    save_gif(out, f'{PETS}/{key}/demo.gif')
    return names


def all_idle(keys):
    """Every pet idling, side by side."""
    strips, used = [], []
    for k in keys:
        p = f'{PETS}/{k}/previews/idle.gif'
        if os.path.exists(p):
            strips.append(frames(p)); used.append(k)
    if not strips:
        return []
    n = max(len(s) for s in strips)
    pad = 6
    out_w = len(strips)*W + pad*(len(strips)+1)
    out_h = H + pad*2
    out = []
    for i in range(n):
        c = Image.new('RGBA', (out_w, out_h), (250,251,252,255))
        for j, s in enumerate(strips):
            c.alpha_composite(s[i % len(s)].resize((W,H), Image.NEAREST), (pad + j*(W+pad), pad))
        out.append(c)
    save_gif(out, f'{EX}/showcase-all-idle.gif', duration=200)
    return used


if __name__ == '__main__':
    keys = sorted(d for d in os.listdir(PETS)
                  if os.path.isdir(f'{PETS}/{d}') and os.path.exists(f'{PETS}/{d}/spritesheet.webp'))
    print(f'{len(keys)} complete pets: {", ".join(keys)}\n')
    for k in keys:
        lanes = pet_demo(k)
        if lanes:
            print(f'  {k:18s} demo.gif  ({len(lanes)} lanes)')
    used = all_idle(keys)
    print(f'\n  showcase-all-idle.gif  ({len(used)} pets)')
