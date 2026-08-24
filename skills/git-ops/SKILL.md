---
name: git-ops
description: Terminal git housekeeping around agentic sessions — commit messages, conflict resolution, cherry-picks, branch cleanup.
---

Agent sessions usually write their own commits; this covers the manual git work around that.

**Commit messages**: read only `git diff --staged`. Imperative, one line under ~72 chars, body only for non-obvious motivation not visible in the diff. Never invent context — ask rather than guess.

**Conflicts**: if `gh stack` is active, resolve via `gh stack rebase --continue`/`--abort`, not raw git — it restores every branch in the stack. Otherwise: `git status` for conflicted files only; `rg -n "^<{7}|^={7}|^>{7}"` to jump to markers; read only the conflicting hunk plus minimal context each side; propose a resolution; confirm markers are gone with a scoped `git diff --staged`.

**Cherry-picks**: scope `git log --oneline <range>` to find the target; `git show --stat <sha>` to confirm before picking.

**Branch cleanup**: stack-tracked branches go through `gh stack sync --prune`. Otherwise `git branch --merged main`, cross-check `gh pr list --state merged --search "head:<branch>"` when squash-merges hide it, always list and confirm before `git branch -d` (never `-D` without explicit confirmation).

Prefer `--stat`/`--oneline`/scoped diffs over full dumps; never `cat` a whole file when a diff or grep answers it.
