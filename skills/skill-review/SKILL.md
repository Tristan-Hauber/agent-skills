---
name: skill-review
description: |
  Cross-agent adversarial review of an agent skill for operational correctness,
  algorithmic effectiveness, scope, cost, safety, self-containedness, and
  demonstrated behaviour where static inspection is insufficient.
---

# skill-review

Review an agent skill and its operational package.

The central question is:

> Will following this instruction system reliably produce the result it promises, at reasonable cost and without hidden assumptions?

A skill can be **procedurally correct but ineffective**. Distinguish:

1. **Static operational correctness** — can the written package execute as intended?
2. **Algorithmic effectiveness** — does its search/allocation/filtering strategy plausibly achieve the promised result?
3. **Behavioural evidence** — what happens on representative real targets or benchmarks?

Do not infer layer 3 from layers 1–2.

This skill is cross-agent by default. Do not assume Claude Code, Codex, ChatGPT, or any specific
sub-agent API unless the target skill explicitly depends on one. Use the current agent's available
worker/sub-agent mechanism when independent contexts are required. If no such mechanism exists,
perform the best bounded review possible and state that independent-context coverage was unavailable;
do not pretend serial passes in one context are independent.

## Invocation

Require a skill name or path.

Accept trailing effort:

- `low`
- `medium` — default
- `high`
- `ultra`

Optional flags:

- `--behavioural` — run the target skill's own applicable benchmark even below `high`.
- `--fix` — review first, then apply allowed fixes. Structural/algorithmic fixes require benchmark
  comparison when an applicable benchmark exists.
- `--high-confidence` — suppress probable/manual-verification findings.

Benchmarks belong to the skill whose quality they measure.

- This `skill-review` package may contain its own benchmark for evaluating revisions of
  `skill-review` itself.
- A different target skill may contain its own benchmark for evaluating that target's behaviour.

Never substitute one skill's benchmark for another.

Default `medium` does **not** run benchmarks.

## Effort levels

| Effort | Static/algorithmic discovery | Behavioural evaluation |
|---|---|---|
| `low` | One bounded review context | None unless `--behavioural` |
| `medium` | Two genuinely independent review contexts for every non-trivial target | None unless `--behavioural` |
| `high` | Medium + one further independent angle when justified | None unless `--behavioural` |
| `ultra` | High + deeper package/strategy challenge | Run an applicable benchmark when one exists |

Determine whether a target is trivial **before substantive review begins**. A skill is non-trivial
when it has meaningful branching, delegation, search/evaluation strategy, helper scripts, side-effect
policy, multiple effort levels, or non-obvious external dependencies.

At `medium`, every non-trivial target gets two fresh independent discovery contexts. Do not skip the
second merely because the first reviewer already found clear defects.


## Cross-agent portability

This skill is intended to work across capable agent harnesses.

- Use capabilities rather than one vendor's worker API where practical.
- `low`/`medium`/`high`/`ultra` are **skill effort levels**, independent of any model-specific
  thinking/reasoning-depth control.
- Stronger models or deeper reasoning may improve recall; the skill does not promise equal performance
  across models.
- If the harness cannot supply fresh worker contexts, perform the best bounded fallback and disclose
  that the requested independence was unavailable.


## Step 0 — resolve skill identity

Resolve the requested target before judging it.

For an explicit path, that path is the primary target.

For a name, search the current environment's supported skill locations. Common examples include
project- and user-scoped `.agents/skills`, `.claude/skills`, `.codex/skills`, plugin/package skill
roots, or equivalent locations exposed by the current agent. These are examples, not a fixed required
layout.

Record:

- the active/resolved copy;
- every same-name copy visible in relevant supported roots;
- materially divergent copies;
- which README/scripts/helpers belong to which copy.

Do not silently assume one same-name copy is canonical. A duplicate is a finding only when the
ambiguity/divergence can affect invocation, maintenance, documentation, or behaviour.

The explicitly requested or active/resolved copy remains the **primary review target**. Alternate
same-name copies are evidence about package identity or drift, not co-equal skills to audit by default.
Inspect them only as far as needed to establish relevant divergence unless the caller asks to review
them independently.

## Step 1 — read the operational package

Read the complete target `SKILL.md` or equivalent entrypoint.

Inventory, without recursively absorbing unrelated material:

