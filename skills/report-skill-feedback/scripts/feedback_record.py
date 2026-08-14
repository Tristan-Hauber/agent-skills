#!/usr/bin/env python3
"""Validate and compact one Stage 1 skill-feedback record."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

EVENTS = {
    "missed-safeguard",
    "incorrect-claim",
    "unsupported-reversal",
    "wrong-workflow-result",
    "workflow-inefficiency",
    "other",
}
EVIDENCE_LEVELS = {"weak", "moderate", "strong"}
IMPACT_LEVELS = {"low", "medium", "high"}
REQUIRED = {
    "event",
    "evidence",
    "impact",
    "subject",
    "trigger",
    "observed",
    "evidence_summary",
    "context",
}
OPTIONAL = {"expected", "correction", "existing_suggestion", "pattern", "repro"}
FORBIDDEN = {
    "cause",
    "root_cause",
    "diagnosis",
    "owner",
    "solution",
    "recommendation",
    "proposed_change",
    "go_no_go",
}
FIELD_LIMITS = {
    "subject": 240,
    "trigger": 320,
    "observed": 600,
    "evidence_summary": 800,
    "expected": 320,
    "correction": 320,
    "existing_suggestion": 320,
    "pattern": 320,
    "repro": 400,
}
CONTEXT_KEYS = {"product", "active", "repo_state", "skill_revision"}
CONTEXT_VALUE_LIMIT = 160
MAX_RECORD_CHARS = 3200


class RecordError(ValueError):
    """Report an invalid Stage 1 record without exposing implementation details."""


def compact_text(value: Any, field: str, limit: int, *, required: bool) -> str | None:
    """Normalise a bounded text field and reject invalid required values."""
    if value is None and not required:
        return None
    if not isinstance(value, str):
        raise RecordError(f"{field} must be a string")
    compact = " ".join(value.split())
    if not compact:
        if required:
            raise RecordError(f"{field} must not be empty")
        return None
    if len(compact) > limit:
        raise RecordError(f"{field} exceeds {limit} characters ({len(compact)} provided)")
    return compact


def normalize_context(value: Any) -> dict[str, str]:
    """Keep only compact, already-known provenance fields."""
    if not isinstance(value, dict):
        raise RecordError("context must be an object")
    unknown = set(value) - CONTEXT_KEYS
    if unknown:
        raise RecordError("unknown context field(s): " + ", ".join(sorted(unknown)))
    result: dict[str, str] = {}
    for key in sorted(CONTEXT_KEYS):
        normalized = compact_text(value.get(key), f"context.{key}", CONTEXT_VALUE_LIMIT, required=False)
        if normalized is not None:
            result[key] = normalized
    return result


def normalize_record(raw: Any) -> dict[str, Any]:
    """Validate one observation and return its canonical Stage 1 representation."""
    if not isinstance(raw, dict):
        raise RecordError("record must be a JSON object")
    forbidden = set(raw) & FORBIDDEN
    if forbidden:
        raise RecordError("Stage 1 must not contain later-stage field(s): " + ", ".join(sorted(forbidden)))
    unknown = set(raw) - REQUIRED - OPTIONAL
    if unknown:
        raise RecordError("unknown field(s): " + ", ".join(sorted(unknown)))
    missing = REQUIRED - set(raw)
    if missing:
        raise RecordError("missing required field(s): " + ", ".join(sorted(missing)))
    for field, allowed in (("event", EVENTS), ("evidence", EVIDENCE_LEVELS), ("impact", IMPACT_LEVELS)):
        if raw[field] not in allowed:
            raise RecordError(f"invalid {field}: {raw[field]!r}")

    result: dict[str, Any] = {
        "schema": 1,
        "event": raw["event"],
        "evidence": raw["evidence"],
        "impact": raw["impact"],
        "subject": compact_text(raw["subject"], "subject", FIELD_LIMITS["subject"], required=True),
        "trigger": compact_text(raw["trigger"], "trigger", FIELD_LIMITS["trigger"], required=True),
        "observed": compact_text(raw["observed"], "observed", FIELD_LIMITS["observed"], required=True),
        "evidence_summary": compact_text(raw["evidence_summary"], "evidence_summary", FIELD_LIMITS["evidence_summary"], required=True),
        "context": normalize_context(raw["context"]),
    }
    for field in sorted(OPTIONAL):
        normalized = compact_text(raw.get(field), field, FIELD_LIMITS[field], required=False)
        if normalized is None:
            continue
        result[field] = ({"text": normalized, "status": "unassessed"} if field == "existing_suggestion" else normalized)

    encoded = json.dumps(result, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    if len(encoded) > MAX_RECORD_CHARS:
        raise RecordError(f"record exceeds {MAX_RECORD_CHARS} characters ({len(encoded)} provided)")
    return result


def load_stdin() -> Any:
    """Parse one JSON value from standard input."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as error:
        raise RecordError(f"invalid JSON: {error.msg}") from error


def main() -> int:
    """Write canonical JSON to stdout or a concise validation error to stderr."""
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        record = normalize_record(load_stdin())
    except RecordError as error:
        print(f"feedback-record: {error}", file=sys.stderr)
        return 2
    print(json.dumps(record, ensure_ascii=False, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
