# Candidate benchmark evidence

This file records cases that may improve the future `skill-review` benchmark portfolio but are not yet
mature enough to become scored fixtures.

Do not expose this file to a benchmark discovery reviewer when the candidate later becomes a formal
fixture.

## 2026-09 — `issue-review` development

**Category:** Review / critique  
**Status:** candidate evidence only; do not add as formal benchmark yet.  
**Reason not formalised:** the existing benchmark is already a review skill, and the portfolio needs
cross-category variance before another review fixture. The `issue-review` cases also do not yet have a
frozen live-issue behavioural ground truth.

### Useful `skill-review` discoveries

Across successive static reviews, `skill-review` surfaced several materially useful concerns:

- the issue's stated diagnosis/root cause itself may need bounded challenge rather than being accepted
  as ground truth;
- discovery candidates should not require validation-grade proof before they can reach validation;
- load-bearing implementation premises include behavioural assumptions, not only named types/files/APIs;
- a neutral shared map should augment rather than replace access to the raw issue/context;
- mandatory repository-local review routing can be operationally load-bearing;
- absence of a benchmark should never cause a benchmark to be fabricated;
- stale documentation/effort-level descriptions can diverge from the runtime skill.

### Findings judged overstated or not yet proven

These should not be treated as settled requirements without behavioural evidence:

- shared evidence for two independent reviewers necessarily makes the second pass ineffective;
- qualitative discretion around triviality/capability availability is itself a material defect;
- all bounded retrieval instructions require numeric caps;
- every cross-issue/product convention requires broader relationship traversal;
- theoretical domain-review gaps justify restoring long mandatory security/migration/performance
  checklists.

### Latest static-review observations to preserve

The latest review additionally proposed:

- a validator-context fallback when fresh validators are unavailable;
- explicit numeric/structural bounds for comments/relationships/code reads;
- broader cross-issue/product-convention coverage;
- stronger grounding for security/migration/compatibility cascades;
- concern that shared Step 1/2 filtering correlates reviewer blind spots.

These remain **candidate hypotheses** until validated against real frozen issue benchmarks. The
package-identity conflict between Claude-specific and general/Codex `issue-review` copies is considered
a workspace/library-topology concern for this user's setup rather than a reason to change the
Claude-specific skill itself.

### What this teaches about `skill-review`

`skill-review` is valuable as an adversarial candidate generator, including for algorithmic design,
but its findings still require domain validation. It can promote plausible behavioural hypotheses into
"material" findings before behavioural evidence exists. Future benchmark scoring should therefore
measure both recall **and calibration/false-positive rate**, not just number of concerns produced.
