#!/usr/bin/env bash
# quick-code-review cost audit: reads this session's own subagent transcripts created since a
# given timestamp and reports actual token cost per agent. Weighted the same way the user's
# own `explain-usage` skill weights it (cache reads ~0.1x, cache writes ~2x, output ~5x, plain
# input 1x) so the numbers are directly comparable to what that skill would report.
#
# Usage: audit-cost.sh <since-epoch-seconds>
set -euo pipefail

command -v jq >/dev/null 2>&1 || { echo "SKIPPED: jq not installed, cannot audit cost"; exit 0; }

since="${1:?since-epoch-seconds required}"
session_id="${CLAUDE_CODE_SESSION_ID:-}"
if [[ -z "$session_id" ]]; then
  echo "SKIPPED: CLAUDE_CODE_SESSION_ID not set, cannot locate this session's transcripts"
  exit 0
fi

slug="$(pwd | sed 's/\//-/g')"
subdir="$HOME/.claude/projects/$slug/$session_id/subagents"
if [[ ! -d "$subdir" ]]; then
  echo "SKIPPED: no subagent transcript folder found for this session"
  exit 0
fi

total_eff=0
found=0
for f in "$subdir"/agent-*.jsonl; do
  [[ -e "$f" ]] || continue
  mtime=$(stat -f '%m' "$f" 2>/dev/null || stat -c '%Y' "$f" 2>/dev/null || echo 0)
  [[ "$mtime" -lt "$since" ]] && continue
  found=$((found + 1))
  id=$(basename "$f" .jsonl | sed 's/agent-//')
  metafile="$subdir/agent-$id.meta.json"
  desc="$id"
  if [[ -f "$metafile" ]]; then
    d=$(jq -r '.description // empty' "$metafile" 2>/dev/null || echo "")
    [[ -n "$d" ]] && desc="$d"
  fi
  vals=$(jq -c '
    [.[] | select(.message.usage != null) | .message.usage] as $u
    | {i: ([$u[].input_tokens // 0]|add//0), cw: ([$u[].cache_creation_input_tokens // 0]|add//0), cr: ([$u[].cache_read_input_tokens // 0]|add//0), o: ([$u[].output_tokens // 0]|add//0)}
  ' -s "$f" 2>/dev/null || echo '{"i":0,"cw":0,"cr":0,"o":0}')
  input=$(echo "$vals" | jq '.i')
  cw=$(echo "$vals" | jq '.cw')
  cr=$(echo "$vals" | jq '.cr')
  output=$(echo "$vals" | jq '.o')
  eff=$(awk -v i="$input" -v cw="$cw" -v cr="$cr" -v o="$output" 'BEGIN{printf "%d", i + cw*2 + cr*0.1 + o*5}')
  total_eff=$((total_eff + eff))
  echo "AGENT_COST: $desc | effective_tokens=$eff (input=$input cache_write=$cw cache_read=$cr output=$output)"
done

if [[ "$found" -eq 0 ]]; then
  echo "SKIPPED: no subagent transcripts newer than the given timestamp"
  exit 0
fi

echo "TOTAL_EFFECTIVE_TOKENS: $total_eff"
