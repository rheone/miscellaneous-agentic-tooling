# Claude Code Keyboard Shortcuts Cheat Sheet

## Default keybinds — Windows edition

> No leader key — shortcuts fire directly. Vim editing mode is optional (enable via `/config` → Editor mode).

---

## 1. General Controls

| Keys | Action |
|---|---|
| `Ctrl+C` | Interrupt running operation; if idle, clears input (press again to exit) |
| `Ctrl+D` | Exit Claude Code session (EOF signal) |
| `Ctrl+X` `Ctrl+K` | Stop all background subagents (press twice within 3s to confirm) |
| `Ctrl+G` / `Ctrl+X` `Ctrl+E` | Open prompt in your default text editor |
| `Ctrl+L` | Redraw screen (fixes garbled display) |
| `Ctrl+O` | Toggle transcript viewer |
| `Ctrl+R` | Reverse search command history |
| `Ctrl+V` (or `Alt+V` on WSL) | Paste image from clipboard |
| `Ctrl+B` | Background running task (tmux: press twice) |
| `Ctrl+T` | Toggle task list |
| `←` / `→` | Cycle dialog tabs |
| `↑` / `↓` or `Ctrl+P` / `Ctrl+N` | Move cursor within input, then navigate history |
| `Esc` | Interrupt Claude mid-turn |
| `Esc` `Esc` | Clear input draft, or open rewind menu (if input empty) |
| `Shift+Tab` (or `Alt+M`\*) | Cycle permission modes (default → acceptEdits → plan → …) |
| `Alt+P` | Switch model |
| `Alt+T` | Toggle extended thinking |
| `Alt+O` | Toggle fast mode |

\* `Alt+M` is a fallback for older Node (<24.2.0/22.17.0) or Bun (<1.2.23) without VT mode, where Shift+Tab may not register on Windows.

---

## 2. Text Editing (Readline-style)

| Keys | Action |
|---|---|
| `Ctrl+A` | Move to start of current line |
| `Ctrl+E` | Move to end of current line |
| `Ctrl+K` | Delete to end of line (stored for pasting) |
| `Ctrl+U` | Delete from cursor to line start (stored for pasting) |
| `Ctrl+W` / `Ctrl+Backspace` | Delete previous word |
| `Ctrl+Y` | Paste text deleted with Ctrl+K / Ctrl+U / Ctrl+W |
| `Alt+Y` (after `Ctrl+Y`) | Cycle through paste history |
| `Alt+B` | Move cursor back one word |
| `Alt+F` | Move cursor forward one word |

---

## 3. Multiline Input

