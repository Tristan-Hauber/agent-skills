#!/usr/bin/env python3
"""Record and enrich privacy-bounded semantic telemetry context."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 2
ACTIVITIES = {"review", "plan", "implement", "fix-review", "diagnose", "refine", "deliver", "other"}
SCOPES = {"issue", "pr", "sub-feature", "review-batch", "individual-finding", "repository", "other"}
REVIEW_SOURCES = {"self", "claude", "codex", "human", "other"}
SKILL_ACTIVITY = {
    "pr-review": "review", "code-review": "review", "test-review": "review",
    "artifact-review": "review", "issue-review": "review", "issue-review-9-step": "review",
    "plan-issue-work": "plan", "issue-decomposition": "plan", "issue-refinement": "refine",
    "deliver-issue": "deliver", "deliver-work-item": "implement", "execute-reviewed-item": "implement",
    "diagnose-bug": "diagnose", "adversarial-review-loop": "fix-review", "update-pr": "fix-review",
    "address-comments": "fix-review", "evaluate-github-comments": "review",
}
PHASE_RE = re.compile(r"(?i)\b(issue|pr|pull[- ]request)[/# -]*(\d+)\b")
BRANCH_RE = re.compile(r"(?i)(?:issue|issues|pr|pull[- ]request|#)[/_-]?(\d+)\b")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def short(value: Any, limit: int = 240) -> str | None:
    if value is None:
        return None
    value = " ".join(str(value).split())
    return value[:limit] or None


def bounded(value: Any, limit: int = 512) -> str | None:
    return short(value, limit)


def run_git(repo: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=2, check=True)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def run_gh(repo: Path) -> dict[str, Any] | None:
    try:
        result = subprocess.run(
            ["gh", "pr", "view", "--json", "number,title,baseRefName,headRefName,state"],
            cwd=repo, capture_output=True, text=True, timeout=2, check=True,
            env={**os.environ, "GH_PAGER": "cat"},
        )
        value = json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict):
        return None
    return {
        "number": value.get("number"),
        "title": bounded(value.get("title")),
        "baseRefName": bounded(value.get("baseRefName"), 128),
        "headRefName": bounded(value.get("headRefName"), 128),
        "state": bounded(value.get("state"), 32),
    }


def repo_root(cwd: str | Path | None) -> Path | None:
    if not cwd:
        return None
    root = run_git(Path(cwd), "rev-parse", "--show-toplevel")
    return Path(root) if root else None


def infer_activity(instruction_path: str | None, explicit: str | None = None) -> tuple[str | None, str]:
    if explicit:
        return explicit, "explicit"
    if instruction_path:
        for skill, activity in SKILL_ACTIVITY.items():
            if f"/{skill}/" in f"/{instruction_path}" or instruction_path.endswith(f"/{skill}/SKILL.md"):
                return activity, "skill"
    return None, "unknown"


def infer_issue(branch: str | None, text: str | None = None) -> str | None:
    for value in (branch, text):
        if value:
            match = BRANCH_RE.search(value) or PHASE_RE.search(value)
            if match:
                return match.group(1) if match.lastindex else None
    return None


def infer_scope(activity: str | None, branch: str | None, object_kind: str | None = None) -> str | None:
    if object_kind in {"issue", "pr"}:
        return object_kind
    if activity in {"review", "fix-review"}:
        return "review-batch" if branch and "review" in branch.lower() else "pr"
    if activity in {"plan", "refine", "diagnose", "deliver", "implement"}:
        return "issue" if branch and "issue" in branch.lower() else "sub-feature"
    return None


def github_metadata(repo: Path, cache_root: str | Path | None, repo_id: str, branch: str | None) -> dict[str, Any] | None:
    cache = None
    if cache_root and branch:
        cache = Path(cache_root) / "state" / f"github-{repo_id}-{hashlib.sha256(branch.encode()).hexdigest()[:12]}.json"
        try:
            if cache.exists() and (datetime.now().timestamp() - cache.stat().st_mtime) < 300:
                cached = json.loads(cache.read_text(encoding="utf-8"))
                return cached if isinstance(cached, dict) else None
        except (OSError, json.JSONDecodeError):
            pass
    value = run_gh(repo)
    if cache:
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("w", dir=cache.parent, prefix=f".{cache.name}.", delete=False, encoding="utf-8") as output:
                json.dump(value or {}, output, separators=(",", ":"))
                temporary = output.name
            os.replace(temporary, cache)
        except OSError:
            if "temporary" in locals():
                Path(temporary).unlink(missing_ok=True)
            pass
    return value


def git_metadata(cwd: str | Path | None, cache_root: str | Path | None = None) -> dict[str, Any]:
    root = repo_root(cwd)
    if not root:
        return {"repository": None, "repo_id": None, "remote_hash": None, "branch": None, "head": None,
                "diff": None}
    remote = run_git(root, "config", "--get", "remote.origin.url")
    safe_remote = re.sub(r"^([A-Za-z][A-Za-z0-9+.-]*://)[^/@]+@", r"\1", remote or "")
    safe_remote = re.sub(r"//[^/@]+@", "//", safe_remote).split("?", 1)[0].split("#", 1)[0]
    diff = {}
    for label, args in (("working", ("diff", "--numstat", "HEAD")), ("staged", ("diff", "--cached", "--numstat"))):
        stats = run_git(root, *args) or ""
        files = insertions = deletions = binary = 0
        for line in stats.splitlines():
            columns = line.split("\t", 2)
            if len(columns) != 3:
                continue
            files += 1
            if columns[0] == "-" or columns[1] == "-":
                binary += 1
            else:
                insertions += int(columns[0])
                deletions += int(columns[1])
        diff[label] = {"files": files, "insertions": insertions, "deletions": deletions, "binary_files": binary}
    status = run_git(root, "status", "--porcelain") or ""
    repository_id = hashlib.sha256(str(root).encode()).hexdigest()[:24]
    branch = run_git(root, "branch", "--show-current")
    github = github_metadata(root, cache_root, repository_id, branch)
    return {
        "repository": bounded(root, 1024),
        "repo_id": repository_id,
        "remote_hash": hashlib.sha256(safe_remote.encode()).hexdigest()[:24] if safe_remote else None,
        "branch": bounded(branch, 256),
        "head": run_git(root, "rev-parse", "HEAD"),
        "upstream": bounded(run_git(root, "rev-parse", "--abbrev-ref", "@{upstream}"), 256),
        "diff": diff,
        "untracked_files": sum(line.startswith("?? ") for line in status.splitlines()),
        "github": {"pull_request": github} if github else None,
    }


def context(args: argparse.Namespace) -> dict[str, Any]:
    git = git_metadata(args.cwd, args.root)
    branch = args.branch or git["branch"]
    activity, activity_source = infer_activity(args.instruction_path, args.activity)
    pull_request = (git.get("github") or {}).get("pull_request") or {}
    skill_path = args.instruction_path or ""
    inferred_kind = "issue" if "issue-review" in skill_path or "issue-refinement" in skill_path else None
    inferred_kind = inferred_kind or ("pr" if pull_request or "pr-review" in skill_path else None)
    object_kind = args.object_kind or inferred_kind or ("pr" if activity in {"review", "fix-review"} else None)
    object_id = args.object_id or (str(pull_request["number"]) if pull_request.get("number") is not None else None) or infer_issue(branch, args.text)
    object_kind = object_kind or ("issue" if object_id else None)
    scope = args.scope or infer_scope(activity, branch, object_kind)
    review_source = args.review_source
    if not review_source and activity in {"review", "fix-review"}:
        review_source = "claude"
    return {
        "schema_version": SCHEMA_VERSION, "record_type": "semantic_context", "recorded_at": utc_now(),
        "session_id": bounded(args.session_id), "prompt_id": bounded(args.prompt_id), "phase_id": bounded(args.phase_id or str(uuid.uuid4()), 128),
        "boundary": bounded(args.hook_event, 64),
        "activity": activity, "activity_source": activity_source, "scope": scope,
        "object_kind": bounded(object_kind, 64), "object_id": bounded(object_id, 256), "task_id": bounded(args.task_id),
        "review_source": review_source, "parent_task_id": bounded(args.parent_task_id),
        "confidence": "explicit" if args.activity or args.scope or args.object_id or args.task_id else "inferred",
        "cwd": args.cwd, "git": git,
    }


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
    with path.open("a", encoding="utf-8") as output:
        fcntl.flock(output.fileno(), fcntl.LOCK_EX)
        output.write(line)
        output.flush()
        os.fsync(output.fileno())
        fcntl.flock(output.fileno(), fcntl.LOCK_UN)


def mark(args: argparse.Namespace) -> None:
    root = Path(args.root or os.environ.get("CLAUDE_TELEMETRY_ROOT", Path.home() / ".agents/telemetry"))
    append_jsonl(root / "data/semantic.jsonl", context(args))


def iter_records(path: Path):
    if not path.exists():
        return
    with path.open(encoding="utf-8") as source:
        for line in source:
            try:
                value = json.loads(line)
                if isinstance(value, dict):
                    yield value
            except json.JSONDecodeError:
                continue


def load_records(path: Path) -> list[dict[str, Any]]:
    return list(iter_records(path) or ())


def merged_context(records: list[dict[str, Any]], event_time: str | None, prompt: str | None) -> dict[str, Any] | None:
    candidates = [record for record in records if record.get("record_type") == "semantic_context" and record.get("schema_version") == SCHEMA_VERSION
                  and (not event_time or record.get("recorded_at", "") <= event_time)]
    if not candidates:
        return None
    candidates.sort(key=lambda record: record.get("recorded_at", ""))
    exact = [record for record in candidates if prompt and record.get("prompt_id") == prompt]
    if exact:
        candidates = [record for record in candidates if not record.get("prompt_id") or record.get("prompt_id") == prompt]
    merged: dict[str, Any] = {}
    for record in candidates:
        for key, value in record.items():
            if key in {"schema_version", "record_type", "recorded_at", "phase_id", "prompt_id"}:
                continue
            if value is not None:
                merged[key] = value
        if record.get("prompt_id") == prompt:
            merged["prompt_id"] = prompt
        if record.get("phase_id"):
            merged["phase_id"] = record["phase_id"]
            merged["context_recorded_at"] = record.get("recorded_at")
    merged["record_type"] = "semantic_context"
    merged["schema_version"] = SCHEMA_VERSION
    return merged


def enrich(args: argparse.Namespace) -> None:
    root = Path(args.root or os.environ.get("CLAUDE_TELEMETRY_ROOT", Path.home() / ".agents/telemetry"))
    semantic = load_records(root / "data/semantic.jsonl")
    by_session: dict[str, list[dict[str, Any]]] = {}
    for record in semantic:
        by_session.setdefault(record.get("session_id") or "", []).append(record)
    output = Path(args.output) if args.output else root / "data/enriched.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as destination:
        for source in ("native-logs.jsonl", "native-metrics.jsonl", "lifecycle.jsonl", "status.jsonl"):
            for batch in iter_records(root / "data" / source) or ():
                for event in expand_events(source, batch):
                    session = event.get("session_id") or _find_nested(event, "session.id")
                    prompt = event.get("prompt_id") or _find_nested(event, "prompt.id")
                    event_time = event.get("recorded_at") or _event_time(event)
                    matches = by_session.get(session or "", [])
                    selected = merged_context(matches, event_time, prompt)
                    enriched = {"source": source, "event": event, "semantic": selected}
                    destination.write(json.dumps(enriched, ensure_ascii=False, separators=(",", ":")) + "\n")


def expand_events(source: str, batch: dict[str, Any]):
    if source == "native-logs.jsonl":
        found = False
        for resource_logs in batch.get("resourceLogs", []):
            resource = resource_logs.get("resource")
            for scope_logs in resource_logs.get("scopeLogs", []):
                scope = scope_logs.get("scope")
                for log in scope_logs.get("logRecords", []):
                    found = True
                    yield {"resource": resource, "scope": scope, "log": log}
        if found:
            return
    if source == "native-metrics.jsonl":
        found = False
        for resource_metrics in batch.get("resourceMetrics", []):
            resource = resource_metrics.get("resource")
            for scope_metrics in resource_metrics.get("scopeMetrics", []):
                scope = scope_metrics.get("scope")
                for metric in scope_metrics.get("metrics", []):
                    for metric_type in ("sum", "gauge", "histogram", "exponentialHistogram", "summary"):
                        points = metric.get(metric_type, {}).get("dataPoints", [])
                        for point in points:
                            found = True
                            yield {"resource": resource, "scope": scope, "metric": metric.get("name"),
                                   "metric_type": metric_type, "point": point}
        if found:
            return
    yield batch


def _event_time(value: Any) -> str | None:
    timestamp = _find_nested(value, "event.timestamp") or _find_nested(value, "recorded_at")
    if timestamp:
        return str(timestamp)
    raw = _find_nested(value, "timeUnixNano")
    if raw is None:
        return None
    try:
        return datetime.fromtimestamp(int(raw) / 1_000_000_000, timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def _find_nested(value: Any, key: str) -> str | None:
    if isinstance(value, dict):
        direct = value.get(key)
        if isinstance(direct, (str, int, float)):
            return str(direct)
        if value.get("key") == key:
            inner = value.get("value", {})
            return next((inner.get(name) for name in ("stringValue", "intValue") if inner.get(name) is not None), None)
        for child in value.values():
            result = _find_nested(child, key)
            if result:
                return result
    elif isinstance(value, list):
        for child in value:
            result = _find_nested(child, key)
            if result:
                return result
    return None


def parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root")
    common.add_argument("--cwd", default=os.getcwd())
    common.add_argument("--session-id")
    common.add_argument("--prompt-id")
    common.add_argument("--phase-id")
    common.add_argument("--hook-event")
    common.add_argument("--instruction-path")
    common.add_argument("--activity", choices=sorted(ACTIVITIES))
    common.add_argument("--scope", choices=sorted(SCOPES))
    common.add_argument("--object-kind")
    common.add_argument("--object-id")
    common.add_argument("--task-id")
    common.add_argument("--parent-task-id")
    common.add_argument("--review-source", choices=sorted(REVIEW_SOURCES))
    common.add_argument("--branch")
    common.add_argument("--text")
    command = argparse.ArgumentParser()
    commands = command.add_subparsers(dest="command", required=True)
    commands.add_parser("phase", parents=[common])
    commands.add_parser("context", parents=[common])
    enrich_parser = commands.add_parser("enrich")
    enrich_parser.add_argument("--root")
    enrich_parser.add_argument("--output")
    return command


def main() -> None:
    args = parser().parse_args()
    if args.command == "phase":
        mark(args)
    elif args.command == "context":
        print(json.dumps(context(args), ensure_ascii=False, separators=(",", ":")))
    else:
        enrich(args)


if __name__ == "__main__":
    main()
