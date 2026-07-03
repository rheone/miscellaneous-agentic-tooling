#!/usr/bin/env bash
# Validates a Templater template file for syntax errors.
# Checks for balanced <% %> tags, unclosed commands, and unrecognized
# tp.* function names against a known API reference table.
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <template.md>"
  exit 1
fi

FILE="$1"
if [ ! -f "$FILE" ]; then
  echo "File not found: $FILE"
  exit 1
fi

ERRORS=()

OPEN_COUNT=$(grep -c '<%' "$FILE" || true)
CLOSE_COUNT=$(grep -c '%>' "$FILE" || true)

if [ "$OPEN_COUNT" -ne "$CLOSE_COUNT" ]; then
  ERRORS+=("UNBALANCED TAGS: $OPEN_COUNT opening vs $CLOSE_COUNT closing")
fi

# Known tp.* functions (grep patterns)
KNOWN_FUNCTIONS=(
  'tp\.date\.now' 'tp\.date\.tomorrow' 'tp\.date\.yesterday' 'tp\.date\.weekday'
  'tp\.file\.content' 'tp\.file\.create_new' 'tp\.file\.creation_date'
  'tp\.file\.cursor' 'tp\.file\.cursor_append' 'tp\.file\.exists'
  'tp\.file\.find_tfile' 'tp\.file\.folder' 'tp\.file\.include'
  'tp\.file\.last_modified_date' 'tp\.file\.move' 'tp\.file\.path'
  'tp\.file\.rename' 'tp\.file\.selection' 'tp\.file\.tags' 'tp\.file\.title'
  'tp\.frontmatter' 'tp\.hooks\.on_all_templates_executed'
  'tp\.system\.clipboard' 'tp\.system\.prompt' 'tp\.system\.suggester'
  'tp\.system\.multi_suggester' 'tp\.web\.daily_quote' 'tp\.web\.random_picture'
  'tp\.web\.request' 'tp\.obsidian' 'tp\.app' 'tp\.config' 'tp\.user'
)

# Extract all tp.* function calls and check against known list
TP_CALLS=$(grep -oP 'tp\.\w+(?:\.\w+)*' "$FILE" | sort -u || true)
while IFS= read -r call; do
  [ -z "$call" ] && continue
  FOUND=0
  for fn in "${KNOWN_FUNCTIONS[@]}"; do
    if echo "$call" | grep -qP "^$fn"; then
      FOUND=1
      break
    fi
  done
  if [ "$FOUND" -eq 0 ]; then
    LINE=$(grep -n "$call" "$FILE" | head -1 | cut -d: -f1)
    ERRORS+=("UNKNOWN FUNCTION at line $LINE: $call")
  fi
done <<< "$TP_CALLS"

# Check for unclosed tags
if awk 'BEGIN{tag=0} /<%[\*\+\-]?/{tag=1} /%>/{tag=0} END{exit tag}' "$FILE"; then
  ERRORS+=("UNCLOSED TAG reaches end of file")
fi

if [ ${#ERRORS[@]} -eq 0 ]; then
  echo "OK: Template validated successfully ($OPEN_COUNT commands)"
  exit 0
else
  echo "ISSUES FOUND (${#ERRORS[@]}):"
  for err in "${ERRORS[@]}"; do
    echo "  $err"
  done
  exit 1
fi
