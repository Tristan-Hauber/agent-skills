# skill-review benchmarks

These benchmarks measure **skill-review itself**.

## Portfolio roadmap

Build breadth before depth:

| Category | Status | Current benchmark |
|---|---|---|
| Review / critique | **Populated** | `old-quick-code-review/` |
| Creation / transformation | Unpopulated | — |
| Orchestration / workflow | Unpopulated | — |
| Retrieval / research | Optional future | — |
| Action / mutation | Optional future | — |
| Selection / routing / decision | Optional future | — |

The priority initial portfolio is **one review + one creation/transformation + one orchestration**
benchmark. Do not add several review-skill fixtures merely because they are readily available.

A later category should be added when an actively used skill exercises a materially different failure
mode that the existing portfolio does not test.

## Formal benchmarks versus candidate evidence

A formal benchmark needs:

- immutable inputs/fixture;
- enough confirmed expected behaviour or findings to score meaningfully;
- useful false-positive traps where available;
- a repeatable protocol;
- model/harness/effort metadata;
- measured wall-clock runtime and token usage where available.

Interesting but immature cases belong in `candidate-evidence.md`. Candidate evidence can record
potential failure classes and later confirmation/rejection without changing benchmark scores or
freezing premature ground truth.

## Evaluation axes

Keep these separate:

1. **Behavioural quality/correctness**
   - for review skills: important confirmed findings recovered, important misses, false positives and
     material overstatements;
   - for general skills: whether the promised behaviour/output is correct.
2. **Total effective message tokens**
   - main/orchestrator plus all worker/sub-agent usage when exposed.
3. **Wall-clock runtime**
   - elapsed time for the same benchmark protocol.

Equivalent quality in less time is a win. Equivalent quality with fewer tokens is a win. Lower cost or
runtime does not compensate automatically for a material behavioural regression.

## Current formal benchmark

`old-quick-code-review/` contains an archived review-skill package with confirmed expected findings
and known precision traps.

Keep fixture bytes immutable, hide expected findings during discovery, and record model, harness,
model reasoning depth, skill effort, wall-clock runtime, and worker/main token usage separately.
