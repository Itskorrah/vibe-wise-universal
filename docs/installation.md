# Installation and invocation

Use Python 3.10+ (`python` or `py -3` on Windows; `python3` on macOS/Linux).
No Python dependencies are required. JavaScript/TypeScript native adapter code runs
inside OpenCode's own plugin runtime. Node 24.15+ is recommended only for development
SDK checks. Everything stays local.

Run from the source checkout. Replace `/absolute/learner-project` with an **existing
absolute directory**. PowerShell examples may use `C:\dev\my-project` in quotes.
Do not install into the VibeWise source repository unless it is the learner project.

```sh
python scripts/install.py install --host codex --project "/absolute/learner-project" --dry-run
python scripts/install.py install --host codex --project "/absolute/learner-project"
python scripts/install.py doctor --host codex --project "/absolute/learner-project"
```

Use `--host claude`, `codex`, `opencode-v1`, `opencode-v2`, `antigravity`,
`antigravity-manual` or `portable`. Preview is read-only. Installation validates
all resources/destinations before writing. It copies only owned resources;
it does not change application files, models, permissions, credentials or Git.

Native hook commands use the current Python executable and the installed bundle
location. To use another installed Python, pass `--python "/path/to/python3"`.
Do not use a multi-word interpreter command such as `--python "py -3"`; pass the
actual interpreter executable. On Windows, hook destinations containing `%` or `!`
are rejected to avoid command-shell path expansion.

## Claude Code

Project-local installer copies a self-contained plugin to `.vibe-wise-bundle/claude`.
Start Claude from the **learner project**:

```sh
claude --plugin-dir "/absolute/learner-project/.vibe-wise-bundle/claude"
```

Then explicitly run `/vibe-wise:learn` or `/vibe-wise:reset`. If Python/hooks cannot
run, invoke Learn again to restore manually. Review the host's normal trust prompts.

The original marketplace installation remains available for this derived repository:
run `/plugin marketplace add Itskorrah/vibe-wise-universal`, then
`/plugin install vibe-wise@vibe-wise`. Choose **one** installation method, not both.
The marketplace preserves the `vibe-wise` plugin/command identity. Source manifests
use `python3`; the project installer is preferred on Windows because it selects the
actual interpreter. Do not interpret source-checkout demos as adapter verification.

## Codex

Default installation creates `.agents/skills/vibe-wise-learn` and `vibe-wise-reset`
entry points, the complete bundle in `.vibe-wise-bundle/codex`, and one identifiable
SessionStart fragment in `.codex/hooks.json`. Other hook groups are preserved.
Use a currently supported local Codex client and trust the project and hook definition
through Codex's own review UI. The installer does **not** grant trust. Existing inline
TOML hooks also run; check that another VibeWise installation is not registered there.

Restart Codex. Invoke `$vibe-wise-learn` and `$vibe-wise-reset`, or select them with
`/skills`. `allow_implicit_invocation: false` prevents unsolicited skill activation.
Native restoration handles documented startup, resume, clear and compact sources;
each event reloads current notes. No permanent session cache suppresses compaction.

If automatic hooks are unavailable/untrusted, install with `--manual` (skills only),
and explicitly invoke `$vibe-wise-learn` after restart, resume, clear, compaction or
agent switching. For very old clients without skills, ask in text: “Explicitly resume
VibeWise Learn; read `/absolute/project/.vibe-wise-bundle/codex/skills/learn/SKILL.md`.”
This fallback remains subject to host filesystem/tool permissions.

