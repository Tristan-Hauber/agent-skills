import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from telemetry import semantic


class SemanticTelemetryTests(unittest.TestCase):
    def test_skill_activity_and_issue_inference(self):
        args = semantic.parser().parse_args([
            "context", "--cwd", "/tmp", "--instruction-path", "/Users/me/.agents/skills/pr-review/SKILL.md",
            "--branch", "feature/issue-713-review", "--session-id", "s1",
        ])
        value = semantic.context(args)
        self.assertEqual(value["activity"], "review")
        self.assertEqual(value["activity_source"], "skill")
        self.assertEqual(value["object_id"], "713")
        self.assertEqual(value["scope"], "pr")
        self.assertEqual(value["review_source"], "claude")

    def test_explicit_values_override_inference(self):
        args = semantic.parser().parse_args([
            "context", "--cwd", "/tmp", "--instruction-path", "/skills/pr-review/SKILL.md",
            "--activity", "implement", "--scope", "individual-finding", "--object-id", "x",
            "--review-source", "human",
        ])
        value = semantic.context(args)
        self.assertEqual(value["activity"], "implement")
        self.assertEqual(value["scope"], "individual-finding")
        self.assertEqual(value["object_id"], "x")
        self.assertEqual(value["review_source"], "human")
        self.assertEqual(value["confidence"], "explicit")
        self.assertTrue(value["phase_id"])

    def test_pull_request_metadata_supplies_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            with patch.object(semantic, "run_gh", return_value={"number": 725, "title": "Review"}):
                value = semantic.git_metadata(repo, repo)
            args = semantic.parser().parse_args(["context", "--cwd", str(repo), "--root", str(repo), "--instruction-path", "/skills/pr-review/SKILL.md"])
            with patch.object(semantic, "run_gh", return_value={"number": 725, "title": "Review"}):
                context = semantic.context(args)
            self.assertEqual(value["github"]["pull_request"]["number"], 725)
            self.assertEqual(context["object_kind"], "pr")
            self.assertEqual(context["object_id"], "725")

    def test_issue_review_is_not_promoted_to_pull_request(self):
        args = semantic.parser().parse_args([
            "context", "--cwd", "/tmp", "--instruction-path", "/skills/issue-review/SKILL.md",
            "--branch", "feature/issue-713-review",
        ])
        value = semantic.context(args)
        self.assertEqual(value["object_kind"], "issue")
        self.assertEqual(value["object_id"], "713")

    def test_git_metadata_collects_safe_stats(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
            (repo / "file.txt").write_text("one\n")
            subprocess.run(["git", "-C", str(repo), "add", "file.txt"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], check=True)
            (repo / "file.txt").write_text("one\ntwo\n")
            value = semantic.git_metadata(repo)
            self.assertTrue(value["branch"])
            self.assertEqual(value["diff"]["working"]["files"], 1)
            self.assertEqual(value["diff"]["working"]["insertions"], 1)
            self.assertNotIn("file contents", json.dumps(value))

    def test_phase_and_enrich_keep_low_level_event(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = semantic.parser().parse_args([
                "phase", "--root", str(root), "--session-id", "s1", "--prompt-id", "p1",
                "--activity", "review", "--scope", "pr", "--object-id", "725",
            ])
            semantic.mark(args)
            (root / "data/native-logs.jsonl").write_text(json.dumps({"session_id": "s1", "event": "api_request"}) + "\n")
            semantic.enrich(semantic.parser().parse_args(["enrich", "--root", str(root)]))
            result = json.loads((root / "data/enriched.jsonl").read_text())
            self.assertEqual(result["event"]["event"], "api_request")
            self.assertEqual(result["semantic"]["object_id"], "725")
            self.assertTrue(result["semantic"]["phase_id"])

    def test_enrichment_carries_context_forward_but_not_backward(self):
        records = [
            {"schema_version": 2, "record_type": "semantic_context", "recorded_at": "2026-01-01T00:00:00.000Z", "activity": "review", "scope": "pr", "session_id": "s", "phase_id": "p1"},
            {"schema_version": 2, "record_type": "semantic_context", "recorded_at": "2026-01-01T00:02:00.000Z", "activity": "implement", "session_id": "s", "phase_id": "p2"},
        ]
        before = semantic.merged_context(records, "2026-01-01T00:01:00.000Z", None)
        after = semantic.merged_context(records, "2026-01-01T00:03:00.000Z", None)
        self.assertEqual(before["activity"], "review")
        self.assertEqual(after["activity"], "implement")

    def test_enrichment_splits_native_batches_and_normalizes_metric_time(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for activity, prompt, timestamp in (("review", "p1", "2026-01-01T00:00:00.000Z"), ("implement", "p2", "2026-01-01T00:02:00.000Z")):
                record = {"schema_version": 2, "record_type": "semantic_context", "recorded_at": timestamp,
                          "session_id": "s1", "prompt_id": prompt, "phase_id": prompt, "activity": activity}
                (root / "data").mkdir(exist_ok=True)
                with (root / "data/semantic.jsonl").open("a") as output:
                    output.write(json.dumps(record) + "\n")
            batch = {"resourceLogs": [{"scopeLogs": [{"logRecords": [
                {"attributes": [{"key": "session.id", "value": {"stringValue": "s1"}}, {"key": "prompt.id", "value": {"stringValue": "p1"}}, {"key": "event.timestamp", "value": {"stringValue": "2026-01-01T00:01:00.000Z"}}]},
                {"attributes": [{"key": "session.id", "value": {"stringValue": "s1"}}, {"key": "prompt.id", "value": {"stringValue": "p2"}}, {"key": "event.timestamp", "value": {"stringValue": "2026-01-01T00:03:00.000Z"}}]},
            ]}]}]}
            (root / "data/native-logs.jsonl").write_text(json.dumps(batch) + "\n")
            metric = {"resourceMetrics": [{"scopeMetrics": [{"metrics": [{"name": "cost", "sum": {"dataPoints": [
                {"attributes": [{"key": "session.id", "value": {"stringValue": "s1"}}], "timeUnixNano": "1767225660000000000"}
            ]}}]}]}]}
            (root / "data/native-metrics.jsonl").write_text(json.dumps(metric) + "\n")
            semantic.enrich(semantic.parser().parse_args(["enrich", "--root", str(root)]))
            results = [json.loads(line) for line in (root / "data/enriched.jsonl").read_text().splitlines()]
            logs = [result for result in results if result["source"] == "native-logs.jsonl"]
            self.assertEqual(len(logs), 2)
            self.assertEqual([result["semantic"]["activity"] for result in logs], ["review", "implement"])
            metrics = [result for result in results if result["source"] == "native-metrics.jsonl"]
            self.assertEqual(metrics[0]["semantic"]["activity"], "review")


if __name__ == "__main__":
    unittest.main()