- README and human-facing rationale/changelog;
- references and templates;
- nested skills;
- scripts/helpers/hooks;
- required tools/plugins/files;
- benchmarks;
- package size and likely invocation cost.

Treat executable helpers as part of the instruction system. Open scripts/helpers enough to verify
that they exist and that their deterministic behaviour supports the promise made by the skill.

Do not assume README claims are operational truth. Compare them with the active entrypoint and helpers.

## Step 2 — build a neutral package map

Extract without judging:

- promised outcome;
- inputs and target resolution;
- defaults and effort levels;
- branches and early exits;
- context/lookup budgets;
- delegation/worker strategy;
- fallbacks;
- filtering/scoring/validation;
- side effects and permission gates;
- output contract;
- external instruction/router handling;
- scripts/helpers used on each path;
- hard prerequisites versus optional dependencies;
- benchmarks and what they claim to test.

Share this neutral map with independent reviewers. Do not share one reviewer's suspected findings
with another discovery reviewer.

## Step 3 — independent discovery

### Low

Use one bounded reviewer covering both operational correctness and effectiveness.

### Medium

For every non-trivial skill, use two **fresh** independent contexts in parallel when supported:

**Reviewer A — operational adversary**

Review the primary active copy first. Treat alternate copies as drift evidence unless a candidate
specifically depends on them.

Challenge:

- broken defaults/branches/early exits, including an early stop that makes a later documented
  fallback unreachable;
- missing prerequisites or incorrect prerequisite classification;
- target/package identity ambiguity;
- README/entrypoint/helper contradictions;
- helper-script bugs that defeat promised behaviour;
- unsafe or unauthorised actions;
- uncontrolled recursion/fan-out;
- output/permission failures;
- missing graceful fallback for an optional dependency or capability. Do not demand graceful
  degradation for an explicitly declared hard prerequisite unless the skill also claims to work
  without it.

**Reviewer B — effectiveness adversary**

Use package-identity facts as neutral context rather than spending most of this independent search
rediscovering the same drift.

Challenge:

- how attention/search budget is allocated;
- systematic blind spots;
- premature filtering;
- recall versus precision trade-offs;
- whether higher effort buys genuinely new search coverage;
- whether independent contexts inherit earlier conclusions;
- whether rigid budgets prevent completing causal chains;
- whether repository/local instruction routers are actually obeyed;
- whether the skill can follow every written instruction and still fail its promised outcome.

Do not allow the first reviewer's success to cancel the second pass.

### High

Run the two medium reviewers, then add one fresh angle only when the package has a genuinely independent
risk area, such as:

- complex side effects or external posting;
- multi-agent orchestration;
- cost/telemetry machinery;
- benchmark design;
- extensive tool integration.

Then run the target skill's applicable benchmark if one exists.

### Ultra

Run high, then use benchmark evidence to evaluate structural/algorithmic fixes. Construct proposed
fixes in a temporary copy, run the applicable benchmark against baseline and candidate, and compare
results before recommending the structural change as validated.

Do not modify the real target merely to test an idea.

## Step 4 — static operational review

Adversarially dry-run meaningful paths, including where relevant:

- default/override;
- true/false;
- empty/non-empty;
- present/absent dependency;
- success/failure;
- small/large target;
- supported/unsupported worker capability;
- optional tool available/unavailable;
- allowed/disallowed side effect.

For each important path ask whether literal compliance could:

- produce the wrong result or omit a required result;
- stop too early or continue after it should stop;
- produce a misleading report;
- silently use the wrong target/copy/ref;
- duplicate work or fan out unexpectedly;
- exceed a reasonable cost;
- perform an unsafe action;
- lose promised behaviour when a helper/tool is absent.

For scripts/helpers, exercise deterministic edge cases when cheap and load-bearing rather than merely
reading them. Examples include parser variants, paths with spaces/renames, missing files, empty output,
and boundary values. Do not invent exhaustive fuzzing unless the helper's role warrants it.

## Step 5 — algorithmic effectiveness review

This step is mandatory for review, search, research, planning, orchestration, ranking, summarisation,
selection, and other judgement-heavy skills.

### Search and attention allocation

Ask:

- What information does the strategy inspect?
- What does it deliberately exclude?
- Can a promising candidate receive enough context to be resolved?
- Can a hard budget systematically hide the class of result being sought?

