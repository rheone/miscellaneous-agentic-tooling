# Claude Code CLI Cheat Sheet

## Command-line reference — Linux / macOS edition

> `claude` starts an interactive session. Pass `-p` for non-interactive (print) mode.

---

## 1. Starting Sessions

| Command                         | Action                                |
| ------------------------------- | ------------------------------------- |
| `claude`                        | Start interactive session             |
| `claude "explain this project"` | Start interactive with initial prompt |
| `claude -p "query"`             | Print mode — run query, exit          |
| `cat file \| claude -p "query"` | Pipe file content as context          |
| `claude -c`                     | Continue most recent conversation     |
| `claude -c -p "query"`          | Continue in print mode                |
| `claude -r <session>`           | Resume a session by ID or name        |
| `claude -r <session> "prompt"`  | Resume with a new prompt              |
| `claude -n "my-feature"`        | Set a display name for the session    |

---

## 2. Non-interactive / Print Mode

| Flag                                      | Description                                     |
| ----------------------------------------- | ----------------------------------------------- |
| `-p, --print "query"`                     | Run query, print response, exit                 |
| `--output-format text\|json\|stream-json` | Output format                                   |
| `--json-schema <schema>`                  | Get validated JSON output matching a schema     |
| `--max-turns <N>`                         | Limit agentic turns (exits with error at limit) |
| `--max-budget-usd <$>`                    | Max spend on API calls                          |
| `--no-session-persistence`                | Don't save session to disk                      |

### Examples

```sh
# Quick query
claude -p "Explain closures in JavaScript"

# JSON output
claude -p --output-format json "List all API endpoints"

# With turn limit
claude -p --max-turns 5 "Refactor this file"
```

---

## 3. Pipeline & Automation

| Command                           | Action                                       |
| --------------------------------- | -------------------------------------------- |
| `cat file \| claude -p "query"`   | Pipe file content as context                 |
| `claude --bare -p "query"`        | Minimal mode — skip auto-discovery for speed |
| `claude --init -p "query"`        | Run setup hooks before query                 |
| `claude --init-only`              | Run setup hooks, then exit                   |
| `claude --effort high`            | Set effort level (low/medium/high/xhigh/max) |
| `claude --fallback-model <model>` | Comma-separated fallback models              |

### Examples

```sh
# Pipe log output for analysis
cat app.log | claude -p "Find errors and suggest fixes"

# Bare mode for fast scripting
claude --bare -p "Count lines in all .py files"

# With setup hooks
claude --init -p "Build the project"
```

---

## 4. Permission Modes

| Flag                                    | Description                                   |
| --------------------------------------- | --------------------------------------------- |
| `--permission-mode default`             | Manual mode — prompt for each action          |
| `--permission-mode acceptEdits`         | Auto-accept edits, prompt for commands        |
| `--permission-mode plan`                | Plan-only mode — no edits or commands         |
| `--permission-mode auto`                | Auto-decide based on risk                     |
| `--permission-mode bypassPermissions`   | Skip all permission prompts                   |
| `--dangerously-skip-permissions`        | Same as `--permission-mode bypassPermissions` |
| `--allowedTools "Bash(git *)" "Read"`   | Tools that skip permission prompts            |
| `--disallowedTools "Bash(rm *)" "Edit"` | Tools to deny entirely                        |
| `--tools "Bash,Edit,Read"`              | Restrict available built-in tools             |

### Example

```sh
claude --permission-mode plan "Design the database schema"
```

---

## 5. System Prompt Flags

| Flag                                 | Description                       |
| ------------------------------------ | --------------------------------- |
| `--system-prompt "text"`             | Replace entire system prompt      |
| `--system-prompt-file <path>`        | Load replacement prompt from file |
| `--append-system-prompt "text"`      | Append to default system prompt   |
| `--append-system-prompt-file <path>` | Append from file                  |

```sh
claude --append-system-prompt "Always use TypeScript" -p "Fix this file"
```

---

## 6. Background Agents & Daemon

| Command                          | Action                                            |
| -------------------------------- | ------------------------------------------------- |
| `claude --bg "task"`             | Start a background session, return immediately    |
| `claude --bg --exec "pytest -x"` | Run shell command as PTY background job           |
| `claude agents`                  | Open agent view to monitor/dispatch sessions      |
| `claude agents --json`           | List active sessions as JSON                      |
| `claude attach <id>`             | Attach terminal to a background session           |
| `claude logs <id>`               | Print recent output from a background session     |
| `claude stop <id>`               | Stop a background session                         |
| `claude rm <id>`                 | Remove a background session from list             |
| `claude respawn <id>`            | Restart a background session (keeps conversation) |
| `claude respawn --all`           | Restart all running sessions                      |
| `claude daemon status`           | Check supervisor state                            |
| `claude daemon stop --any`       | Stop supervisor and sessions                      |

---

## 7. Authentication

| Command                       | Action                                 |
| ----------------------------- | -------------------------------------- |
| `claude auth login`           | Sign in to Anthropic account           |
| `claude auth login --console` | Sign in with API key (Console)         |
| `claude auth login --sso`     | Force SSO authentication               |
| `claude auth logout`          | Log out                                |
| `claude auth status`          | Show auth status as JSON               |
| `claude auth status --text`   | Human-readable auth status             |
| `claude setup-token`          | Generate long-lived OAuth token for CI |

