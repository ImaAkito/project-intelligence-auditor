#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TRACKED_SCORES = [
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
]


def load(path: Path) -> dict[str, Any]:
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def index_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = item.get('id')
        if isinstance(item_id, str) and item_id:
            indexed[item_id] = item
    return indexed


def delta(old: Any, new: Any) -> float | None:
    if isinstance(old, bool) or isinstance(new, bool):
        return None
    if isinstance(old, (int, float)) and isinstance(new, (int, float)):
        return round(float(new) - float(old), 2)
    return None


def list_section(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key, [])
    return value if isinstance(value, list) else []


def id_changes(old: dict[str, Any], new: dict[str, Any], key: str) -> dict[str, list[str]]:
    old_index = index_by_id(list_section(old, key))
    new_index = index_by_id(list_section(new, key))
    return {
        'resolved': sorted(set(old_index) - set(new_index)),
        'new': sorted(set(new_index) - set(old_index)),
        'persistent': sorted(set(old_index) & set(new_index)),
    }


def gate_evaluation(data: dict[str, Any], gate_name: str) -> dict[str, Any]:
    gates = data.get('readiness_gates', {})
    if not isinstance(gates, dict):
        return {}
    gate = gates.get(gate_name, {})
    if not isinstance(gate, dict):
        return {}
    evaluation = gate.get('evaluation', {})
    return evaluation if isinstance(evaluation, dict) else {}


def compare(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    old_scores = old.get('scores', {}) if isinstance(old.get('scores'), dict) else {}
    new_scores = new.get('scores', {}) if isinstance(new.get('scores'), dict) else {}
    tracked = set(TRACKED_SCORES) | set(old_scores) | set(new_scores)
    score_deltas = {
        key: delta(old_scores.get(key), new_scores.get(key))
        for key in sorted(tracked)
        if old_scores.get(key) is not None or new_scores.get(key) is not None
    }

    old_modules = index_by_id(list_section(old, 'modules'))
    new_modules = index_by_id(list_section(new, 'modules'))
    module_changes: list[dict[str, Any]] = []
    for module_id in sorted(set(old_modules) | set(new_modules)):
        before = old_modules.get(module_id)
        after = new_modules.get(module_id)
        if before is None:
            module_changes.append({'id': module_id, 'change': 'added'})
            continue
        if after is None:
            module_changes.append({'id': module_id, 'change': 'removed'})
            continue
        changes = {
            'completion_delta': delta(before.get('completion'), after.get('completion')),
            'confirmed_completion_delta': delta(before.get('confirmed_completion'), after.get('confirmed_completion')),
            'quality_delta': delta(before.get('quality'), after.get('quality')),
            'confidence_delta': delta(before.get('confidence'), after.get('confidence')),
        }
        classification_changed = before.get('classification') != after.get('classification')
        if any(value not in (None, 0.0) for value in changes.values()) or classification_changed:
            module_changes.append({
                'id': module_id,
                'change': 'updated',
                **changes,
                'classification_before': before.get('classification') if classification_changed else None,
                'classification_after': after.get('classification') if classification_changed else None,
            })

    old_gates = old.get('readiness_gates', {}) if isinstance(old.get('readiness_gates'), dict) else {}
    new_gates = new.get('readiness_gates', {}) if isinstance(new.get('readiness_gates'), dict) else {}
    gate_changes: dict[str, Any] = {}
    for gate_name in sorted(set(old_gates) | set(new_gates)):
        before = gate_evaluation(old, gate_name)
        after = gate_evaluation(new, gate_name)
        gate_changes[gate_name] = {
            'score_delta': delta(before.get('score'), after.get('score')),
            'coverage_delta': delta(before.get('coverage'), after.get('coverage')),
            'confidence_delta': delta(before.get('confidence'), after.get('confidence')),
            'state_before': before.get('state'),
            'state_after': after.get('state'),
            'state_changed': before.get('state') != after.get('state'),
        }

    risk_changes = id_changes(old, new, 'risks')
    debt_changes = id_changes(old, new, 'technical_debt')
    bottleneck_changes = id_changes(old, new, 'bottlenecks')

    old_metadata = old.get('metadata', {}) if isinstance(old.get('metadata'), dict) else {}
    new_metadata = new.get('metadata', {}) if isinstance(new.get('metadata'), dict) else {}
    methodology_changed = old_metadata.get('auditor_version') != new_metadata.get('auditor_version')

    regressions: list[dict[str, Any]] = []
    for metric, value in score_deltas.items():
        if isinstance(value, (int, float)) and value < -1.0:
            regressions.append({'kind': 'score', 'id': metric, 'delta': value})
    for item in module_changes:
        if item.get('change') != 'updated':
            continue
        for metric in ('completion_delta', 'confirmed_completion_delta', 'quality_delta'):
            value = item.get(metric)
            if isinstance(value, (int, float)) and value < -3.0:
                regressions.append({'kind': 'module', 'id': item['id'], 'metric': metric, 'delta': value})
    regressions.sort(key=lambda item: item['delta'])

    return {
        'score_deltas': score_deltas,
        'module_changes': module_changes,
        'readiness_gate_changes': gate_changes,
        'closed_risks': risk_changes['resolved'],
        'new_risks': risk_changes['new'],
        'resolved_technical_debt': debt_changes['resolved'],
        'new_technical_debt': debt_changes['new'],
        'resolved_bottlenecks': bottleneck_changes['resolved'],
        'new_bottlenecks': bottleneck_changes['new'],
        'regressions': regressions,
        'scope_change': {
            'modules_added': [item['id'] for item in module_changes if item['change'] == 'added'],
            'modules_removed': [item['id'] for item in module_changes if item['change'] == 'removed'],
        },
        'methodology': {
            'changed': methodology_changed,
            'before': old_metadata.get('auditor_version'),
            'after': new_metadata.get('auditor_version'),
            'warning': (
                'Direct score deltas may mix methodology change with project change.'
                if methodology_changed else None
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Compare two Project Intelligence Auditor snapshots.')
    parser.add_argument('old', type=Path)
    parser.add_argument('new', type=Path)
    parser.add_argument('-o', '--output', type=Path)
    args = parser.parse_args()

    result = compare(load(args.old), load(args.new))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding='utf-8')
        print(f'Wrote snapshot comparison to {args.output}')
    else:
        print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
