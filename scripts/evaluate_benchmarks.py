#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import collect_dependencies
import collect_tests
import detect_false_completion
import detect_technical_debt
import discover_modules
import infer_architecture
from audit_utils import load_json, resolve_root, write_json

Collector = Callable[[Path], dict[str, Any]]

COLLECTORS: dict[str, Collector] = {
    "modules": discover_modules.discover,
    "architecture": infer_architecture.infer,
    "dependencies": collect_dependencies.collect,
    "tests": collect_tests.collect,
    "false_completion": detect_false_completion.scan,
    "technical_debt": detect_technical_debt.collect,
}


def normalize_cycle(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple, set)):
        return tuple()
    return tuple(sorted(str(item) for item in value))


def check_architecture_edge(result: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    source = str(check.get("from", ""))
    target = str(check.get("to", ""))
    edges = result.get("edges", []) if isinstance(result, dict) else []
    present = any(
        isinstance(edge, dict)
        and str(edge.get("from")) == source
        and str(edge.get("to")) == target
        for edge in edges
    )
    expected = bool(check.get("present", True))
    return present == expected, f"edge {source} -> {target}: expected present={expected}, actual={present}"


def check_architecture_cycle(result: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    expected = normalize_cycle(check.get("members", []))
    cycles = {
        normalize_cycle(cycle)
        for cycle in result.get("cycles", [])
        if isinstance(cycle, list)
    }
    present = expected in cycles
    wanted = bool(check.get("present", True))
    return present == wanted, f"cycle {list(expected)}: expected present={wanted}, actual={present}"


def check_module_candidate(result: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    module_id = str(check.get("id", ""))
    modules = result.get("module_candidates", []) if isinstance(result, dict) else []
    present = any(isinstance(item, dict) and str(item.get("id")) == module_id for item in modules)
    wanted = bool(check.get("present", True))
    return present == wanted, f"module candidate {module_id}: expected present={wanted}, actual={present}"


def check_dependency(result: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    name = str(check.get("name", ""))
    dependencies = result.get("dependencies", []) if isinstance(result, dict) else []
    present = any(isinstance(item, dict) and str(item.get("name")) == name for item in dependencies)
    wanted = bool(check.get("present", True))
    return present == wanted, f"dependency {name}: expected present={wanted}, actual={present}"


def check_finding_kind(result: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    kind = str(check.get("kind", ""))
    findings = result.get("findings", []) if isinstance(result, dict) else []
    count = sum(1 for item in findings if isinstance(item, dict) and str(item.get("kind")) == kind)
    minimum = int(check.get("minimum", 1))
    maximum = check.get("maximum")
    passed = count >= minimum and (maximum is None or count <= int(maximum))
    return passed, f"finding kind {kind}: expected count >= {minimum}" + ("" if maximum is None else f" and <= {maximum}") + f", actual={count}"


def check_test_signal(result: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    signal = str(check.get("signal", ""))
    signals = result.get("suspicious_signals", []) if isinstance(result, dict) else []
    count = sum(1 for item in signals if isinstance(item, dict) and str(item.get("signal")) == signal)
    minimum = int(check.get("minimum", 1))
    maximum = check.get("maximum")
    passed = count >= minimum and (maximum is None or count <= int(maximum))
    return passed, f"test signal {signal}: expected count >= {minimum}" + ("" if maximum is None else f" and <= {maximum}") + f", actual={count}"


def check_test_summary(result: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    key = str(check.get("key", ""))
    summary = result.get("summary", {}) if isinstance(result, dict) else {}
    actual = summary.get(key)
    if "equals" in check:
        expected = check["equals"]
        return actual == expected, f"test summary {key}: expected={expected!r}, actual={actual!r}"
    minimum = check.get("minimum")
    maximum = check.get("maximum")
    try:
        numeric = float(actual)
    except (TypeError, ValueError):
        return False, f"test summary {key}: expected numeric value, actual={actual!r}"
    passed = (minimum is None or numeric >= float(minimum)) and (maximum is None or numeric <= float(maximum))
    return passed, f"test summary {key}: expected range {minimum!r}..{maximum!r}, actual={numeric}"


def check_debt_signal(result: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    signal = str(check.get("signal", ""))
    signals = result.get("signals", []) if isinstance(result, dict) else []
    count = sum(1 for item in signals if isinstance(item, dict) and str(item.get("signal")) == signal)
    minimum = int(check.get("minimum", 1))
    maximum = check.get("maximum")
    passed = count >= minimum and (maximum is None or count <= int(maximum))
    return passed, f"technical-debt signal {signal}: expected count >= {minimum}" + ("" if maximum is None else f" and <= {maximum}") + f", actual={count}"


CHECKERS: dict[str, tuple[str, Callable[[dict[str, Any], dict[str, Any]], tuple[bool, str]]]] = {
    "architecture_edge": ("architecture", check_architecture_edge),
    "architecture_cycle": ("architecture", check_architecture_cycle),
    "module_candidate": ("modules", check_module_candidate),
    "dependency": ("dependencies", check_dependency),
    "finding_kind": ("false_completion", check_finding_kind),
    "test_signal": ("tests", check_test_signal),
    "test_summary": ("tests", check_test_summary),
    "technical_debt_signal": ("technical_debt", check_debt_signal),
}


def run_case(repo_root: Path, case: dict[str, Any]) -> dict[str, Any]:
    case_id = str(case.get("id") or "unnamed")
    fixture_rel = str(case.get("fixture") or "")
    fixture = (repo_root / fixture_rel).resolve()
    if not fixture.exists() or not fixture.is_dir():
        return {
            "id": case_id,
            "fixture": fixture_rel,
            "score": 0.0,
            "passed": 0,
            "failed": 1,
            "checks": [{"type": "fixture_exists", "passed": False, "detail": f"Fixture not found: {fixture}"}],
        }

    checks = case.get("checks", [])
    if not isinstance(checks, list):
        raise ValueError(f"benchmark case {case_id!r} has non-list checks")

    requested_collectors: set[str] = set()
    for check in checks:
        if not isinstance(check, dict):
            continue
        check_type = str(check.get("type", ""))
        mapping = CHECKERS.get(check_type)
        if mapping:
            requested_collectors.add(mapping[0])

    results: dict[str, dict[str, Any]] = {}
    collector_errors: dict[str, str] = {}
    for name in sorted(requested_collectors):
        collector = COLLECTORS[name]
        try:
            results[name] = collector(fixture)
        except Exception as exc:  # benchmark harness must report failure instead of aborting the suite
            collector_errors[name] = f"{type(exc).__name__}: {exc}"

    rendered_checks: list[dict[str, Any]] = []
    passed_weight = 0.0
    total_weight = 0.0
    for raw in checks:
        if not isinstance(raw, dict):
            continue
        check = dict(raw)
        check_type = str(check.get("type", ""))
        weight = max(0.0, float(check.get("weight", 1.0)))
        total_weight += weight
        mapping = CHECKERS.get(check_type)
        if mapping is None:
            passed = False
            detail = f"Unknown benchmark check type: {check_type}"
        else:
            collector_name, checker = mapping
            if collector_name in collector_errors:
                passed = False
                detail = f"collector {collector_name} failed: {collector_errors[collector_name]}"
            else:
                passed, detail = checker(results.get(collector_name, {}), check)
        if passed:
            passed_weight += weight
        rendered_checks.append({
            "type": check_type,
            "weight": weight,
            "passed": passed,
            "detail": detail,
        })

    score = 100.0 if total_weight == 0 else round(100.0 * passed_weight / total_weight, 2)
    return {
        "id": case_id,
        "fixture": fixture_rel,
        "description": case.get("description"),
        "score": score,
        "passed": sum(1 for item in rendered_checks if item["passed"]),
        "failed": sum(1 for item in rendered_checks if not item["passed"]),
        "checks": rendered_checks,
        "collector_errors": collector_errors,
    }


def evaluate(repo_root: Path | str, manifest: Path | str) -> dict[str, Any]:
    root = resolve_root(repo_root)
    manifest_path = Path(manifest)
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path
    payload = load_json(manifest_path)
    cases = payload.get("cases", []) if isinstance(payload, dict) else []
    if not isinstance(cases, list):
        raise ValueError("benchmark manifest 'cases' must be a list")

    rendered = [run_case(root, case) for case in cases if isinstance(case, dict)]
    total_checks = sum(item["passed"] + item["failed"] for item in rendered)
    passed_checks = sum(item["passed"] for item in rendered)
    suite_score = 100.0 if total_checks == 0 else round(100.0 * passed_checks / total_checks, 2)
    return {
        "benchmark_version": str(payload.get("version", "1")) if isinstance(payload, dict) else "1",
        "manifest": str(manifest_path.relative_to(root)),
        "case_count": len(rendered),
        "check_count": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": total_checks - passed_checks,
        "suite_score": suite_score,
        "cases": rendered,
        "limitations": [
            "Synthetic fixtures evaluate deterministic collectors, not the semantic judgment quality of an LLM audit.",
            "A perfect benchmark score only means the declared fixture expectations were met.",
            "Real repositories can contain languages, build systems, runtime coupling, and architecture patterns absent from these fixtures.",
        ],
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Project Intelligence Auditor Benchmark Report",
        "",
        f"Suite score: **{result.get('suite_score', 0)}%**",
        f"Cases: {result.get('case_count', 0)}",
        f"Checks: {result.get('passed_checks', 0)} passed / {result.get('failed_checks', 0)} failed",
        "",
    ]
    for case in result.get("cases", []):
        lines.extend([
            f"## {case.get('id', 'unnamed')} — {case.get('score', 0)}%",
            "",
            str(case.get("description") or case.get("fixture") or ""),
            "",
        ])
        for check in case.get("checks", []):
            marker = "PASS" if check.get("passed") else "FAIL"
            lines.append(f"- **{marker}** `{check.get('type')}` — {check.get('detail')}")
        lines.append("")
    lines.append("## Limitations")
    lines.append("")
    for limitation in result.get("limitations", []):
        lines.append(f"- {limitation}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate deterministic Project Intelligence Auditor collectors against synthetic fixtures.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Auditor repository root")
    parser.add_argument("--manifest", type=Path, default=Path("benchmarks/manifest.json"))
    parser.add_argument("-o", "--output", type=Path, help="Write JSON report")
    parser.add_argument("--markdown", type=Path, help="Write Markdown report")
    parser.add_argument("--minimum-score", type=float, default=100.0, help="Exit non-zero when suite score is below this threshold")
    args = parser.parse_args()

    result = evaluate(args.root, args.manifest)
    if args.output:
        write_json(args.output, result)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(render_markdown(result), encoding="utf-8")

    print(json.dumps({
        "suite_score": result["suite_score"],
        "passed_checks": result["passed_checks"],
        "failed_checks": result["failed_checks"],
        "case_count": result["case_count"],
    }, indent=2))
    return 0 if float(result["suite_score"]) >= float(args.minimum_score) else 1


if __name__ == "__main__":
    raise SystemExit(main())
