---
name: report-skill-feedback
description: Capture one compact, evidence-bounded record of an agent, skill, review, validation, or workflow failure for later improvement assessment. Use when a user explicitly asks to report feedback, or when current-run evidence shows a material missed safeguard, incorrect claim, unsupported reversal, wrong workflow result, or avoidable workflow inefficiency.
---

Record the observed event. Do not diagnose its cause, assign ownership, or choose a change.

## Invocation

On explicit invocation, infer the referent from the current turn or immediately preceding unresolved correction or review when unambiguous. If several unrelated events are plausible, ask one concise question. Do not search older history merely to find feedback.

On implicit invocation, report only when at least one applies:

- A material review, validation, verification, or workflow safeguard plausibly failed.
- A material assertion was shown wrong or unsupported, or was materially reversed without adequate evidence.
- A material wrong result or already-observed avoidable workflow cost provides reusable improvement evidence.

Do not report trivial isolated coding, naming, preference, reasoning, tool, or efficiency issues. Do not call an earlier claim wrong merely because the underlying state later changed.

Prefer one record per invocation. Keep records separate only when independently assessable safeguards or workflow boundaries failed. Consequences, repeated instances, corrections, and discussion of one failure normally strengthen one record. If the visible event already has a record, do not create another unless new evidence materially changes it.

## Evidence boundary

Use current-run evidence. Do not retrieve new source, instruction, historical, or repository evidence solely to create a record.

Preserve enough for a later assessor to reconstruct the concrete event without replaying the conversation. Do not investigate enough to determine cause, applicable ownership, instruction conflict, remedy, or broader recurrence.

Treat challenges, reviewer findings, concessions, and summaries as evidence rather than verified fact. State what is verified and what remains unresolved. A relevant artefact may be outside a diff when a change made it stale; preserve an already-discovered relationship but do not search for more.

Record only instruction-layer provenance that is already visible: the active workflow/skill, known repository instruction, plugin skill/instruction, global instruction, runtime behaviour, or tool/model capability. Mark unknown rather than infer a layer or diagnose conflict.

When already known, preserve an established expected outcome, an immediate verified correction, and an existing suggested remedy as unassessed. Never generate a remedy. Describe observed duplicated or unnecessary work rather than estimating cost.

Stop once the incident can be faithfully reconstructed.

## Classification

Choose one event:

- `missed-safeguard`
- `incorrect-claim`
- `unsupported-reversal`
- `wrong-workflow-result`
- `workflow-inefficiency`
- `other`

Rate `evidence`:

- `weak`: important facts remain unverified.
- `moderate`: the event is established, but material correctness, scope, or consequence remains unresolved.
- `strong`: current evidence verifies the material failure itself.

Rate `impact=low|medium|high` by the actual or reasonably immediate consequence if the failure remained undetected; do not use evidence strength as impact.

## Boundaries

Do not recursively report defects in this invocation's in-progress reasoning or output. After completion, its output is ordinary agent behaviour and can become a later subject if subsequent evidence exposes a feedback-worthy failure.

This skill is diagnostic only. Do not edit instructions or skills, mutate Git/GitHub, persist records, or alter future workflow behaviour.

## Record

Construct one JSON object with:

- `event`, `evidence`, `impact`
- `subject`: the task, output, review, or invocation being reported
- `trigger`: what exposed the event as feedback-worthy
- `observed`: the smallest faithful account
- `evidence_summary`: compact action/claim → finding/correction → verified-result chain
- `context`: known, compact provenance only; `{}` is valid

Optionally include `expected`, `correction`, `existing_suggestion`, `pattern`, or `repro` only when already known and useful.

Run the bundled helper with the object on standard input. Return its canonical one-line JSON output verbatim. If it rejects the object, correct the record rather than weakening the boundary.

```sh
python3 "$SKILL_ROOT/scripts/feedback_record.py" < record.json
```
