---
name: post-github-feedback
description: Post a completed finding list as deduplicated issue or PR feedback without reviewing or fixing.
---

Accept one target and completed `Q#`/`P#` findings. Do not re-review, fix, edit bodies/state/labels, approve/request changes, resolve threads, or check out a branch.

1. Verify every finding belongs to the target's current revision/head; reject stale lists unless historical posting was requested.
2. Preserve all distinct findings and IDs; deduplicate overlaps and already-posted items without weakening, inventing, or omitting.
3. Post concise Markdown under `## Review feedback`: direct questions first, then problems by severity/ID, retaining evidence, required action, validation, and answer options/recommendation.
4. Mark the comment with target, reviewed revision/head, and finding fingerprints: `<!-- codex-github-feedback:... -->`. Update this actor's matching marked comment; otherwise post one conversation comment. Split only on GitHub size rejection; never truncate.
5. Post nothing for `CLEAN` or all duplicates.

Return target, comment link(s), posted IDs, skipped/stale IDs, or `NO FEEDBACK POSTED | reason`.
