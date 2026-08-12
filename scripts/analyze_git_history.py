#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_utils import resolve_root, write_json


def run_git(root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    return completed.stdout


def collect(root: Path | str, max_commits: int = 500) -> dict[str, Any]:
    root_path = resolve_root(root)
    try:
        inside = run_git(root_path, ["rev-parse", "--is-inside-work-tree"]).strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        return {
            "collector": "analyze_git_history", "root": str(root_path), "available": False,
            "error": f"{type(exc).__name__}: {exc}",
        }
    if inside != "true":
        return {
            "collector": "analyze_git_history", "root": str(root_path), "available": False,
            "error": "Not a Git work tree",
        }

    head = run_git(root_path, ["rev-parse", "HEAD"]).strip()
    branch = run_git(root_path, ["rev-parse", "--abbrev-ref", "HEAD"]).strip()
    raw = run_git(root_path, [
        "log", f"--max-count={max_commits}", "--format=%H%x09%an%x09%ae%x09%aI",
        "--numstat", "--no-renames",
    ])

    commits: list[dict[str, Any]] = []
    authors: Counter[str] = Counter()
    churn: dict[str, dict[str, int]] = defaultdict(lambda: {"added": 0, "deleted": 0, "touches": 0})
    current: dict[str, Any] | None = None

    for line in raw.splitlines():
        if not line:
            continue
        fields = line.split("\t")
        if len(fields) == 4 and len(fields[0]) >= 7 and "T" in fields[3]:
            sha, author, email, authored_at = fields
            current = {
                "sha": sha, "author": author, "email": email, "authored_at": authored_at,
                "files_changed": 0, "added": 0, "deleted": 0,
            }
            commits.append(current)
            authors[f"{author} <{email}>"] += 1
            continue
        if current is None or len(fields) != 3:
            continue
        added_raw, deleted_raw, path = fields
        if not path:
            continue
        added = int(added_raw) if added_raw.isdigit() else 0
        deleted = int(deleted_raw) if deleted_raw.isdigit() else 0
        current["files_changed"] += 1
        current["added"] += added
        current["deleted"] += deleted
        churn[path]["added"] += added
        churn[path]["deleted"] += deleted
        churn[path]["touches"] += 1

    velocity = {"last_7_days": 0, "last_30_days": 0, "last_90_days": 0}
    now = datetime.now(timezone.utc)
    for commit in commits:
        try:
            timestamp = datetime.fromisoformat(commit["authored_at"].replace("Z", "+00:00"))
        except ValueError:
            continue
        age_days = (now - timestamp.astimezone(timezone.utc)).total_seconds() / 86400
        if age_days <= 7:
            velocity["last_7_days"] += 1
        if age_days <= 30:
            velocity["last_30_days"] += 1
        if age_days <= 90:
            velocity["last_90_days"] += 1

    hotspots = []
    for path, values in churn.items():
        hotspots.append({"path": path, **values, "churn": values["added"] + values["deleted"]})
    hotspots.sort(key=lambda item: (-item["churn"], -item["touches"], item["path"]))

    author_rows = [{"author": author, "commits": count} for author, count in authors.most_common()]
    bus_factor_signal = None
    if commits and author_rows:
        top_share = author_rows[0]["commits"] / len(commits)
        bus_factor_signal = {
            "top_author_commit_share": round(top_share, 4),
            "unique_authors": len(author_rows),
            "concentration": "high" if top_share >= 0.75 else "medium" if top_share >= 0.5 else "low",
        }

    return {
        "collector": "analyze_git_history", "root": str(root_path), "available": True,
        "head": head, "branch": branch, "sampled_commits": len(commits),
        "latest_commit_at": commits[0]["authored_at"] if commits else None,
        "oldest_sampled_commit_at": commits[-1]["authored_at"] if commits else None,
        "velocity": velocity, "authors": author_rows, "bus_factor_signal": bus_factor_signal,
        "hotspots": hotspots[:50], "recent_commits": commits[:30],
        "limitations": [
            f"History is limited to the most recent {max_commits} commits.",
            "Commit count and churn are activity signals, not direct quality or completion metrics.",
            "Author concentration is only a bus-factor signal and requires contextual interpretation.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect Git history, churn, velocity, and concentration signals.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--max-commits", type=int, default=500)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    result = collect(args.root, max_commits=max(1, args.max_commits))
    if args.output:
        write_json(args.output, result)
        print(f"Wrote Git history analysis to {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
