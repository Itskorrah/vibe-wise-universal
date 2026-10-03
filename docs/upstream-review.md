# Baseline and proposal review

Reviewed fetched source diffs, not just PR descriptions, on 2026-10-03.
No upstream proposal was merged or cherry-picked wholesale.

| Proposal | Reviewed head | Decision |
|---|---|---|
| [#3](https://github.com/nykooi1/vibe-wise/pull/3) | `7658e15e9cbe959b281218b01aa34ab5279f3b5e` | Reuse the documented Antigravity packaging/output idea. Reject its `invocationNum == 1` gate: official numbering starts at 0 and ephemeral context is transient. Reject choosing workspacePaths[0] in ambiguous events. |
| [#4](https://github.com/nykooi1/vibe-wise/pull/4) | `7bb2041635f308a330bd9f8866cc4471333ffc0c` | Codex's SessionStart output shape is valid, but the `source` field cannot identify the host (Claude also supplies it). Use a dedicated adapter and documented invocation policy/trust, not unused host guessing. |
| [#5](https://github.com/nykooi1/vibe-wise/pull/5) | `200b4e5c1b02ff8b79f5e05fee0c939f38673869` | Adapt the shared Python state extraction, project-contained paths, allowlist and self-contained bundle ideas. Its installer refuses all existing destinations and has no update/removal ownership or native OpenCode integrations; implement those separately. |
| [#6](https://github.com/nykooi1/vibe-wise/pull/6) | `197e8f95591b0d5b3e2a71c0e8a843278256fab6` | Correct Antigravity zero-based numbering and output shape, but first-invocation-only restoration cannot establish compaction parity. Repository-local AGENTS/Cursor rules do not install instructions in another learner project. Use actual-target managed blocks; preserve the more precise canonical checkpoint semantics. |
| [#7](https://github.com/nykooi1/vibe-wise/pull/7) | `a11a8ee8712cccff41442553d7c00c394c7cae6e` | Copilot's distinct output suggests keeping protocols separate. Copilot native support is outside scope; do not add environment guessing to Claude/Codex handlers. Other agents receive the portable bundle. |

Baseline test run: 37 tests; 30 failing assertions and 6 errors (including subtests)
on Windows. Most failures were `python3` absent from the isolated PATH and POSIX
variable expansion; errors were unavailable Windows symlink privileges. The test
harness now resolves its registration template and uses the current interpreter.
Windows privilege-dependent symlink cases skip explicitly; Unix CI exercises them.

The upstream demo in `docs/demos/notion-dupe.md` remains illustrative source material.
It is not evidence that this derived project's adapters passed live model evaluations.
