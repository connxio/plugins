"""Calculate a stable release version and change only the manifest version value."""

import json
import re
import sys
from pathlib import Path


def parse_version(value):
    if not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", value):
        raise ValueError(f"Expected a stable X.Y.Z version, got {value!r}")
    return tuple(map(int, value.split(".")))


def bump_manifest(text, bump, override=""):
    current = json.loads(text)["version"]
    parts = list(parse_version(current))
    if bump not in ("patch", "minor", "major"):
        raise ValueError(f"Unknown bump type: {bump!r}")
    if override:
        target = parse_version(override)
    else:
        index = {"major": 0, "minor": 1, "patch": 2}[bump]
        parts[index] += 1
        parts[index + 1:] = [0] * (2 - index)
        target = tuple(parts)
    if target <= parse_version(current):
        raise ValueError("The new version must exceed the current version")
    version = ".".join(map(str, target))
    pattern = r'("version"\s*:\s*")' + re.escape(current) + r'(")'
    updated, count = re.subn(pattern, lambda match: match[1] + version + match[2], text)
    if count != 1:
        raise ValueError("Expected exactly one matching version field")
    return updated, current, version


if __name__ == "__main__":
    manifest = Path("plugins/connxio/.claude-plugin/plugin.json")
    updated, current, version = bump_manifest(
        manifest.read_bytes().decode("utf-8"), sys.argv[1], sys.argv[2]
    )
    manifest.write_bytes(updated.encode("utf-8"))
    print(f"old_version={current}")
    print(f"new_version={version}")
