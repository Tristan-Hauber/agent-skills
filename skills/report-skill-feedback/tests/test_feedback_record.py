"""Deterministic contract tests for feedback_record.py."""

import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "feedback_record.py"
SPEC = importlib.util.spec_from_file_location("feedback_record", SCRIPT)
assert SPEC and SPEC.loader
feedback_record = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(feedback_record)


def valid_record(**overrides):
    record = {
        "event": "missed-safeguard",
        "evidence": "strong",
        "impact": "medium",
        "subject": "pr-review result",
        "trigger": "manual review found stale documentation after CLEAN",
        "observed": "A struct change invalidated related documentation outside the diff.",
        "evidence_summary": "Review returned CLEAN; manual review verified one stale comment; focused rerun found six more.",
        "context": {"active": "pr-review", "product": "Codex"},
    }
    record.update(overrides)
    return record


class NormalizeRecordTests(unittest.TestCase):
    def test_canonicalises_and_compacts(self):
        record = feedback_record.normalize_record(valid_record(subject="  pr-review\nresult  "))
        self.assertEqual(record["schema"], 1)
        self.assertEqual(record["subject"], "pr-review result")
        self.assertEqual(list(record["context"]), ["active", "product"])

    def test_allows_empty_context(self):
        self.assertEqual(feedback_record.normalize_record(valid_record(context={}))["context"], {})

    def test_marks_existing_suggestion_unassessed(self):
        record = feedback_record.normalize_record(valid_record(existing_suggestion="Review related docs."))
        self.assertEqual(record["existing_suggestion"], {"text": "Review related docs.", "status": "unassessed"})

    def test_rejects_later_stage_fields(self):
        with self.assertRaisesRegex(feedback_record.RecordError, "later-stage"):
            feedback_record.normalize_record(valid_record(cause="bad prompt"))

    def test_rejects_unknown_and_missing_fields(self):
        with self.assertRaisesRegex(feedback_record.RecordError, "unknown field"):
            feedback_record.normalize_record(valid_record(extra="no"))
        record = valid_record()
        del record["trigger"]
        with self.assertRaisesRegex(feedback_record.RecordError, "missing required"):
            feedback_record.normalize_record(record)

    def test_rejects_invalid_values_and_oversized_text(self):
        with self.assertRaisesRegex(feedback_record.RecordError, "invalid impact"):
            feedback_record.normalize_record(valid_record(impact="critical"))
        with self.assertRaisesRegex(feedback_record.RecordError, "subject exceeds"):
            feedback_record.normalize_record(valid_record(subject="x" * 241))


if __name__ == "__main__":
    unittest.main()
