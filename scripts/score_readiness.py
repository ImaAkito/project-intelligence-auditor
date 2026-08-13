#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_utils import bounded, load_json, write_json

STATUS_VALUES = {
    'pass': 100.0,
    'partial': 50.0,
    'fail': 0.0,
}

GATE_SCORE_KEYS = {
    'prototype': 'prototype_readiness',
    'mvp': 'mvp_readiness',
    'commercial': 'commercial_readiness',
    'production': 'production_readiness',
    'scale': 'scale_readiness',
    'research': 'research_readiness',
    'publication': 'publication_readiness',
    'ml_production': 'ml_production_readiness',
    'clinical': 'clinical_readiness',
    'hardware': 'hardware_readiness',
    'system_integration': 'system_integration_readiness',
}


def numeric(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_confidence(value: Any) -> float:
    confidence = numeric(value, 1.0)
    if confidence > 1.0:
        confidence /= 100.0
    return max(0.0, min(1.0, confidence))


def evaluate_gate(gate: dict[str, Any], *, minimum_coverage: float = 0.60) -> dict[str, Any]:
    criteria = gate.get('criteria', [])
    if not isinstance(criteria, list):
        raise ValueError("readiness gate 'criteria' must be a list")

    total_weight = 0.0
    known_weight = 0.0
    known_value = 0.0
    confidence_value = 0.0
    critical_failures: list[str] = []
    critical_unknowns: list[str] = []
    status_counts = {'pass': 0, 'partial': 0, 'fail': 0, 'unknown': 0, 'not_applicable': 0}

    normalized_criteria: list[dict[str, Any]] = []
    for index, raw in enumerate(criteria):
        if not isinstance(raw, dict):
            continue
        item = dict(raw)
        criterion_id = str(item.get('id') or f'criterion-{index + 1}')
        status = str(item.get('status', 'unknown')).strip().lower()
        if status in {'n/a', 'na'}:
            status = 'not_applicable'
        if status not in {*STATUS_VALUES, 'unknown', 'not_applicable'}:
            status = 'unknown'
        weight = max(0.0, numeric(item.get('weight'), 1.0))
        confidence = normalize_confidence(item.get('confidence', 1.0))
        critical = item.get('critical') is True
        status_counts[status] += 1

        item['id'] = criterion_id
        item['status'] = status
        item['weight'] = weight
        item['confidence'] = round(confidence, 4)
        normalized_criteria.append(item)

        if status == 'not_applicable' or weight <= 0:
            continue
        total_weight += weight
        if status == 'unknown':
            if critical:
                critical_unknowns.append(criterion_id)
            continue

        known_weight += weight
        value = STATUS_VALUES[status]
        known_value += value * weight
        confidence_value += confidence * weight
        if status == 'fail' and critical:
            critical_failures.append(criterion_id)

    if total_weight <= 0:
        return {
            'score': None,
            'assessed_score': None,
            'lower_bound': None,
            'upper_bound': None,
            'coverage': 0.0,
            'confidence': 0.0,
            'state': 'not_applicable',
            'blocked': False,
            'critical_failures': [],
            'critical_unknowns': [],
            'status_counts': status_counts,
            'criteria': normalized_criteria,
        }

    coverage = known_weight / total_weight
    assessed_score = known_value / known_weight if known_weight else None
    lower_bound = known_value / total_weight
    unknown_weight = total_weight - known_weight
    upper_bound = (known_value + 100.0 * unknown_weight) / total_weight
    evidence_confidence = confidence_value / known_weight if known_weight else 0.0
    effective_confidence = evidence_confidence * coverage

    threshold = bounded(numeric(gate.get('threshold'), 70.0))
    min_coverage = max(0.0, min(1.0, numeric(gate.get('minimum_coverage'), minimum_coverage)))
    score = assessed_score if assessed_score is not None and coverage >= min_coverage else None
    blocked = bool(critical_failures)

    if blocked:
        state = 'blocked'
    elif coverage < min_coverage:
        state = 'insufficient_evidence'
    elif critical_unknowns:
        state = 'critical_evidence_missing'
    elif score is not None and score >= threshold:
        state = 'ready'
    elif score is not None and score >= max(0.0, threshold - 15.0):
        state = 'nearly_ready'
    else:
        state = 'not_ready'

    return {
        'score': None if score is None else round(score, 2),
        'assessed_score': None if assessed_score is None else round(assessed_score, 2),
        'lower_bound': round(lower_bound, 2),
        'upper_bound': round(upper_bound, 2),
        'coverage': round(coverage * 100.0, 2),
        'confidence': round(effective_confidence * 100.0, 2),
        'threshold': round(threshold, 2),
        'minimum_coverage': round(min_coverage * 100.0, 2),
        'state': state,
        'blocked': blocked,
        'critical_failures': critical_failures,
        'critical_unknowns': critical_unknowns,
        'status_counts': status_counts,
        'criteria': normalized_criteria,
    }


def apply(data: dict[str, Any]) -> dict[str, Any]:
    result = dict(data)
    gates = result.get('readiness_gates', {})
    if not isinstance(gates, dict):
        raise ValueError("'readiness_gates' must be an object")
    scores = result.setdefault('scores', {})
    if not isinstance(scores, dict):
        raise ValueError("'scores' must be an object")

    evaluated: dict[str, Any] = {}
    for name, raw_gate in gates.items():
        if not isinstance(raw_gate, dict):
            continue
        gate = dict(raw_gate)
        evaluation = evaluate_gate(gate)
        gate['evaluation'] = {key: value for key, value in evaluation.items() if key != 'criteria'}
        gate['criteria'] = evaluation['criteria']
        evaluated[name] = gate
        score_key = gate.get('score_key') or GATE_SCORE_KEYS.get(name)
        if isinstance(score_key, str) and score_key and evaluation['score'] is not None:
            scores[score_key] = evaluation['score']

    result['readiness_gates'] = evaluated
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description='Evaluate evidence-backed readiness gates deterministically.')
    parser.add_argument('input', type=Path)
    parser.add_argument('-o', '--output', type=Path)
    args = parser.parse_args()
    result = apply(load_json(args.input))
    output = args.output or args.input
    write_json(output, result)
    summary = {
        name: gate.get('evaluation', {})
        for name, gate in result.get('readiness_gates', {}).items()
        if isinstance(gate, dict)
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
