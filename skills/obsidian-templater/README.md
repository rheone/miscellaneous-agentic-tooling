# Obsidian Templater Skill

Create and validate Obsidian templates using the Templater plugin. Covers Templater v2.x — the `tp.date`, `tp.file`, `tp.system`, `tp.web`, `tp.frontmatter`, `tp.hooks`, `tp.obsidian`, `tp.app`, `tp.config`, and `tp.user` modules.

## Installation

```bash
npx skills add rheone/miscellaneous-agentic-tooling --skill obsidian-templater
```

## Contents

| File | Description |
|------|-------------|
| `SKILL.md` | Main instructions, workflows, gotchas, checklist-driven execution |
| `references/commands.md` | Command syntax, whitespace control, tR |
| `references/date-module.md` | tp.date, moment.js |
| `references/file-module.md` | tp.file (16 functions) |
| `references/system-module.md` | tp.system prompts and suggesters |
| `references/web-module.md` | tp.web daily quote, images, requests |
| `references/app-obsidian.md` | tp.app, tp.config, tp.obsidian |
| `references/frontmatter-hooks.md` | tp.frontmatter, tp.hooks |
| `references/user-functions.md` | Scripts, system commands, settings |
| `examples/EXAMPLES.md` | 6 practical templates |
| `scripts/validate-template.ps1` | PowerShell template validator |
| `scripts/validate-template.py` | Python template validator |
| `scripts/validate-template.sh` | Bash template validator |
| `testing/TESTING.md` | Jest testing for user scripts |

## Requirements

- [Obsidian](https://obsidian.md/) with the [Templater](https://github.com/SilentVoid13/Templater) plugin installed.
- For validation scripts: PowerShell 7+, Python 3.6+, or Bash.
- For user script testing: Node.js 18+ and Jest.
