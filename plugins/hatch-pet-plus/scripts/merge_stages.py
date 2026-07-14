#!/usr/bin/env python3
"""Merge separately-built pets into ONE evolving pet.

Each evolution stage is a full 8x11 atlas — Codex has no notion of "the same pet,
one level up", so every stage is built by the ordinary pipeline as if it were its
own pet. This collapses those builds into a single pet directory:

    pets/volt/
      pet.json          stages[] + attributes
      stage-1.webp      <- pets/volt-s1/spritesheet.webp
      stage-2.webp      <- pets/volt-s2/spritesheet.webp
      contact-sheet-1.png, contact-sheet-2.png
      validation-1.json, validation-2.json
      previews/stage-1/*.gif, previews/stage-2/*.gif

`spritesheetPath` still points at stage 1, so a host that knows nothing about
stages — Codex itself, and agentpet upstream — loads the pet and shows its first
form, exactly as before.

    merge_stages.py <out-dir> <spec.json>
"""
import json
import shutil
import sys
from pathlib import Path


def die(msg: str) -> None:
    print(f"merge_stages: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    out = Path(sys.argv[1])
    spec = json.loads(Path(sys.argv[2]).read_text())

    stages = spec["stages"]
    if not stages:
        die("spec has no stages")

    out.mkdir(parents=True, exist_ok=True)
    manifest_stages = []

    for n, st in enumerate(stages, start=1):
        src = Path(st["buildDir"]).expanduser()
        sheet = src / "spritesheet.webp"
        if not sheet.is_file():
            die(f"stage {n} has no spritesheet at {sheet} — the build did not finish")

        shutil.copy2(sheet, out / f"stage-{n}.webp")
        for name, dst in (
            ("contact-sheet.png", f"contact-sheet-{n}.png"),
            ("validation.json", f"validation-{n}.json"),
        ):
            if (src / name).is_file():
                shutil.copy2(src / name, out / dst)

        prev_src, prev_dst = src / "previews", out / "previews" / f"stage-{n}"
        if prev_src.is_dir():
            if prev_dst.exists():
                shutil.rmtree(prev_dst)
            shutil.copytree(prev_src, prev_dst)

        entry = {
            "minLevel": st["minLevel"],
            "name": st["name"],
            "spritesheetPath": f"stage-{n}.webp",
        }
        if st.get("attributes"):
            entry["attributes"] = st["attributes"]
        manifest_stages.append(entry)

    pet = {
        "id": spec["id"],
        "displayName": stages[0]["name"],
        "description": spec.get("description", f"{stages[0]['name']} — an evolving Codex pet."),
        "spriteVersionNumber": 2,
        # Stage one, so hosts that do not understand `stages` still work.
        "spritesheetPath": "stage-1.webp",
        "stages": manifest_stages,
    }
    if spec.get("type"):
        pet["type"] = spec["type"]

    (out / "pet.json").write_text(json.dumps(pet, indent=2, ensure_ascii=False) + "\n")

    chain = " -> ".join(f"{s['name']}(L{s['minLevel']})" for s in manifest_stages)
    print(f"merged {spec['id']}: {chain}  -> {out}")


if __name__ == "__main__":
    main()
