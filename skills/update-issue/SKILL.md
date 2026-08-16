---
name: update-issue
description: Update an existing issue from authorised findings or decisions through a reviewed draft.
---

Input: issue, `P#`, answered `Q#`, optional approved `M#`, authority, and optional verified issue-review receipt. The main thread owns evidence state and remote mutation.

1. Verify issue/comment/parent/linked/docs fingerprints; retrieve only changed or missing material, falling back to full affected context when freshness is unknown. Revalidate findings; mark stale/already-resolved items.
2. Convert answered decisions into explicit wording; never infer an unanswered semantic choice. Preserve remaining `Please answer:` questions and stop before mutation.
3. Without exact authority, show the smallest proposal: separate `Already established:` from stable `M#` rules and allow natural Approve/Revise/Reject/Recheck, partial approval, and replacement wording. Revalidate revisions; show material changes once more.
4. Record original state and create a local draft. Apply only approved rules and the smallest complete change; preserve unrelated human context and do not alter metadata fields outside authority.
5. Run `$adversarial-review-loop artifact_kind=issue-draft checkpoint=save`, then `$issue-review` against the draft using verified unchanged linked evidence. Absorb new `P#`; surface new `Q#`; stop on oscillation.
6. Require `CLEAN`, verify/reconcile remote revision, update intended fields, verify remotely, refresh the receipt, then delete the draft.

Return `UPDATED/BLOCKED | issue | resolved/stale IDs | approved M#/- | verification | review receipt | blocker/draft/-`, followed by exact questions. For an orchestrator, `UPDATED` is an internal hand-off: re-fetch and rerun `$issue-review` from scratch using verified unchanged evidence, then continue. A standalone invocation may end after verification.
