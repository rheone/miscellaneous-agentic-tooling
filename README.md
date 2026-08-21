# Miscellaneous Agentic Tooling

Miscellaneous Agentic AI tooling [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview), [OpenCode](https://opencode.ai/), and other AI coding agents.

- [Skills](#skills)
- [Installation](#installation)
- [Cheatsheets](#cheatsheets)
- [Guides](#guides)

## Skills

| Category             | Skill                                                             | Description                                                                  |
| -------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Home Assistant**   | [`homeassistant-awtrix`](skills/homeassistant-awtrix)             | Control AWTRIX 3 on Ulanzi TC001 pixel clocks — notifications, apps, sounds  |
| **Home Assistant**   | [`homeassistant-pixoo64`](skills/homeassistant-pixoo64)           | Control Divoom Pixoo 64 displays — 8 page types, push notifications          |
| **Obsidian**         | [`obsidian-templater`](skills/obsidian-templater)                 | Create Obsidian templates with Templater syntax, validation, and testing     |
| **Obsidian**         | [`obsidian-ics-sync`](skills/obsidian-ics-sync)                   | Sync ICS calendar events into Obsidian daily notes with wikilink matching    |

### Installation

Install all skills:

```bash
npx skills add rheone/miscellaneous-agentic-tooling
```

Install specific skills:

```bash
# Home Assistant skills
npx skills add rheone/miscellaneous-agentic-tooling --skill homeassistant-awtrix --skill homeassistant-pixoo64

# Obsidian skills
npx skills add rheone/miscellaneous-agentic-tooling --skill obsidian-templater --skill obsidian-ics-sync
```

Install from a local path:

```bash
npx skills add /path/to/misc-agentic-tooling
```

### Manage installed skills

```bash
# See what's installed and active
npx skills list

# Enable / disable selectively
npx skills enable homeassistant-awtrix homeassistant-pixoo64
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
