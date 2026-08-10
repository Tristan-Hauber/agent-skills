---
name: test-review
description: Verify that changed tests prove their claims, add distinct coverage, and avoid unnecessary seams or scaffolding.
---

Review only; do not edit. Accept changed behaviour/tests/seams, requirements, and optional verified evidence/review receipt.

1. Pin the target revision/worktree. Use fresh high-reasoning read-only review. Start from changed production behaviour and any changed test hunks. Verify/reuse fingerprints; cache evidence, not conclusions. Search nearby tests by behaviour/symbol/name before broader suite reads; expand only for equivalent coverage or the real boundary. Keep fragments near 1,000 tokens and below 10,000 unless unavoidable.
2. **Claim fidelity:** every behaviour named must be created by setup and observed by assertions. Flag injected/precomputed decisions. Ask whether breaking each material claim makes the test fail; changed guards/predicates need risk-proportionate falsifiable allowed and disallowed coverage.
3. **Boundary fidelity:** seams may replace effects/hard dependencies, not the production decision. Critical wiring needs coverage at the smallest practical production action boundary; prefer existing practical integration boundaries over bespoke seams; if removed/bypassed wiring could stay green, require focused mutation evidence without mutating the reviewed worktree.
4. **Cohesion/cost:** keep one coherent behavioural contract per test; split independently meaningful/failing contracts, not multiple assertions. Challenge helpers, funcs, types, spies, fixtures, protocols, or production seams that add no observability, controllability, architectural boundary, reuse, clearer failure signal—or bypass real inputs.
5. **Coverage value:** compare nearby coverage semantically. Flag additions with no distinct condition, boundary, regression, failure signal, or useful layer. Preserve intentional unit/integration/UI/platform overlap and dedicated regressions. When valuable overlap or unusual scaffolding could look redundant, make the durable reason discoverable through naming/structure/docs or a concise *why* comment; never restate the test.

Render evidence-backed `P#`; put decisions under `Please answer:` as direct `Q#`; never emit `NEXT`. Return findings or `CLEAN` plus a receipt with fingerprints, inspected tests/production ranges, coverage comparisons, and result IDs.
