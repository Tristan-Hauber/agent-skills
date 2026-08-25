---
name: github-review-learnings
description: Convert evaluated GitHub issue or pull-request review comments into concise, evidence-bounded project learnings.
---

## Purpose

Turn a current GitHub review receipt and its comment dispositions into reusable learnings about
project contracts, implementation hazards, test gaps, or review workflow. This skill is not a
comment fixer and does not change code, issues, pull requests, or review state.

## Input boundary

- Prefer the structured receipt from `evaluate-github-comments`, including target head, comment
  fingerprints, thread state, dispositions, and linked evidence.
- If no receipt is available, require enough metadata to identify the repository, target, revision,
  comment IDs, and current thread state before recording anything.
- Use only verified evidence and explicitly answered decisions. Do not turn suggestions,
  unsupported claims, or unresolved questions into settled project policy.
- Preserve the originating comment URL, author, path/line, target revision, and date so a learning
  can be rechecked when the code or policy changes.
- This skill is automatically run after `evaluate-github-comments` completes. The caller supplies
  the receipt; do not independently re-fetch the whole review unless the receipt is missing or
  stale.

## Classification

Classify each candidate as one of:

- `contract`: a settled product or data-model rule;
- `implementation`: a verified code or architecture hazard;
- `testing`: a verified coverage or test-strength lesson;
- `workflow`: a verified review, validation, or delivery lesson.

Do not record a learning merely because a reviewer made a comment. A comment becomes a learning
only when current code, specifications, later discussion, or a verified test result establishes the
underlying fact. Keep duplicate comments as one learning while retaining all supporting URLs.
Unresolved questions and `Please answer:` items are review output, not learning records.

## Record shape

Create or append compact records under `~/.agents/notes/github-review-learnings.md` (create the
`notes` directory and file when absent). Do not write review learnings to `codex-notes.md` or
`claude-notes.md`; those root files may contain a one-line pointer to this topic note when their
owner chooses to add one. Append records rather than rewriting prior entries, and use a dated
`## YYYY-MM-DD` heading, newest at the end.

Each record contains:

- `kind` — one classification above;
- `learning` — one durable, actionable statement;
- `evidence` — exact file/spec/issue/PR locations and the verified observation;
- `scope` — repository, module, or cross-repository applicability;
- `source` — target, revision, comment URLs/IDs, and review date;
- `confidence` — `moderate` or `strong`;
- `revisit_when` — the code, issue, or decision that would invalidate it, when known.

Do not include a proposed fix unless the source already records an accepted decision.

## Safety

- Never record a reviewer preference as a project fact without corroborating evidence or an
  explicitly settled decision.
- Do not record unresolved questions, rejected suggestions, or unsupported claims.
- Do not modify GitHub, source code, issue/PR bodies, review state, or commits.
- Do not duplicate an existing record unless adding new evidence or changing its confidence.
- If the receipt contains no settled learning, report `NO LEARNINGS` and do not create an empty
  note.

## Output

Report the records created or drafted, the source receipt, and any questions that prevented a
learning from being settled. If no comment supports a durable learning, say `NO LEARNINGS`.
