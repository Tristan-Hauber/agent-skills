# Expected findings — old quick-code-review

**Do not expose this file to discovery reviewers before discovery and validation are complete.**

Compare failure mechanisms rather than exact prose.

## Primary confirmed findings

### QCR-1 — same-name packages materially diverge while shared documentation describes one architecture

`target/` and `alternate/` use the same skill name and shared README/scripts but materially different
entrypoint algorithms. The README says a Step -1 whole-review delegation redesign is the current
fixed behaviour. That mechanism exists in `alternate/SKILL.md` but not in `target/SKILL.md`, whose
current entrypoint runs the core review inline and conditionally adds only a narrower high-effort
reviewer.

**Expected:** confirmed; material/fix before real use.

The benchmark does not require restoring Step -1 specifically. The defect is unreconciled package
identity/documentation/behaviour.

### QCR-2 — `preflight.sh` mis-parses Git brace-abbreviated renames in diff mode

Git can emit same-parent rename paths such as:

```text
Some/Path/{Old => New}/Foo.swift
```

The helper's `${path##* => }` logic produces `New}/Foo.swift`, not the actual new path. Subsequent
size/exclusion lookups silently operate on the wrong path.

**Expected:** confirmed; material. Scope the claim to the affected diff-mode rename handling.

### QCR-3 — mandatory repository skill routing conflicts with the target's reference policy

`target/SKILL.md` reads literal repository instructions but prevents following arbitrary references
at low/medium and permits only a narrow referenced document at high. `fixture-repo/CLAUDE.md` requires
a repository-local review skill for sensitive-store changes.

The target therefore cannot both obey that mandatory route and its own reference restrictions.

**Expected:** confirmed static operational conflict; material. Behavioural evidence is needed only to
quantify real defect-recall impact, not to establish the instruction conflict.

### QCR-4 — Step 0 empty-target stop makes the later no-argument branch fallback unreachable

Step 0 says an empty target should report and stop. Step 1 says a no-argument review should first use
staged/unstaged changes and, if empty, review the current branch against its merge-base.

Under literal execution order the Step 0 stop prevents the Step 1 fallback.

**Expected:** confirmed; material/fix before real use.

## Secondary/additional confirmed findings

### QCR-5 — ownership of `scripts/preflight.sh` is ambiguous

The entrypoint says to run "the repository's `scripts/preflight.sh` if present" while the deterministic
helper is packaged with the skill.

This can cause an agent to skip the packaged helper and reproduce the facts manually. Because a manual
fallback exists, do not overstate this as guaranteed loss of all preflight facts.

**Expected:** confirmed; material or high-end polish depending on environment.

### QCR-6 — prior-review detection is incomplete and overly broad

PR preflight scans only PR comment bodies for the generic substring `Generated with`.

It can miss formal review submissions and can false-positive on unrelated comments containing the same
attribution phrase.

**Expected:** confirmed; secondary material/polish depending on workflow.

### QCR-7 — `EMPTY` reflects touched files, not reviewable files

`preflight.sh` derives `EMPTY` from the pre-exclusion touched-file count rather than the post-exclusion
reviewable count. A diff touching only excluded files can therefore report zero reviewable files while
still reporting `EMPTY: no`, so the entrypoint's empty-target stop does not fire.

**Expected:** confirmed; secondary material efficiency/control-flow finding.

This finding was discovered after the original primary benchmark set was frozen and does not change
historical QCR-1..QCR-4 scores.

## Known non-findings / calibration traps

### NF-1 — missing graceful fallback for `gh`

Do not report absence of a graceful PR-mode fallback merely because another optional tool such as `jq`
degrades gracefully. Authenticated `gh` is explicitly declared as a hard prerequisite for PR targets.

### NF-2 — delegated early-exit output based on the alternate copy

Do not apply the alternate `.agents` copy's whole-skill delegation semantics to the primary `target/`
copy. Package divergence is a valid finding; downstream consequences must use the correct execution
path.

### NF-3 — low omits medium/high checks

Omission of expensive sibling/platform/history checks at `low` is not itself a defect unless low's
contract promises equivalent coverage.

### NF-4 — WIP-first no-argument policy

Do not report the documented policy of reviewing staged/unstaged changes first and branch history only
when WIP is empty as scope loss merely because both may exist.

### NF-5 — helper ownership does not prove total preflight loss

The ambiguous helper path is real, but the entrypoint allows manual equivalent checks. Do not claim
every affected invocation necessarily loses all size/exclusion facts.

### NF-6 — bounded multi-hop search is not impossibility

A context/tool budget may disfavor deeper causal chains. It does not establish that such defects are
literally impossible to discover.

### NF-7 — deletion review does not inherently require history

A removed guard/invariant is visible in a diff. History may help establish intent, but is not inherently
required to reason about deletions.

### NF-8 — large-file lookup cap automatically permits huge arbitrary reads

The entrypoint also instructs targeted enclosing-symbol/section extraction and says not to page through
whole large files. Do not claim that a per-file lookup count alone necessarily reopens an unlimited
full-file-read blowout without reconciling those instructions.

### NF-9 — present-but-failing helper necessarily leaves no fallback

A shell helper can fail, but a capable executing agent may still fall back to the entrypoint's manual
equivalent path. A finding should distinguish missing explicit recovery instructions from claiming
that failure necessarily leaves the run without facts.
