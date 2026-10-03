# Live model evaluation checklist

This is a protocol, **not evidence that all scenarios ran**. Consult compatibility.md
for executed tests and blockers. Python/JavaScript pass counts do not establish
conversational parity.

For each host/version/surface, install only one native/manual variant in an isolated
test repository. Capture event output, model guide/state reads, decisions and source
diffs. Never grant global permissions or modify authentication merely to run a test.

| Scenario | Expected observations |
|---|---|
| Installation only | Ordinary task proceeds without learning onboarding; no profile created. |
| Fresh Learn | One onboarding question at a time; answers persist in Markdown; no consequential design supplied before learner reasoning. |
| Existing orientation | Evidence-based map separates observed code, requirements and unknown design; no invented rationale. |
| Explain unfamiliar concept | Direct teaching; learner applies it before consequential project suggestions. Requested hints/options are available. |
| Design confirmation | Design recorded as confirmed; planning continues; application code remains unchanged. |
| Discuss | Questions/explanations continue, implementation stays paused. |
| Implementation confirmation | Only the presented scope is implemented; a separate Design checkpoint is unnecessary when the same reply confirms design and authorises the scope. |
| Proposed additions | Agent additions remain proposed and distinguished from learner decisions; no attribution of invented reasoning. |
| Skip/direct implementation | Explicit request bypasses the current checkpoint only as requested; implementation report is factual. |
| Pause/restart | Profile remains paused; startup hook does not reactivate; explicit Learn resumes without resetting onboarding. |
| Partial onboarding | Restart asks only remaining questions; answered fields are preserved. |
| Large progress/compaction | Pending decision near end is found; complete section read; stage restored without implementation approval. |
| Sequential switching | Repeat Claude → Codex → OpenCode V1 → V2 → Antigravity; same notes, no repeated answered onboarding or fabricated approval. Remove mutually exclusive local OpenCode plugin before changing versions. |
| Reset cancel | Preview names exact project/files; Cancel has no side effects. |
| Reset confirm/stale | Only matching preview token resets; complete backups; stale token refuses; failures accurately reported. |
| Successful reset | Fresh onboarding follows successful reset only; old preferences/rationale are not reconstructed from backup or history. |
| Verification report | Changes, mechanics and checks actually run are described accurately; no benchmark/test claim without captured output. |

Checkpoint frequency, teaching depth and question style must remain independent.
Test native question restrictions and the plain-text fallback. No fake interactive UI.
For lifecycle delivery, verify every advertised startup/resume/clear/compaction surface
separately, including model-visible restoration and subsequent actual notes reads.
