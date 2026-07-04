# OpenCode Keybinding Cheat Sheet

## Default keybinds — Linux / macOS edition

> Leader key: **Ctrl+X** — press it, release, then press the next key.
> Example: **Ctrl+X** then **N** = new session.

---

## 1. Leader Key Basics

| Keys | Action |
|---|---|
| `Ctrl+X` then `key` | Leader combo — activates a 2-second window to press the next key |
| `Ctrl+P` | Open command palette |

---

## 2. App Control

| Keys | Action |
|---|---|
| `Ctrl+C` / `Ctrl+D` / `Ctrl+X Q` | Exit OpenCode |
| `Ctrl+X E` | Open external editor for composing messages |
| `Ctrl+X T` | Open theme list |
| `Ctrl+X B` | Toggle sidebar |
| `Ctrl+X S` | Toggle status view |

---

## 3. Session Management

| Keys | Action |
|---|---|
| `Ctrl+X N` | New session |
| `Ctrl+X L` | List sessions |
| `Ctrl+X G` | Session timeline |
| `Ctrl+X X` | Export session to Markdown |
| `Ctrl+X C` | Compact / summarize session |
| `Ctrl+R` | Rename session |
| `Ctrl+D` | Delete session |
| `Escape` | Interrupt running response |

---

## 4. Subagent / Session Navigation

| Keys | Action |
|---|---|
| `Ctrl+X` then `↓` | Go to first child (subagent) session |
| `→` | Cycle to next child session |
| `←` | Cycle to previous child session |
| `↑` | Go to parent session |

---

## 5. Models & Agents

| Keys | Action |
|---|---|
| `Ctrl+A` | List model providers |
| `Ctrl+F` | Toggle model as favorite |
| `Ctrl+X M` | Open model list |
| `F2` | Cycle recent models (forward) |
| `Shift+F2` | Cycle recent models (reverse) |
| `Ctrl+X A` | Open agent list |
| `Tab` | Cycle agent (e.g. Build → Plan) |
| `Shift+Tab` | Cycle agent (reverse) |
| `Ctrl+T` | Cycle variant |

---

## 6. Messages: Scrolling & Navigation

| Keys | Action |
|---|---|
| `Page Up` / `Ctrl+Alt+B` | Page up |
| `Page Down` / `Ctrl+Alt+F` | Page down |
| `Ctrl+Alt+Y` | Line up |
| `Ctrl+Alt+E` | Line down |
| `Ctrl+Alt+U` | Half page up |
| `Ctrl+Alt+D` | Half page down |
| `Ctrl+G` / `Home` | Jump to first message |
| `Ctrl+Alt+G` / `End` | Jump to last message |

---

## 7. Messages: Actions

| Keys | Action |
|---|---|
| `Ctrl+X Y` | Copy message |
| `Ctrl+X U` | Undo |
| `Ctrl+X R` | Redo |
| `Ctrl+X H` | Toggle message concealment (also toggles tips) |

---

## 8. Input Editing — Move Cursor

| Keys | Action |
|---|---|
| `←` / `Ctrl+B` | Move left one character |
| `→` / `Ctrl+F` | Move right one character |
| `↑` | Move up a line / previous history |
| `↓` | Move down a line / next history |
| `Alt+F` / `Alt+→` / `Ctrl+→` | Move forward one word |
| `Alt+B` / `Alt+←` / `Ctrl+←` | Move backward one word |
| `Ctrl+A` | Move to start of line |
| `Ctrl+E` | Move to end of line |
| `Alt+A` | Move to start of visual line |
| `Alt+E` | Move to end of visual line |
| `Home` | Move to start of buffer |
| `End` | Move to end of buffer |

## 9. Input Editing — Select Text

| Keys | Action |
|---|---|
| `Shift+←` / `Shift+→` | Select character left / right |
| `Shift+↑` / `Shift+↓` | Select line up / down |
| `Alt+Shift+F` / `Alt+Shift+→` | Select word forward |
| `Alt+Shift+B` / `Alt+Shift+←` | Select word backward |
| `Ctrl+Shift+A` | Select to start of line |
| `Ctrl+Shift+E` | Select to end of line |
| `Alt+Shift+A` | Select to start of visual line |
| `Alt+Shift+E` | Select to end of visual line |
| `Shift+Home` | Select to start of buffer |
| `Shift+End` | Select to end of buffer |
| `Cmd+A` (macOS) / `Super+A` (Linux) | Select all |

## 10. Input Editing — Delete

| Keys | Action |
|---|---|
| `Backspace` / `Shift+Backspace` | Delete character backward |
| `Ctrl+D` / `Delete` / `Shift+Delete` | Delete character forward |
| `Ctrl+K` | Delete to end of line |
| `Ctrl+U` | Delete to start of line |
| `Ctrl+Shift+D` | Delete entire line |
| `Alt+D` / `Alt+Delete` / `Ctrl+Delete` | Delete word forward |
| `Ctrl+W` / `Ctrl+Backspace` / `Alt+Backspace` | Delete word backward |

## 11. Input Editing — Undo / History

