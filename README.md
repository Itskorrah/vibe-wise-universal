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

Use Python 3.10+ and an existing learner project. From this source checkout:

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

| Host | Explicit entry point | Integration status |
|---|---|---|
| Claude Code | `/vibe-wise:learn`, `/vibe-wise:reset` | Native plugin; live parity pending |
| Codex | `$vibe-wise-learn`, `$vibe-wise-reset` | Native skills + trusted lifecycle hooks; live parity pending |
| OpenCode V1 | `/vibe-wise-learn`, `/vibe-wise-reset` | Separate V1 plugin; live parity pending |
| OpenCode V2 | `/vibe-wise-learn`, `/vibe-wise-reset` | Separate V2 plugin; live parity pending |
| Antigravity | Explicit VibeWise Learn / Reset skill | Dedicated native plugin; live parity pending |
| Antigravity without hooks | `/vibe-wise-learn`, `/vibe-wise-reset` | Manual restoration fallback |
| Other compatible agents | Installed `LEARN.md` / `RESET.md` | Portable/manual; dependable file access required |

[Exact host installation instructions](docs/installation.md) include plugin launch,
trust, invocation, explicit-resume fallback, diagnostics, updates and removal.
[Compatibility and evidence](docs/compatibility.md) distinguish deterministic tests
from actual model behaviour and record tested versions and limitations.

Shared notes stay in `.vibe-wise/profile.md`, `progress.md`, `project-map.md`.
Legacy `.sensible-vibes/` notes work in place without migration. Sequential host
switching is supported; concurrent note editing is not. No backend, database,
telemetry, separate teaching model, custom UI or additional product model calls.

## What it feels like

You're building a Notion-style notes app: users sign in, create and edit private
notes, and organize them into folders. Here, you're working through how notes and
folders relate—and what should happen when someone deletes a folder.

This condensed example is adapted from a real learning session. Later implementation
steps are illustrative; intervening design discussions are omitted.

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

You don't need to know the answer already. Claude can explain unfamiliar concepts, sketch the relevant pieces, and help you tackle a smaller question. You stay involved in forming the plan. Answer in plain English; ask for more help or say “skip” whenever you want.

Describing what you want sets the requirements. Build Checkpoints ask you to work
out how it should function; a feature preference doesn't approve an architecture.

| Checkpoint | What happens |
| --- | --- |
| **Build** | You reason through how to approach the problem with Claude. |
| **Design** | Review the design. **Confirm and continue** records it and continues planning; no code yet. |
| **Implementation** | Review the specific code changes. **Implement this step** authorizes Claude to make them. |

These aren't three mandatory stops. When ready to code, the Implementation
checkpoint also confirms the design, skipping a separate Design checkpoint.
Both confirmations offer **Discuss** to ask questions, clarify anything confusing,
or explore alternatives before deciding.

When Claude proposes additional implementation details, it separates them from your
decisions in a short list or table explaining each addition and why it matters.
You can question or change any item before proceeding.

After implementation, Claude briefly explains what changed, how the key code works,
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

Everyone reasons first. Claude adapts to what you demonstrate and how familiar you
are with the stack. Checkpoint frequency—Light, Normal, or Frequent—is separate.

- “Use fewer checkpoints.”
- “Focus on backend architecture.”
- “Use multiple-choice questions.”
- “Just implement this one.”
- “Pause learning.” Resume with `/vibe-wise:learn`.

Preferences, learning notes, and a project map live in `.vibe-wise/` in your project. Learning mode resumes in future sessions and after compaction. Add `.vibe-wise/` to your `.gitignore` to keep your notes out of Git; the plugin won't change it silently.

No extra account, backend, or telemetry. Saved notes are included in Claude's context, so your normal Claude Code data settings still apply.

To start learning this project from scratch, run `/vibe-wise:reset`. It shows the
project and asks **Cancel / Reset learning**. After confirmation, it backs up your
profile, progress, and project map inside the notes directory's `backups/` folder,
then restarts onboarding. Source code and other projects stay untouched. To change
your experience level or preferences, just tell Claude; no reset is needed.

## Updating

For automatic updates, open `/plugin` → **Marketplaces** → **vibe-wise** →
**Enable auto-update**. Auto-update is off by default for third-party marketplaces.
Claude Code notifies you after an update; restart Claude Code to load the new version.

To update manually, run these in your terminal:

```sh
claude plugin marketplace update vibe-wise
claude plugin update vibe-wise@vibe-wise
```

Then restart Claude Code. Your project learning notes stay intact; no reset is needed.
Run `claude plugin list` to check the installed version.
[More about plugin updates](https://code.claude.com/docs/en/discover-plugins#keep-plugins-updated).

## License

[MIT](LICENSE). You can use, modify, and share this software, including commercially. Keep the license notice with copies. The software comes without a warranty.
