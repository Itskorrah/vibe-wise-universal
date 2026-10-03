# Compatibility and verification

Recorded 2026-10-03 on Windows, Python **3.13.5**, Node **24.1.0**.
SDK contract snapshots: **@opencode-ai/plugin 1.18.34** (V1) and
**@opencode/plugin 2.0.22** (V2). These are SDK versions, not tested OpenCode binaries.
CI passed Python 3.10/3.13 and Node 24.15 on Windows, Linux and macOS
([nine successful jobs](https://github.com/Itskorrah/vibe-wise-universal/actions/runs/37116119005)).

| Host / capability | Status | Evidence and limitation |
|---|---|---|
| Shared discovery, pause, partial onboarding pointers, legacy boundaries, reset | Verified | Deterministic Python tests. Behavioural understanding is not inferred from these tests. |
| Installation, update/remove ownership, config preservation, relocated helper resources | Verified | Real filesystem and process tests on Windows, Linux and macOS, locally and in CI. |
| Claude Code native plugin and startup/resume/clear/compact/fork contracts | Implemented but live verification pending | Installed hook commands and JSON contracts tested. Project-local CLI **2.1.288** attempted; OAuth session expired and could not refresh before a model request. Pre-existing global CLI **1.0.119** lacks current plugin CLI support. |
| Codex native lifecycle adapter and standalone skills | Implemented but live verification pending | Project-local CLI **0.160.0** authenticated; a model received the bootstrap via explicitly configured native hook, attempted the installed Learn guide, and kept code paused. Environment policy blocked every local file read, preventing full note restoration/parity tests. Global CLI **0.46.0** predates current packaging. |
| Codex bootstrap delivery under explicit test hook configuration | Verified | Actual model's guide-read attempt matches installed guide path supplied by the hook. This narrow result does not verify whole-history reads, onboarding or project discovery/trust. |
| Codex Desktop / IDE / Cloud conversational and lifecycle parity | Implemented but live verification pending | No isolated adapter conversation tested on those surfaces. CLI results do not establish parity. Cloud needs deployed helpers, file access and trusted hooks. |
| OpenCode V1 native plugin | Implemented but live verification pending | SDK typecheck plus request system/compaction/command tests; no installed authenticated OpenCode V1 host available. |
| OpenCode V2 native plugin | Implemented but live verification pending | Separate SDK typecheck, context/compaction/command/cleanup tests; no installed authenticated OpenCode V2 host available. |
| Antigravity native single-workspace plugin | Implemented but live verification pending | Documented PreInvocation protocol, actual installed command and sequential handover tests. No callable authenticated Antigravity CLI or controllable IDE conversation available in this run. |
| Antigravity automatic multi-workspace selection | Unsupported | No reliable active-workspace selector established in official event input. Ambiguous events remain quiet rather than choose the wrong project's notes. |
| Antigravity named compaction/startup/resume events | Unsupported | Not documented for this hook API. PreInvocation supplies transient bootstrap on every model request; live lifecycle evaluation remains pending. |
| Explicit resume on hosts with absent/untrusted hooks | Manual fallback | Complete skill/guide entry points; learner invokes Learn again after context loss. |
| Portable agents with dependable file access | Manual fallback | Complete local bundle and optional actual-target managed AGENTS.md block. No lifecycle API invented. |
| Persistent learning in chat-only/no-file-access environments | Unsupported | Markdown notes cannot be reliably read or written. |
| Concurrent cross-agent note editing | Unsupported | Sequential switching only; no lock/merge protocol claimed. |

## Tests actually executed

- Baseline `python -m unittest discover -s tests -v`: 37 tests, pre-existing Windows
  failures described in upstream-review.md.
- Expanded `python -m unittest discover -s tests -q`: **61 tests, passing, 7 skipped**
  due to Windows symlink creation privilege. The Windows junction protection test passed without that privilege. No application source is edited by tests.
- Cross-platform CI: all **9 jobs passed**. Each Python job ran 61 tests on
  Python 3.10/3.13. Windows CI had no skips; Linux/macOS skipped the single
  Windows-only junction test, exercising the symlink cases skipped locally.
  The three Node 24.15 jobs passed typechecking, all 6 bridge/plugin tests and
  the production-only dependency audit. The initial Windows 3.10 test harness
  omitted SystemRoot; retaining required Windows system paths fixed OS random
  initialization without changing the product or security configuration.
- `npm test`: **6 JavaScript tests passed**, including actual Python bridge execution.
- `npm run typecheck`: passed against both separately pinned native SDK contracts.
- Native hook command execution in installed bundles passed; this proves process/output
  contracts, not model compliance. Relocated helpers worked without source imports.
- Live Claude and Codex attempts as above. Raw local output is ignored under
  `.verification/`; published conclusions contain no credentials, learner transcripts
  or account details.

The Codex delivery test used a vetted fixture hook supplied by per-invocation config,
with the CLI's one-invocation hook-trust test flag. It did not persist trust or change
account/security configuration. Default project hook discovery and hook review must
still be evaluated in a trusted host project. Do not use that test flag as normal
installation advice. Policy rejection prevented complete guide/profile/map/progress
reads and therefore the remaining conversation scenarios were not marked verified.

## Remaining live evaluation protocol

Use an isolated learner repository; record host version/model, emitted restoration
context and relevant file diffs. Keep logs local and redact sensitive data before sharing.
Evaluate each host/surface independently with `docs/live-evaluation.md`.
Tests must check the model's actual reads and response, not just event notifications.

## Development dependency audit

The product's Python helpers and shared JavaScript bridge have no third-party runtime
dependencies. Typechecking uses published OpenCode SDK packages as dev dependencies.
V2 SDK imports are type-only; its typed plugin descriptor has no third-party runtime dependency. Full `npm audit` currently reports **12 high
transitive findings** in the V2 SDK's package-resolution graph, rooted in
`http-cache-semantics <=4.2.0`; the registry's latest version was 4.2.0 and no fixed SDK
release was established. The integration does not call that package-resolution API.
Do not treat a clean production-only audit as a clean full SDK dependency audit.
Update the SDK snapshot when a fixed official release exists; do not silently force an
unpublished package or rewrite host dependencies. No npm package/release was published.