### Independence

Ask:

- Does extra effort create genuinely independent search or just longer reasoning in one context?
- Are workers given shared neutral facts or inherited conclusions?
- Is consensus mistakenly required before investigating a candidate?

### Recall versus precision

Ask:

- Does filtering happen before adequate candidate generation?
- Are discovery and validation conflated?
- Does a confirm-first posture suppress realistic state-dependent or boundary failures?

### Cost effectiveness

For each expensive step, ask whether its cost buys at least one of:

1. new information;
2. independent search coverage;
3. resolution of a concrete uncertainty.

Flag material cost that buys none of these.

### Systematic blind spots

Explicitly ask:

> What important class of result could this strategy repeatedly miss even if every written instruction is followed perfectly?

Construct a concrete scenario where practical.


When the evidence shows only that a strategy **disfavours** or is likely to miss a class of result,
say that. Use categorical language such as "impossible", "never", or "structurally out of reach" only
when the instructions actually prohibit the behaviour.

For deletion/removal concerns, identify a concrete removed invariant, guard, route, state transition,
or behaviour. Do not assume history is required merely because code/instructions were deleted.

### Routed/local instructions

When the reviewed skill claims to obey repository/project instructions, distinguish literal rules
from routing rules. If an applicable instruction says another local skill/reference **must** be used,
a review strategy that forbids following that mandatory route is an operational conflict, not merely
a speculative behavioural risk.

Do not recursively follow arbitrary references; follow only mandatory or load-bearing routes needed
to judge the skill's promise.

## Step 6 — behavioural evaluation and benchmarks

Behavioural evidence may come from real prior runs, representative invocations, or benchmarks.

### Benchmark ownership

A benchmark belongs to the skill whose quality it measures.

- `skill-review` may own a benchmark that tests whether revisions of `skill-review` still discover
  known review failures.
- A target skill may own a benchmark that tests that target skill's own behaviour.

Do not use `skill-review`'s self-benchmark as evidence about an unrelated target skill, or vice versa.

A useful benchmark should identify:

- exact immutable target/fixture version;
- expected confirmed findings or other success criteria;
- known non-findings/false-positive traps where useful;
- execution protocol;
- metrics to record;
- known limitations.

Do not reveal expected findings to discovery reviewers before discovery and validation are complete.

### When to run

Default `medium` does not run a benchmark.

Run an applicable benchmark when:

- `--behavioural` is supplied;
- effort is `ultra`;
- `--fix` proposes a structural/algorithmic change and a benchmark owned by the skill being changed
  exists.

`high` remains a deeper static/algorithmic review unless `--behavioural` is explicitly supplied.

### Baseline versus candidate

When validating a structural/algorithmic change:

1. use the benchmark owned by the skill being changed;
2. run or reuse a compatible baseline result for the unchanged skill;
3. create a temporary candidate copy containing the proposed change;
4. run the same benchmark protocol against the candidate;
5. compare recall/quality, false positives/overstatements, total effective token cost,
   wall-clock runtime, and important regressions;
6. reject or qualify changes that improve one dimension by materially regressing another without an
   explicit justified trade-off.

A benchmark is evidence, not proof of universal effectiveness. Do not overfit a skill to one fixture.

## Step 7 — consolidate and validate findings

Merge discovery candidates without voting. One reviewer finding something another missed is expected.

Freshly validate high-impact, disputed, or causal claims in a narrow context when possible.

Before assigning impact, answer separately:

1. **Truth** — is the condition actually present?
2. **Reachability/scope** — exactly which copy, effort level, target, or invocation path triggers it?
3. **Fallback/mitigation** — what documented alternate path, prerequisite semantics, or harness
   behaviour reduces/prevents the failure?
4. **Consequence** — after accounting for those facts, what actually fails?

Do not turn a true local condition into a broader consequence than the evidence supports.

Before final classification, perform one consistency check:

> Do any two surviving findings require mutually incompatible assumptions about the same active
> execution path?

If so, narrow or reject the weaker claim.

Classify validity:

- `confirmed`
- `probable`
- `uncertain`
- `rejected`

Classify impact separately:

- `blocks real use`
- `material`
- `polish`

