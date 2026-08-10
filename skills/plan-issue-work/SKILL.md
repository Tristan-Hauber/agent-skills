---
name: plan-issue-work
description: Turn an implementation-ready issue into semantic commit units, dependencies, and safe execution waves.
---

Read the verified issue decision/ownership ledger/receipt, relevant linked decisions, repo instructions, and only missing code evidence. Plan only `target-owned`/`inherited` requirements. Dependencies may constrain or block but are not target work; `downstream`/`context` do not expand scope unless explicitly assigned. Verify fingerprints; do not reread unchanged source bodies. Use one `explorer` for nontrivial mapping, starting with symbols/changed paths before full files.

Resolve ambiguity first. Material semantic uncertainty requires a direct `Q#` under `Please answer:` with context, options, and recommendation. Same-session answers resume; only reversible implementation choices may be assumptions.

Derive semantic commit units before dependencies or execution waves; parallelism must not determine commit boundaries. Each item must be reviewable after prerequisites and leave a coherent state with focused validation. Keep tests/docs with the behaviour they validate. Split meaningful foundations, preparatory refactors, distinct behaviours, or platform/integration stages; do not split by file/layer, production-vs-tests, worker/review iteration, or into knowingly broken/incomplete states. Sequential items may overlap paths/symbols.

For each:
`ID | goal | depends: IDs/- | owns: paths/symbols | accept: checks | validate: commands`
For a nontrivial one-item plan add `Single-item rationale:`; same files/subsystem, sequentiality, or inability to parallelise are insufficient reasons.

Require an acyclic dependency graph and complete issue coverage. Then derive `Waves: [ready IDs] -> [next IDs] ...`. Only concurrently active items require non-overlapping ownership and one active owner per area. Do not pre-start dependent workers/worktrees; start them after prerequisites integrate from exact new `HEAD`. Respect configured concurrency; use no agent for a trivial task.

Return task lines, any single-item rationale, waves, assumptions, the full question block, and inspected evidence locations for the caller's receipt.