Native plugin packaging is also included (`plugin.json` OpenAI extension and legacy
`.codex-plugin/plugin.json`). For managed plugin distribution, package the repository
or copied bundle using [the official plugin workflow](https://developers.openai.com/plugins/build/plugins).
Use the plugin's `learn`/`reset` skills when choosing that installation method; do not
also register the project hooks/standalone skills. The project installer uses native
repo hooks so it can preserve configuration without altering account-level plugin
registries. Desktop, IDE and Cloud parity requires separate live tests.

## OpenCode V1

Install `--host opencode-v1`; restart OpenCode in the target project. The installer
adds `.opencode/plugins/vibe-wise.ts` and commands `vibe-wise-learn` / `vibe-wise-reset`.
Invoke `/vibe-wise-learn` or `/vibe-wise-reset`. Commands use `subtask: false`, preserve
the main conversation and command arguments, and reference the installed guides.

The plugin queries each event's session directory. It never assumes every session
shares the original load directory. No standalone skill directories are installed,
avoiding duplicate skill discovery. Existing agents, models, plugins and permissions
remain intact. If the experimental context hooks aren't available, explicitly request
Learn restoration again, pointing to `.vibe-wise-bundle/opencode-v1/skills/learn/SKILL.md`.

## OpenCode V2

Install `--host opencode-v2`; restart OpenCode. The separate native plugin under
`.opencode/plugins/vibe-wise/index.ts` registers the same `/vibe-wise-learn` and
`/vibe-wise-reset` commands through V2 transforms. It uses V2 session context and
compaction hooks, not V1 experimental hooks. The adapter exports the typed descriptor accepted by the published
`@opencode/plugin@2.0.22` contract (its Plugin.define function is an identity function).
SDK imports are type-only; no second runtime SDK or production npm dependency is installed.
No configuration is replaced, and no teaching subagent/model is introduced.

Remove V1 before installing V2 (or vice versa). The installer rejects simultaneous
local installations. Also remove any external/global VibeWise plugin registration
through its owning host before installing locally. If native loading is unavailable,
use the complete guide at `.vibe-wise-bundle/opencode-v2/skills/learn/SKILL.md` manually.

## Google Antigravity

Install `--host antigravity`. The self-contained native plugin is placed at the
documented workspace location `.agents/plugins/vibe-wise`; restart the host and inspect
its loaded skills/hooks in Customizations. Explicitly invoke the plugin's Learn or
Reset skill (mention “VibeWise Learn” / “VibeWise Reset” if command names differ by
surface). Installation or semantic discovery alone does not start onboarding.

The adapter uses Antigravity's own `PreInvocation` contract. Small ephemeral restoration
context is delivered on each model invocation because it is transient. This avoids
losing the bootstrap after compaction without fabricating a compaction event. Paused
profiles remain paused. Automatic restoration supports a single mounted workspace;
with multiple workspace paths, explicitly resume Learn in the relevant project.

For a surface without plugin hooks, remove the native installation and install
`--host antigravity-manual`. It uses `.agents/skills/vibe-wise-learn` and `vibe-wise-reset`
(current documented skill discovery) and the complete bundle. Explicitly invoke
`/vibe-wise-learn` or `/vibe-wise-reset`; after startup, resume or compaction, invoke
Learn again. Older hosts supporting `.agent/skills` but not `.agents/skills` can use
the portable guide directly; no undocumented lifecycle capability is claimed.

Do not install both native and manual Antigravity variants. Current documentation
prefers skills over deprecated workflows, so this project does not create workflows.

## Portable agents

Install `--host portable`, optionally `--instructions` to append a small managed
block to the **target project's** AGENTS.md. Existing instructions are preserved.
Open `.vibe-wise-bundle/portable/LEARN.md` to explicitly Learn/resume or `RESET.md`
to start the confirmed reset workflow. A host using another instruction filename can
reference those entry points manually; this installer does not guess or overwrite it.

After restart, resume, compaction or changing agents, read the guides again, read
profile/map, search the entire progress file and load complete pending sections.
You may run `scripts/context.py --cwd "/absolute/learner-project"` from the installed
bundle for read-only restoration instructions. Persistent state requires dependable
file access. Chat-only/no-files environments are unsupported for persistent notes.

## Maintenance

```sh
python scripts/install.py update --host codex --project "/absolute/learner-project" --dry-run
python scripts/install.py update --host codex --project "/absolute/learner-project"
python scripts/install.py remove --host codex --project "/absolute/learner-project" --dry-run
python scripts/install.py remove --host codex --project "/absolute/learner-project"
```

Doctor reports owned resources, config fragments, manual/native capability and live
verification limitations. “Healthy” means files/config match the manifest, not that
hooks are trusted or a model followed the learning loop. Modified owned files or
fragments stop update/removal so user edits can be preserved and reconciled. Keep the
manifest; it proves ownership. Extra files placed in an installed bundle are preserved.
Learner notes are never removed by uninstall. Managed config files may retain empty
objects after removing only the VibeWise fragment; unrelated contents stay intact.

The source checkout may be moved/deleted after installation. If the **target project**
moves, run update from this source at its new location to refresh absolute native
hook paths. When changing computers or interpreters, pass the new Python executable.
Windows deterministic tests ran locally. Cross-platform Python and OpenCode contract
checks passed in CI on Windows, macOS and Linux; see `docs/compatibility.md` for
versions, skips and the separate live-conversation verification gaps.
