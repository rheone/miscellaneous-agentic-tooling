# OpenCode CLI Cheat Sheet

## Command-line reference — Linux / macOS edition

> `opencode` starts the TUI by default. Pass a prompt or command for non-interactive mode.

---

## 1. Basic Usage

| Command | Action |
|---|---|
| `opencode` | Start TUI in current directory |
| `opencode <project-dir>` | Start TUI in a specific project |
| `opencode run <message>` | Run non-interactive with a prompt |
| `opencode run "refactor this file"` | Single-shot query, exits after response |
| `opencode -c` | Continue the last session |
| `opencode -s <sessionID>` | Continue a specific session by ID |
| `opencode --fork` | Fork (copy) the session when continuing |

---

## 2. Session Management

| Command | Action |
|---|---|
| `opencode session list` | List all sessions (`-n N` to limit, `--format json`) |
| `opencode session delete <id>` | Delete a session |
| `opencode export <sessionID>` | Export session as JSON (`--sanitize` to redact) |
| `opencode import <file\|url>` | Import from JSON file or share URL |
| `opencode stats` | Show token/cost stats (`--days N`, `--models`, `--project`) |

---

## 3. Authentication & Providers

| Command | Action |
|---|---|
| `opencode auth login` | Interactive login — configure API keys |
| `opencode auth login --provider <id>` | Login to a specific provider |
| `opencode auth list` / `auth ls` | List authenticated providers |
| `opencode auth logout` | Remove stored credentials |

---

## 4. Model & Agent Selection

| Command | Action |
|---|---|
| `opencode run -m <provider/model>` | Run with a specific model |
| `opencode models` | List available models |
| `opencode models <provider>` | List models for a specific provider |
| `opencode models --refresh` | Refresh model cache from models.dev |
| `opencode agent list` | List available agents |
| `opencode agent create` | Create a new agent interactively |
| `opencode run --agent <name>` | Run with a specific agent |

### Agent Create (non-interactive)

```sh
opencode agent create \
  --path .opencode/agents/my-agent.md \
  --description "Reviews pull requests" \
  --mode subagent \
  --permissions read,edit,glob,grep
```

---

## 5. MCP Management

| Command | Action |
|---|---|
| `opencode mcp add` | Add an MCP server interactively |
| `opencode mcp list` / `mcp ls` | List configured MCP servers |
| `opencode mcp auth <name>` | Authenticate with an OAuth MCP server |
| `opencode mcp auth list` / `mcp auth ls` | List OAuth-capable servers |
| `opencode mcp logout <name>` | Remove OAuth credentials |
| `opencode mcp debug <name>` | Debug OAuth connection issues |

---

## 6. Server & Web Mode

| Command | Action |
|---|---|
| `opencode serve` | Start headless HTTP server (API access) |
| `opencode web` | Start server with web interface (opens browser) |
| `opencode attach <url>` | Attach TUI to a running backend server |

### Server flags

| Flag | Description |
|---|---|
| `--port` | Port to listen on |
| `--hostname` | Hostname to listen on |
| `--mdns` | Enable mDNS discovery |
| `--cors` | Additional browser origin(s) for CORS |

### Example: headless server + attached client

```sh
# Terminal 1 — start server
export OPENCODE_SERVER_PASSWORD=mypass
opencode serve --port 4096

# Terminal 2 — attach TUI
opencode attach http://localhost:4096
```

---

## 7. GitHub & PRs

| Command | Action |
|---|---|
| `opencode github install` | Install GitHub agent in repository |
| `opencode github run` | Run GitHub agent (for Actions) |
| `opencode pr <number>` | Fetch PR branch and run OpenCode |

---

## 8. Plugin Management

| Command | Action |
|---|---|
| `opencode plugin <module>` | Install a plugin |
| `opencode plug <module>` | Short alias for plugin install |
| `opencode plugin <module> -g` | Install globally |
| `opencode plugin <module> -f` | Force replace existing version |

---

## 9. Utilities

| Command | Action |
|---|---|
| `opencode upgrade` | Update to latest version |
| `opencode upgrade <version>` | Upgrade to a specific version (e.g. `v1.17.13`) |
| `opencode uninstall` | Remove OpenCode and all files |
| `opencode uninstall --keep-config` | Uninstall but keep config |
| `opencode uninstall --dry-run` | Preview what would be removed |
| `opencode db` | Run database query |
| `opencode db path` | Print database path |
| `opencode debug` | Debugging/troubleshooting tools |

---

## 10. Global Flags

| Flag | Short | Description |
|---|---|---|
| `--help` | `-h` | Display help |
| `--version` | `-v` | Print version number |
| `--print-logs` | | Print logs to stderr |
| `--log-level <level>` | | Log level: `DEBUG`, `INFO`, `WARN`, `ERROR` |
| `--pure` | | Run without external plugins |

---

## 11. Key Environment Variables

| Variable | Description |
|---|---|
| `OPENCODE_CONFIG` | Path to config file |
| `OPENCODE_CONFIG_DIR` | Path to config directory |
| `OPENCODE_TUI_CONFIG` | Path to TUI config file |
| `OPENCODE_SERVER_PASSWORD` | Password for `serve`/`web` HTTP basic auth |
| `OPENCODE_SERVER_USERNAME` | Username for basic auth (default: `opencode`) |
| `OPENCODE_DISABLE_AUTOUPDATE` | Disable auto-update checks |
| `OPENCODE_DISABLE_MOUSE` | Disable mouse in TUI |
| `OPENCODE_AUTO_SHARE` | Auto-share sessions (boolean) |

---

## 12. Practical Examples

```sh
# Quick question
opencode run "How do I sort a list in Python?"

# With file context
opencode run -f src/main.js "Find bugs in this file"

# Specific model
opencode run -m anthropic/claude-sonnet-5 "Explain this code"

# Continue last session non-interactively
opencode run -c "Finish what you started"

# Export thinking blocks
opencode run --thinking "Debug this crash"

# List recent sessions as JSON
opencode session list -n 10 --format json

# Start web interface on a specific port
opencode web --port 8080 --hostname 0.0.0.0

# Auto-approve permissions (use with caution)
opencode run --auto "Install and configure ESLint"
```

---

*Version: 2026-07-04 · OpenCode v1.17.13 | Source: [opencode.ai/docs/cli](https://opencode.ai/docs/cli) — verify against your installed version.*

*© 2026 Robert H. Engelhardt · Apache 2.0 License*
*Latest version: [https://github.com/rheone/miscellaneous-agentic-tooling](https://github.com/rheone/miscellaneous-agentic-tooling)*
