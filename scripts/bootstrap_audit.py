#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_utils import load_json, write_json


def collector_result(discovery: dict[str, Any], name: str) -> dict[str, Any]:
    collectors = discovery.get('collectors', {})
    outcome = collectors.get(name, {}) if isinstance(collectors, dict) else {}
    if not isinstance(outcome, dict) or outcome.get('status') != 'ok':
        return {}
    result = outcome.get('result', {})
    return result if isinstance(result, dict) else {}


def module_skeleton(source: dict[str, Any]) -> dict[str, Any]:
    return {
        'id': source.get('id') or str(source.get('name', 'unknown')).lower(),
        'name': source.get('name') or source.get('path') or 'Unknown',
        'path': source.get('path'),
        'role_hint': source.get('role_hint'),
        'responsibility': None,
        'classification': 'unknown',
        'implementation': None,
        'integration': None,
        'validation': None,
        'documentation': None,
        'operational_readiness': None,
        'completion': None,
        'confirmed_completion': None,
        'quality': None,
        'confidence': None,
        'criticality': None,
        'evidence_level': 'E0',
        'dependencies': list(source.get('dependencies', [])) if isinstance(source.get('dependencies'), list) else [],
        'consumers': list(source.get('consumers', [])) if isinstance(source.get('consumers'), list) else [],
        'evidence_ids': [],
        'status': 'unreviewed',
    }


def architecture_evidence(architecture: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    evidence: list[dict[str, Any]] = []
    dependency_edges: list[dict[str, Any]] = []
    for index, edge in enumerate(architecture.get('edges', []), start=1):
        if not isinstance(edge, dict):
            continue
        source = edge.get('from')
        target = edge.get('to')
        if not isinstance(source, str) or not isinstance(target, str):
            continue
        evidence_id = f'ev-arch-{index:04d}'
        samples = edge.get('evidence', []) if isinstance(edge.get('evidence'), list) else []
        first = samples[0] if samples and isinstance(samples[0], dict) else {}
        confidence = edge.get('confidence')
        evidence.append({
            'id': evidence_id,
            'level': 'E2',
            'claim': f'Static imports indicate that module {source} depends on module {target}.',
            'kind': 'static_import_dependency',
            'source': first.get('path'),
            'location': None if first.get('line') is None else f"line {first.get('line')}",
            'confidence': confidence,
            'verified_at': None,
            'samples': samples,
            'note': 'This supports code-level dependency existence, not successful runtime integration.',
        })
        dependency_edges.append({
            'from': source,
            'to': target,
            'kind': edge.get('kind', 'static_import'),
            'confidence': confidence,
            'evidence_ids': [evidence_id],
            'occurrences': edge.get('occurrences'),
        })
    return evidence, dependency_edges


def bootstrap(discovery: dict[str, Any], project_name: str | None = None) -> dict[str, Any]:
    module_result = collector_result(discovery, 'modules')
    architecture = collector_result(discovery, 'architecture')
    candidates = module_result.get('module_candidates', []) if isinstance(module_result, dict) else []
    architecture_nodes = architecture.get('nodes', []) if isinstance(architecture, dict) else []

    merged: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        if isinstance(candidate, dict):
            skeleton = module_skeleton(candidate)
            merged[skeleton['id']] = skeleton
    for node in architecture_nodes:
        if not isinstance(node, dict):
            continue
        skeleton = module_skeleton(node)
        existing = merged.get(skeleton['id'])
        if existing is None:
            merged[skeleton['id']] = skeleton
            continue
        if skeleton['dependencies']:
            existing['dependencies'] = skeleton['dependencies']
        if skeleton['consumers']:
            existing['consumers'] = skeleton['consumers']
        if existing.get('path') is None:
            existing['path'] = skeleton.get('path')

    evidence, dependency_edges = architecture_evidence(architecture)
    root = discovery.get('metadata', {}).get('root') if isinstance(discovery.get('metadata'), dict) else None
    inferred_name = Path(root).name if root else 'Unknown project'

    return {
        'metadata': {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'auditor_version': '0.4.0',
            'repository': root,
            'commit': None,
            'snapshot_kind': 'bootstrap',
        },
        'project': {
            'name': project_name or inferred_name,
            'mission': None,
            'target_users': [],
            'current_stage': None,
            'trl': None,
            'scope_status': 'unreviewed',
        },
        'scores': {
            'confirmed_completion': None,
            'estimated_completion': None,
            'project_health': None,
            'prototype_readiness': None,
            'mvp_readiness': None,
            'commercial_readiness': None,
            'production_readiness': None,
            'scale_readiness': None,
            'research_readiness': None,
            'confidence': None,
        },
        'modules': sorted(merged.values(), key=lambda item: (str(item.get('path')), item['id'])),
        'dependency_edges': dependency_edges,
        'architecture_analysis': {
            'cycles': architecture.get('cycles', []),
            'hotspots': architecture.get('hotspots', []),
            'limitations': architecture.get('limitations', []),
            'status': 'collector_output_requires_review',
        },
        'evidence': evidence,
        'validation_runs': [],
        'risks': [],
        'technical_debt': [],
        'bottlenecks': [],
        'directions': [],
        'commercialization': {},
        'readiness_gates': {},
        'recommendations': [],
        'action_plan': {},
        'limitations': [
            'This snapshot is a bootstrap generated from deterministic discovery only.',
            'Scores remain null until Codex reviews evidence and applies the audit methodology.',
            'Static dependency edges are not proof that the corresponding runtime integration works.',
        ],
        'history': {},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Create an unscored audit skeleton from discovery.json.')
    parser.add_argument('discovery', type=Path)
    parser.add_argument('-o', '--output', type=Path, default=Path('.project-audit/audit.json'))
    parser.add_argument('--project-name')
    args = parser.parse_args()
    result = bootstrap(load_json(args.discovery), project_name=args.project_name)
    write_json(args.output, result)
    print(json.dumps({
        'output': str(args.output),
        'module_count': len(result['modules']),
        'dependency_edge_count': len(result['dependency_edges']),
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
