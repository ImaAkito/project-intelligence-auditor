#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from audit_utils import iter_files, relative_posix, resolve_root, write_json

SOURCE_EXTENSIONS = {'.py', '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}
CONTAINER_NAMES = {'src', 'packages', 'apps', 'services', 'modules'}
EXCLUDED_MODULE_NAMES = {
    'test', 'tests', 'docs', 'documentation', 'examples', 'example', 'fixtures', 'fixture',
    'assets', 'static', 'public', 'images', '.github',
}
JS_IMPORT_RE = re.compile(
    r"(?:import\s+(?:[^'\"]+?\s+from\s+)?|export\s+[^'\"]+?\s+from\s+|require\s*\(|import\s*\()"
    r"['\"]([^'\"]+)['\"]"
)


def slug(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-') or 'module'


def source_file_count(path: Path) -> int:
    return sum(1 for _ in iter_files(path, extensions=SOURCE_EXTENSIONS, max_bytes=None))


def discover_module_roots(root: Path) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen_paths: set[str] = set()

    def add_candidate(path: Path, *, container: str | None = None) -> None:
        rel = relative_posix(path, root)
        if rel in seen_paths or source_file_count(path) == 0:
            return
        seen_paths.add(rel)
        candidates.append({
            'id': slug(rel.replace('/', '-')),
            'name': path.name,
            'path': rel,
            'container': container,
            'source_file_count': source_file_count(path),
        })

    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir() or child.name.lower() in EXCLUDED_MODULE_NAMES or child.name.startswith('.'):
            continue
        count = source_file_count(child)
        if count == 0:
            continue
        if child.name.lower() in CONTAINER_NAMES:
            nested = [
                item for item in sorted(child.iterdir(), key=lambda p: p.name.lower())
                if item.is_dir()
                and item.name.lower() not in EXCLUDED_MODULE_NAMES
                and not item.name.startswith('.')
                and source_file_count(item) > 0
            ]
            if nested:
                for item in nested:
                    add_candidate(item, container=relative_posix(child, root))
                direct_sources = [
                    item for item in child.iterdir()
                    if item.is_file() and item.suffix.lower() in SOURCE_EXTENSIONS
                ]
                if direct_sources:
                    add_candidate(child)
                continue
        add_candidate(child)

    root_sources = [
        path for path in root.iterdir()
        if path.is_file() and path.suffix.lower() in SOURCE_EXTENSIONS
    ]
    if root_sources:
        candidates.append({
            'id': 'root',
            'name': root.name,
            'path': '.',
            'container': None,
            'source_file_count': len(root_sources),
        })

    candidates.sort(key=lambda item: (-len(PurePosixPath(item['path']).parts), item['path']))
    return candidates


def module_for_relative_path(relative: PurePosixPath, modules: list[dict[str, Any]]) -> str | None:
    relative_parts = relative.parts
    best: tuple[int, str] | None = None
    for module in modules:
        module_path = module['path']
        if module_path == '.':
            if len(relative_parts) == 1:
                candidate = (0, module['id'])
            else:
                continue
        else:
            module_parts = PurePosixPath(module_path).parts
            if relative_parts[: len(module_parts)] != module_parts:
                continue
            candidate = (len(module_parts), module['id'])
        if best is None or candidate[0] > best[0]:
            best = candidate
    return None if best is None else best[1]


def normalize_relative_import(current: PurePosixPath, level: int, module: str | None) -> PurePosixPath:
    package_parts = list(current.parent.parts)
    climbs = max(level - 1, 0)
    if climbs:
        package_parts = package_parts[: max(0, len(package_parts) - climbs)]
    if module:
        package_parts.extend(part for part in module.split('.') if part)
    return PurePosixPath(*package_parts)


def python_import_targets(path: Path, root: Path, modules: list[dict[str, Any]]) -> list[tuple[str, int, float, str]]:
    text = path.read_text(encoding='utf-8', errors='replace')
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    relative = PurePosixPath(relative_posix(path, root))
    aliases: dict[str, str] = {}
    for module in modules:
        if module['path'] == '.':
            continue
        parts = PurePosixPath(module['path']).parts
        if parts:
            aliases[parts[0]] = module['id']
            aliases[parts[-1]] = module['id']

    targets: list[tuple[str, int, float, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                first = alias.name.split('.')[0]
                target = aliases.get(first)
                if target:
                    targets.append((target, getattr(node, 'lineno', 0), 0.88, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                target_path = normalize_relative_import(relative, node.level, node.module)
                target = module_for_relative_path(target_path, modules)
                if target:
                    targets.append((target, getattr(node, 'lineno', 0), 0.96, f"relative:{node.module or ''}"))
            elif node.module:
                first = node.module.split('.')[0]
                target = aliases.get(first)
                if target:
                    targets.append((target, getattr(node, 'lineno', 0), 0.90, node.module))
    return targets


def lexical_resolve(base: PurePosixPath, specifier: str) -> PurePosixPath:
    parts: list[str] = list(base.parts)
    for part in PurePosixPath(specifier).parts:
        if part in ('', '.'):
            continue
        if part == '..':
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return PurePosixPath(*parts)


def js_import_targets(path: Path, root: Path, modules: list[dict[str, Any]]) -> list[tuple[str, int, float, str]]:
    text = path.read_text(encoding='utf-8', errors='replace')
    relative = PurePosixPath(relative_posix(path, root))
    aliases: dict[str, str] = {}
    for module in modules:
        if module['path'] == '.':
            continue
        parts = PurePosixPath(module['path']).parts
        if parts:
            aliases[parts[0]] = module['id']
            aliases[parts[-1]] = module['id']

    targets: list[tuple[str, int, float, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in JS_IMPORT_RE.finditer(line):
            specifier = match.group(1)
            target: str | None = None
            confidence = 0.84
            if specifier.startswith('.'):
                target_path = lexical_resolve(relative.parent, specifier)
                target = module_for_relative_path(target_path, modules)
                confidence = 0.94
            elif not specifier.startswith('@'):
                first = specifier.split('/')[0]
                target = aliases.get(first)
            else:
                scoped_parts = specifier.split('/')
                if len(scoped_parts) >= 2:
                    target = aliases.get(scoped_parts[1])
            if target:
                targets.append((target, line_number, confidence, specifier))
    return targets


def strongly_connected_components(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> list[list[str]]:
    graph: dict[str, list[str]] = defaultdict(list)
    for source, target in edges:
        graph[source].append(target)

    index = 0
    stack: list[str] = []
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for target in graph.get(node, []):
            if target not in indices:
                visit(target)
                lowlink[node] = min(lowlink[node], lowlink[target])
            elif target in on_stack:
                lowlink[node] = min(lowlink[node], indices[target])

        if lowlink[node] == indices[node]:
            component: list[str] = []
            while stack:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node:
                    break
            if len(component) > 1:
                components.append(sorted(component))

    for node in sorted(set(nodes)):
        if node not in indices:
            visit(node)
    return sorted(components)


def infer(root: Path | str) -> dict[str, Any]:
    root_path = resolve_root(root)
    modules = discover_module_roots(root_path)
    module_index = {item['id']: item for item in modules}
    edge_accumulator: dict[tuple[str, str], dict[str, Any]] = {}

    for path in iter_files(root_path, extensions=SOURCE_EXTENSIONS, max_bytes=2_000_000):
        relative = PurePosixPath(relative_posix(path, root_path))
        source = module_for_relative_path(relative, modules)
        if source is None:
            continue
        if path.suffix.lower() == '.py':
            targets = python_import_targets(path, root_path, modules)
        else:
            targets = js_import_targets(path, root_path, modules)
        for target, line, confidence, declaration in targets:
            if target == source or target not in module_index:
                continue
            key = (source, target)
            item = edge_accumulator.setdefault(key, {
                'from': source,
                'to': target,
                'kind': 'static_import',
                'occurrences': 0,
                'confidence': 0.0,
                'evidence': [],
            })
            item['occurrences'] += 1
            item['confidence'] = max(item['confidence'], confidence)
            if len(item['evidence']) < 20:
                item['evidence'].append({
                    'path': relative.as_posix(),
                    'line': line,
                    'declaration': declaration,
                })

    edges = sorted(edge_accumulator.values(), key=lambda item: (item['from'], item['to']))
    incoming: dict[str, set[str]] = defaultdict(set)
    outgoing: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        outgoing[edge['from']].add(edge['to'])
        incoming[edge['to']].add(edge['from'])

    max_degree = max((len(incoming[m['id']]) + len(outgoing[m['id']]) for m in modules), default=1)
    nodes: list[dict[str, Any]] = []
    for module in modules:
        module_id = module['id']
        fan_in = len(incoming[module_id])
        fan_out = len(outgoing[module_id])
        centrality = (fan_in + fan_out) / max_degree if max_degree else 0.0
        nodes.append({
            **module,
            'dependencies': sorted(outgoing[module_id]),
            'consumers': sorted(incoming[module_id]),
            'fan_in': fan_in,
            'fan_out': fan_out,
            'centrality': round(centrality, 4),
        })

    cycles = strongly_connected_components(
        (module['id'] for module in modules),
        ((edge['from'], edge['to']) for edge in edges),
    )
    hotspots = [
        {'module_id': node['id'], 'fan_in': node['fan_in'], 'fan_out': node['fan_out'], 'centrality': node['centrality']}
        for node in sorted(nodes, key=lambda item: (-item['centrality'], -item['fan_in'], item['id']))
        if node['centrality'] >= 0.5 and (node['fan_in'] + node['fan_out']) > 0
    ][:10]

    return {
        'collector': 'infer_architecture',
        'root': str(root_path),
        'nodes': nodes,
        'edges': edges,
        'cycles': cycles,
        'hotspots': hotspots,
        'limitations': [
            'Edges are inferred from static Python and JavaScript/TypeScript imports only.',
            'Reflection, runtime dependency injection, RPC, message queues, database coupling, and generated code can create dependencies not visible here.',
            'Hotspots are structural candidates for review, not automatic architecture defects.',
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Infer a repository module dependency graph from static imports.')
    parser.add_argument('root', nargs='?', default='.', type=Path)
    parser.add_argument('-o', '--output', type=Path)
    args = parser.parse_args()
    result = infer(args.root)
    if args.output:
        write_json(args.output, result)
        print(f"Wrote architecture inference to {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
