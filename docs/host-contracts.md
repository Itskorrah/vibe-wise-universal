# Official contracts consulted

Reviewed 2026-10-03. These pages establish supported APIs, not live verification.

| Host | Primary sources | Contract used |
|---|---|---|
| Claude | [Hooks reference](https://code.claude.com/docs/en/hooks), [Plugins](https://code.claude.com/docs/en/plugins) | SessionStart sources and hookSpecificOutput.additionalContext; plugin skills and explicit commands. |
| Codex | [Build skills](https://learn.chatgpt.com/docs/build-skills), [Hooks](https://learn.chatgpt.com/docs/hooks), [Package plugins](https://developers.openai.com/plugins/build/plugins) | agents/openai.yaml invocation policy; current SessionStart sources; reviewed/trusted non-managed hooks; extra developer context after compaction; repo-local hooks and plugin manifests. |
| OpenCode V1 | [Plugins](https://opencode.ai/docs/plugins/), [Commands](https://opencode.ai/docs/commands/), published `@opencode-ai/plugin@1.18.34` and its SDK type declarations | Plugin function, experimental system transform and compacting hooks, session.get(path.id).data.directory; commands without subtask. |
| OpenCode V2 | [Plugins](https://opencode.ai/v2/docs/build/plugins), [Migration](https://opencode.ai/v2/docs/build/plugins/migrate-v1), published `@opencode/plugin@2.0.22` and schema declarations | Plugin.define descriptor shape, scoped session context/compaction hooks, command transform, session.get({sessionID}).location.directory, registration cleanup. |
| Antigravity | [Skills](https://antigravity.google/docs/skills), [Plugins](https://antigravity.google/docs/plugins), [Hooks](https://antigravity.google/docs/hooks/), [Workflow migration](https://antigravity.google/docs/migration/workflows-to-skills) | .agents/plugins and .agents/skills discovery; zero-indexed PreInvocation; workspacePaths; transient ephemeralMessage; no established selected-workspace or compaction event. |

Native question tools are used only when both available and permitted for that
question. Codex modes may restrict question tools. Text plus an explicit answer
is always supported; permissions to use file/shell tools do not approve teaching
checkpoints or reset operations. Adapters never simulate a native picker.
