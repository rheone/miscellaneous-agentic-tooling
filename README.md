# Miscellaneous Agentic Tooling

Miscellaneous Agentic AI tooling [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview), [OpenCode](https://opencode.ai/), and other AI coding agents.

- [Miscellaneous Agentic Tooling](#miscellaneous-agentic-tooling)
  - [Skills](#skills)
    - [Installation](#installation)
    - [Licenses](#licenses)
    - [Using AWTRIX 3 or AWTRIX NG](#using-awtrix-3-or-awtrix-ng)
    - [Manage installed skills](#manage-installed-skills)
  - [Cheatsheets](#cheatsheets)
  - [Guides](#guides)
  - [References](#references)

## Skills

| Category             | Skill                                                             | Description                                                                  |
| -------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Home Assistant**   | [`homeassistant-awtrix`](skills/homeassistant-awtrix)             | Control AWTRIX 3 on Ulanzi TC001 pixel clocks — notifications, apps, sounds  |
| **Home Assistant**   | [`homeassistant-awtrix-ng`](skills/homeassistant-awtrix-ng)       | Control AWTRIX NG (Blueforcer) clocks over MQTT — notifications, pushed apps, icons, sounds, Berry scripts. Noncommercial license |
| **Home Assistant**   | [`homeassistant-pixoo64`](skills/homeassistant-pixoo64)           | Design Divoom Pixoo 64 pages with the `divoom_pixoo` 1.24.0 integration — font and glyph checks, PNG previews, tested example pages |
| **Obsidian**         | [`obsidian-templater`](skills/obsidian-templater)                 | Create Obsidian templates with Templater syntax, validation, and testing     |
| **Obsidian**         | [`obsidian-ics-sync`](skills/obsidian-ics-sync)                   | Sync ICS calendar events into Obsidian daily notes with wikilink matching    |
| **Markdown**         | [`github-markdown`](skills/github-markdown)                       | Author GitHub Flavored Markdown — tables, code blocks, diagrams, math, alerts |


### Installation

Install all skills:

```bash
npx skills add rheone/miscellaneous-agentic-tooling
```

Install specific skills:

```bash
# Home Assistant skills
npx skills add rheone/miscellaneous-agentic-tooling --skill homeassistant-awtrix --skill homeassistant-awtrix-ng --skill homeassistant-pixoo64

# Obsidian skills
npx skills add rheone/miscellaneous-agentic-tooling --skill obsidian-templater --skill obsidian-ics-sync

# Markdown skills
npx skills add rheone/miscellaneous-agentic-tooling --skill github-markdown
```

Install from a local path:

```bash
npx skills add /path/to/misc-agentic-tooling
```

### Licenses

Most of this repository is Apache-2.0. [`homeassistant-awtrix-ng`](skills/homeassistant-awtrix-ng) is licensed [PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0), the same license as AWTRIX NG, and is for noncommercial use only. See its [NOTICE.md](skills/homeassistant-awtrix-ng/NOTICE.md). [`homeassistant-pixoo64`](skills/homeassistant-pixoo64) bundles a copy of the MIT-licensed `divoom_pixoo` font code and SIL OFL fonts, with their licenses next to them.

### Using AWTRIX 3 or AWTRIX NG

The two firmwares share no API. Use `homeassistant-awtrix` for AWTRIX 3 and `homeassistant-awtrix-ng` for AWTRIX NG.

### Manage installed skills

```bash
# See what's installed and active
npx skills list

# Enable / disable selectively
npx skills enable homeassistant-awtrix homeassistant-awtrix-ng homeassistant-pixoo64
npx skills disable obsidian-ics-sync
```

## Cheatsheets

| Tool | Subject | Platform | HTML | Markdown |
|------|---------|----------|------|----------|
| **Claude Code** | CLI | Linux/macOS | [HTML](cheatsheets/claude/claude-code-cli-linux-mac.html) | [Markdown](cheatsheets/claude/claude-code-cli-linux-mac.md) |
| **Claude Code** | CLI | Windows | [HTML](cheatsheets/claude/claude-code-cli-windows.html) | [Markdown](cheatsheets/claude/claude-code-cli-windows.md) |
| **Claude Code** | Keybindings | Linux/macOS | [HTML](cheatsheets/claude/claude-code-keybindings-linux-mac.html) | [Markdown](cheatsheets/claude/claude-code-keybindings-linux-mac.md) |
| **Claude Code** | Keybindings | Windows | [HTML](cheatsheets/claude/claude-code-keybindings-windows.html) | [Markdown](cheatsheets/claude/claude-code-keybindings-windows.md) |
| **OpenCode** | CLI | Linux/macOS | [HTML](cheatsheets/opencode/opencode-cli-linux-mac.html) | [Markdown](cheatsheets/opencode/opencode-cli-linux-mac.md) |
| **OpenCode** | CLI | Windows | [HTML](cheatsheets/opencode/opencode-cli-windows.html) | [Markdown](cheatsheets/opencode/opencode-cli-windows.md) |
| **OpenCode** | Keybindings | Linux/macOS | [HTML](cheatsheets/opencode/opencode-keybindings-linux-mac.html) | [Markdown](cheatsheets/opencode/opencode-keybindings-linux-mac.md) |
| **OpenCode** | Keybindings | Windows | [HTML](cheatsheets/opencode/opencode-keybindings-windows.html) | [Markdown](cheatsheets/opencode/opencode-keybindings-windows.md) |

## Guides

Narrative, conceptual guides — slash commands, models, reasoning-effort levels, and sub-agent dispatch (parallel vs serial) — for developers new to agentic coding tools. Complements the terse Cheatsheets above rather than replacing them.

| Tool | Guide | Description |
|------|-------|-------------|
| **Claude Code** | [`claude-code-guide.md`](cheatsheets/claude/claude-code-guide.md) | Slash commands (TUI vs UI, plan vs build), CLI args, models, `--effort` levels, sub-agent dispatch, and a Skills/Agents/Plugins/MCP/Hooks/LSP glossary |
| **OpenCode** | [`opencode-guide.md`](cheatsheets/opencode/opencode-guide.md) | Slash commands, Plan/Build mode, CLI args, provider-agnostic models, reasoning variants, `@agent` sub-agent dispatch, and a Skills/Plugins/MCP/Hooks/LSP glossary |

## References

Deep-dive reference documentation for third-party agent skill ecosystems and related tooling.

| Subject | Document | Description |
|---------|----------|-------------|
| **Matt Pocock Skills** | [`matt-pocock-skills-v1.2.3.md`](references/matt-pocock-skills-v1.2.3.md) | A reference & guide to Matt Pocock's [`mattpocock/skills`](https://github.com/mattpocock/skills) ecosystem (v1.2.3) — 25 agent skills for grilling, TDD, code review, triage, wayfinder, and codebase maintenance, with workflow diagrams |
