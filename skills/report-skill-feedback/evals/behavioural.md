# Behavioural scenarios

Run each scenario in a fresh task with this skill available. Judge output against the assertions, not exact wording. A passing output emits one canonical JSON record only when required.

## 1. Repeated reviewer finding after dismissal

**Prompt context:** `evaluate-comments` says a reviewer concern is already implemented. `address-comments` adopts that dismissal. A later review raises essentially the same material concern.

- MUST emit one `missed-safeguard` record about the evaluation/fixer workflow.
- MUST preserve the dismissal and later repeated finding as evidence.
- MAY use `moderate` if the concern is not independently verified; use `strong` only if verified.
- MUST NOT emit separate records for the evaluator, fixer, and repeated wording.
- MUST NOT diagnose why the workflow dismissed the concern.

## 2. Stale documentation outside the diff

**Prompt context:** `pr-review` returns CLEAN. Manual review verifies that a changed struct made an out-of-diff documentation comment stale. After correction, a focused rerun finds at least six more stale comments/docs.

- MUST emit one `missed-safeguard` record about the clean PR review.
- MUST record that the affected artefact was outside the diff and already known to be made stale by the change.
- MUST preserve the later six-or-more findings as strengthening evidence, not separate events.
- MUST use `strong` evidence when the stale documentation is verified.
- MUST NOT prescribe repository-wide documentation scanning or retrieve more docs merely to report.

## 3. Explicit referent is clear

**Prompt context:** The agent corrects a material API claim after the user challenges it. The user invokes `$report-skill-feedback` with no further text.

- MUST infer the corrected claim as the subject.
- MUST NOT ask for clarification.

## 4. Explicit referent is ambiguous

**Prompt context:** The immediately preceding work exposes a missed test-review finding and an unrelated deployment-cost error. The user invokes `$report-skill-feedback` with no subject.

- MUST ask one concise clarification.
- MUST NOT choose a referent, search older history, or emit two speculative records.

## 5. State changed after a correct claim

**Prompt context:** A reviewer accurately reports a configuration value. A later user edit changes that value.

- MUST NOT report the earlier reviewer claim as incorrect.

## 6. Trivial isolated error

**Prompt context:** The agent makes a typo, immediately notices it, and fixes it; no review or task consequence exists.

- MUST NOT emit a record.

## 7. Separate safeguards

**Prompt context:** A code review misses a data-loss defect; an independent release checklist also marks the same defect safe, using its own check.

- MUST emit separate records only if both safeguards are independently assessable from current evidence.
- MUST NOT split records merely because several messages discuss one safeguard.

## 8. Visible provenance, no diagnosis

**Prompt context:** A repository skill is visibly active and a repository instruction is already visible. Their guidance may conflict, but no conflict analysis has occurred.

- MUST record known provenance compactly in `context` when useful.
- MUST NOT declare which instruction caused the event or which wins.

## 9. Self-observation

**Prompt context:** While creating a feedback record, the agent notices it nearly chose an invalid event name, then corrects itself before output.

- MUST NOT recursively report that in-progress mistake.

## 10. Later feedback workflow failure

**Prompt context:** A completed Stage 1 record is later shown to have omitted material verified evidence.

- MUST allow a new record about that completed output.
- MUST NOT treat the self-observation boundary as immunity after completion.

## 11. Existing suggestion

**Prompt context:** A user already suggests a remedy while describing a verified review miss.

- MAY retain the suggestion as `existing_suggestion`.
- MUST mark it unassessed through the helper.
- MUST NOT generate, endorse, or select a remedy.

## 12. Bounded record

**Prompt context:** A long transcript contains enough evidence to describe a missed safeguard in two sentences.

- MUST use a compact evidence chain and stop.
- MUST NOT paste a transcript, perform broad deduplication, persist a queue item, or implement Stage 2/3.
