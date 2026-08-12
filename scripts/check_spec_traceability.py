#!/usr/bin/env python3
"""Spec traceability guard.

The contract between the plain-English review layer and the code layer: every
scenario written in an OpenSpec spec must be claimed by at least one test, and
every claim a test makes must name a scenario that actually exists.

Scenarios are read from ``openspec/specs/<capability>/spec.md`` — the layout the
OpenSpec CLI produces — where they appear as ``#### Scenario: <title>`` headings.
Each one gets an id of ``<capability>/<slugified-title>``.

Tests claim a scenario with a pytest marker::

    @pytest.mark.spec("foundation/every-scenario-is-claimed-by-a-test")
    def test_something():
        ...

Claims are found by parsing the test files' syntax tree, so this never imports
or executes test code.

Run it directly (``python scripts/check_spec_traceability.py``) or let the test
suite run it — both report the same thing.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SCENARIO_HEADING = re.compile(r"^####\s+Scenario:\s*(.+?)\s*$")
REQUIREMENT_HEADING = re.compile(r"^###\s+Requirement:\s*(.+?)\s*$")

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = REPO_ROOT / "openspec" / "specs"
TESTS_DIR = REPO_ROOT / "tests"


def slugify(title: str) -> str:
    """Turn a scenario title into the stable part of its id."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower())
    return slug.strip("-")


@dataclass(frozen=True)
class Scenario:
    """A scenario declared in a spec."""

    id: str
    title: str
    requirement: str
    source: Path
    line: int


@dataclass(frozen=True)
class Claim:
    """A test's claim that it covers a scenario."""

    scenario_id: str
    test_name: str
    source: Path
    line: int


@dataclass
class Report:
    """The result of checking claims against scenarios."""

    scenarios: list[Scenario] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    unclaimed: list[Scenario] = field(default_factory=list)
    unknown: list[Claim] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.unclaimed and not self.unknown

    def summary(self) -> str:
        claimed = len(self.scenarios) - len(self.unclaimed)
        return f"{claimed}/{len(self.scenarios)} scenarios claimed by tests"


def find_scenarios(specs_dir: Path = SPECS_DIR) -> list[Scenario]:
    """Collect every scenario declared under ``specs_dir``."""
    scenarios: list[Scenario] = []
    if not specs_dir.is_dir():
        return scenarios

    for spec_file in sorted(specs_dir.glob("*/spec.md")):
        capability = spec_file.parent.name
        requirement = ""
        for lineno, line in enumerate(spec_file.read_text(encoding="utf-8").splitlines(), 1):
            if match := REQUIREMENT_HEADING.match(line):
                requirement = match.group(1)
            elif match := SCENARIO_HEADING.match(line):
                title = match.group(1)
                scenarios.append(
                    Scenario(
                        id=f"{capability}/{slugify(title)}",
                        title=title,
                        requirement=requirement,
                        source=spec_file,
                        line=lineno,
                    )
                )
    return scenarios


def _spec_marker_ids(decorator: ast.expr) -> list[str]:
    """Return the scenario ids named by a ``@pytest.mark.spec(...)`` decorator."""
    if not isinstance(decorator, ast.Call):
        return []
    func = decorator.func
    if not isinstance(func, ast.Attribute) or func.attr != "spec":
        return []
    # Match the `...mark.spec` shape without caring how pytest was imported.
    parent = func.value
    if not isinstance(parent, ast.Attribute) or parent.attr != "mark":
        return []
    return [
        arg.value
        for arg in decorator.args
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
    ]


def find_claims(tests_dir: Path = TESTS_DIR) -> list[Claim]:
    """Collect every scenario claim made by a test."""
    claims: list[Claim] = []
    if not tests_dir.is_dir():
        return claims

    for test_file in sorted(tests_dir.rglob("test_*.py")):
        tree = ast.parse(test_file.read_text(encoding="utf-8"), filename=str(test_file))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            for decorator in node.decorator_list:
                for scenario_id in _spec_marker_ids(decorator):
                    claims.append(
                        Claim(
                            scenario_id=scenario_id,
                            test_name=node.name,
                            source=test_file,
                            line=node.lineno,
                        )
                    )
    return claims


def check(specs_dir: Path = SPECS_DIR, tests_dir: Path = TESTS_DIR) -> Report:
    """Check that scenarios and test claims line up in both directions."""
    scenarios = find_scenarios(specs_dir)
    claims = find_claims(tests_dir)

    claimed_ids = {claim.scenario_id for claim in claims}
    known_ids = {scenario.id for scenario in scenarios}

    return Report(
        scenarios=scenarios,
        claims=claims,
        unclaimed=[s for s in scenarios if s.id not in claimed_ids],
        unknown=[c for c in claims if c.scenario_id not in known_ids],
    )


def _display_path(path: Path) -> Path:
    """Show a repo-relative path when we can, and the full path when we cannot."""
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


def format_report(report: Report) -> str:
    """Render a report as the plain-English explanation of what is missing."""
    lines: list[str] = []

    if report.unclaimed:
        lines.append("Scenarios with no test claiming them:")
        for scenario in report.unclaimed:
            location = _display_path(scenario.source)
            lines.append(f"  {scenario.id}")
            lines.append(f'    "{scenario.title}" under "{scenario.requirement}"')
            lines.append(f"    {location}:{scenario.line}")
            lines.append(f'    fix: add @pytest.mark.spec("{scenario.id}") to a test')
        lines.append("")

    if report.unknown:
        lines.append("Tests claiming scenarios that do not exist:")
        for claim in report.unknown:
            location = _display_path(claim.source)
            lines.append(f"  {claim.scenario_id}")
            lines.append(f"    claimed by {claim.test_name}() at {location}:{claim.line}")
            lines.append("    fix: correct the id, or write the scenario in the spec")
        lines.append("")

    lines.append(report.summary())
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--specs-dir", type=Path, default=SPECS_DIR)
    parser.add_argument("--tests-dir", type=Path, default=TESTS_DIR)
    args = parser.parse_args(argv)

    report = check(args.specs_dir, args.tests_dir)
    print(format_report(report))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