| Method | Keys | Notes |
|---|---|---|
| Quick escape | `\` then `Enter` | Works in every terminal |
| Shift+Enter | `Shift+Enter` | Native in Windows Terminal |
| Control sequence | `Ctrl+J` | Works anywhere, no setup |
| Paste mode | Paste directly | For code blocks / logs |

> VS Code, Cursor, Alacritty, and Zed on Windows need `/terminal-setup` run once to enable Shift+Enter.

---

## 4. Quick Commands

| Trigger | Action |
|---|---|
| `/` at start of input | Open command / skill menu |
| `!` at start of input | Shell mode — run a command directly |
| `@` | File path autocomplete |

---

## 5. Transcript Viewer *(opened with Ctrl+O)*

| Keys | Action |
|---|---|
| `?` | Toggle shortcut help panel (fullscreen rendering only) |
| `{` / `}` | Jump to previous / next user prompt (fullscreen only) |
| `Ctrl+E` | Toggle "show all content" |
| `[` | Write conversation to terminal's native scrollback (fullscreen) |
| `v` | Open conversation in `$VISUAL`/`$EDITOR` (fullscreen) |
| `q` / `Ctrl+C` / `Esc` | Exit transcript view |

---

## 6. Vim Mode — Switching *(enable in `/config`)*

| Keys | Action | From |
|---|---|---|
| `Esc` | Enter NORMAL mode | INSERT, VISUAL |
| `i` / `I` | Insert before cursor / at line start | NORMAL |
| `a` / `A` | Insert after cursor / at line end | NORMAL |
| `o` / `O` | Open line below / above | NORMAL |
| `v` / `V` | Start char-wise / line-wise visual selection | NORMAL |

## 7. Vim Mode — Navigation (NORMAL)

| Keys | Action |
|---|---|
| `h` `j` `k` `l` | Left / down / up / right |
| `w` / `e` / `b` | Next word / end of word / previous word |
| `0` / `$` / `^` | Line start / line end / first non-blank char |
| `gg` / `G` | Start / end of input |
| `f{char}` / `F{char}` | Jump to next / previous occurrence of char |
| `t{char}` / `T{char}` | Jump just before / after occurrence of char |
| `;` / `,` | Repeat last f/F/t/T motion (forward / reverse) |
| `/` | Open reverse history search (same as Ctrl+R) |

## 8. Vim Mode — Editing (NORMAL)

| Keys | Action |
|---|---|
| `x` | Delete character |
| `dd` | Delete line |
| `D` | Delete to end of line |
| `dw` / `de` / `db` | Delete word / to end / back |
| `cc` / `C` | Change line / change to end of line |
| `cw` / `ce` / `cb` | Change word / to end / back |
| `yy` / `Y` | Yank (copy) line |
| `yw` / `ye` / `yb` | Yank word / to end / back |
| `p` / `P` | Paste after / before cursor |
| `>>` / `<<` | Indent / dedent line |
| `J` | Join lines |
| `u` | Undo |
| `.` | Repeat last change |

## 9. Vim Mode — Text Objects *(with d / c / y)*

| Keys | Action |
|---|---|
| `iw` / `aw` | Inner / around word |
| `iW` / `aW` | Inner / around WORD |
| `i"` / `a"` | Inner / around double quotes |
| `i'` / `a'` | Inner / around single quotes |
| `i(` / `a(` | Inner / around parentheses |
| `i[` / `a[` | Inner / around brackets |
| `i{` / `a{` | Inner / around braces |

## 10. Vim Mode — Visual Mode

| Keys | Action |
|---|---|
| `d` / `x` | Delete selection |
| `y` | Yank selection |
| `c` / `s` | Change selection |
| `p` | Replace selection with register |
| `r{char}` | Replace every selected char |
| `~` / `u` / `U` | Toggle / lowercase / uppercase selection |
| `>` / `<` | Indent / dedent selected lines |
| `J` | Join selected lines |
| `o` | Swap cursor and anchor |
| `v` / `V` | Toggle char-wise/line-wise, or exit |

*(Block-wise visual mode — `Ctrl+V` — is not supported.)*

---

## 11. Command History & Reverse Search

| Keys | Action |
|---|---|
| `↑` / `↓` | Navigate input history |
| `Ctrl+R` | Start reverse history search |
| `Ctrl+R` (again) | Cycle to older matches |
| `Ctrl+S` | Cycle search scope: session → project → all |
| `Tab` / `Esc` | Accept match, keep editing |
| `Enter` | Accept match and execute immediately |
| `Ctrl+C` | Cancel search, restore original input |
| `Backspace` (empty query) | Cancel search |

---

## 12. Background Bash & Shell Mode

| Keys | Action |
|---|---|
| `Ctrl+B` | Move a running Bash command to the background (tmux: press twice) |
| `!command` | Run directly in shell mode; output + response added to context |
| `Tab` (in `!` mode) | Autocomplete from `!` history or file paths |
| `Escape` / `Backspace` / `Ctrl+U` (empty `!`) | Exit shell mode |

---

## 13. Voice Input

| Keys | Action |
|---|---|
| Hold or tap `Space` | Voice dictation (if enabled; run `/voice tap` for tap-to-toggle) |

---

## 14. Windows-Specific Notes

- **Alt-key shortcuts** (`Alt+B`, `Alt+F`, `Alt+Y`, `Alt+P`, `Alt+T`, `Alt+O`, `Alt+M`) work **natively** on Windows and Linux — no terminal configuration needed. (macOS requires enabling Option-as-Meta; see the Linux/macOS sheet.)
- **Image paste**: `Ctrl+V` normally works; on **WSL** specifically, both `Ctrl+V` and `Alt+V` are bound — use `Alt+V` if your terminal intercepts `Ctrl+V`.
- **`Ctrl+Backspace`** is an extra Windows-only binding for "delete previous word" (same as `Ctrl+W`).
- **Shift+Enter** works natively in **Windows Terminal**. In VS Code, Cursor, Alacritty, or Zed on Windows, run `/terminal-setup` once to install the binding.
- If **Shift+Tab** doesn't cycle permission modes, you're likely on an older Node (<24.2.0/22.17.0) or Bun (<1.2.23) without VT mode — use `Alt+M` instead.
- PR links in the footer: `Ctrl+click` to open in your browser (macOS uses `Cmd+click`).

---

*Version: 2026-07-04 · Claude Code v2.1+ | Source: [code.claude.com/docs/en/interactive-mode](https://code.claude.com/docs/en/interactive-mode) — shortcuts can vary by terminal and Claude Code version — verify against your installed version.*

*© 2026 Robert H. Engelhardt · Apache 2.0 License*
*Latest version: [https://github.com/rheone/miscellaneous-agentic-tooling](https://github.com/rheone/miscellaneous-agentic-tooling)*
