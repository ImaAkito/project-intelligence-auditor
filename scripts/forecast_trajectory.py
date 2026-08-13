#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from audit_utils import load_json, write_json

DEFAULT_SCORE_METRICS = (
    'confirmed_completion',
    'estimated_completion',
    'project_health',
    'prototype_readiness',
    'mvp_readiness',
    'commercial_readiness',
    'production_readiness',
    'scale_readiness',
    'research_readiness',
    'confidence',
)


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace('Z', '+00:00')
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def linear_trend(points: list[tuple[datetime, float]], *, target: float = 80.0) -> dict[str, Any] | None:
    if len(points) < 2:
        return None
    points = sorted(points, key=lambda item: item[0])
    start = points[0][0]
    xs = [(timestamp - start).total_seconds() / 86400.0 for timestamp, _ in points]
    ys = [value for _, value in points]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    variance_x = sum((x - mean_x) ** 2 for x in xs)
    if variance_x <= 0:
        return None
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / variance_x
    intercept = mean_y - slope * mean_x
    predictions = [intercept + slope * x for x in xs]
    ss_res = sum((y - predicted) ** 2 for y, predicted in zip(ys, predictions))
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    r2 = None if ss_tot <= 0 else max(0.0, min(1.0, 1.0 - ss_res / ss_tot))
    monthly_delta = slope * 30.4375
    latest_delta = ys[-1] - ys[-2]

    if abs(monthly_delta) < 1.0:
        direction = 'flat'
    elif monthly_delta > 0:
        direction = 'improving'
    else:
        direction = 'regressing'

    eta_days: float | None = None
    eta_timestamp: str | None = None
    can_estimate_eta = len(points) >= 3 and slope > 0 and r2 is not None and r2 >= 0.35 and ys[-1] < target
    if can_estimate_eta:
        target_x = (target - intercept) / slope
        latest_x = xs[-1]
        if target_x > latest_x:
            eta_days = target_x - latest_x
            eta_timestamp = datetime.fromtimestamp(
                points[-1][0].timestamp() + eta_days * 86400.0,
                tz=timezone.utc,
            ).isoformat()

    return {
        'points': len(points),
        'series': [
            {'timestamp': timestamp.isoformat(), 'value': round(value, 2)}
            for timestamp, value in points
        ],
        'first_value': round(ys[0], 2),
        'latest_value': round(ys[-1], 2),
        'latest_delta': round(latest_delta, 2),
        'slope_per_day': round(slope, 4),
        'delta_per_30d': round(monthly_delta, 2),
        'direction': direction,
        'r2': None if r2 is None else round(r2, 4),
        'target': target,
        'eta_days': None if eta_days is None else round(eta_days, 1),
        'eta_timestamp': eta_timestamp,
        'eta_is_descriptive_only': eta_timestamp is not None,
    }


def snapshot_timestamp(snapshot: dict[str, Any]) -> datetime | None:
    metadata = snapshot.get('metadata', {})
    if not isinstance(metadata, dict):
        return None
    return parse_timestamp(metadata.get('generated_at'))


def collect_score_points(snapshots: Iterable[dict[str, Any]], metric: str) -> list[tuple[datetime, float]]:
    points: list[tuple[datetime, float]] = []
    for snapshot in snapshots:
        timestamp = snapshot_timestamp(snapshot)
        scores = snapshot.get('scores', {})
        value = numeric(scores.get(metric)) if isinstance(scores, dict) else None
        if timestamp is not None and value is not None:
            points.append((timestamp, value))
    return points


