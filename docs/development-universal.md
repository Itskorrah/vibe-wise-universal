# Developing VibeWise Universal

Read `IMPLEMENTATION.md` for execution status. Product learning guides do not
activate Learn while maintaining the integration. The historical upstream development
record in `development.md` is preserved; its older pass counts and Claude conversation
reports are upstream history, **not verification of this derived project**.

```sh
python -B -m unittest discover -s tests -v
npm ci --ignore-scripts
npm run typecheck
npm test
npm audit --omit=dev
git diff --check
```

Python 3.10+; Node 24.15+ recommended. The two published SDKs are development-only
contract snapshots. Installed TypeScript uses type-only SDK imports; production
helpers need no npm or Python packages. Do not run live model tests in CI; they
require authenticated accounts and have separately documented evidence limits.

See architecture.md for extension points, host-contracts.md for official sources,
upstream-review.md for baseline/proposals, installation.md for managed ownership,
and compatibility.md for current tests and unresolved live evaluations.

To validate the Claude manifest without starting a model conversation:

```sh
claude plugin validate .claude-plugin/plugin.json
claude plugin validate .claude-plugin/marketplace.json
```

Validate a copied installed plugin too. Hook JSON tests cover process contracts;
actual model-visible delivery and subsequent note reads require live-evaluation.md.
