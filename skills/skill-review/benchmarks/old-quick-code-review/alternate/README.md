# Why this skill exists

The stock `/code-review` command (`code-review` plugin, `commands/code-review.md`) fans out into an
uncapped number of cold-start sub-agents: one eligibility check, one CLAUDE.md-path finder, one PR
summarizer, five parallel Sonnet reviewers — including one that reads full git blame/history for
every touched file and one that searches previous PRs on those files with no result cap — and then
**one more confidence-scoring agent per issue found**. On a repo with a dense commit history or a
large diff, the history/prior-PR agents alone can pull in enormous context, and the per-issue scoring
fan-out multiplies with however many (possibly overlapping) issues the five reviewers surfaced. None
of these steps have a size cap or an early exit, so a big or long-lived PR can exhaust a token budget
before the command ever gets to posting anything. That's a property of the command's design, not a
sign it was used wrong.

`SKILL.md` in this directory keeps the same overall shape — eligibility check, gather context,
review, filter, report — but puts a hard ceiling on cost at every step, and defaults to the cheapest
useful pass. This file is background reading for a human looking at the skill folder; it is not
loaded when the skill runs, so `SKILL.md` restates any of this that actually matters operationally
(the size cap in Step 0, the per-agent caps in Step 3) rather than pointing back here.

## Findings from an adversarial review of this skill (2026-09-08)

Tristan pushed back on the skill "getting quite long" and specifically on Step 4's exclusion list
lumping things that shouldn't be excluded together with things that should. An adversarial pass over
the file (prompted by that pushback, alongside an unrelated same-day fix that added a doc-comment
check to Step 3) found and fixed:

- **Security findings could be silently discarded, even under `--all`.** The exclusion list lumped
  `security` into "general quality issues... unless a relevant CLAUDE.md requires them," excluded
  "regardless of score" — so a concrete, 100-confidence vulnerability the bug-hunt agent actually found
  would be thrown away unless a CLAUDE.md file happened to mandate security review. Fixed: a concrete
  security issue the diff introduces or exposes is now always scored and surfaced like any other bug,
  never excluded; the skill also now points at the dedicated `security-review` skill for a thorough
  pass, since this skill's default passes were never meant to substitute for one.
- **`--all`'s own promise was broken by exclusion-list ordering.** `--all` is documented as "get to a
  genuinely clean state," but the exclusion list ran before scoring and unconditionally, so
  test-coverage/doc-absence findings never surfaced even when the user explicitly asked for everything.
  Fixed: that bucket is now excluded by default but surfaced under `--all`.
- **The "explicitly silenced" exclusion didn't check whether the diff itself added the silencing** — a
  diff that introduces a bug and suppresses the linter for it in the same hunk would have gotten a free
  pass. Fixed: only a suppression already present *before* the diff is excluded.
- **The effort-level table fell out of sync with Step 3** the moment the doc-comment check was added to
  Step 3's medium bullet without updating the table's medium row — caught only because this review
  happened to read both side by side.
- **The doc-comment mismatch check (a comment claiming behavior the code doesn't have) required no
  extra reads** yet was gated behind `medium` alongside reuse/simplification checks that do cost extra
  reads. Moved to `low`, next to "flag obvious bugs," since that's what it actually is.

## Default reporting inverted from `--all` to `--high-confidence` (2026-09-08)

Tristan asked for the default to become "show everything," with a flag to narrow down to only
high-confidence/high-impact issues, rather than the other way around. `--all` (opt-in to see
everything) was replaced with `--high-confidence` (opt-in to see only score ≥80); Step 4's exclusion
list — which had applied regardless of `--all` — was restructured so it only ever removes things that
aren't real findings at all (pre-existing issues, lint/compiler-catchable items, a diff's own
new-and-then-suppressed problem, scope-creep suggestions, out-of-diff issues, and a genuine `0`
false-positive score); everything else, including security issues and test-coverage/doc gaps, now
scores normally and surfaces by default. Caught during self-review: an early draft of the "report
everything by default" wording would have surfaced score-`0` false positives too — fixed to always drop
those regardless of flags, since a `0` means "verified not real," not "low-confidence."