def index_modules(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    modules = snapshot.get('modules', [])
    if not isinstance(modules, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in modules:
        if isinstance(item, dict) and isinstance(item.get('id'), str):
            result[item['id']] = item
    return result


def analyze(snapshots: list[dict[str, Any]], *, target: float = 80.0) -> dict[str, Any]:
    valid_snapshots = [snapshot for snapshot in snapshots if snapshot_timestamp(snapshot) is not None]
    valid_snapshots.sort(key=lambda snapshot: snapshot_timestamp(snapshot) or datetime.min.replace(tzinfo=timezone.utc))

    metric_names = set(DEFAULT_SCORE_METRICS)
    for snapshot in valid_snapshots:
        scores = snapshot.get('scores', {})
        if isinstance(scores, dict):
            metric_names.update(key for key, value in scores.items() if numeric(value) is not None)

    score_trends: dict[str, Any] = {}
    for metric in sorted(metric_names):
        trend = linear_trend(collect_score_points(valid_snapshots, metric), target=target)
        if trend is not None:
            score_trends[metric] = trend

    module_ids: set[str] = set()
    for snapshot in valid_snapshots:
        module_ids.update(index_modules(snapshot))
    module_trends: dict[str, Any] = {}
    for module_id in sorted(module_ids):
        per_metric: dict[str, Any] = {}
        for metric in ('completion', 'confirmed_completion', 'quality', 'confidence'):
            points: list[tuple[datetime, float]] = []
            for snapshot in valid_snapshots:
                timestamp = snapshot_timestamp(snapshot)
                module = index_modules(snapshot).get(module_id)
                value = numeric(module.get(metric)) if module else None
                if timestamp is not None and value is not None:
                    points.append((timestamp, value))
            trend = linear_trend(points, target=target)
            if trend is not None:
                per_metric[metric] = trend
        if per_metric:
            module_trends[module_id] = per_metric

    regressions = [
        {'metric': metric, 'latest_delta': trend['latest_delta'], 'delta_per_30d': trend['delta_per_30d']}
        for metric, trend in score_trends.items()
        if trend.get('latest_delta') is not None and trend['latest_delta'] < -1.0
    ]
    regressions.sort(key=lambda item: item['latest_delta'])

    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'snapshot_count': len(valid_snapshots),
        'score_trends': score_trends,
        'module_trends': module_trends,
        'regressions': regressions,
        'interpretation': [
            'Trend estimates are descriptive extrapolations, not delivery commitments.',
            'ETA is emitted only with at least three observations, positive slope, and R² >= 0.35.',
            'Changes in audit methodology, scope, or scoring weights can invalidate direct historical comparisons.',
        ],
    }


def load_snapshots(paths: Iterable[Path], directory: Path | None = None) -> list[dict[str, Any]]:
    candidates = list(paths)
    if directory is not None:
        candidates.extend(sorted(directory.glob('*.json')))
    snapshots: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved in seen or not resolved.is_file():
            continue
        seen.add(resolved)
        data = load_json(resolved)
        if isinstance(data, dict):
            snapshots.append(data)
    return snapshots


def main() -> int:
    parser = argparse.ArgumentParser(description='Analyze score and module trajectories across audit snapshots.')
    parser.add_argument('snapshots', nargs='*', type=Path)
    parser.add_argument('--history-dir', type=Path)
    parser.add_argument('--target', type=float, default=80.0)
    parser.add_argument('-o', '--output', type=Path)
    parser.add_argument('--update-audit', type=Path, help='Attach trajectory under history.trajectory in an audit JSON file.')
    args = parser.parse_args()
    snapshots = load_snapshots(args.snapshots, args.history_dir)
    result = analyze(snapshots, target=args.target)
    if args.output:
        write_json(args.output, result)
        print(f"Wrote trajectory analysis to {args.output}")
    if args.update_audit:
        audit = load_json(args.update_audit)
        if not isinstance(audit, dict):
            raise ValueError('audit JSON must be an object')
        history = audit.setdefault('history', {})
        if not isinstance(history, dict):
            raise ValueError("audit 'history' must be an object")
        history['trajectory'] = result
        write_json(args.update_audit, audit)
        print(f"Attached trajectory to {args.update_audit}")
    if not args.output and not args.update_audit:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
