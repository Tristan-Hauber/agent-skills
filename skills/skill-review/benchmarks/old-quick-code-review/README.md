# Benchmark: old quick-code-review

## Purpose

Measure whether `skill-review` can discover concrete operational defects and algorithmic blind spots
in a realistic review skill while avoiding known false-positive traps.

This benchmark measures **skill-review itself**.

## Fixture

- `target/` — exact archived `.claude/skills/quick-code-review` package supplied during development.
  This is the primary review target.
- `alternate/` — exact archived divergent `.agents/skills/quick-code-review` package. It is
  package-identity evidence, not a second co-equal review target.
- `fixture-repo/` — minimal repository-routing fixture used for the mandatory-local-skill finding.

Do not modify fixture files during a benchmark run.

## Protocol

1. Review `target/` at the effort level being evaluated.
2. Allow package inventory to notice `alternate/`, but keep `target/` primary.
3. Use `fixture-repo/` only when testing repository-instruction/router behaviour.
4. **Do not read `expected-findings.md` until discovery and validation are complete.**
5. Preserve the resulting review.
6. Compare underlying failure mechanisms, not exact wording.
7. Record:
   - primary findings recovered;
   - secondary/additional confirmed findings;
   - known traps incorrectly reported;
   - materially overstated findings;
   - independent contexts actually used;
   - model/harness/skill effort;
   - main and worker message tokens;
   - wall time.

## Scoring

Primary benchmark mechanisms remain QCR-1 through QCR-4 so historical scores stay comparable.

QCR-5 through QCR-7 are secondary/additional confirmed findings.

Do not retroactively change old primary scores when new valid findings are discovered.

A strong medium run should recover most or all primary findings without major false positives.
Precision and cost are separate axes; do not collapse the result into one opaque number.

## Effort profiles

Use the same immutable fixture for `low`, `medium`, and `high`.

- `low`: measure the cheapest useful floor.
- `medium`: production/default development baseline.
- `high`: should buy meaningfully better recall/validation or it is not worth the extra cost.
- `ultra`: mainly for structural candidate evaluation with behavioural evidence.
