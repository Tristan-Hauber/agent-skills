#!/usr/bin/env python3
"""Read-only git regression scan for $mistake-analysis: reverts + hotfix-after-merge
candidates. No LLM calls, no writes to git or the workflow-improvement store —
the calling skill decides what to record."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def scan(repo_path, days):
    since = f"{days}.days.ago"
    candidates = []

    reverts = [
        l for l in run([
            "git", "-C", repo_path, "log", f"--since={since}", "--grep=^Revert",
            "--pretty=%H|%ct|%s",
        ]).strip().splitlines() if l
    ]
    for line in reverts:
        sha, ts, subject = line.split("|", 2)
        candidates.append({
            "type": "revert",
            "sha": sha,
            "subject": subject,
            "at": datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat(),
        })

    merges = [
        l for l in run([
            "git", "-C", repo_path, "log", f"--since={since}", "--merges", "--pretty=%H|%ct",
        ]).strip().splitlines() if l
    ]
    for line in merges:
        sha, ts = line.split("|")
        merge_time = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        merged_files = [
            f for f in run([
                "git", "-C", repo_path, "diff-tree", "--no-commit-id", "--name-only", "-r", sha,
            ]).splitlines() if f
        ]
        if not merged_files:
            continue
        window_end = (merge_time + timedelta(hours=72)).isoformat()
        follow = [
            f for f in run([
                "git", "-C", repo_path, "log",
                f"--since={merge_time.isoformat()}", f"--until={window_end}",
                "--pretty=%H|%s", "--", *merged_files,
            ]).strip().splitlines()
            if f and not f.startswith(sha)
        ]
        if follow:
            candidates.append({
                "type": "hotfix-after-merge",
                "merge_sha": sha,
                "merged_at": merge_time.isoformat(),
                "followups": [f.split("|", 1)[1] for f in follow[:5]],
                "files": sorted(merged_files)[:10],
            })

    for c in candidates:
        fp_source = json.dumps(c, sort_keys=True)
        c["fingerprint"] = hashlib.sha256(fp_source.encode()).hexdigest()[:16]

    return candidates


if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    print(json.dumps(scan(repo, days), indent=2))
