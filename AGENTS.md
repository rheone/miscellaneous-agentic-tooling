# AGENTS.md — miscellaneous-agentic-tooling

Agentic AI skills for Home Assistant automation and Obsidian knowledge management, distributed as [OpenCode/Claude Code skills](https://github.com/rheone/miscellaneous-agentic-tooling).

## Repository structure

```
skills/
├── homeassistant-awtrix/    # SKILL.md + EXAMPLES.md + REFERENCE.md
├── homeassistant-pixoo64/   # SKILL.md + EXAMPLES.md + REFERENCE.md
├── obsidian-ics-sync/       # SKILL.md + scripts/sync_calendar.py
└── obsidian-templater/      # SKILL.md + references/ + scripts/ + testing/TESTING.md
```

## Skills

Skill should be structured as:

```file tree
my-skill/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
├── README.md         # User facing documentation about the skill
└── ...               # Any additional files or directories
```

include appropriate yaml frontmatter:

```yaml
---
name: [skill-name]
description: [What the skill does and when to use it]
license: Apache 2.0
compatibility: opencode
metadata:
  audience: [e.g., maintainers]
---
```

## Installation

```bash
# All skills
npx skills add rheone/miscellaneous-agentic-tooling
# Single skill
npx skills add rheone/miscellaneous-agentic-tooling --skill homeassistant-awtrix
# List/enable/disable
npx skills list
npx skills enable homeassistant-awtrix
npx skills disable obsidian-ics-sync
```

## Conventions

- **EditorConfig**: 3-space indent for `*.{json,jsonc,yml,yaml,md,ps1}`, 4-space for `*.py`, LF line endings, UTF-8
- **License**: Apache-2.0
- **Skill frontmatter**: `name`, `description`, `license: Apache-2.0`, `author`, `version`, optionally `user-invocable: true`
- **No build/lint/CI tooling** — content-only repo. No package.json at root.
- **Python**: `obsidian-ics-sync` requires Python 3.6+; `obsidian-templater/scripts/validate-template.py` also available
- **Templater validation**: scripts in `skills/obsidian-templater/scripts/validate-template.{ps1,py,sh}` — each works independently
- **Templater testing**: Node 18+ and Jest; see `skills/obsidian-templater/testing/TESTING.md`
