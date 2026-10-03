# Implementation checklist

Baseline: upstream VibeWise 0.1.43, `1135f4ae8205da78404a71e85f567d5911da4e4d`.
Fork and upstream match. Branch: `feat/cross-agent-universal`.

- [x] Clone empty selected folder; verify remotes and inspect original guides/helpers.
- [x] Run baseline: 37 tests; Windows result 30 failing assertions / 6 errors
  (subtests included), from python3/shell assumptions and unavailable symlink privileges.
- [x] Fetch and inspect upstream PRs 3-7 and official host contracts.
- [x] Extract shared state/restoration/reset and generalize canonical guides.
- [x] Package Claude, Codex, separate OpenCode V1/V2, Antigravity, portable support.
- [x] Safe preview/install/update/remove and read-only diagnostics.
- [x] Deterministic adapter, ownership, relocation and cross-agent tests.
- [x] Attempt available live hosts in isolated fixtures; record exact gaps.
- [x] CI, installation, compatibility and attribution documentation.
- [x] Final diff review, passing local checks, commit, push and PR against fork only.
- [x] Check final cross-platform CI after repairing the Windows Python 3.10
  contract-test environment (preserve SystemRoot/WINDIR for OS initialization).

Do not activate Learn in this implementation session. Installation is not activation.
No releases, packages, merges, upstream writes or system configuration changes.

Current verification: 61 Python tests pass (7 Windows symlink privilege skips);
6 JavaScript tests pass; both SDK typechecks and Claude manifests pass.
Production-only npm audit: clean; full dev SDK audit has 12 upstream transitive
high findings with no established fixed release (see docs/compatibility.md).
Claude 2.1.288 live attempt blocked by expired OAuth. Codex 0.160.0 received
bootstrap but environment policy blocked file reads; full live parity pending.

Published pull request: https://github.com/Itskorrah/vibe-wise-universal/pull/1.
Initial CI passed eight of nine jobs: Python on Linux/macOS (3.10/3.13), Windows
3.13, and all three Node/SDK jobs. Windows 3.10 failed before hook execution
because the isolated test environment omitted SystemRoot; the harness now retains
only the necessary Windows system paths alongside its existing isolated values.
All nine jobs then passed on the repaired implementation commit:
https://github.com/Itskorrah/vibe-wise-universal/actions/runs/37116119005.
Windows CI exercised all 61 Python tests with no skips; Linux/macOS skipped only
the Windows-specific junction test. All three SDK/typecheck/bridge jobs passed.
OpenCode and Antigravity live sessions unavailable. No authentication/system
settings were changed. Tests and fixtures remain under ignored .verification/.
