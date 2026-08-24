---
name: workflow-analysis
description: Report on engineering-workflow health from git/GitHub activity and the worklist; recommend, never apply.
---

Separate lenses, run any subset via `lens=git|worklist|codex|claude|all` (default `all`).

**git**: `scripts/workflow_signals.py git <repo>` — commit cadence, revert rate, PR turnaround (open->first-review, open->merge), stale-branch count. Read-only, no LLM calls in the script itself.

**worklist**: `scripts/workflow_signals.py worklist <tasks.md path>` — open-item count, oldest unresolved item's age, items with an unresolved `blocker` annotation.

**codex**: defer entirely to the weekly-codex-usage-review and weekly-skill-gap-review automations (outside this catalogue) — do not re-derive Codex usage or skill-gap findings here; summarise their latest memory only.

**claude**: best-effort from the current session only, unless mistake-analysis's shared store has Claude-sourced records — this lens has no persistent cross-session log to draw on and must say so rather than imply full coverage.

Merge lens outputs into one compact report: metric, current value, trend if known, one-line concern. For a concern worth acting on, emit a `GO: <exact next step>` or `NOGO: <short reason>` per finding, in the same style as the workflow-improvement pipeline's recommender stage (outside this catalogue) — never edit skills, rules, or the worklist directly.
