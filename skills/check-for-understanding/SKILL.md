---
name: check-for-understanding
description: Verify the user's understanding before carrying out a request whose correctness depends on understanding its context, consequences, or evidence.
---

# Check for understanding

Use this skill automatically before carrying out a request that depends materially on the user
understanding content or consequences. Typical triggers include analysing review comments,
reviewing or changing a PR, drafting or posting GitHub comments, approving a plan, making a
product-policy decision, or carrying out a consequential repository change. Do not add this gate
to trivial mechanical requests whose meaning and effect are already unambiguous.

The gate is on by default. If the user explicitly asks to skip the check-for-understanding
process, honour that request for the current action and proceed under the user's existing scope and
permissions. Do not infer a skip from urgency, confidence, a previous successful check, or a vague
request to "just do it".

## Before asking

1. Identify the exact action the user wants completed and the minimum context needed to understand
   it.
2. Perform only safe, read-only investigation needed to build accurate questions. Do not edit
   files, post comments, change issues or PRs, commit, push, merge, or perform other consequential
   actions before the gate passes.
3. Separate facts, decisions, open questions, and proposed actions. Questions must test the
   material facts and decisions that control the requested action, not incidental trivia.

## Question set

Ask at least three multiple-choice questions in one turn. Scale the set with the material being
understood:

- 3 questions for a small, single-decision task;
- 4–5 for a moderate review, comment, or change;
- 6 or more when the task spans multiple files, interacting policies, risks, or external actions.

Use medium-difficulty questions with one defensible answer. Test understanding of the objective,
scope/ownership, relevant evidence, expected behaviour, and important consequences or validation
limits. Use plausible distractors, but do not use trick wording, obscure details, or answers that
depend on guessing the agent's preference. Accept equivalent explanations when grading.

Do not reveal the answers before the user responds. Keep the questions focused on the content that
must be understood to perform the requested action.

## Gate

- If every answer demonstrates understanding, state that the check passed and carry out the exact
  requested action. Preserve the original scope; passing the check does not grant extra authority.
- If any answer is wrong, incomplete, or materially ambiguous, do not finish the requested action.
  Identify the misunderstood concept briefly, correct the relevant fact when useful, and ask a new
  focused set of at least three questions. Do not merely repeat the same questions or turn the
  process into a gotcha quiz.
- Continue until the user demonstrates understanding or explicitly asks to skip the process.
- If the task or its material context changes, discard the old result and run a fresh check for the
  changed action.
- A refusal to answer is not a passing result. Ask whether the user wants to answer the questions or
  explicitly skip the gate.

## Completion

After a passing check or explicit skip, perform the requested work and report any validation limits
or unresolved decisions honestly. If the requested action becomes unsafe, out of scope, or requires
new authority, stop and ask for that separately; this skill never overrides repository, tool, or
user-permission boundaries.
