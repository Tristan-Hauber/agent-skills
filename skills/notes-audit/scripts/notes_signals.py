#!/usr/bin/env python3
"""Read-only notes-file signals for $notes-audit: size stats, dated-entry
extraction, and cheap near-duplicate candidates (within a file and across
files). No LLM calls, no writes anywhere — the calling skill does the
semantic judgment (clarity, skill-candidate framing, proposed diffs)."""
import difflib
import glob
import json
import os
import re
import sys

ENTRY_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
BULLET_RE = re.compile(r"^[ \t]*-\s+(.+)$", re.MULTILINE)

SIZE_LINES = 300
SIZE_WORDS = 2000
MIN_REPEAT = 3
SIMILARITY = 0.6


def find_notes_files(root):
    return sorted(glob.glob(os.path.join(os.path.expanduser(root), "*-notes.md")))


def parse_entries(text):
    """Split into dated '## YYYY-MM-DD' sections; collect each section's
    top-level bullet lines (continuation lines of a wrapped bullet are not
    included — first line is enough signal for a similarity pre-filter)."""
    matches = list(ENTRY_RE.finditer(text))
    entries = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        bullets = [b.strip() for b in BULLET_RE.findall(body)]
        entries.append({"date": m.group(1), "bullets": bullets})
    return entries


def size_stats(text):
    lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    words = len(text.split())
    return {"lines": lines, "words": words, "size_flag": lines > SIZE_LINES or words > SIZE_WORDS}


def similar(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def repeat_candidates(entries, min_repeat=MIN_REPEAT, threshold=SIMILARITY):
    """Bullets that recur near-identically across >= min_repeat distinct
    dated entries in the same file."""
    tagged = [(e["date"], idx, b) for idx, e in enumerate(entries) for b in e["bullets"]]
    used = [False] * len(tagged)
    groups = []
    for i in range(len(tagged)):
        if used[i]:
            continue
        date_i, idx_i, bullet_i = tagged[i]
        group = [tagged[i]]
        used[i] = True
        for j in range(i + 1, len(tagged)):
            if used[j]:
                continue
            date_j, idx_j, bullet_j = tagged[j]
            if idx_j == idx_i:
                continue  # same dated entry: not a recurrence
            if similar(bullet_i, bullet_j) >= threshold:
                group.append(tagged[j])
                used[j] = True
        distinct_entries = {g[1] for g in group}
        if len(distinct_entries) >= min_repeat:
            groups.append({
                "representative": bullet_i,
                "distinct_entry_count": len(distinct_entries),
                "occurrences": [{"date": g[0], "bullet": g[2]} for g in group],
            })
    return groups


def cross_file_candidates(files_bullets, threshold=SIMILARITY):
    """Bullets that appear near-identically in two or more different files."""
    flat = [(path, b) for path, bullets in files_bullets for b in bullets]
    used = [False] * len(flat)
    out = []
    for i in range(len(flat)):
        if used[i]:
            continue
        path_i, bullet_i = flat[i]
        matches = []
        for j in range(i + 1, len(flat)):
            if used[j]:
                continue
            path_j, bullet_j = flat[j]
            if path_j == path_i:
                continue
            if similar(bullet_i, bullet_j) >= threshold:
                matches.append((path_j, bullet_j))
                used[j] = True
        if matches:
            used[i] = True
            out.append({
                "representative": bullet_i,
                "files": sorted({path_i, *[m[0] for m in matches]}),
                "occurrences": [{"file": path_i, "bullet": bullet_i}] +
                               [{"file": p, "bullet": b} for p, b in matches],
            })
    return out


def scan(root):
    paths = find_notes_files(root)
    files_out = []
    files_bullets = []
    for path in paths:
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as e:
            files_out.append({"path": path, "error": str(e)})
            continue
        entries = parse_entries(text)
        all_bullets = [b for e in entries for b in e["bullets"]]
        files_bullets.append((path, all_bullets))
        files_out.append({
            "path": path,
            **size_stats(text),
            "entry_count": len(entries),
            "repeat_candidates": repeat_candidates(entries),
        })

    cross = cross_file_candidates(files_bullets) if len(files_bullets) > 1 else []
    return {"files": files_out, "cross_file_candidates": cross}


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "~/.agents"
    print(json.dumps(scan(root), indent=2))
