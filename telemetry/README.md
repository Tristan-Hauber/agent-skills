# Claude telemetry — Stage 2

Stage 2 associates Stage 1 low-level Claude API telemetry with the work being performed.

## Install

```sh
./telemetry/install.sh
```

The installer updates only the semantic runtime files and adds one deduplicated asynchronous command to the existing Claude lifecycle hooks. It backs up `~/.claude/settings.json` before that merge. Existing telemetry data, collector configuration, binaries, and unrelated settings are preserved. The hook reads only allow-listed fields and writes a semantic boundary record.

## Automatic context

The recorder derives activity from known workflow-skill paths, object identity from branch names, issue/PR-shaped text, and a bounded optional `gh pr view`, scope from activity and branch context, and repository/branch/HEAD/diff metadata from Git. Weak or missing evidence remains unknown. Values include provenance so analysis can separate inference from explicit markers.

## Explicit phase marker

Use one marker only when automatic inference is insufficient:

```sh
~/.agents/telemetry/bin/telemetry phase \
  --session-id "$CLAUDE_SESSION_ID" \
  --activity fix-review \
  --scope individual-finding \
  --object-kind pr --object-id 725 \
  --task-id finding-1 --parent-task-id 713
```

The marker records a boundary; it does not rewrite earlier events or require repeated Git metadata entry.

## Analysis

```sh
~/.agents/telemetry/bin/telemetry enrich
```

This joins native API requests, prompts, tools, metrics, lifecycle boundaries, status snapshots, and compactions with the latest semantic context for each session. Raw native files remain unchanged.

## Validation

```sh
python3 -m unittest discover -s telemetry/tests -v
```
