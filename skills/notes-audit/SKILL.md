---
name: notes-audit
description: Periodically audit each agent's notes file for size, clarity, repetition; surface skill candidates and reference-doc splits. Recommend only.
---

Runs against every `~/.agents/*-notes.md` file and anything linked under `~/.agents/notes/`. A new agent's file is picked up automatically. Local files only — via Codex directly or Cowork's `device_bash`.

`scripts/notes_signals.py [~/.agents]` runs first — read-only, no LLM calls: per-file line/word counts vs the size thresholds, dated-entry extraction, and difflib near-duplicate candidates (3+ dated entries within a file; matches across files). Reason from its output and the flagged bullets, not every file cold.

1. **Size**: use the script's `size_flag`; growth belongs in split-out topic docs, not the root.
2. **Clarity**: flag vague, unbounded, or now-contradicted statements — a later entry superseding an earlier one that isn't trimmed or marked stale.
3. **Repetition**: for each script-flagged group, confirm it's a real recurrence before reporting.
4. Recurring **task**-shaped group: report as a skill candidate, `weekly-skill-gap-review`'s shape — name, evidence, gap, proposed change, benefit, cautions. Do not create or edit a skill.
5. Recurring or oversized **reference material**: propose a split into `~/.agents/notes/<topic-slug>.md`, shared if more than one file touches the topic. Show the diff; do not apply it.
6. A `cross_file_candidates` match: note it once as a shared-notes candidate, not per-file repetition.
7. `$workflow-analysis`/`$mistake-analysis` cover workflow and git/store mistakes, not notes hygiene — don't fold their output in or query their store.

Output: one compact report, sectioned per file, plus cross-file findings from #6. Nothing here edits a notes file, its topic docs, or any skill; every action needs explicit confirmation to apply.
