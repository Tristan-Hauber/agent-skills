#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_dir="$root/skills"
destination="${CODEX_SKILLS_DIR:-$HOME/.agents/skills}"
replace=false

case "${1:-}" in
  "") ;;
  --replace) replace=true ;;
  *) printf 'Usage: %s [--replace]\n' "$0" >&2; exit 2 ;;
esac

"$root/validate.sh"
mkdir -p "$destination"
staging="$(mktemp -d "${destination%/}/.codex-github-workflow.XXXXXX")"
cleanup() { rm -rf "$staging"; }
trap cleanup EXIT

cp -R "$source_dir"/. "$staging"/

for skill in "$staging"/*; do
  name="$(basename "$skill")"
  target="$destination/$name"
  backup="$destination/.${name}.backup.$$"

  if [[ -e "$target" && "$replace" != true ]]; then
    printf 'Refusing to overwrite existing skill: %s\n' "$target" >&2
    printf 'Re-run with --replace to update this bundle.\n' >&2
    exit 1
  fi

  rm -rf "$backup"
  if [[ -e "$target" ]]; then
    mv "$target" "$backup"
  fi

  if mv "$skill" "$target"; then
    rm -rf "$backup"
  else
    rm -rf "$target"
    if [[ -e "$backup" ]]; then mv "$backup" "$target"; fi
    exit 1
  fi
done

printf 'Installed %s skills in %s\n' "$(find "$source_dir" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')" "$destination"
printf 'All skills are explicit-only; invoke them with $skill-name.\n'
