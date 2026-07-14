#!/usr/bin/env python3
"""Print the Codex plan quota used, as a percentage.

Every pet is ~11 image generations and the weekly window is shared with the
user's ordinary work, so the batch runner checks this before starting each pet
and stops rather than burning the week's allowance on sprites.

The number is not exposed by any API — it is recorded in the session rollouts:
    ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl
      payload.type == "token_count" -> rate_limits.primary.used_percent
Prints the most recent reading found. Prints -1 if there is none.
"""
import glob
import json
import os
from datetime import datetime, timedelta


def main() -> None:
    paths: list[str] = []
    day = datetime.now()
    for back in range(3):  # today plus a couple of days back, newest last
        d = day - timedelta(days=back)
        paths = sorted(glob.glob(os.path.expanduser(
            f"~/.codex/sessions/{d:%Y/%m/%d}/rollout-*.jsonl"))) + paths

    latest = None
    for path in paths:  # oldest file first, so the last hit wins
        try:
            with open(path) as fh:
                for line in fh:
                    try:
                        payload = json.loads(line).get("payload", {})
                    except json.JSONDecodeError:
                        continue
                    if payload.get("type") != "token_count":
                        continue
                    primary = (payload.get("rate_limits") or {}).get("primary") or {}
                    if primary.get("used_percent") is not None:
                        latest = float(primary["used_percent"])
        except OSError:
            continue

    print(f"{latest:.1f}" if latest is not None else "-1")


if __name__ == "__main__":
    main()
