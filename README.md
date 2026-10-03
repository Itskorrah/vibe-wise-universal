<img src=".claude-plugin/icon.svg" alt="VibeWise brain with code brackets" width="96" height="96">

# VibeWise Universal

**You build. AI writes.**

A derived MIT version of [Noah Kim's VibeWise](https://github.com/nykooi1/vibe-wise),
with the same learner-owned design, teaching, checkpoints and local notes across
Claude Code, Codex, OpenCode V1/V2, Google Antigravity and portable coding agents.
The original attribution and demonstrations are preserved.

The learner designs; the agent explains unfamiliar concepts, helps when requested,
and implements only the agreed scope. Installation alone never starts learning.
Design confirmation is separate from implementation approval. Restarting, compaction
and switching hosts never approve code. Pause/resume and reset remain explicit.

## Get started

Use Python 3.10+ and an existing learner project. Clone this derived repository:

```sh
git clone https://github.com/Itskorrah/vibe-wise-universal.git
cd vibe-wise-universal
```

Choose your host below, then preview and install from this source checkout. This
example installs Codex support into a separate learner project:

```sh
python scripts/install.py install --host codex --project "/absolute/learner-project" --dry-run
python scripts/install.py install --host codex --project "/absolute/learner-project"
python scripts/install.py doctor --host codex --project "/absolute/learner-project"
```

In PowerShell, use a quoted path such as `"C:\dev\my-project"`. Use `python3` on
macOS/Linux if `python` is unavailable. Native hook commands use the actual interpreter.
Choose `claude`, `codex`, `opencode-v1`, `opencode-v2`, `antigravity`,
`antigravity-manual` or `portable`. Source checkout relocation/removal is safe after
installation. Updates and removal preserve unrelated content and learner notes.

All native integrations are **Implemented but live verification pending** for full
conversational parity. Their deterministic contracts are tested; the manual options
are **Manual fallback**. Installation does not activate Learn or grant hook trust.

| Host / installer value | Explicit entry point | Integration |
|---|---|---|
| Claude Code / `claude` | `/vibe-wise:learn`, `/vibe-wise:reset` | Native plugin |
| Codex / `codex` | `$vibe-wise-learn`, `$vibe-wise-reset` | Native skills and lifecycle hooks, subject to host trust |
| OpenCode V1 / `opencode-v1` | `/vibe-wise-learn`, `/vibe-wise-reset` | Separate V1 plugin |
| OpenCode V2 / `opencode-v2` | `/vibe-wise-learn`, `/vibe-wise-reset` | Separate V2 plugin |
| Antigravity / `antigravity` | Explicit VibeWise Learn / Reset skill | Dedicated native plugin, single workspace |
| Antigravity without hooks / `antigravity-manual` | `/vibe-wise-learn`, `/vibe-wise-reset` | Manual restoration |
| Other compatible agents / `portable` | Installed `LEARN.md` / `RESET.md` | Manual restoration; dependable file access required |

For Claude's project-local installation, launch from the learner project with
`claude --plugin-dir "/absolute/learner-project/.vibe-wise-bundle/claude"`.
For other native hosts, restart the host after installation and invoke Learn explicitly.
Choose one OpenCode version and one Antigravity installation method per project.

[Exact host installation instructions](docs/installation.md) include plugin launch,
trust, invocation, explicit-resume fallback, diagnostics, updates and removal.
[Compatibility and evidence](docs/compatibility.md) distinguish deterministic tests
from actual model behaviour and record tested versions and limitations.

Shared notes stay in `.vibe-wise/profile.md`, `progress.md`, `project-map.md`.
Legacy `.sensible-vibes/` notes work in place without migration. Sequential host
switching is supported; concurrent note editing is not. No backend, database,
telemetry, separate teaching model, custom UI or additional product model calls.

## Verification status

The deterministic suite passed all nine CI jobs on Windows, macOS and Linux, using
Python 3.10/3.13 and Node 24.15. Each Python job ran 61 tests; Windows CI had no skips,
while macOS/Linux skipped only the Windows-specific junction test. Six JavaScript
tests and separate OpenCode V1/V2 SDK typechecks passed.

Live attempts used Claude Code 2.1.288 and Codex 0.160.0. Claude authentication had
expired. Codex delivered restoration context to a model, but the environment blocked
file reads, so complete restoration and conversational parity remain unverified.
No authenticated OpenCode or Antigravity conversation was available. SDK snapshots
are V1 1.18.34 and V2 2.0.22; these are not tested OpenCode application versions.

See [CI runs](https://github.com/Itskorrah/vibe-wise-universal/actions/workflows/tests.yml)
and the [compatibility matrix](docs/compatibility.md) for evidence, unsupported
capabilities, live evaluation gaps and recorded development dependency findings.

## What it feels like

You're building a Notion-style notes app: users sign in, create and edit private
notes, and organize them into folders. Here, you're working through how notes and
folders relate—and what should happen when someone deletes a folder.

This condensed Claude example preserves the original learning experience. It is
adapted from a real learning session; later implementation steps are illustrative
and intervening design discussions are omitted. Numbered choices illustrate an
available question interface. On hosts without a permitted native question tool,
the agent asks clearly in text and waits for your explicit response.

**You:**

```text
A note can be in several folders. Deleting a folder should delete its notes.
```

**Claude:**

```text
✦ Build checkpoint: Deleting a shared note

"Trip ideas" is in both Travel and Summer. Deleting it removes it from both.

When someone deletes Travel, what should happen to that note in Summer?
```

**You:**

```text
Keep it in Summer. If it has no folders left, keep the note outside any folder.
```

**Claude:**

```text
That separates deleting a folder from deleting a note.

✦ Build checkpoint: Connecting notes and folders

How would you represent which folders a note belongs to, without copying the note?
```

**You:**

```text
A links table with note_id and folder_id. Deleting a folder removes its links,
not the notes.
```

**Claude:**

```text
Each link records one membership. Several links can point to the same note;
a note with no links is unfiled.

notes ← folder links → folders

✦ Design checkpoint: Folder membership

Proposed: store notes once and track folder membership in a links table.
Deleting a folder removes its links and keeps the notes. This supports multiple
folders per note; loading a folder's notes needs a lookup through those links.

Confirming records this design. We still need to work through access rules
and technology choices before writing code.

❯ 1. Confirm and continue
     This approach makes sense to me; move to the next piece.
  2. Discuss
     Ask questions or clarify anything that doesn't make sense before deciding.
```

**You:**

```text
Confirm and continue.
```

*Later, after the remaining choices for this step are worked through...*

**Claude:**

```text
✦ Implementation checkpoint: Folder membership

I'll add the agreed tables and folder-deletion operation, then test that deleting
a folder preserves its notes and their membership in other folders.
This step builds storage behavior; the UI comes later.

❯ 1. Implement this step
     This approach makes sense to me; write the code for this step.
  2. Discuss
     Ask questions or clarify anything that doesn't make sense before deciding.
```

**You:**

```text
Implement this step.
```

*Claude writes the code and runs the tests.*

**Claude:**

```text
✦ Implementation report: Folder membership

- Added the schema migration: each membership references one note and one folder.
- Added folder deletion: removes the folder and its links, preserving note content.
- Added and ran tests for shared notes and notes left without a folder; both passed.
```

You don't need to know the answer already. Your agent can explain unfamiliar
concepts, sketch the relevant pieces, and help you tackle a smaller question.
You stay involved in forming the plan. Answer in plain English; ask for more help
or say “skip” whenever you want.

Describing what you want sets the requirements. Build Checkpoints ask you to work
out how it should function; a feature preference doesn't approve an architecture.

| Checkpoint | What happens |
| --- | --- |
| **Build** | You reason through how to approach the problem with your agent. |
| **Design** | Review the design. **Confirm and continue** records it and continues planning; no code yet. |
| **Implementation** | Review the specific code changes. **Implement this step** authorizes the agent to make them. |

These aren't three mandatory stops. When ready to code, the Implementation
checkpoint also confirms the design, skipping a separate Design checkpoint.
Both confirmations offer **Discuss** to ask questions, clarify anything confusing,
or explore alternatives before deciding. Discuss keeps implementation paused.

When your agent proposes additional implementation details, it separates them from your
decisions in a short list or table explaining each addition and why it matters.
You can question or change any item before proceeding.

After implementation, your agent briefly explains what changed, how the key code works,
why it fits your decision, any tests it added or updated and what they cover, and
which checks ran with their results. Ask to dig deeper anywhere it's unclear.

Small diagrams help you trace data, understand relationships, and see how the system fits together.

## Make it yours

Experience changes the support you get, not your ownership of decisions:

| Level | Teaching approach |
| --- | --- |
| Beginner | Explain unfamiliar pieces, use diagrams, ask smaller reasoning questions. |
| Intermediate | Less introductory context; explore interactions and tradeoffs. |
| Advanced | Probe difficult constraints, failure modes, and design assumptions. |

The agent asks for your approach before consequential design and adapts to what you
demonstrate and how familiar you are with the stack. You can explicitly skip or
request direct implementation. Checkpoint frequency—Light, Normal, or Frequent—and
question style are separate preferences.

- “Use fewer checkpoints.”
- “Focus on backend architecture.”
- “Use multiple-choice questions.”
- “Just implement this one.”
- “Pause learning.” Resume explicitly with your host's Learn entry point above.

Preferences, evidence-based learning notes, and a project map live in `.vibe-wise/`
in your project. Native hooks restore pointers to these notes when available and
trusted. Otherwise, invoke Learn again after restarting, resuming, compaction or
switching agents. Paused mode stays paused; restoration never grants implementation
approval or invents completed onboarding answers. Add `.vibe-wise/` to your
`.gitignore` to keep your notes out of Git; the installer won't change it silently.

Saved notes enter your coding agent's context, so that host's normal data settings
still apply. VibeWise adds no separate account or model service.

To start learning this project from scratch, invoke your host's Reset entry point.
It previews the selected project and notes, then asks **Cancel / Reset learning**.
Confirmation is tied to that target and its note contents; stale confirmation is
rejected. Complete backups of the profile, progress and project map are made inside
the notes directory's `backups/` folder before active notes are replaced. Fresh
onboarding starts only after successful reset. Failures report what happened and
any backup location. Source code and other projects stay untouched. To change your
experience level or preferences, tell your agent; no reset is needed.

## Updating

For installer-managed bundles, pull the latest source and preview an update:

```sh
git pull --ff-only
python scripts/install.py update --host codex --project "/absolute/learner-project" --dry-run
python scripts/install.py update --host codex --project "/absolute/learner-project"
python scripts/install.py doctor --host codex --project "/absolute/learner-project"
```

Use the same host and target project as installation, then restart the host.
Ownership manifests protect unrelated configuration and learner notes. Updates or
removal stop if an owned file or managed fragment has been edited; reconcile those
changes before retrying. If the learner project moves, update at its new location
to refresh absolute hook paths. The source checkout can be moved or removed after
installation; keep or obtain a source checkout for future maintenance.

To remove only the integration:

```sh
python scripts/install.py remove --host codex --project "/absolute/learner-project" --dry-run
python scripts/install.py remove --host codex --project "/absolute/learner-project"
```

Uninstall preserves learning notes. It does not perform a learning reset.

For the alternative **Claude marketplace installation**, keep using its own update
workflow. Do not install both the marketplace plugin and an installer-managed copy.

To update manually, run these in your terminal:

```sh
claude plugin marketplace update vibe-wise
claude plugin update vibe-wise@vibe-wise
```

Then restart Claude Code. Your project learning notes stay intact; no reset is needed.
Run `claude plugin list` to check the installed version.
[More about plugin updates](https://code.claude.com/docs/en/discover-plugins#keep-plugins-updated).

## Development and architecture

Canonical guides live in `skills/learn/` and `skills/reset/`. Shared deterministic
helpers live in `vibe_wise/`; small host adapters live in `adapters/`. Additional
hosts can reuse the learning system and Markdown state without duplicating guides.

```sh
python -m unittest discover -s tests -q
npm ci --ignore-scripts
npm test
npm run typecheck
```

Python helpers use the standard library. Node 24.15+ and the pinned development SDKs
are needed for adapter checks, not portable bundle use. See
[architecture](docs/architecture.md), [development](docs/development-universal.md),
[host contracts](docs/host-contracts.md), and [live evaluation](docs/live-evaluation.md).

## License

[MIT](LICENSE). You can use, modify, and share this software, including commercially. Keep the license notice with copies. The software comes without a warranty.

Derived from [VibeWise by Noah Kim](https://github.com/nykooi1/vibe-wise), baseline
0.1.43 at `1135f4ae8205da78404a71e85f567d5911da4e4d`. Original copyright notices
and attribution are preserved. This repository is maintained as a separate derived
project; it does not modify the original upstream repository.
