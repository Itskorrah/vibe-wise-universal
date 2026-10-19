# VibeWise Universal — Codex setup and run

## Copy into Codex

```text
In my currently open Codex project, use https://github.com/Itskorrah/vibe-wise-universal as the upstream capability. Read the latest README, existing project instructions and the applicable SKILL.md files. Inspect and preserve Git status, existing skills and host settings. Do the task now, not just a plan.

Use the upstream Python installer from a reviewed checkout to preview, then install the Codex learning skills into the open learner project (`python scripts/install.py install --host codex --project TARGET --dry-run`, then the supported install and doctor checks). Confirm the `$vibe-wise-learn` and `$vibe-wise-reset` entry points where the host supports them. Invoke learning mode for the actual codebase: introduce a short diagnosis of the next learning task, ask the learner what they want to understand, explain concepts and collaborate on the design. Do not implement application code before the learner's explicit implementation approval.

The learner designs, the agent assists. Installation is not approval to code, and automatic Git merge authorisation applies only to approved implementation tasks; setup changes may be delivered if verified. Never silently enable trust/hooks, reset learner context or bypass learning checkpoints.

Check actual local results, then follow the delivery contract below. Report what installed, what was invoked, tests and merge status.
```

## Reusable execution and delivery contract

- The **currently open Codex project** is the target; the linked GitHub repository is the upstream capability. Inspect both README and any AGENTS.md, skill definitions, host instructions, licence and exact installer semantics. Resolve paths from the real checkout and verify tools before running them.
- Check Git status, branch and remote. Preserve all unrelated changes, installed customisations, credentials and user data. Prefer project-scoped installation. Review untrusted downloads and never run unexpected upstream scripts or install unrelated skills.
- After executing an authorised task, locally validate behaviour and source changes. The user's copied prompt authorises committing verified scoped changes on a feature branch, pushing and opening a PR, and **merging automatically where permitted**. Respect stricter project-specific approval gates, branch protection, required reviews and security checks. No force-push, critical-defect merge, paid API spend, publication or deployment by implication.
- Do not rely on GitHub Actions; avoid dispatching hosted workflows during exhausted minutes and report unrun CI honestly. Do not claim host skill activation, real device verification or full product capability without evidence. If an essential input or permission is missing, complete safe setup, ask one focused question and leave a verifiable handoff.
