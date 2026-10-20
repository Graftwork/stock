## Context

The previous change, `owner-opens-pull-requests`, wrote the rule that the agent
does not open pull requests and left the premise sentence as it found it,
naming "a pull request or issue body". Its design listed issues as a non-goal
because nobody had measured them. They have now been measured (see the
proposal), so the premise can be settled.

## Goals / Non-Goals

**Goals:**

- The requirement claims only what has been measured.
- Nothing that names a scenario breaks.

**Non-Goals:**

- Issue comments, issue updates and review comments. Only creation was tested.
  The requirement's first paragraph still governs what the agent writes there.
- The REST footer on issues. It links to `claude.ai/code`, not to a session, so
  it falls outside this requirement. If it should not appear on public issues
  either, the existing house rule already covers it: the agent does not open
  issues unasked.

## Decisions

- **Narrow the premise; do not extend the rule to issues.** Extending
  `SHALL NOT open pull requests` to issues would forbid something that leaks
  nothing, to guard against a leak measured twice as absent. *Alternative:*
  extend the rule "to be safe"; rejected because a rule that forbids harmless
  work gets worked around.
- **Keep the measurements out of the spec.** A requirement states what must
  hold; the ADR holds the dates, sample sizes and methods, which will go stale.
- **Keep both scenario titles byte-for-byte**, as before. The first still says
  "pull request or issue": it is about what the agent *writes*, which does
  cover issues.

## Risks / Trade-offs

- [Small samples, and creation only] → The ADR records both, and the
  requirement does not claim issues are safe, only that no session link was
  measured on them. A platform change would need the measurement repeated.
- [The sentence has no scenario of its own] → As before: no test can observe
  what the platform appends, and the declared gap says so.
