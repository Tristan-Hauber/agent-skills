---
name: explain-content
description: Explain the context, changes, risks, and evidence around a requested action, code state, review, decision, or other scenario.
---

# Explain content

Use this skill when the user asks for an explanation, walkthrough, clarification, summary, or
similar understanding of a scenario. The scenario may be a proposed action, a code state, a diff,
a review comment, an issue or PR, a product decision, a test, or an interaction between them.

This skill explains and investigates; it does not perform the requested action unless the user
separately asks for that action. Read-only inspection of the relevant repository, issue, PR, tests,
specifications, history, and linked sources is allowed when needed for an accurate explanation.

## Investigation

1. Identify the scenario, the question the user is really trying to answer, and the relevant
   baseline or current revision.
2. Trace the scenario through the smallest useful set of authoritative sources: current code,
   specifications, issue/PR discussion, tests, history, and validation results.
3. Follow the actual data or control flow. Explain preconditions, key transitions, outcomes, and
   what changes in important alternative cases.
4. Separate verified facts from reasonable inferences, unresolved decisions, historical behaviour,
   and suggestions. Do not present an old comment or stale documentation as current policy.
5. Include direct links to relevant GitHub issues, PRs, local files, specifications, commits, or
   test results when available. Use exact file paths and line references for local evidence.

## Explanation content

Cover the parts that matter to the scenario, using plain language:

- what the thing is and what problem it addresses;
- the key changes or state transitions;
- ownership and scope boundaries;
- risks, failure modes, data-loss or lifecycle implications, and important trade-offs;
- what is deliberately not changed or not implemented;
- the key references and links supporting the explanation;
- how the behaviour is validated, including meaningful gaps or limits;
- the direct decision or conclusion the user needs to make, if one exists.

For a code or review explanation, name the relevant symbols and show a short step-by-step path. For
a policy explanation, state the rule, its exceptions, its owner, and its consequences. For a PR or
comment explanation, distinguish the comment's claim, the evidence at the cited revision, the
current state, and whether the comment is still applicable.

## Presentation

Lead with the conclusion or current state. Use a compact table or short numbered sequence when it
makes relationships, alternatives, or event order clearer; otherwise use concise prose and bullets.
Avoid unexplained jargon, speculative fixes, and irrelevant history. Explain enough detail that the
user can reason about the scenario and its consequences without relying on hidden agent context.

If the evidence is incomplete or conflicting, say exactly what is known, what is not known, and what
would resolve it. Do not silently choose between materially different product or implementation
interpretations.

Do not edit files, modify GitHub state, commit, push, approve, or otherwise mutate external state as
part of an explanation unless the user separately authorises that operation.
