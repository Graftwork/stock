# foundation

## Purpose

The guarantees Graftwork Stock makes to a project grafted from it. These are the
promises of the foundation itself, not of any project built on top — a stamped
project keeps this spec, adds its own capabilities alongside it, and can check at
any time that the foundation still holds.

## Requirements

### Requirement: Green From Commit One

A freshly stamped project SHALL pass its checks with no edits, so the first real
commit is the idea rather than the plumbing.

#### Scenario: A freshly stamped project passes its test suite

- **WHEN** a project is stamped from Stock and its test suite is run
- **THEN** the suite passes without any source edits

### Requirement: Spec Traceability

Every scenario written in a spec SHALL be claimed by at least one test, and every
claim a test makes SHALL name a scenario that exists. This is the contract
between the plain-English review layer and the code layer: a scenario nobody
tests is a promise nobody keeps, and a test claiming a scenario that does not
exist is a link that has quietly rotted.

#### Scenario: Every scenario is claimed by a test

- **WHEN** the traceability guard runs against the specs and the tests
- **THEN** it reports no unclaimed scenarios

#### Scenario: An unclaimed scenario is reported

- **WHEN** a spec contains a scenario that no test claims
- **THEN** the guard names that scenario and fails

#### Scenario: A claim naming an unknown scenario is reported

- **WHEN** a test claims a scenario id that appears in no spec
- **THEN** the guard names that claim and fails
