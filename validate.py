#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
SKILLS = ROOT / "skills"
EXPECTED_COUNT = 22
TOKEN_REVIEW_BASELINE_WORDS = 5953
MAX_TOTAL_WORDS = 6245  # About 5% drift allowance above the reviewed 5,953-word baseline.
MAX_DELIVER_WORDS = 500
MAX_REVIEW_WORDS = 350
MAX_OTHER_WORDS = 280
REVIEW_WORD_SKILLS = {"adversarial-review-loop", "artifact-review", "code-review", "diagnose-bug", "issue-review", "pr-review", "test-review", "verify-issue-delivery"}
MAX_DESCRIPTION_WORDS = 18
NEAR_CAP_RATIO = 0.90
ARCHITECTURE_REVIEW = ROOT / "ARCHITECTURE-REVIEW.md"

errors: list[str] = []
skill_paths = sorted(SKILLS.glob("*/SKILL.md"))
names = {path.parent.name for path in skill_paths}
texts: dict[str, str] = {}
word_counts: dict[str, int] = {}
skill_refs: dict[str, set[str]] = {}

if len(skill_paths) != EXPECTED_COUNT:
    errors.append(f"expected {EXPECTED_COUNT} skills, found {len(skill_paths)}")

for path in skill_paths:
    text = path.read_text(encoding="utf-8")
    name = path.parent.name
    texts[name] = text
    word_counts[name] = len(text.split())

    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append(f"{path}: missing YAML frontmatter")
        continue
    try:
        frontmatter = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        errors.append(f"{path}: invalid YAML frontmatter: {exc}")
        continue

    if frontmatter.get("name") != name:
        errors.append(f"{path}: name {frontmatter.get('name')!r} does not match directory")
    description = str(frontmatter.get("description", "")).strip()
    if not description:
        errors.append(f"{path}: missing description")
    elif len(description.split()) > MAX_DESCRIPTION_WORDS:
        errors.append(f"{path}: description exceeds {MAX_DESCRIPTION_WORDS} words")

    refs = set(re.findall(r"\$([a-z0-9-]+)", text))
    skill_refs[name] = refs
    missing = sorted(refs - names)
    if missing:
        errors.append(f"{path}: missing referenced skills: {', '.join(missing)}")

    policy = path.parent / "agents" / "openai.yaml"
    if not policy.exists():
        errors.append(f"{path.parent}: missing agents/openai.yaml")
    else:
        try:
            policy_data = yaml.safe_load(policy.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            errors.append(f"{policy}: invalid YAML: {exc}")
        else:
            if policy_data.get("policy", {}).get("allow_implicit_invocation") is not False:
                errors.append(f"{policy}: every catalogue skill must be explicit-only")


# Skill composition must remain acyclic; recursive review/orchestration can loop or duplicate evidence indefinitely.
visited: set[str] = set()
visiting: set[str] = set()
stack: list[str] = []

def visit_skill(name: str) -> None:
    if name in visited:
        return
    if name in visiting:
        start = stack.index(name)
        cycle = stack[start:] + [name]
        errors.append("skill call cycle: " + " -> ".join(cycle))
        return
    visiting.add(name)
    stack.append(name)
    for ref in sorted(skill_refs.get(name, set())):
        if ref in names:
            visit_skill(ref)
    stack.pop()
    visiting.remove(name)
    visited.add(name)

for skill_name in sorted(names):
    visit_skill(skill_name)

# Architectural governance: adding/removing a skill or changing composition requires a reviewed architecture snapshot.
architecture_lines = [f"{name}:{','.join(sorted(skill_refs.get(name, set())))}" for name in sorted(names)]
architecture_signature = hashlib.sha256("\n".join(architecture_lines).encode("utf-8")).hexdigest()
architecture_text = ARCHITECTURE_REVIEW.read_text(encoding="utf-8") if ARCHITECTURE_REVIEW.exists() else ""
if not architecture_text:
    errors.append("missing ARCHITECTURE-REVIEW.md")
else:
    if f"<!-- reviewed-skill-count: {len(names)} -->" not in architecture_text:
        errors.append("ARCHITECTURE-REVIEW.md: reviewed skill count is stale")
    if f"<!-- architecture-signature: {architecture_signature} -->" not in architecture_text:
        errors.append("ARCHITECTURE-REVIEW.md: skill set/call graph changed; perform and record an architectural review")

for name in ("issue-review", "verify-issue-delivery"):
    text = texts.get(name, "")
    for required in ("falsifiable", "allowed and disallowed", "documented fallback", "every supported locale", "neighbouring/glossary"):
        if required not in text:
            errors.append(f"{name}: missing review probe contract {required!r}")

for name in ("adversarial-review-loop", "pr-review"):
    text = texts.get(name, "")
    for required in ("$code-review", "$artifact-review", "exact complete current", "never old conclusions"):
        if required not in text:
            errors.append(f"{name}: missing specialised-review routing {required!r}")

for required in ("code/config/resource scope", "$code-review` owns fresh review", "$artifact-review` owns fresh review", "prose-only artifacts"):
    if required not in texts.get("adversarial-review-loop", ""):
        errors.append(f"adversarial-review-loop: missing typed review routing {required!r}")
for required in ("code/config/resource changes", "prose-only/docs-only", "$artifact-review kind=documentation", "scope=final"):
    if required not in texts.get("pr-review", ""):
        errors.append(f"pr-review: missing PR review routing {required!r}")

pr_review = texts.get("pr-review", "")
for required in ("stacked PRs", "child-head delta", "known review cutoff", "cross-stack contracts"):
    if required not in pr_review:
        errors.append(f"pr-review: missing stacked-PR contract {required!r}")

artifact_review = texts.get("artifact-review", "")
for required in (
    "kind=issue-draft|pr-description|documentation|other", "claim/evidence fidelity",
    "fresh high-reasoning read-only reviewer", "do not substitute for `issue-review`",
    "final net change", "reverted or no-longer-present work", "metadata-first",
    "preservation of meaningful human intent", "scope=final", "exact complete current artifact",
):
    if required not in artifact_review.lower():
        errors.append(f"artifact-review: missing artifact-review contract {required!r}")

for skill, required in (
    ("issue-fixer", "$adversarial-review-loop artifact_kind=issue-draft"),
    ("create-or-update-pr", "$adversarial-review-loop artifact_kind=pr-description"),
):
    if required not in texts.get(skill, ""):
        errors.append(f"{skill}: missing typed artifact-review routing {required!r}")

code_review = texts.get("code-review", "")
for required in (
    "scope hygiene", "partial-revert", "do not load intermediate commit diffs",
    "compiler warnings", "lifecycle/retention/cleanup", "source anchors", "forwarding indirection/duplication", "rationale comment",
    "documented fallback", "every supported locale", "neighbouring/glossary", "ignore unrelated defects",
    "$test-review", "coverage-affecting deltas", "scope=final", "exact complete diff",
):
    if required not in code_review.lower():
        errors.append(f"code-review: missing code-review contract {required!r}")

test_review = texts.get("test-review", "")
for required in (
    "claim fidelity", "falsifiable allowed and disallowed", "production action boundary",
    "focused mutation evidence", "without mutating the reviewed worktree",
    "cohesion/cost", "coverage value", "compare nearby coverage semantically",
    "dedicated regressions", "practical integration boundaries", "fresh high-reasoning read-only review", "concise *why* comment", "bypass real inputs",
):
    if required not in test_review.lower():
        errors.append(f"test-review: missing test-credibility contract {required!r}")

issue_review = texts.get("issue-review", "")
for required in (
    "material to readiness or acceptance", "metadata-first", "closed/reference state alone is not proof",
    "Do not fetch linked diffs unless", "Documentation-only delivery",
    "decision/ownership ledger", "`target-owned`", "`inherited`", "`dependency`", "`downstream`", "`context`",
    "Shared terminology or semantic proximity is not ownership evidence",
    "dependent/downstream sources alone are insufficient",
    "Swift repos: check established architecture, actor, and ownership boundaries",
):
    if required not in issue_review:
        errors.append(f"issue-review: missing dependency/ownership contract {required!r}")

for skill, required_phrases in {
    "plan-issue-work": (
        "decision/ownership ledger", "Plan only `target-owned`/`inherited` requirements",
        "Dependencies may constrain or block but are not target work", "`downstream`/`context` do not expand scope",
    ),
    "verify-issue-delivery": (
        "decision/ownership ledger", "Check every `target-owned`/`inherited` requirement",
        "their deliverables are not target acceptance", "`downstream`/`context` do not expand scope",
    ),
}.items():
    text = texts.get(skill, "")
    for required in required_phrases:
        if required not in text:
            errors.append(f"{skill}: missing requirement-ownership safeguard {required!r}")

# Legacy-skill consolidation and commit-unit safeguards.
for required in ("selected PR review threads", "thread ID", "GitHub GraphQL", "Never infer unresolved from flat comments alone"):
    if required not in texts.get("evaluate-github-comments", ""):
        errors.append(f"evaluate-github-comments: missing thread-aware retrieval safeguard {required!r}")

for required in ("Prefer GitHub connector/API", "fall back to authenticated `gh`", "ambiguous mutation results", "re-fetch before fallback"):
    if required not in texts.get("create-or-update-pr", ""):
        errors.append(f"create-or-update-pr: missing connector fallback safeguard {required!r}")

for skill in ("implement-task", "implement-reviewed-item"):
    lower = texts.get(skill, "").lower()
    for phrase in ("pre-existing", "never stage/overwrite", "semantic commit unit", "unrelated cleanup"):
        if phrase not in lower:
            errors.append(f"{skill}: missing dirty-tree/commit-unit safeguard {phrase!r}")

# Commit decomposition is semantic first; dependencies and agent waves are derived afterwards.
for required in (
    "Derive semantic commit units before dependencies or execution waves",
    "parallelism must not determine commit boundaries",
    "Sequential items may overlap paths/symbols",
    "Single-item rationale:",
    "same files/subsystem, sequentiality, or inability to parallelise are insufficient reasons",
    "Only concurrently active items require non-overlapping ownership",
    "Do not pre-start dependent workers/worktrees",
    "exact new `HEAD`",
):
    if required not in texts.get("plan-issue-work", ""):
        errors.append(f"plan-issue-work: missing semantic commit-planning safeguard {required!r}")

for required in (
    "one semantic commit unit", "multiple coherent commit units",
    "Findings discovered before commit", "never emitted as separate review-fix commits",
):
    if required not in texts.get("implement-reviewed-item", ""):
        errors.append(f"implement-reviewed-item: missing clean-item commit safeguard {required!r}")

for required in (
    "one semantic commit unit", "multiple coherent commit units",
    "same files/subsystem, sequentiality, or inability to parallelise do not make them one unit",
):
    if required not in texts.get("implement-task", ""):
        errors.append(f"implement-task: missing task-decomposition safeguard {required!r}")

for skill, phrases in {
    "deliver-github-issue": (
        "never pre-create dependent worktrees", "Start dependants after prerequisites integrate from exact new `HEAD`",
        "Later in-scope defects in committed items become minimal fix items", "preserve/restart dependants from resulting `HEAD`", "never rewrite reviewed history",
    ),
    "verify-issue-delivery": (
        "already committed item", "new minimal fix item/commit", "do not amend/reset/rewrite reviewed commits by default",
    ),
    "pr-fixer": (
        "Post-commit findings become new fix commits", "do not amend/reset/rewrite reviewed commits by default",
    ),
}.items():
    for required in phrases:
        if required not in texts.get(skill, ""):
            errors.append(f"{skill}: missing post-commit defect safeguard {required!r}")

for skill in ("code-review", "pr-review"):
    lower = texts.get(skill, "").lower()
    for phrase in ("explicitly requested", "compact table", "without weakening p#/q#"):
        if phrase not in lower:
            errors.append(f"{skill}: missing optional table-output safeguard {phrase!r}")

# Runtime prompt budgets. Increase deliberately only with matching eval evidence.
total_words = sum(word_counts.values())
if total_words > MAX_TOTAL_WORDS:
    errors.append(f"skill catalogue has {total_words} words; budget is {MAX_TOTAL_WORDS}")
def skill_word_limit(name: str) -> int:
    if name == "deliver-github-issue":
        return MAX_DELIVER_WORDS
    if name in REVIEW_WORD_SKILLS:
        return MAX_REVIEW_WORDS
    return MAX_OTHER_WORDS

near_cap_skills: list[str] = []
for name, count in word_counts.items():
    limit = skill_word_limit(name)
    if count > limit:
        errors.append(f"{name}: {count} words exceeds budget {limit}")
    if count >= limit * NEAR_CAP_RATIO:
        near_cap_skills.append(name)

# Near-cap is a design-review trigger, not an automatic split. Record the keep/compress/split decision.
for name in sorted(near_cap_skills):
    if f"<!-- cap-review: {name} -->" not in architecture_text:
        errors.append(f"ARCHITECTURE-REVIEW.md: {name} is >=90% of its cap; record a split/compress/keep decision")

evidence_receipt_skills = {
    "adversarial-review-loop", "artifact-review", "code-review", "diagnose-bug", "evaluate-github-comments", "issue-review",
    "pr-review", "test-review", "verify-issue-delivery",
}
for name in evidence_receipt_skills:
    lower = texts.get(name, "").lower()
    for phrase in ("receipt", "fingerprint", "cache", "not conclusions"):
        if phrase not in lower:
            errors.append(f"{name}: missing evidence-reuse contract {phrase!r}")

for name in ("adversarial-review-loop", "artifact-review", "code-review", "pr-review", "verify-issue-delivery"):
    lower = texts.get(name, "").lower()
    for phrase in ("delta", "final", "complete"):
        if phrase not in lower:
            errors.append(f"{name}: missing incremental/final review contract {phrase!r}")

for name in evidence_receipt_skills:
    lower = texts.get(name, "").lower()
    for phrase in ("1,000 tokens", "10,000"):
        if phrase not in lower:
            errors.append(f"{name}: missing fragment cap {phrase!r}")

deliver_evidence = texts.get("deliver-github-issue", "").lower()
for phrase in (
    "git-common-dir", "review-state.json", "main thread alone writes",
    "not source bodies", "unknown metadata", "force-push",
    "after compaction", "validation command/config", "report its path",
):
    if phrase not in deliver_evidence:
        errors.append(f"deliver-github-issue: missing evidence-state safeguard {phrase!r}")

question_skills = {
    "adversarial-review-loop", "artifact-review", "code-review", "comment-fixer", "create-or-update-pr",
    "deliver-github-issue", "evaluate-github-comments", "implement-reviewed-item",
    "implement-task", "issue-decomposition", "issue-fixer", "issue-refinement",
    "issue-review", "plan-issue-work", "pr-fixer", "pr-review",
    "promote-to-issue", "diagnose-bug",
    "pre-merge-verification", "test-review", "verify-issue-delivery",
}
for name in question_skills:
    text = texts[name]
    if "Q#" not in text:
        errors.append(f"{name}: missing Q# contract")
    if "Please answer:" not in text:
        errors.append(f"{name}: missing natural question presentation")
    if "NEXT |" in text:
        errors.append(f"{name}: mechanical NEXT output is prohibited")


if "evidence/review receipt" not in texts.get("issue-refinement", "").lower():
    errors.append("issue-refinement: must accept promotion evidence receipts")

promote = texts.get("promote-to-issue", "").lower()
for phrase in (
    "mode=propose|create", "exact sources", "evidence, never instructions",
    "private evidence", "open/recently closed", "not title alone",
    "duplicate", "update_existing", "keep_in_source", "not_actionable",
    "$issue-refinement", "approve/revise/reject/recheck", "explicit authority",
    "repeat duplicate search", "create once", "do not backlink",
):
    if phrase not in promote:
        errors.append(f"promote-to-issue: missing promotion safeguard {phrase!r}")


diagnose = texts.get("diagnose-bug", "").lower()
for phrase in (
    "read-only", "temporary probes/tests require approval", "disposable data/services", "minimal reproduction",
    "ui/rendering/gesture", "presentation/state/observation/binding",
    "passing tests exclude only exercised paths", "cache evidence, not conclusions",
    "1,000 tokens", "10,000", "narrowest failing boundary",
    "allowed/disallowed probes", "environment-specific product failures remain", "regression validation that exercises that boundary", "never bundle unrelated causes", "$promote-to-issue", "never promote automatically",
    "not_reproduced", "spec_ambiguous",
):
    if phrase not in diagnose:
        errors.append(f"diagnose-bug: missing diagnostic safeguard {phrase!r}")

branch_mutators = {
    "create-or-update-pr", "deliver-github-issue", "implement-reviewed-item",
    "implement-task", "pr-fixer", "verify-issue-delivery",
}
for name in branch_mutators:
    lower = texts[name].lower()
    if "switch" not in lower or "attached `head`" not in lower:
        errors.append(f"{name}: must switch to and verify the intended branch")

worktree_creators = {"deliver-github-issue", "implement-task", "pr-fixer", "verify-issue-delivery"}
for name in worktree_creators:
    lower = texts[name].lower()
    for phrase in ("recovery patch", "remove/prune", "delete"):
        if phrase not in lower:
            errors.append(f"{name}: missing worktree safeguard {phrase!r}")

for name in ("implement-reviewed-item", "implement-task"):
    lower = texts[name].lower()
    if "exactly one" not in lower and "one focused commit" not in lower:
        errors.append(f"{name}: missing one-final-commit invariant")

if "never use `[codex]`" not in texts["create-or-update-pr"].lower():
    errors.append("create-or-update-pr: missing PR title prefix prohibition")

issue_review = texts["issue-review"]
for phrase in ("relationship-bearing", "do not ask anything already answered", "directly answerable", "Never ask the user to “answer P#”"):
    if phrase.lower() not in issue_review.lower():
        errors.append(f"issue-review: missing source/question safeguard {phrase!r}")

deliver = texts["deliver-github-issue"].lower()
for phrase in (
    "issue_update=ask|auto|never", "already established:",
    "proposed decisions requiring approval:", "please choose:",
    "approve", "revise", "reject", "recheck", "m#", "updated",
    "fresh review", "internal transition", "reconcile any retained branch commits",
    "continuation gate", "known next steps are work, not blockers",
):
    if phrase not in deliver:
        errors.append(f"deliver-github-issue: missing proposal/continuation safeguard {phrase!r}")

issue_fixer = texts["issue-fixer"].lower()
for phrase in ("m#", "approve", "revise", "reject", "recheck", "internal hand-off", "rerun `$issue-review` from scratch"):
    if phrase not in issue_fixer:
        errors.append(f"issue-fixer: missing editable-proposal safeguard {phrase!r}")

continuation_skills = {
    "deliver-github-issue", "implement-task", "implement-reviewed-item",
    "adversarial-review-loop", "comment-fixer", "pr-fixer",
}
for name in continuation_skills:
    lower = texts[name].lower()
    if name == "deliver-github-issue":
        if "explicit invocation requests execution, not a status report" not in lower:
            errors.append(f"{name}: missing execution-not-status continuation gate")
    elif "do not stop at orientation or known remaining work" not in lower:
        errors.append(f"{name}: missing compact continuation rule")

if "always run a fresh `$pr-review" not in texts["pre-merge-verification"].lower():
    errors.append("pre-merge-verification: must review the exact current head freshly")

for required in (
    ROOT / "README.md", ROOT / "ADVERSARIAL-REVIEW.md",
    ROOT / "EVALS.md", ROOT / "TOKEN-REVIEW.md", ROOT / "INPUT-EFFICIENCY-REVIEW.md",
):
    if not required.exists():
        errors.append(f"missing {required.name}")

if errors:
    print("Validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print(f"Validated {len(skill_paths)} explicit-only skills; {total_words}/{MAX_TOTAL_WORDS} words.")