| Keys | Action |
|---|---|
| `Ctrl+-` / `Cmd+Z` (macOS) / `Super+Z` (Linux) | Undo |
| `Ctrl+.` / `Cmd+Shift+Z` (macOS) / `Super+Shift+Z` (Linux) | Redo |
| `↑` (in empty input) | Previous history entry |
| `↓` (in empty input) | Next history entry |

\* `Ctrl+Z` is **not** bound to undo on Linux/macOS — see Platform Notes below, it's reserved for suspending OpenCode.

## 12. Input Editing — Submit & Newline

| Keys | Action |
|---|---|
| `Enter` | Submit prompt |
| `Shift+Enter` / `Ctrl+Enter` / `Alt+Enter` / `Ctrl+J` | Insert newline |
| `Ctrl+C` | Clear input |
| `Cmd+V` (macOS) / `Ctrl+V` (Linux) | Paste |

---

## 13. Dialogs & Autocomplete

| Keys | Action |
|---|---|
| `↑` / `Ctrl+P` | Previous item in list dialog |
| `↓` / `Ctrl+N` | Next item in list dialog |
| `Page Up` / `Page Down` | Page through dialog list |
| `Home` / `End` | Jump to top / bottom of dialog list |
| `Enter` | Confirm selection |
| `Space` | Toggle item (MCP list, plugin list) |
| `Escape` | Hide autocomplete |
| `Tab` | Complete autocomplete suggestion |
| `Shift+I` | Install plugin (plugin dialog) |
| `Ctrl+F` | Fullscreen permission prompt |

---

## 14. Which-Key Menu

| Keys | Action |
|---|---|
| `Ctrl+Alt+K` | Toggle which-key menu |
| `Ctrl+Alt+Shift+K` | Toggle which-key layout |
| `Ctrl+Alt+Shift+P` | Toggle pending keys display |
| `Ctrl+Alt+←` / `Ctrl+Alt+[` | Previous key group |
| `Ctrl+Alt+→` / `Ctrl+Alt+]` | Next key group |
| `Ctrl+Alt+↑` / `Ctrl+Alt+P` | Scroll up |
| `Ctrl+Alt+↓` / `Ctrl+Alt+N` | Scroll down |
| `Ctrl+Alt+Page Up/Down` | Page through which-key |
| `Ctrl+Alt+Home/End` | Jump to top / bottom |

---

## 15. Platform Notes: Linux vs macOS

**Terminal suspend (both platforms)**

- `Ctrl+Z` suspends OpenCode to the background by default (`terminal_suspend`). Run `fg` in your shell to bring it back.
- Because `Ctrl+Z` is reserved for suspend, it is **not** part of the default Undo binding here (unlike Windows). Use `Ctrl+-` or `Cmd+Z`/`Super+Z` for Undo instead.

**macOS specifics**

- The `Super` modifier maps to **Cmd**. `Super+Z` in config = `Cmd+Z` on your keyboard.
- Many `Alt`-based shortcuts (`Alt+F`, `Alt+B`, `Alt+D`, the `Ctrl+Alt+…` which-key shortcuts) require **Option acting as Meta** in your terminal:
  - **iTerm2**: Settings → Profiles → Keys → General → set Left/Right Option key to "Esc+"
  - **Terminal.app**: Settings → Profiles → Keyboard → check "Use Option as Meta Key"
  - **VS Code**: set `"terminal.integrated.macOptionIsMeta": true`
- Paste is `Cmd+V`.

**Linux specifics**

- `Alt`-based shortcuts work natively in most Linux terminals — no Meta configuration needed.
- The `Super` modifier is your keyboard's **Windows/Super key**. Many desktop environments (GNOME, KDE) intercept bare `Super` presses for the Activities/app overview, which can swallow `Super+Z` / `Super+A` before OpenCode sees them. If a Super-based binding doesn't register, either remap it in `tui.json` or disable the conflicting OS-level shortcut in your desktop settings.
- Paste is typically `Ctrl+V`.

**Both**

- `Shift+Enter` for a newline works natively in most Linux/macOS terminal emulators. If yours doesn't send it correctly, use `Ctrl+Enter`, `Alt+Enter`, or `Ctrl+J` instead.

---

## Customizing Keybinds

Edit `tui.json` in your OpenCode config directory (typically `~/.config/opencode/tui.json`). Example:

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "keybinds": {
    "leader": "ctrl+x",
    "session_new": "<leader>n"
  }
}
```

- Multiple bindings: separate with commas, e.g. `"ctrl+g,home"`
- Leader prefix: use `<leader>`, e.g. `"<leader>n"`
- Disable a keybind: set its value to `"none"`

*Version: 2026-07-04 · OpenCode v1.17.13 | Source: [opencode.ai/docs/keybinds](https://opencode.ai/docs/keybinds) — verify against your installed version, as defaults can change between releases.*

*© 2026 Robert H. Engelhardt · Apache 2.0 License*
*Latest version: [https://github.com/rheone/miscellaneous-agentic-tooling](https://github.com/rheone/miscellaneous-agentic-tooling)*