## Delegated to a sub-agent (2026-09-08)

Tristan asked for the review skills to run in a sub-agent and report findings back, rather than
running inline in the calling thread — a full `high`-effort run's own diff reads and reasoning were
themselves filling up the calling thread's context, on top of whatever the dedicated Step 3 agents
already isolate. Fixed by adding a new Step -1: the skill now re-invokes itself inside one dispatched
`general-purpose` `Agent` call (never `fork`, since a fork inherits the calling thread's context,
which is exactly what this change avoids), with a `[delegated]` marker prepended to the arguments so
the re-invocation inside the sub-agent knows to run the review itself rather than dispatching again.
The calling thread only launches that agent and adds a one-line pointer to the result — the findings
themselves reach the user via the sub-agent's own `ReportFindings` call, which is rendered directly
rather than needing to be relayed.

## Possible future enhancements

- A reusable "extract the enclosing function/type at line N" helper script, to replace the ad-hoc
  `grep`/`awk`/`sed` incantations Step 3 currently asks each agent to construct per hunk when a file
  is flagged `LARGE_FILE`. Real value (more reliable extraction, one less thing an agent has to get
  right under pressure), but making it robust across arbitrary Swift structure (and prose section
  boundaries in a spec doc) is a nontrivial lift — not something to write unverified. Surfaced by a
  `skill-review` pass on 2026-08-31.

## What `scripts/audit-cost.sh` already found, and what it changed (2026-08-31)

Added to check, with real data, whether the `LARGE_FILE`/surrounding-context fix actually worked. It
mostly didn't: auditing the actual "Quick command" session that originally reported the 220k-token
blowout (subagent transcripts at
`~/.claude/projects/-Users-tristan-Documents-GitHub-SongSheet/660790a2-50ad-41ad-a14a-f254be4ee6a0/subagents/`)
showed the pre-fix 3-agent run cost ~948k effective tokens, and a **post-fix** 2-agent run on the same
PR — after the `LARGE_FILE` guard, the tightened surrounding-context definition, and the
reverted-to-parallel-agents/adversarial-posture changes were all in place — still cost ~908k, only
about 4% less. The single bug-hunt agent alone accounted for ~673k (pre-fix) and ~733k (post-fix,
*higher*) effective tokens.

Looking at that post-fix agent's actual tool calls (the transcript records the literal Bash commands
it ran) showed why: it made only 21 tool calls, but 5 of them were separate large `sed` reads of the
*same* 800-line file — cumulatively covering nearly all of it — plus a `cat` of a whole other file.
Every individual lookup respected the surrounding-context rule's letter; the rule just never stopped
the agent from making a 2nd, 3rd, 4th, 5th separate lookup into the same file, each one individually
justified by a genuinely adversarial posture that always wants to check one more interaction.

**Fix applied**: Step 3 now states an explicit tool-call budget in each dedicated agent's prompt — at
most 2 additional targeted lookups per touched file beyond the first extraction, and a total budget of
roughly 15 tool calls per agent, with an explicit instruction to stop and report partial findings past
that rather than pushing on.

**Verified (2026-08-31, same day)**: the next real `high`-effort run on the same PR — after it grew
slightly (154→174 lines, 9→11 files, ruling out "the diff just got smaller" as the explanation) —
cost ~484k effective tokens total, down from ~908k. A 47% reduction. The bug-hunt agent used only 2
tool calls (the diff fetch, plus one precisely-scoped 60-line extraction) versus the prior run's 21,
including the 5 overlapping same-file reads that drove the earlier cost. Checked the agents' actual
findings, not just their cost, to rule out the cheaper run just cutting corners: both produced
substantive, specific findings (a non-trivial whitespace-comparison edge case with file:line citations,
correctly declining to manufacture a CLAUDE.md violation that wasn't really one) — the budget produced
genuine efficiency, not a shallower pass. One fair caveat: this run was implicitly narrower (checking a
specific fix made in response to review feedback, per its own description), which may have contributed
some of the efficiency independent of the budget — but the visible tool-call discipline (one targeted
extraction instead of five overlapping ones) is a direct, attributable result of the fix either way.
