## ADDED Requirements

### Requirement: Coding Session Links Are Not Disclosed

A commit, pull request, or issue authored with an AI coding agent SHALL name
the coding agent and the model, per *AI Authorship Is Disclosed*, but SHALL
NOT include a link to the private coding session or conversation that
produced it. The agent and the model are the reviewer's business; which
specific conversation produced a change is not — a session link identifies
more than either: an account, sometimes a device, always a private exchange
nobody but its participants agreed to publish.

#### Scenario: A pull request or issue contains no session link

- **WHEN** a coding agent opens or comments on a pull request or issue
- **THEN** its body names the coding agent and model but contains no link to
  the session or conversation that produced it

#### Scenario: A commit message containing a coding-session link is refused

- **WHEN** a commit message contains a link to a coding session or
  conversation
- **THEN** the commit is refused and the offending line is reported
