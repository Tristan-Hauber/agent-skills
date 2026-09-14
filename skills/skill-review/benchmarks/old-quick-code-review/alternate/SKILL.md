---
name: quick-code-review
description: |
    Budget-aware code review for the current diff, a PR number, a branch, or a path. A lighter,
    cost-capped alternative to /code-review's multi-agent fan-out — use when you want a review but
    want to control token spend, or after /code-review has burned through budget without finishing.
---

# quick-code-review

Requires `git`; a PR target or GitHub posting additionally requires the `gh` CLI, authenticated.
`high` effort's cost audit (Step 5) additionally uses `jq` if present — it degrades gracefully
(skips reporting a cost figure) without it, so this isn't a hard requirement.

If the target is a GitHub PR and what's wanted is a fast first-pass triage (not CLAUDE.md compliance,
historical context, or this skill's full report), the `pr-review-assist` skill already does that —
capped output, generated-file exclusion, no multi-agent fan-out. Prefer it for that case, or run this
skill with `--high-confidence`; use this skill for a local diff/branch/path (which `pr-review-assist`
explicitly doesn't handle), or a PR that needs more than a first-pass triage.

## Step -1 — dispatch to a sub-agent

Every step below — reading the diff, running the agents in Step 3, scoring in Step 4 — must happen
inside one dispatched sub-agent, not inline in the calling thread, so that reading and reviewing work
doesn't fill up the calling thread's own context. The calling thread's only job is to launch that
agent and add a one-line pointer to its result.

The dispatched sub-agent is *this same skill*, re-invoked with a `[delegated]` marker prepended to
its argument so it knows not to dispatch again. Check the invocation argument now: if it already
starts with the literal marker `[delegated]`, this *is* the dispatched sub-agent — strip the marker
and continue straight on to "Resolving the target" below, running every remaining step yourself in
this thread. Otherwise, do only the following and then stop — do not read a diff, run
`scripts/preflight.sh`, or perform any step below directly in the calling thread:

1. Call `Agent` once, with `subagent_type: "general-purpose"` (never `"fork"` — a fork inherits this
   thread's full context, which defeats the point), a short `description` (e.g. "quick code review:
   <target>"), and `prompt` set to exactly: `Invoke the quick-code-review skill with args
   "[delegated] <the original argument string verbatim, including target, effort level, and any
   flags>". Follow every one of its steps yourself in full, including calling ReportFindings in Step
   5 and asking before any Step 6 posting action — do not summarize, skip, or abbreviate any step
   because you're a sub-agent.`
2. Wait for that agent to finish, then add a one-line pointer to what it found (e.g. "3 findings
   above" or "no findings") to your own reply — nothing more. The agent calls `ReportFindings` itself
   (rendered directly to the user, not something you need to relay) and states its own review cost
   per Step 5; restating either back into this thread's context would defeat the point of delegating.

## Resolving the target

Parse the invocation argument:

- No argument: review the current working diff (staged + unstaged; if both are empty, review the
  diff between the current branch and its merge-base with the default branch).
- A number: treat it as a PR number (`gh pr view`, `gh pr diff`).
- A branch name: diff that branch against its merge-base with the default branch.
- A path: restrict the diff to that path.

## Effort levels

Accept `low` (default), `medium`, or `high` as a trailing argument. There is no `ultra` here — if the
user wants the deep multi-agent cloud review, tell them to run the real `/code-review ultra`; do not
try to imitate it.

Also accept two optional flags, any position:
- `--high-confidence` — narrows Step 4's report to only scores ≥80, see below. By default this skill
  reports every finding that survives the exclusion list, since the point of a review is usually to get
  to a genuinely clean state, not just to see the safest bugs; pass this flag when what's wanted instead
  is a short, act-on-it-immediately list. Does not change how many passes run or what gets read.
- `--history` — adds a third, separate historical-context agent to `high` (see Step 3). Without it,
  `high` runs its 2 dedicated agents only. History/prior-PR digging is expensive even with its own
  caps, in a repo with a dense commit history — so it's opt-in, not bundled into every `high` run.

| Level | Passes | Posture | History/prior-PR search |
|---|---|---|---|
| low | one inline pass, no sub-agent | confirm-first: flag clear, obvious issues | none |
| medium | low's pass + one inline pass for reuse/simplification/efficiency/architecture/doc-comment quality | confirm-first, but the CLAUDE.md check actively looks for violations rather than assuming compliance | none |
| high | an inline reuse/simplification/architecture pass, same as medium; **plus** 2 dedicated parallel `Agent` calls — one for bug-hunting, one for CLAUDE.md compliance (which also grounds architecture findings against a doc CLAUDE.md points at, when the diff's scope matches it); +1 separate historical-context agent if `--history` | the two dedicated agents are each explicitly adversarial — see Step 3 | only with `--history`, capped, see below |

Posture is a deliberate, separate choice from how much gets read, not just "try harder": see Step 3
for what "confirm-first" and "adversarial" concretely mean for each kind of check.

## Step 0 — size check, before spending anything

Run `scripts/preflight.sh diff [<revision-range>] [<path-filter>]` (or `scripts/preflight.sh pr
<number>` for a PR target) — a deterministic pass that gets the diff/PR metadata, excludes lockfiles
(`Package.resolved`, `*.lock`), `*.xcodeproj/project.pbxproj`, `Pods/`, generated code
(`*.generated.swift`, `*.pb.swift`), and reports file/line counts and a `SIZE_FLAG` for what's left.
For a PR target it also reports draft/closed/already-reviewed state (used in Step 1). Note excluded
files as "skipped, non-substantive" in the final report rather than reading them to prove they're
skippable.

It also reports `LARGE_FILE: <path> (<size>)` for any touched, non-excluded file that's large on its
own — over 400 lines (`diff` mode, exact) or roughly over 16KB (`pr` mode, a byte-size proxy so the
script doesn't have to download the whole file just to measure it) — regardless of how small the diff
to that file is; this, not diff size, is what actually drives review cost, since judging correctness
means reading real surrounding context, not just the changed lines. Pass every `LARGE_FILE` path into
every agent launched in Step 3 — they must apply the stricter reading discipline described there for
those files specifically.

If `EMPTY: yes`, say so and stop. If `SIZE_FLAG: large` and the requested effort is `medium` or
`high`, stop and tell the user the size (`FILES_REVIEWABLE`/`LINES_CHANGED`) and ask whether to
proceed at that effort or drop to `low`. Never silently pay for a large `high`-effort review.

## Step 1 — eligibility

Only for a PR target: read `ELIGIBLE_DRAFT` / `ELIGIBLE_STATE` / `ELIGIBLE_ALREADY_REVIEWED` from
Step 0's `preflight.sh pr` output. If the PR is closed, a draft, or already has a review comment from
you, say so and stop — do not spend a sub-agent on this.

## Step 2 — bounded context

List (do not read the contents of) CLAUDE.md files relevant to the touched paths: the root one plus
any in directories the diff touches. This is a cheap `find`/`ls`, not an agent call. If none exist,
that's a normal outcome, not a problem to work around — this skill works the same in a repo with no
CLAUDE.md files, it just skips the CLAUDE.md-compliance angle entirely in that case.

**How CLAUDE.md compliance is checked (applies at every effort level that checks it):** read the
CLAUDE.md files found above, but only their **literal text** — don't open a document or skill CLAUDE.md
merely *points* at (e.g. "always use X skill / keep Y spec current for Z kind of change") to deeply
verify the diff's correctness against it; that document can be arbitrarily large, and verifying deep
correctness against it is a different, heavier task than this review. Do, however, do the *cheap* half
of that check: if the diff's own scope clearly falls into a category CLAUDE.md names, look at whether
the diff's own touched-file list already includes what the pointer names (a spec doc, a generated
artifact) — that's a free comparison against a list you already have. If it's clearly missing, flag it
as a likely gap worth a human look, without opening the target to confirm it in depth. This keeps the
valuable "you probably forgot to update X" signal without paying to fully re-verify X's contents.

## Step 3 — review

**Surrounding context.** A hunk's surrounding context, at every level below and regardless of
posture, means: the enclosing function/type the hunk sits in, plus — only if the hunk's correctness
genuinely can't be judged without it — a targeted `grep`/definition lookup of a specific symbol it
calls, not the whole file that symbol lives in. For a hunk inside a long prose document (a spec, not
code), it means the enclosing section, not the whole document. This applies however large or
cross-referenced the touched file is — a file with hundreds of lines of related logic is exactly the
case where it's tempting to read "just a bit more" repeatedly until most of the file has been read;
don't. **For any file Step 0 flagged as `LARGE_FILE`, this cap is not optional and not just a prose
ask: pull the enclosing function/type with a targeted `grep -n`/`awk`/`sed` extraction (e.g. `awk
'/^func matches/,/^}/'`), never open the file with a general-purpose file-read tool that pages in more
than that.** For a flagged large prose document, find the nearest section heading before the touched
line with `grep -n '^#'` and read only from there to the next heading.

**Tool-call budget.** Content-size caps bound what's read per lookup, not how many lookups happen — a
skill that only caps size per read can still let an agent make repeated, individually-justified reads
into the same file (see README for the audited case that showed this in practice). So: for a dedicated
`Agent` call in `high` (below), state this explicitly in its prompt — **at most 2 additional targeted
lookups (`grep`/`sed`/`awk`) per touched file beyond the first enclosing-function extraction**, and **a
total budget of roughly 15 tool calls** for the whole review (not counting the initial diff fetch).
Approaching either limit is the signal to stop, write up the strongest findings from what's already
been read, and explicitly note anything left uninvestigated — not a reason to push past the budget to
chase one more lookup. The same discipline applies more loosely to low/medium's inline passes: making
far more tool calls than the diff's size would suggest is itself a signal to wrap up.

**Posture.** "Confirm-first" means reading to check the change looks correct — flag what's clearly
wrong, don't manufacture doubt about what reads fine. "Adversarial" means actively trying to prove the
change is wrong: construct the input, interleaving, or edge case that would break it, rather than just
reading it and judging whether it looks right. Adversarial reasoning finds more real issues but costs
more per check, so it's used only where it earns that cost — see each tier below.

- **low**: read the diff hunks yourself, inline, confirm-first. Flag obvious bugs, CLAUDE.md
  violations relevant to touched files, and any touched or added doc comment whose claimed behavior,
  guarantee, or invariant doesn't match what the code actually does — this needs no extra reads beyond
  the hunk already in view, so it belongs here rather than gated behind a higher tier. Do not look at
  git history or other PRs.
- **medium**: low's pass, still confirm-first for bugs, plus two additions: (1) the CLAUDE.md check
  now actively hunts for violations — assume one exists somewhere in scope and look for it, rather
  than reading through and noting if one happens to be obvious; (2) a second inline pass for reuse,
  simplification, and architecture, posture "steelman then challenge": for each piece of apparent
  complexity, first consider whether there's a real reason for it (don't flag something that's complex
  for a documented reason), then flag it if it still doesn't hold up. Duplicated logic that could share
  an existing helper, abstraction the diff didn't need, dead code the diff left behind, obviously
  wasteful patterns. A reimplementation of logic that already exists elsewhere in the codebase under a
  different name or location is still duplicated logic — flag it even when it looks deliberate or
  carries a comment explaining why it wasn't reused directly; a documented rationale explains the
  constraint that blocked reuse, it doesn't resolve the duplication, so surface the existing mechanism
  alongside the constraint and let the human decide whether the constraint should be worked around. The
  architecture half of this pass needs no doc and no extra reads — it's the same
  hunks already in view, judged against general layer-responsibility principles: a view/controller
  deciding navigation or business logic instead of forwarding it; business logic living in
  wiring/composition-root code that should only assemble dependencies; a reusable/shared component (a
  view, a service, anything meant for more than one call site or more than one simultaneous instance)
  quietly owning local state that a caller coordinating multiple instances of it would need to
  synchronize, when that state should instead be injected or bound from whatever owns the group. Still
  no git history, still no PR search, still no reading a doc CLAUDE.md merely points at — that's high's
  job, next. This same pass also extends low's doc-comment mismatch check with two more angles on any
  doc comment touched or added by the diff (`///`, `/** */`, or a plain `//` block documenting a
  declaration): (1) it describes the code's *current* state, not the change's history — a comment that
  says what something "used to" do or narrates the diff itself (e.g. "moved here from X," "this used to
  be duplicated") belongs in the commit message, not in code a future reader sees with no diff attached;
  (2) it's concise and descriptive rather than verbose or vague — a comment that could lose a clause
  without losing information, or one that says "handles the edge case" with no specifics, is worth
  flagging. When a comment fails (1) by narrating history, propose a state-only replacement that still
  captures whatever *non-obvious constraint or invariant* the historical framing was actually
  protecting — don't recommend deleting it outright if it re-derives to a rule a future editor needs.
- **high**: before launching any agent below, run `date +%s` and remember it (as `$since`) — Step 5
  uses it to find and cost only the agents spawned by this invocation, not older ones from earlier in
  the session. Then: the same inline reuse/simplification/architecture pass as medium, plus two
  dedicated parallel `Agent` calls (fresh, dedicated reviewers, not this conversation's own reasoning)
  — each told about the surrounding-context caps **and the tool-call budget** above, and given the
  `LARGE_FILE` list from Step 0:
  1. Bug hunt — **explicitly adversarial**: for each touched hunk, try to construct a concrete input,
     ordering, or interaction with the surrounding code that breaks it, rather than reading it and
     judging whether it looks correct. Read only the diff's changed hunks plus surrounding context
     under the caps above. Do not go looking for pre-existing issues outside the diff.
  2. CLAUDE.md compliance — **actively hunts for violations**, same posture as medium's check, applied
     more thoroughly: read the CLAUDE.md files found in Step 2 against their **literal text only** (see
     Step 2 for the full rule, including the cheap file-list presence check); skip this agent entirely
     if Step 2 found none. Extend this agent's brief with one bounded exception to the literal-text-only
     rule: if a CLAUDE.md instruction points at an architecture/layering doc, and the diff's own scope
     clearly falls into a layer that doc governs (a view/view-controller, an interactor/ViewModel, a
     composition root, or a component built for reuse across call sites), read that one doc — not
     anything it in turn references — and check the diff's layer-placement and state-ownership choices
     against what it says, same as the medium-tier heuristic above but grounded in the doc's actual
     rules instead of general principles. This is still a single bounded read, not a license to chase
     every cross-reference.

  With `--history`, launch a **third**, separate parallel `Agent` call for historical context only —
  that one doesn't add to the file-reading cost above, since it works from `git log`/`gh` output, not
  from re-reading the touched files. Its job is `git blame` on **only the exact changed hunks**, never
  a whole file's history. Before pulling full patches with `git log -p -L <start>,<end>:<file>`, check
  the count first with `git log --oneline -L <start>,<end>:<file>` — some files in this project have
  been touched by dozens of commits even within one narrow line range, and `-L` walks the entire
  history of that range regardless of hunk boundaries. If the count is small, read the full patches; if
  it's large (say, more than ~8), read only the most recent ~5 and summarize the rest from the oneline
  count rather than pulling every patch. If checking prior PRs on these files, cap it at the 5 most
  recently merged PRs touching them, and stop after 2 queries if nothing relevant turns up. Fold
  anything useful "previous PR comments" would find into this same agent rather than adding a fourth.
  Give it the same total tool-call budget as the two dedicated agents above (roughly 15) — history
  digging is exactly the kind of task that feels like it always warrants "just one more query." It
  must be told all of these caps explicitly in its prompt.

## Step 4 — consolidate, then filter once

Before any confidence scoring, de-duplicate overlapping findings from the parallel agents yourself
(inline, no agent call). Then, in **one single pass** — inline, or one `Agent` call covering every
finding at once, never more than one call total — score each remaining finding 0-100 for how
confident you are it's real and worth surfacing:

- **0**: false positive that doesn't survive light scrutiny, or a pre-existing issue.
- **25**: might be real, but unverified, or a stylistic nitpick no CLAUDE.md explicitly calls out.
- **50**: verified real, but minor — a nitpick, or something that rarely triggers in practice.
- **75**: verified real and will be hit in practice, or explicitly required by a relevant CLAUDE.md.
- **100**: certain, directly confirmed by the evidence, and will happen frequently.

Exclude, regardless of score or flags — these aren't low-confidence findings, they're not findings this
review makes at all: pre-existing issues; anything a linter, typechecker, or compiler would catch
(imports, types, formatting, broken tests — assume CI runs these); pedantic nitpicks a senior engineer
wouldn't raise; a suppression already present in the code before this diff (an existing lint-ignore
comment, an existing `@ts-ignore`) — but not one the diff itself adds, since a diff that introduces a
problem and suppresses the tool that would catch it in the same hunk is exactly the case this check must
not wave through; a reviewer's own scope-creep suggestion on already-correct, intentional behavior (not
a genuine defect — a real bug is never excluded just because it looks deliberate, since intentional and
correct are different things); and real issues on lines the diff didn't touch.

Everything else scores normally on the 0-100 rubric above, including two categories worth calling out
explicitly because they're easy to mishandle as a blanket "quality" bucket:

- A concrete security issue the diff introduces or exposes (injection, a hardcoded secret, a missing
  auth/authz check, unsafe deserialization, and the like) is a correctness bug, not a lesser category —
  score and surface it like any other bug-hunt finding. This skill's default passes aren't a substitute
  for a dedicated pass, though: for a thorough security review, use the built-in `security-review` skill
  instead or in addition.
- A test-coverage or missing-documentation gap — the *absence* of a test or comment, not the content of
  a doc comment the diff actually touched or added (that's Step 3's doc-comment check, unrelated to this
  bullet) — typically scores low (25-50) per the rubric, since it's rarely "certain" or "will be hit in
  practice" the way a bug is. A relevant CLAUDE.md requirement for either promotes it to 75+, same as
  any other CLAUDE.md-required finding.

A score of 0 means the scoring pass determined the finding isn't actually real — drop those always,
regardless of flags; they were never a real finding, not just a low-confidence one. Of what's left
(score 25 and up), by default report all of it, sorted most-confident first, each labeled with its
confidence number so the user can see why a low-confidence item is there — the default is "get to a
genuinely clean state," not just "show the safest bugs." If `--high-confidence` was passed, drop
anything scored under 80 instead, to keep the report to only what a reviewer would act on immediately
without further verification. A finding the scoring pass verified as real should never be silently
dropped for being low-severity — only a 0 score, the exclusion list above, or an explicit
`--high-confidence`, should ever cause that.

## Step 5 — report

If `high` effort spawned at least one agent, run `scripts/audit-cost.sh $since` *after* Step 4's own
confidence-scoring pass (including it in the audit if that pass also used an `Agent` call — it's a
real part of this review's total cost, not overhead to hide). It reads this session's own subagent
transcripts created since Step 3 started and reports each one's actual token cost (`AGENT_COST:
<description> | effective_tokens=N ...`) plus a `TOTAL_EFFECTIVE_TOKENS` sum, weighted the same way
the user's `explain-usage` skill weights it, so the number is directly comparable if they ever run
that separately. A `SKIPPED: ...` line means the audit couldn't run (no `jq`, no session env var,
etc.) — that's fine, just don't report a cost figure in that case, don't treat it as an error.

Mention the actual total in the response, briefly (a "this review cost about N effective tokens"
sentence is enough, not a breakdown table) — this is data the user otherwise has no way to see without
separately running `explain-usage` and reverse-engineering which subagents were this review's. If the
total is unusually high for what the diff's size implied, say so plainly rather than letting a
good-looking `SIZE_FLAG: ok` from Step 0 imply the review was actually cheap — see README for a real
case where cache-read volume from many tool-call rounds dominated cost independent of file-content
size. This is a known open gap: the caps in this skill bound *what* gets read per lookup, not *how
many* tool-call rounds an agent takes, and that second thing turned out to matter more in practice.

Call `ReportFindings` with the surviving findings, most confident first (empty array if none survived).
Unless `--high-confidence` was passed, include each finding's confidence score in its summary so the
user can see why a low-confidence item is there. If the surviving list is very long (say, past ~20
findings), report the strongest ~20 and say how many more exist rather than dumping everything — offer
to go deeper on request instead of paying to read a huge list nobody asked to see in full. Do not
hand-format a markdown comment unless the user asked you to post to GitHub.

## Step 6 — posting (opt-in only)

Never run `gh pr comment` unless the user explicitly asked for the review to be posted. If they did,
show them the exact comment text first and get an explicit go-ahead before posting — this is sending
a message on the user's behalf, so it needs confirmation every time, not just the first time.
