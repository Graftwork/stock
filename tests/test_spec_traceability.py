"""The traceability guard, checked against this repo and against known-bad input.

The first test is the live one: it runs the guard over the real specs and tests,
so a scenario added without a claiming test turns CI red. The rest prove the
guard actually catches what it promises to catch — a guard that cannot fail is
not a guard.
"""

import textwrap
from pathlib import Path

import pytest

from scripts.check_spec_traceability import check, format_report, slugify


def write_spec(specs_dir: Path, capability: str, body: str) -> None:
    spec_file = specs_dir / capability / "spec.md"
    spec_file.parent.mkdir(parents=True)
    spec_file.write_text(textwrap.dedent(body), encoding="utf-8")


def write_test(tests_dir: Path, name: str, body: str) -> None:
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / name).write_text(textwrap.dedent(body), encoding="utf-8")


@pytest.mark.spec("foundation/every-scenario-is-claimed-by-a-test")
def test_every_scenario_in_this_repo_is_claimed():
    report = check()

    assert report.scenarios, "expected at least one scenario in openspec/specs/"
    assert report.ok, "\n" + format_report(report)


@pytest.mark.spec("foundation/an-unclaimed-scenario-is-reported")
def test_unclaimed_scenario_is_reported(tmp_path):
    write_spec(
        tmp_path / "specs",
        "billing",
        """
        # billing

        ## Requirements

        ### Requirement: Refunds

        #### Scenario: A refund returns the full amount
        - **WHEN** a customer requests a refund
        - **THEN** the full amount is returned
        """,
    )

    report = check(tmp_path / "specs", tmp_path / "tests")

    assert not report.ok
    assert [s.id for s in report.unclaimed] == ["billing/a-refund-returns-the-full-amount"]
    assert "billing/a-refund-returns-the-full-amount" in format_report(report)


@pytest.mark.spec("foundation/a-claim-naming-an-unknown-scenario-is-reported")
def test_claim_on_unknown_scenario_is_reported(tmp_path):
    write_spec(
        tmp_path / "specs",
        "billing",
        """
        # billing

        ## Requirements

        ### Requirement: Refunds

        #### Scenario: A refund returns the full amount
        - **WHEN** a customer requests a refund
        - **THEN** the full amount is returned
        """,
    )
    write_test(
        tmp_path / "tests",
        "test_billing.py",
        """
        import pytest

        @pytest.mark.spec("billing/a-refund-returns-the-full-ammount")
        def test_refund():
            pass
        """,
    )

    report = check(tmp_path / "specs", tmp_path / "tests")

    assert not report.ok
    # The typo shows up twice over: nothing claims the real scenario, and the
    # claim itself points at an id that does not exist.
    assert [c.scenario_id for c in report.unknown] == ["billing/a-refund-returns-the-full-ammount"]
    assert [s.id for s in report.unclaimed] == ["billing/a-refund-returns-the-full-amount"]


def test_a_matching_claim_satisfies_the_guard(tmp_path):
    write_spec(
        tmp_path / "specs",
        "billing",
        """
        # billing

        ## Requirements

        ### Requirement: Refunds

        #### Scenario: A refund returns the full amount
        - **WHEN** a customer requests a refund
        - **THEN** the full amount is returned
        """,
    )
    write_test(
        tmp_path / "tests",
        "test_billing.py",
        """
        import pytest

        @pytest.mark.spec("billing/a-refund-returns-the-full-amount")
        def test_refund():
            pass
        """,
    )

    report = check(tmp_path / "specs", tmp_path / "tests")

    assert report.ok, "\n" + format_report(report)
    assert report.summary() == "1/1 scenarios claimed by tests"


def test_no_specs_yet_is_not_a_failure(tmp_path):
    report = check(tmp_path / "specs", tmp_path / "tests")

    assert report.ok
    assert report.scenarios == []


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("A refund returns the full amount", "a-refund-returns-the-full-amount"),
        ("Rejects an expired coupon", "rejects-an-expired-coupon"),
        ("Handles 100% discounts (edge case)", "handles-100-discounts-edge-case"),
    ],
)
def test_slugify_makes_stable_ids(title, expected):
    assert slugify(title) == expected
