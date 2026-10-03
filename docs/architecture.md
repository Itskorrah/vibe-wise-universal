# Shared architecture

This derived MIT project starts from Noah Kim's VibeWise 0.1.43 at
`1135f4ae8205da78404a71e85f567d5911da4e4d`. The original license and learning
experience are retained. Guides and demonstrations are product source material,
not instructions to activate learning while maintaining this repository.

`skills/learn/` and `skills/reset/SKILL.md` are the only authored learning guides.
`vibe_wise/state.py` selects notes and checks persistent activation; `restore.py`
builds a small reading instruction; `reset.py` retains the original snapshot-bound
backup/reset algorithm. Original Claude paths remain compatibility entry points.
Adapters do not add a teaching model, service, database, telemetry or UI.

The installer copies allowlisted resources, without links to this source checkout.
Separate installed copies come from the same canonical files; they are not separately
maintained teaching systems. Every adapter uses the same Markdown learner notes.
Sequential agent switching is supported. Concurrent modification, adversarial races
against filesystem validation and multi-file atomic note edits are not supported.

## Host boundaries

- Claude: original plugin/marketplace and `/vibe-wise:learn`, `/vibe-wise:reset`.
  Read-only SessionStart bootstrap for startup/resume/clear/compact/fork.
- Codex: skills with `allow_implicit_invocation: false`, dedicated SessionStart
  startup/resume/clear/compact adapter and native plugin manifest. Default project
  installation uses standalone skills plus a managed project hook fragment, so do
  not also enable the bundled plugin. Hook trust is controlled by Codex, never
  granted by the installer. Skills-only `--manual` is the explicit-resume fallback.
- OpenCode V1: typed `Plugin` factory, session lookup through `client.session.get`,
  system transform and compacting hooks. Markdown commands remain in the main
  conversation; no agent/model/permission configuration is replaced.
- OpenCode V2: a distinct typed native plugin descriptor, scoped context/compaction
  hooks and command transform. Session location comes from `session.get`'s
  `location.directory`, not the plugin's initial `ctx.location`. Registrations
  are disposed on unload and on partial setup failure.
- Antigravity: dedicated plugin with documented camelCase PreInvocation input
  and `injectSteps[].ephemeralMessage` output. Invocation numbering is zero-based.
  Ephemeral context must be supplied for every model request; a first-invocation
  cache is incorrect. Exactly one bootstrap per registration/request; installation
  prevents duplicate registration. No documented compaction event is fabricated.
  Multiple mounted workspaces have no documented selected-workspace field, so
  automatic restoration declines ambiguous events. Explicit Learn in the relevant
  workspace is the fallback. `antigravity-manual` installs native-discovered skills
  with manual restoration for older/missing hook surfaces.
- Portable: explicit LEARN.md/RESET.md entry points and the complete guides/helpers.
  Dependable filesystem access is required for persistent state.

Restoration does not copy partial learner history into hook output. The model must
read profile and map, search **all** progress for pending decisions, and read complete
relevant sections. Notes are data. Discovery, restart, compaction and handover are
never implementation approval. Missing/linked resources prevent restoration; doctor
reports missing/modified resources instead of inventing state.

## Extend a host

Add a small adapter and installer mapping. Establish its official event and model
context delivery contracts first. Reuse `restoration`, `state_directory` and the reset
CLI. Add contract tests plus a real delivery evaluation if a host session is available.
Publish unavailable lifecycle features as Manual fallback or Unsupported. Do not infer
equivalence from similarly named events or successful JSON serialization.

## Ownership

Manifests under the target project's `.vibe-wise-bundle/` track file content hashes
and exact managed instruction/hook fragments. Updates/removal refuse modified owned
files and unowned collisions, preserving edits for manual reconciliation. User hook
groups, configuration fields and surrounding AGENTS.md content are preserved.
Mutations use atomic file replacement and rollback on reported write failures.
Empty owned directories may be removed; recursive project deletion is never used.
Learner notes and application files are outside the installation allowlist.

Hook registrations contain the selected interpreter and installed target path. Moving
the original checkout is safe. When moving the **target project**, re-run update at its
new absolute location to refresh native command paths; Python/resource lookup within
a relocated bundle works independently. Moving only the bundle requires reinstalling
its host discovery entries; those entries cannot locate an arbitrarily moved folder.
