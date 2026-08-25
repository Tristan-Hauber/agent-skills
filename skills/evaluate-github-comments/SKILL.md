---
name: evaluate-github-comments
description: Determine which selected issue or PR comments still require action, without changing anything.
---

Review only. Accept one target plus selected IDs/URLs, unresolved threads, comments since a ref/date, one author, or all comments, with an optional verified receipt.

1. Verify target revision/head and comment ID/updated-time fingerprints. Reuse unchanged selected comment bodies and code evidence; retrieve new/edited comments, necessary surrounding chronology, changed target/diff/checks, and relationship-bearing context only when the claim depends on it. For selected PR review threads, preserve/paginate thread ID, replies, resolution, outdated/path/line state; prefer configured connector/API and use GitHub GraphQL when flat comments omit thread state. Never infer unresolved from flat comments alone. If metadata cannot establish freshness, retrieve the affected material fully.
2. Use one `explorer` by default. Fetch metadata first. Soft-cap each injected fragment near 1,000 tokens; split/expand intentionally and never exceed 10,000 unless no safe alternative exists. Inject exact snippets rather than complete histories/logs unless conflicts require expansion. Preserve author, URL/ID, location, state, reviewed revision/head, and cutoff.
3. Cache evidence, not conclusions. Resolve each claim against current code, decisions, later comments, linked authoritative sources, and docs. Give exact evidence plus fingerprints—not prior conclusions—to a fresh high-reasoning read-only `default` reviewer.
4. Classify valid defects/questions, deeper implications, duplicates, conflicts, misunderstandings, suggestions, obsolete requests, and satisfied comments. Deduplicate centrally while mapping every selected comment. Current requirements and code outrank stale comment context.

Render fixer-ready `P#` defects and `N# | sources | satisfied|obsolete|duplicate:P#|unsupported|suggestion|superseded|conflict:Q# | evidence` dispositions. Put only unresolved decisions under `Please answer:` as direct `Q#` questions; no `NEXT`. Re-evaluate affected comments after answers.

Output findings/questions or `NO COMMENTS`, plus a receipt containing target revision/head, selected comment fingerprints/cutoff, linked evidence fingerprints, inspected locations, and result IDs. After emitting the receipt, automatically run `$github-review-learnings` with that receipt; it may record only settled, evidence-bounded learnings and must not change the review result.
