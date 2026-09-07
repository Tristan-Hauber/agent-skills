import json
import subprocess
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
