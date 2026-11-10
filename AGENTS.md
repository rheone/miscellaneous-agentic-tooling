# AGENTS.md — miscellaneous-agentic-tooling

This repository ["miscellaneous-agentic-tooling"](https://github.com/rheone/miscellaneous-agentic-tooling) contains:

- Agentic AI skills for
  - Home Assistant
  - Obsidian.md knowledge management
- Agentic cheat sheets for OpenCode and Claude
- Other miscellaneous related tooling

## Repository structure

```structure
.
├── skills/
│   ├── homeassistant-awtrix/    # AWTRIX 3: SKILL.md + EXAMPLES.md + REFERENCE.md
│   ├── homeassistant-awtrix-ng/ # AWTRIX NG: SKILL.md + NOTICE.md + references/ (13 files); PolyForm Noncommercial
│   ├── homeassistant-pixoo64/   # SKILL.md + README.md + references/ + examples/ + tools/ (Python, with tests)
│   ├── obsidian-ics-sync/       # SKILL.md + scripts/sync_calendar.py
│   └── obsidian-templater/      # SKILL.md + references/ (8 files) + scripts/ + examples/ + testing/TESTING.md
├── cheatsheets/
│   ├── claude/                  # Claude Code CLI + keybinding cheatsheets (html+md per platform)
│   └── opencode/                # OpenCode CLI + keybinding cheatsheets (html+md per platform)
├── .editorconfig
├── .gitignore
└── README.md
```

## Skill conventions

```
my-skill/
├── SKILL.md          # Required: agent-facing instructions + YAML frontmatter
├── README.md         # Optional: user-facing documentation about the skill
├── scripts/          # Optional: executable code (prefer cross-platform trio: pwsh + py + sh)
├── references/       # Optional: reference docs split from SKILL.md when it exceeds ~150 lines
├── assets/           # Optional: templates, resources
└── examples/         # Optional: practical examples
```

**Frontmatter** uses 3-space indent per `.editorconfig`. Real skills use these fields:

```yaml
---
name: homeassistant-awtrix
description: >-
  One- or two-sentence description of what the skill does and when to use it.
  Also list key trigger phrases an agent should pick up on.
license: Apache-2.0
user-invocable: true
metadata:
  source: https://github.com/rheone/miscellaneous-agentic-tooling
  author: Robert Engelhardt <rheone@gmail.com>
  version: "1.0.2"
---
```

## Conventions

- **License**: Apache-2.0, except `skills/homeassistant-awtrix-ng/`, which is PolyForm-Noncommercial-1.0.0 (see its NOTICE.md). Skills that bundle third-party files keep those licenses next to the files.
- **No build/lint/CI** — content-only repo. No `package.json` at root.
- **Cheatsheets** in `cheatsheets/{claude,opencode}/` are generated as both `.html` and `.md` per tool per platform — keep in sync when updating.
- **Scripts**: prefer cross-platform coverage (pwsh + py + sh).
