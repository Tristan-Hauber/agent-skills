# Claude telemetry Stage 2 schema

Stage 1 native OTLP logs and metrics remain authoritative and unchanged. Stage 2 adds `data/semantic.jsonl` context records and derives `data/enriched.jsonl` for local analysis.

Each semantic record has `schema_version: 2`, `record_type: semantic_context`, session/prompt correlation fields, the originating lifecycle `boundary`, and separate semantic dimensions:

- `activity`: review, plan, implement, fix-review, diagnose, refine, deliver, or other.
- `scope`: issue, pr, sub-feature, review-batch, individual-finding, repository, or other.
- `object_kind` and `object_id`: the issue, PR, or other tracked object.
- `task_id` and `parent_task_id`: local task identity and optional parent.
- `review_source`: self, Claude, Codex, human, or other.
- `activity_source`, `confidence`, and Git metadata: provenance for automatic versus explicit values.

Git metadata contains repository path, hashed repository and remote identities, branch, HEAD, upstream, staged/working diff statistics, and a bounded optional `gh pr view` result when authenticated GitHub CLI metadata is available. GitHub lookups are cached locally for five minutes per repository/branch. It never contains source contents, prompts, responses, tool payloads, API bodies, credentials, or raw remotes.

Join native events by `session_id` and, where present, `prompt_id`; select the latest preceding semantic context for accurate phase analysis. `telemetry enrich` emits one compact derived record per native/lifecycle/status record.