Do not collapse truth, frequency, reachability, and impact into one pseudo-precise score.

With `--high-confidence`, report only confirmed findings plus explicit confirmed instruction conflicts.

## Step 8 — general skill quality

Check:

- self-containedness;
- cross-agent compatibility promised by the skill;
- description/body match;
- appropriate scope;
- unnecessary instructions;
- generality;
- explicit prerequisites;
- bounded cost;
- scriptability of deterministic repetitive work;
- permission handling;
- actionable output.

For cross-agent skills, flag unguarded assumptions about a particular product, worker API, instruction
filename, transcript layout, or environment variable unless that dependency is explicit in the skill's
scope. Agent-specific optimisations are fine when capability-detected with a portable fallback.

Do not recommend scripting judgement work merely to avoid model reasoning.

## Step 9 — report

### Fix before real use

Confirmed/probable issues that can materially produce wrong, incomplete, unsafe, misleading, or
unnecessarily expensive outcomes.

Every finding needs:

- exact instruction/helper evidence;
- concrete failure scenario;
- trigger scope;
- actual consequence including fallback behaviour;
- focused correction.

### Behavioural risks / needs evidence

Use for effectiveness claims that static inspection cannot establish or benchmark results that need
broader confirmation.

### Polish

Real non-blocking improvements.

### Assessment limits

State:

- package material skipped;
- duplicate copies found/not checked;
- behavioural evidence used or not used;
- independent discovery contexts actually used;
- validation performed;
- benchmark used/not used and why;
- wall-clock runtime when measured;
- cost when measurable.

When worker/sub-agent telemetry is available, report separately:

- main/orchestrator message tokens;
- each discovery reviewer;
- validators/benchmark workers;
- total effective message tokens.

If worker usage is hidden, say so explicitly rather than treating main-thread usage as total cost.
Do not estimate hidden worker tokens from elapsed time.

If the environment lacked fresh worker contexts, state this explicitly.

## Step 10 — `--fix`

Without `--fix`, do not edit the target.

With `--fix`, first complete the review.

### Local mechanical fixes

May be applied without a benchmark when unambiguous and behaviourally local, such as:

- stale path/flag;
- direct README/entrypoint contradiction where intended truth is certain;
- missing known prerequisite wording;
- incorrect frontmatter;
- deterministic helper bug with a focused reproducer and clear correction.

Re-run the relevant local validation after editing.

### Structural/algorithmic fixes

Examples:

- changing delegation or worker count;
- effort-tier behaviour;
- search/validation algorithm;
- filtering thresholds;
- context-budget strategy;
- benchmark or orchestration logic.

If the skill being changed owns an applicable benchmark, test the proposed fix in a temporary copy
against the same benchmark before applying it to the real target. Apply only when the evidence supports
the change or the user explicitly accepts the measured trade-off.

If no applicable benchmark exists, report that behavioural validation is unavailable and ask before
making a structural redesign unless the user explicitly requested the redesign.

After fixes, show the resulting diff and re-run relevant static/local validation. Do not claim that
text validation alone proves behavioural correctness.

## Review principles

1. **Separate discovery from validation.** Discovery may surface plausible candidates; fresh validation
   decides what deserves attention.
2. **Spend extra review budget on independent search before merely deepening one search trajectory.**
3. **Share neutral grounding, not conclusions.** Deterministic facts can be gathered once without
   sacrificing independent interpretation.
4. **Model recall explicitly.** Ask what important result classes the search strategy can systematically
   miss even when followed correctly.
5. **Use behavioural evaluation for emergent judgement.** Internally sensible instructions are not
   evidence that a search/evaluation algorithm performs well.
6. **Keep validity, impact, and priority separate.** Truth and importance are different dimensions.
7. **Calibrate claims to demonstrated scope.** A plausible blind spot is not an impossibility, and a
   local defect is not automatically a global failure.
8. **Prefer a few load-bearing invariants over long checklists that compete for model attention.**

Generic skill-design principles also apply:

- separate deterministic grounding from judgement;
- every material extra cost should buy new information, independent search, or resolution of a concrete uncertainty;
- judgement-heavy skills need behavioural evidence where static inspection cannot establish effectiveness;
- keep epistemic confidence separate from importance;
- treat executable helpers as part of the instruction system;
- resolve package identity as well as package content.
