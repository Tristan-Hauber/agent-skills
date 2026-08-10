---
name: issue-review
description: Verify that an issue or draft is complete, current, and ready to implement.
---

Review only; do not edit. Accept an optional verified evidence/review receipt.

1. Build a decision/ownership ledger from issue/comments, then relationship-bearing parents/links and project/spec/ADR/repo sources. Classify material requirements/sources as `target-owned`, `inherited`, `dependency`, `downstream`, or `context`. Target-owned/inherited define acceptance. Dependencies may block; downstream/context constrain but do not expand acceptance unless the target/applicable parent incorporates them. Shared terminology or semantic proximity is not ownership evidence.
2. On repeats verify IDs/update times or hashes, fingerprints and inspected locations; fetch only changed/new/edited/incomplete material. Unknown freshness invalidates affected evidence. Cache evidence, not conclusions. Use one `explorer`. Give a fresh high-reasoning read-only `default` exact snippets/IDs/fingerprints with permission to expand. Metadata first; target 1,000 tokens/fragment and never exceed 10,000 unless unavoidable.
3. Precedence: issue decisions; later maintainer/owner comments; inherited parent scope; linked items only for their relationship; project/repo rules; code as feasibility evidence, not intent. Conflicts become questions.
4. For dependency/ownership references material to readiness or acceptance, verify status, owner, delivered scope, and source-of-truth metadata-first; a closed/reference state alone is not proof. Do not fetch linked diffs unless cheaper bounded evidence cannot establish what shipped or a cross-item contract needs implementation detail. Documentation-only delivery cannot satisfy implementation acceptance unless explicitly documentation-only. Before a `P#` claims missing acceptance, cite the target/applicable-parent assignment; dependent/downstream sources alone are insufficient.
5. Check clarity, completeness, feasibility, observable acceptance, dependencies, and applicable behaviour/failure/UX/data/safety/performance/compatibility/rollout/tests/docs. Guards/predicates need risk-proportionate falsifiable coverage of allowed and disallowed paths. Localisation needs each touched key or documented fallback in every supported locale plus neighbouring/glossary consistency, preserving regional variants. Swift repos: check established architecture, actor, and ownership boundaries. Deduplicate, require evidence, omit taste-only comments, and do not ask anything already answered.

Render supported `P#` with evidence, consequence, required change, and validation. Put genuine decisions under `Please answer:` as directly answerable `Q#` with checked-source context, options, and useful recommendation. Never ask the user to “answer P#”, emit `NEXT`, or require another invocation.

Output findings/questions or `CLEAN`, plus a receipt with source fingerprints/cutoffs, decision/ownership-ledger hash, inspected locations, review scope, and result IDs. Old results remain advisory.
