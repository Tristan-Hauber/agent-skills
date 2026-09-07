#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
destination=${CLAUDE_TELEMETRY_ROOT:-"$HOME/.agents/telemetry"}
mkdir -p "$destination/bin" "$destination/data" "$destination/state" "$destination/collector" "$destination/tests"
cp "$root/semantic.py" "$destination/semantic.py"
cp "$root/bin/telemetry" "$destination/bin/telemetry"
cp "$root/bin/record-context" "$destination/bin/record-context"
cp "$root/schema.md" "$destination/schema.md"
chmod 700 "$destination/semantic.py" "$destination/bin/telemetry" "$destination/bin/record-context"
settings="$HOME/.claude/settings.json"
if [ -f "$settings" ] && command -v jq >/dev/null 2>&1; then
  backup="$settings.stage1-backup.$(date +%Y%m%d%H%M%S)"
  cp "$settings" "$backup"
  tmp=$(mktemp "$settings.stage2.XXXXXX")
  if jq --arg command "$destination/bin/record-context" '
    .hooks = (.hooks // {}) |
    reduce ["SessionStart", "SessionEnd", "PreCompact", "PostCompact", "InstructionsLoaded", "PreModelSwitch", "PostModelSwitch"][] as $event
      (. ; .hooks[$event] = ((.hooks[$event] // []) |
        if any(.[]?.hooks[]?; .command == $command) then .
        else . + [{hooks: [{type: "command", command: $command, async: true}]}] end))
  ' "$settings" >"$tmp"; then
    chmod 600 "$tmp"
    mv "$tmp" "$settings"
    printf 'Added semantic context hooks; settings backup: %s\n' "$backup"
  else
    rm -f "$tmp"
    printf 'WARNING: settings update failed; backup retained: %s\n' "$backup" >&2
  fi
fi
printf 'Installed semantic telemetry runtime in %s\n' "$destination"
printf 'Run %s/bin/telemetry phase --help for explicit phase markers.\n' "$destination"
printf 'Add %s/bin/record-context as an async command to lifecycle hooks to enable automatic context capture.\n' "$destination"
