from __future__ import annotations

from typing import Any


def compare(left: dict[str, Any], right: dict[str, Any]) -> dict[str, list[str]]:
    left_keys = set(left)
    right_keys = set(right)
    return {
        "added": sorted(right_keys - left_keys),
        "removed": sorted(left_keys - right_keys),
        "shared": sorted(left_keys & right_keys),
    }


def health() -> dict[str, str]:
    return {"status": "ok"}