---

## 8. MCP Management

| Command                    | Action                               |
| -------------------------- | ------------------------------------ |
| `claude mcp`               | Open MCP server configuration        |
| `claude mcp login <name>`  | Run OAuth flow for an MCP server     |
| `claude mcp logout <name>` | Clear stored OAuth credentials       |
| `--mcp-config <path>`      | Load MCP servers from JSON file      |
| `--strict-mcp-config`      | Only use servers from `--mcp-config` |

---

## 9. Utilities

| Command                                  | Action                                     |
| ---------------------------------------- | ------------------------------------------ |
| `claude update`                          | Update to latest version                   |
| `claude install <version>`               | Install specific version                   |
| `claude install stable`                  | Install stable release                     |
| `claude install latest`                  | Install latest (pre-release)               |
| `claude plugin install <name>`           | Install a plugin                           |
| `claude project purge <path>`            | Delete all local state for a project       |
| `claude --worktree <name>` / `-w <name>` | Start in isolated git worktree             |
| `claude --tmux`                          | Create tmux session for worktree           |
| `claude gateway --config <path>`         | Start self-hosted apps gateway (v2.1.195+) |
| `claude remote-control`                  | Start Remote Control server                |
| `claude --cloud "task"`                  | Create web session on claude.ai            |
| `claude --teleport`                      | Resume web session in local terminal       |
| `claude auto-mode defaults`              | Print built-in auto-mode rules             |
| `claude ultrareview <target>`            | Run ultrareview non-interactively          |
| `claude -v`                              | Print version number                       |

---

## 10. Key Flags Reference

| Flag                                 | Description                                          |
| ------------------------------------ | ---------------------------------------------------- |
| `--model <alias\|name>`              | Set model (sonnet, opus, haiku, fable, or full name) |
| `--agent <name>`                     | Specify a custom agent                               |
| `--agents '<json>'`                  | Define custom subagents dynamically                  |
| `--add-dir <path>`                   | Additional working directories                       |
| `--chrome`                           | Enable Chrome browser integration                    |
| `--no-chrome`                        | Disable Chrome integration                           |
| `--safe-mode`                        | Start with all customizations disabled               |
| `--debug "<category>"`               | Enable debug mode with optional filter               |
| `--debug-file <path>`                | Write debug logs to file                             |
| `--verbose`                          | Show full turn-by-turn output                        |
| `--disable-slash-commands`           | Disable all skills and commands                      |
| `--ide`                              | Auto-connect to IDE on startup                       |
| `--betas <feature>`                  | Beta headers for API requests                        |
| `--session-id <uuid>`                | Use a specific session ID                            |
| `--setting-sources user,project`     | Which setting sources to load                        |
| `--settings <file\|json>`            | Override settings for this session                   |
| `--fork-session`                     | Fork when resuming (new session ID)                  |
| `--from-pr <number\|url>`            | Resume sessions linked to a PR                       |
| `--advisor <model>`                  | Enable server-side advisor tool                      |
| `--ax-screen-reader`                 | Screen-reader friendly output                        |
| `--channels <plugin:...>`            | Listen for MCP channel notifications                 |
| `--include-hook-events`              | Include hook events in output stream                 |
| `--include-partial-messages`         | Include partial streaming events                     |
| `--input-format text\|stream-json`   | Input format for print mode                          |
| `--replay-user-messages`             | Re-emit user messages for ack                        |
| `--prompt-suggestions`               | Emit prompt suggestions after each turn              |
| `--teammate-mode auto\|tmux\|iterm2` | Agent team display mode                              |
| `--remote-control` / `--rc`          | Enable Remote Control in interactive mode            |

---

## 11. Practical Examples

```sh
# Quick question
claude -p "How do I sort a list in Python?"

# Resume and continue work
claude -r auth-refactor "Finish the remaining tests"

# Background investigation
claude --bg "Find the cause of the flaky test"

# Pipe content + query
cat package.json | claude -p "Suggest dependency updates"

# Print mode with structured output
claude -p --output-format json "List all npm scripts" > scripts.json

# Budget-limited automation
claude -p --max-budget-usd 2.00 "Fix all lint errors"

# Bare mode for fast scripting
claude --bare -p "Count LOC in src/"

# Safe mode to troubleshoot config issues
claude --safe-mode

# With custom model and effort
claude -p --model claude-sonnet-5 --effort high "Review this PR"

# Worktree for isolated changes
claude -w feature-auth

# System prompt override
claude --system-prompt "You are a Python expert" -p "Review this script"
```

---

_Version: 2026-07-04 · Claude Code v2.1+ | Source: [code.claude.com/docs/en/cli-reference](https://code.claude.com/docs/en/cli-reference) — shortcuts can vary by terminal and Claude Code version — verify against your installed version._

_© 2026 Robert H. Engelhardt · Apache 2.0 License_
_Latest version: [https://github.com/rheone/miscellaneous-agentic-tooling](https://github.com/rheone/miscellaneous-agentic-tooling)_
