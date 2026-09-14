#!/usr/bin/env bash
# quick-code-review preflight: size stat + generated/vendor-file exclusion + (PR only) eligibility,
# in one deterministic pass. The caller has already resolved which target this is (see "Resolving
# the target" in SKILL.md) — this script does not guess between a diff/branch/path/PR itself.
#
# Usage:
#   preflight.sh diff [<revision-range>] [<path-filter>]
#     revision-range defaults to HEAD (staged + unstaged combined)
#   preflight.sh pr <number>
set -euo pipefail

is_excluded() {
  local f="$1"
  case "$f" in
    *.lock|Package.resolved|*.xcodeproj/project.pbxproj|Pods/*|*.generated.swift|*.pb.swift) return 0 ;;
    *) return 1 ;;
  esac
}

# Percent-encode a path segment for use in a GitHub API URL (this repo has directories with
# spaces and parentheses, e.g. "SongSheet (macOS)/"). Preserves "/" as a path separator.
urlencode() {
  local s="$1" out="" c i
  for (( i=0; i<${#s}; i++ )); do
    c="${s:$i:1}"
    case "$c" in
      [a-zA-Z0-9./_-]) out+="$c" ;;
      *) printf -v hex '%%%02X' "'$c"; out+="$hex" ;;
    esac
  done
  printf '%s' "$out"
}

# How big is "large" for a whole touched file (not the diff to it) — the size that makes reading
# real surrounding context for a hunk expensive, regardless of how small the hunk itself is.
LARGE_FILE_LINES=400
LARGE_FILE_BYTES=16000

mode="${1:-}"
total_files=0
reviewable_lines=0
excluded_list=()
reviewable_list=()
large_files=()

case "$mode" in
  diff)
    range="${2:-HEAD}"
    pathfilter="${3:-}"
    if [[ -n "$pathfilter" ]]; then
      rows="$(git diff --numstat "$range" -- "$pathfilter")"
    else
      rows="$(git diff --numstat "$range")"
    fi
    while IFS=$'\t' read -r add del path; do
      [[ -z "${path:-}" ]] && continue
      total_files=$((total_files + 1))
      # binary files report "-" for add/del; count as 0 lines, still counts as a touched file.
      [[ "$add" == "-" ]] && add=0
      [[ "$del" == "-" ]] && del=0
      # A rename (with or without content change) reports as "old => new" in one field; use the
      # new path for exclusion/size checks, but keep the original field for display.
      lookup_path="$path"
      [[ "$path" == *" => "* ]] && lookup_path="${path##* => }"
      if is_excluded "$lookup_path"; then
        excluded_list+=("$path")
      else
        reviewable_list+=("$path")
        reviewable_lines=$((reviewable_lines + add + del))
        # File's own current size, not the diff to it — read from the target revision when the
        # range is a two-commit range (A..B), otherwise from the working tree (the common HEAD case).
        if [[ "$range" == *..* ]]; then
          if file_content=$(git show "${range##*..}:$lookup_path" 2>/dev/null); then
            file_lines=$(printf '%s\n' "$file_content" | wc -l | tr -d ' ')
          else
            file_lines=0
          fi
        elif file_lines_raw=$(wc -l < "$lookup_path" 2>/dev/null); then
          file_lines=$(printf '%s' "$file_lines_raw" | tr -d ' ')
        else
          file_lines=0
        fi
        [[ -n "$file_lines" && "$file_lines" -gt $LARGE_FILE_LINES ]] && large_files+=("$path ($file_lines lines)")
      fi
    done <<< "$rows"
    ;;
  pr)
    number="${2:?PR number required}"
    meta="$(gh pr view "$number" --json isDraft,state,comments --jq '
      "ELIGIBLE_DRAFT: " + (.isDraft|tostring),
      "ELIGIBLE_STATE: " + .state,
      "ELIGIBLE_ALREADY_REVIEWED: " + ([.comments[]?.body // "" | select(contains("Generated with"))] | length > 0 | tostring)
    ')"
    echo "$meta"
    headSha="$(gh pr view "$number" --json headRefOid --jq .headRefOid)"
    rows="$(gh pr view "$number" --json files --jq '.files[] | "\(.additions+.deletions)\t\(.path)"')"
    while IFS=$'\t' read -r lines path; do
      [[ -z "${path:-}" ]] && continue
      total_files=$((total_files + 1))
      if is_excluded "$path"; then
        excluded_list+=("$path")
      else
        reviewable_list+=("$path")
        reviewable_lines=$((reviewable_lines + lines))
        # File's own current byte size at the PR head, as a proxy for line count — avoids
        # downloading full file content just to measure it.
        encoded_path="$(urlencode "$path")"
        file_bytes="$(gh api "repos/{owner}/{repo}/contents/$encoded_path?ref=$headSha" --jq '.size' 2>/dev/null || echo "")"
        [[ -n "$file_bytes" && "$file_bytes" -gt $LARGE_FILE_BYTES ]] && large_files+=("$path (~$file_bytes bytes)")
      fi
    done <<< "$rows"
    ;;
  *)
    echo "usage: preflight.sh diff [range] [pathfilter] | pr <number>" >&2
    exit 2
    ;;
esac

reviewable_count=${#reviewable_list[@]}
excluded_count=${#excluded_list[@]}

echo "FILES_TOTAL: $total_files"
echo "FILES_EXCLUDED: $excluded_count"
for f in "${excluded_list[@]:-}"; do
  [[ -n "$f" ]] && echo "EXCLUDED: $f"
done
echo "FILES_REVIEWABLE: $reviewable_count"
echo "LINES_CHANGED: $reviewable_lines"
for f in "${large_files[@]:-}"; do
  [[ -n "$f" ]] && echo "LARGE_FILE: $f"
done
if [[ $reviewable_count -gt 15 || $reviewable_lines -gt 800 ]]; then
  echo "SIZE_FLAG: large"
else
  echo "SIZE_FLAG: ok"
fi
if [[ $total_files -eq 0 ]]; then
  echo "EMPTY: yes"
else
  echo "EMPTY: no"
fi
