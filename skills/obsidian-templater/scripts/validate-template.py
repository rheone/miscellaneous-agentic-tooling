#!/usr/bin/env python3
"""
Validates a Templater template file for syntax errors.
Checks for balanced <% %> tags, unclosed commands, and unrecognized
tp.* function names against a known API reference table.
"""

import re
import sys
from pathlib import Path


KNOWN_FUNCTIONS = [
    r'tp\.date\.now', r'tp\.date\.tomorrow', r'tp\.date\.yesterday',
    r'tp\.date\.weekday',
    r'tp\.file\.content', r'tp\.file\.create_new', r'tp\.file\.creation_date',
    r'tp\.file\.cursor', r'tp\.file\.cursor_append', r'tp\.file\.exists',
    r'tp\.file\.find_tfile', r'tp\.file\.folder', r'tp\.file\.include',
    r'tp\.file\.last_modified_date', r'tp\.file\.move', r'tp\.file\.path',
    r'tp\.file\.rename', r'tp\.file\.selection', r'tp\.file\.tags',
    r'tp\.file\.title',
    r'tp\.frontmatter', r'tp\.hooks\.on_all_templates_executed',
    r'tp\.system\.clipboard', r'tp\.system\.prompt', r'tp\.system\.suggester',
    r'tp\.system\.multi_suggester', r'tp\.web\.daily_quote',
    r'tp\.web\.random_picture', r'tp\.web\.request',
    r'tp\.obsidian', r'tp\.app', r'tp\.config', r'tp\.user',
]


def validate(path: str) -> int:
    content = Path(path).read_text(encoding="utf-8")
    errors: list[str] = []

    open_count = len(re.findall(r'<%[\*\+\-]?', content))
    close_count = len(re.findall(r'%>', content))

    if open_count != close_count:
        errors.append(
            f"UNBALANCED TAGS: {open_count} opening vs {close_count} closing"
        )

    tp_calls = re.findall(r'tp\.\w+(?:\.\w+)*', content)
    for call in tp_calls:
        if not any(re.match(fn, call) for fn in KNOWN_FUNCTIONS):
            lines = Path(path).read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines, 1):
                if call in line:
                    errors.append(
                        f"UNKNOWN FUNCTION at line {i}: {call}"
                    )
                    break

    lines = Path(path).read_text(encoding="utf-8").splitlines()
    in_tag = False
    for i, line in enumerate(lines):
        if re.search(r'<%[\*\-\+]?', line):
            in_tag = True
        if '%>' in line:
            in_tag = False
        if in_tag and i == len(lines) - 1:
            errors.append("UNCLOSED TAG reaches end of file")

    if not errors:
        print(f"OK: Template validated successfully ({open_count} commands)")
        return 0

    print(f"ISSUES FOUND ({len(errors)}):")
    for err in errors:
        print(f"  {err}")
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <template.md>")
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))
