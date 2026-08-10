---
name: artifact-review
description: Verify that a prose artifact is accurate, current, coherent, and supported by evidence.
---

Review only; do not edit. Accept artifact, requirements, authoritative evidence, optional verified receipt, `kind=issue-draft|pr-description|documentation|other`, and `scope=auto|initial|delta|final` (`auto` default).

1. Pin the exact artifact revision plus authoritative-source fingerprints. Initial review reads the complete artifact; a verified repeat starts from the edited delta and affected claims. Unknown freshness or mismatched fingerprints invalidate dependent evidence.
2. Retrieve the artifact first, then only bounded source snippets needed to judge its claims. Reuse verified packets rather than refetching linked graphs or diffs; expand when a material claim cannot otherwise be established. Cache evidence, not conclusions. Keep fragments near 1,000 tokens and below 10,000 unless unavoidable.
3. Use a fresh high-reasoning read-only reviewer. Check claim/evidence fidelity, declared versus actual scope, internal cohesion, unnecessary/duplicated prose, unsupported certainty, stale references, repo rules, and preservation of meaningful human intent. Non-obvious load-bearing decisions need a discoverable *why* through wording/docs or a concise rationale comment only when the artifact format supports comments; never add commentary that merely restates content.
4. Apply the typed lens:
   - `issue-draft`: requirements, observable acceptance, decisions, assumptions, and dependency wording must match supplied evidence; do not substitute for `issue-review` or independently reread its full GitHub context.
   - `pr-description`: describe the final net change, current validation, deviations, and residual risk; remove claims about reverted or no-longer-present work and preserve unowned human sections.
   - `documentation`: keep source-of-truth/current-state claims and cross-references accurate; distinguish documentation delivery from implementation delivery and verify material external status metadata-first before deeper reads.
   - `other`: apply only the shared contract; do not invent a domain-specific checklist.
5. Before `CLEAN`, `scope=final` requires fresh reasoning over the exact complete current artifact, requirements, and verified authoritative evidence. Unchanged bytes may be reused, never old conclusions.

Render evidence-backed `P#`; put decisions under `Please answer:` as direct `Q#`; never emit `NEXT`. Return findings or `CLEAN` plus a receipt with artifact/source fingerprints, inspected ranges, kind, scope, and result IDs.
