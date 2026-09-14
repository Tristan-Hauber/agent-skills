# skill-review — canonical

This is the canonical `skill-review` package selected after iterative testing on 14 September 2026.

It uses the **v3 review engine** as its behavioural base because v3 produced the strongest observed
medium-effort benchmark result. Later experiments added useful infrastructure, but progressively larger
instruction sets did not improve recall reliably. The canonical version therefore keeps v3's lean
discovery architecture and carries forward only the later changes that were judged worth their
attention cost.

## Default

**Skill effort defaults to `medium`.**

That means every non-trivial skill receives two genuinely independent discovery contexts when the
current harness can provide them.

Skill effort is separate from model-specific thinking/reasoning depth.

## Canonical architecture

Medium review uses:

1. neutral package grounding;
2. an independent **operational adversary**;
3. an independent **effectiveness adversary**;
4. candidate consolidation and narrow validation;
5. a small scope/fallback/consistency check;
6. reporting with explicit assessment limits and worker-token accounting where available.

Default medium does **not** run a benchmark.

## Later improvements retained

The canonical version keeps these post-v3 improvements:

- cross-agent wording and capability-based worker handling;
- primary active target versus alternate same-name copy distinction;
- hard prerequisite versus optional-dependency distinction;
- calibrated language for algorithmic blind spots;
- one cheap cross-finding execution-consistency check;
- separate main/worker token reporting;
- self-benchmark infrastructure containing both archived `quick-code-review` copies;
- precision traps as well as positive expected findings.

It deliberately does **not** retain the large execution-contract/checklist expansions from v4–v6.

## Review principles

The six review-skill principles behind this package are:

1. Separate discovery from validation.
2. Spend additional review budget primarily on independent search.
3. Share neutral grounding, not conclusions.
4. Model recall explicitly: ask what important result classes the strategy can systematically miss.
5. Use behavioural evaluation when static inspection cannot establish effectiveness.
6. Keep validity, impact, and priority separate.

Additional generic skill-design principles used here:

- separate deterministic grounding from judgement;
- every material extra cost should buy new information, independent search, or resolution of a
  concrete uncertainty;
- judgement-heavy skills need behavioural evidence where static inspection cannot establish
  effectiveness;
- keep epistemic confidence separate from importance;
- treat executable helpers as part of the instruction system;
- resolve package identity as well as content;
- prefer a few load-bearing invariants over long checklists that compete for model attention.

## Self-benchmark

`benchmarks/old-quick-code-review/` is a benchmark for **skill-review itself**.

It contains two exact archived packages supplied during development:

- `target/` — the active `.claude/skills/quick-code-review` package;
- `alternate/` — the divergent `.agents/skills/quick-code-review` package.

It also contains a small repository-routing fixture, expected confirmed findings, known
false-positive/calibration traps, fixture hashes, a result template, and the historical version
scorecard.

The benchmark is not run during ordinary medium reviews.

Use it when:

- explicitly testing `skill-review` with `--behavioural`;
- using `ultra`;
- evaluating a structural/algorithmic change to `skill-review`.

Do not expose `expected-findings.md` to discovery reviewers before their review is complete.

## Current observed champion result

The development configuration was Sonnet 5 with Medium model thinking and `skill-review medium`.

Historical results:

| Version | Primary recall | Secondary recall | Time | Effective message tokens |
|---|---:|---:|---:|---:|
| v3 | **4/4** | **2/2** | 5m20s | 47.2k main; worker usage was not captured |
| v4 | 3/4 | 1/2 | 6m15s | ~189.9k |
| v5 | 1/4 | 1/2 | 7m55s | ~198.1k |
| v6 | 3/4 | 1/2 + one new confirmed secondary finding | 5m40s | ~197.9k |

V3 remains the observed local maximum and is the runtime base of this canonical package.

Because v3's worker usage was not captured, its total token cost cannot be compared directly with
later versions.

## Maintenance policy

Treat this package as **frozen by default**.

Revisit it when one of these occurs:

- a real-world review exposes a material false negative or false positive;
- repeated normal use exposes a meaningful cost/pathology;
- your baseline model changes;
- your main harness changes;
- the skill's required capabilities or workflow materially change.

A new model merely being released is not by itself a reason to edit the skill. If you are considering
adopting a new model/harness, rerun the existing benchmark first with the skill unchanged. Edit only if
the new environment exposes a concrete problem or opportunity.

Do not reopen the skill merely because another theoretical improvement can be imagined.

## Effort calibration

The benchmark may also be reused to calibrate `low`, `medium`, and `high` on the same immutable
fixture. Do not create a separate benchmark merely because the effort level differs.

The recommended production default remains **medium** until evidence supports changing it.

## Package layout

```text
skill-review/
├── SKILL.md
├── README.md
└── benchmarks/
    ├── README.md
    └── old-quick-code-review/
        ├── README.md
        ├── expected-findings.md
        ├── results-history.md
        ├── results-template.md
        ├── fixture-manifest.sha256
        ├── target/
        ├── alternate/
        └── fixture-repo/
```
