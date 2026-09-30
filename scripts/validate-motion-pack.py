#!/usr/bin/env python3
"""Validate extension geometry and alpha; visual QA is a separate requirement."""
import argparse
import json
from pathlib import Path
from PIL import Image


def validate(path):
    manifest = json.loads(path.read_text())
    assert manifest['version'] == 1, 'Unsupported manifest version'
    assert isinstance(manifest['petId'], str) and manifest['petId'], 'Missing petId'
    width, height = manifest['cell']['width'], manifest['cell']['height']
    assert (width, height) == (192, 208), 'Expected 192 x 208 cells'
    clips = manifest['clips']
    assert isinstance(clips, dict) and clips, 'No accepted clips'
    for name, clip in clips.items():
        filename = clip['file']
        assert isinstance(filename, str) and Path(filename).name == filename and filename not in ('.', '..'), f'{name}: unsafe file path'
        count = clip['frames']
        assert type(count) is int and 1 <= count <= 32, f'{name}: invalid frame count'
        assert type(clip['frameMs']) is int and 40 <= clip['frameMs'] <= 5000, f'{name}: invalid frame timing'
        assert type(clip['loop']) is bool, f'{name}: missing loop flag'
        image = Image.open(path.parent / filename).convert('RGBA')
        assert image.size == (width * count, height), f'{name}: invalid dimensions {image.size}'
        for index in range(count):
            alpha = image.crop((index * width, 0, (index + 1) * width, height)).getchannel('A')
            bounds = alpha.getbbox()
            assert bounds, f'{name}/{index}: empty frame'
            assert bounds[0] > 0 and bounds[1] > 0 and bounds[2] < width and bounds[3] < height, f'{name}/{index}: artwork touches frame edge'
    return {'ok': True, 'petId': manifest['petId'], 'clips': len(clips), 'visualQA': 'required separately'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.manifest)))
