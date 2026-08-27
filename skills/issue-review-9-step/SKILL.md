---
name: issue-review-9-step
description: Audits a raw GitHub issue or feature request across nine operational angles to ensure it is actionable, secure, and correctly scoped.
---

# 9-Step Issue Review

Audit the supplied GitHub issue title, description, comments, and relevant context. Review only; do not edit the issue, repository, labels, milestones, or project state.

Separate observed facts from assumptions. Use available repository or linked-item context to test feasibility and integration claims, but do not invent architecture, policy, scale, or compliance requirements. Flag missing decisions as open questions rather than silently deciding them.

Assess all nine angles below. Record only material findings. Each finding should state the gap, why it matters, and a concrete requirement or validation change. Mark a question as critical when implementation could not proceed safely or predictably without an answer.

## The nine angles

1. **Requirements completeness and edge cases** — Identify missing business rules, boundaries, empty or duplicate data, retries, offline/network failure, permissions, cancellation, and recovery behaviour.
2. **Technical feasibility and constraints** — Check the stated stack, architecture, APIs, data model, platform support, dependencies, and likely blockers against available repository context.
3. **Security and compliance implications** — Look for authentication or authorisation changes, input trust, injection, secrets, sensitive data exposure, retention, consent, auditability, and relevant privacy or regulatory obligations. Do not claim a legal conclusion without evidence; identify decisions needing specialist confirmation.
4. **Definition of done and acceptance criteria** — Test whether outcomes are objective, observable, and unambiguous. Replace subjective terms such as “fast”, “intuitive”, or “looks right” with measurable behaviour, thresholds, states, or examples.
5. **Testing and validation strategy** — Specify required unit, integration, migration, UI/E2E, accessibility, performance, security, or manual validation. Check that fixtures and test seams can prove the claimed behaviour and failure paths.
6. **Backward compatibility and system integration** — Check existing users, stored data, schema/API contracts, legacy paths, synchronisation, migrations, rollout order, feature flags, and affected components or services.
7. **Performance and resource scaling risk** — Consider algorithmic cost, query/index use, memory, storage, battery, rendering, concurrency, network traffic, rate limits, and worst-case growth. Request a benchmark or budget where scale matters.
8. **Scope creep and blast radius** — Decide whether the issue contains independent outcomes or too many layers. Recommend atomic sub-tasks with explicit boundaries and dependency order.
9. **Documentation, telemetry, and observability** — Identify required user documentation, API/reference updates, support/runbook changes, logs, metrics, traces, alerts, privacy-safe analytics, rollout monitoring, and rollback signals.

## Review method

1. Extract the requested outcome, actors, affected surfaces, constraints, dependencies, and stated non-goals.
2. Build a short evidence ledger. Label each material statement as issue evidence, linked/context evidence, repository evidence, assumption, or unresolved decision.
3. Cross-examine the outcome against every angle. Consider normal, empty, invalid, repeated, interrupted, unauthorised, migrated, and scaled states where relevant.
4. Convert gaps into critical blockers, open questions, detailed findings, or validation requirements. Do not duplicate a gap across angles unless its consequence differs.
5. Assign status, implementation risk, and complexity weight based on supplied evidence. If confidence is low, say what evidence would change the assessment.
6. Render the report using the exact format below. Omit detailed breakdowns only when no angle has a material finding.

## Issue assessment report

### 📋 Issue Triage Executive Summary

- **Issue Status:** [Actionable / Needs Refinement / Incomplete]
- **Implementation Risk:** [Low / Medium / High]
- **Complexity Weight:** [XS / S / M / L / XL]

### 🚨 Critical Blockers & Open Questions

List decisions that must be answered by product, engineering, security, legal, operations, or other stakeholders before implementation. For each, include the affected behaviour and why the answer changes implementation or validation. If none, write `None identified.`

### 🔍 Detailed Audit Breakdowns

Include only angles with material findings:

- **Angle [Number]: [Angle Name]**
  - **Finding:** Clear summary of the gap or problem.
  - **Suggested Fix:** Specific technical language or requirements text to append to the issue.

Use additional `Evidence`, `Consequence`, or `Validation` sub-bullets when they make the finding easier to verify. Suggested fixes are recommendations, not unapproved product decisions.

### 🧩 Suggested Sub-Task Breakdown

If the blast radius is too large, provide a checklist of smaller atomic issues. For each item state its outcome, boundary, dependency, and completion proof. If decomposition is unnecessary, write `No decomposition required.`

End with a brief `Assessment limits` note when repository context, linked discussions, scale data, legal guidance, or runtime validation was unavailable. Never imply that a document-only review proves production behaviour.
