---
name: deliver-work-item
description: Deliver one bounded work item on the intended branch with one reviewed final commit.
---

Input: task, repository, intended branch, optional checks, and optional verified evidence/review receipt. The main thread owns scope, Git lifecycle, evidence state, integration, and cleanup. Do not push, open a PR, or edit GitHub unless requested.

1. Resolve the intended branch; ambiguity blocks. Inventory pre-existing dirty paths: never stage/overwrite them; overlap or uncertain ownership blocks, while safe non-overlap stays untouched. Switch to the intended branch and verify attached `HEAD` before edits.
2. Use one `explorer` only for evidence absent or invalid in the receipt. Derive concise acceptance/validation; resolve requirement questions from referenced issues/comments, linked decisions, docs, and rules before asking.
3. Keep the task one semantic commit unit; exclude unrelated cleanup unless required/generated/inseparable. If it contains multiple coherent commit units, block for decomposition; same files/subsystem, sequentiality, or inability to parallelise do not make them one unit. Work on the persistent branch unless isolation is requested or safer; otherwise create/register a temporary branch/worktree.
4. Run `$execute-reviewed-item` with the evidence packet; it keeps work uncommitted until final `CLEAN` and validation, then creates exactly one commit.
5. Preserve returned `Q#` under `Please answer:`; same-session answers resume. Mention issue recording only for a material undurable decision.
6. If isolated, integrate and revalidate. Update file/diff/validation fingerprints. On every exit export a recovery patch, restore starting state, remove/prune worktrees, and delete only redundant branches; retain/report unique work.

Stop on oscillation or unverifiable state. Do not stop at orientation or known remaining work.

Return `COMPLETE/BLOCKED | branch | commit SHA/- | validation | review receipt | cleanup | recovery/retained work/- | blocker/-`, followed by exact questions.
