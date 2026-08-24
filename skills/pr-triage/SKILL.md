---
name: pr-triage
description: Fast first-pass triage of a PR diff before $pr-review; flags mechanical defects only.
---

Cheaper precursor to `$pr-review`, not a substitute: no ancestry check, no requirement linkage, no receipt. Use for a quick skim; use `$pr-review` before merge.

1. `gh pr view <target> --json number,title,additions,deletions,changedFiles,files` first.
2. Skip lockfiles, `*.pbxproj`, `Pods/`, generated code, snapshot fixtures, asset catalogs — note as skipped, do not open to prove it.
3. `gh pr diff <target>` once. Over 400 changed lines: per-file size summary first, deep-dive only files with real logic changes.
4. Flag: logic errors, unhandled branches, swallowed errors, force `try!`, missing tests for new logic, force unwraps, missing `[weak self]` in escaping closures, off-main-thread UI mutation, retain cycles, hardcoded secrets, unsafe URL construction. Style only against convention visible in the diff's own context.
5. Output, capped ~40 lines, omit empty sections:

```
## PR #<n> — <title> (+<a>/-<d>, <n> files)
Skipped: <list or none>
### Blocking
- `file:line` — <one line>
### Worth a look
### Nits
```

Never `gh pr comment` unless asked.
