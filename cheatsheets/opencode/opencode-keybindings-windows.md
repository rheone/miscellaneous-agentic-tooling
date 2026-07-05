# OpenCode Keybinding Cheat Sheet

## Default keybinds — Windows edition

> Leader key: **Ctrl+X** — press it, release, then press the next key.
> Example: **Ctrl+X** then **N** = new session.

---

## 1. Leader Key Basics

| Keys                | Action                                                           |
| ------------------- | ---------------------------------------------------------------- |
| `Ctrl+X` then `key` | Leader combo — activates a 2-second window to press the next key |
| `Ctrl+P` | Open command palette |

> **Tip:** You don't have to put custom keybinds behind the leader, but it's strongly recommended to avoid conflicts with your terminal or shell.
> The leader timeout is configurable via `leader_timeout` (in milliseconds) in `tui.json`; default is `2000`.

---

## 2. App Control

| Keys                             | Action                                      |
| -------------------------------- | ------------------------------------------- |
| `Ctrl+C` / `Ctrl+D` / `Ctrl+X Q` | Exit OpenCode                               |
| `Ctrl+X E`                       | Open external editor for composing messages |
| `Ctrl+X T`                       | Open theme list                             |
| `Ctrl+X B`                       | Toggle sidebar                              |
| `Ctrl+X S`                       | Toggle status view                          |

---

## 3. Session Management

| Keys       | Action                      |
| ---------- | --------------------------- |
| `Ctrl+X N` | New session                 |
| `Ctrl+X L` | List sessions               |
| `Ctrl+X G` | Session timeline            |
| `Ctrl+X X` | Export session to Markdown  |
| `Ctrl+X C` | Compact / summarize session |
| `Ctrl+R`   | Rename session              |
| `Ctrl+D`   | Delete session              |
| `Escape`   | Interrupt running response  |

---

## 4. Subagent / Session Navigation

| Keys              | Action                               |
| ----------------- | ------------------------------------ |
| `Ctrl+X` then `↓` | Go to first child (subagent) session |
| `→` | Cycle to next child session |
| `←` | Cycle to previous child session |
| `↑` | Go to parent session |

The arrow keys (`→`, `←`, `↑`) intentionally skip the leader key for quick subagent navigation. This means they may conflict with your terminal emulator's own bindings more readily than leader-prefixed shortcuts. To move them behind the leader, remap the corresponding action in `tui.json` (e.g. `"session_parent": "<leader>up"`).

---

## 5. Models & Agents

| Keys        | Action                          |
| ----------- | ------------------------------- |
| `Ctrl+A`    | List model providers            |
| `Ctrl+F`    | Toggle model as favorite        |
| `Ctrl+X M`  | Open model list                 |
| `F2`        | Cycle recent models (forward)   |
| `Shift+F2`  | Cycle recent models (reverse)   |
| `Ctrl+X A`  | Open agent list                 |
| `Tab`       | Cycle agent (e.g. Build → Plan) |
| `Shift+Tab` | Cycle agent (reverse)           |
| `Ctrl+T`    | Cycle variant                   |

---

## 6. Messages: Scrolling & Navigation

| Keys                       | Action                |
| -------------------------- | --------------------- |
| `Page Up` / `Ctrl+Alt+B`   | Page up               |
| `Page Down` / `Ctrl+Alt+F` | Page down             |
| `Ctrl+Alt+Y`               | Line up               |
| `Ctrl+Alt+E`               | Line down             |
| `Ctrl+Alt+U`               | Half page up          |
| `Ctrl+Alt+D`               | Half page down        |
| `Ctrl+G` / `Home`          | Jump to first message |
| `Ctrl+Alt+G` / `End`       | Jump to last message  |

---

## 7. Messages: Actions

| Keys       | Action                                         |
| ---------- | ---------------------------------------------- |
| `Ctrl+X Y` | Copy message                                   |
| `Ctrl+X U` | Undo                                           |
| `Ctrl+X R` | Redo                                           |
| `Ctrl+X H` | Toggle message concealment (also toggles tips) |

---

## 8. Input Editing — Move Cursor

| Keys                         | Action                            |
| ---------------------------- | --------------------------------- |
| `←` / `Ctrl+B`               | Move left one character           |
| `→` / `Ctrl+F`               | Move right one character          |
| `↑`                          | Move up a line / previous history |
| `↓`                          | Move down a line / next history   |
| `Alt+F` / `Alt+→` / `Ctrl+→` | Move forward one word             |
| `Alt+B` / `Alt+←` / `Ctrl+←` | Move backward one word            |
| `Ctrl+A`                     | Move to start of line             |
| `Ctrl+E`                     | Move to end of line               |
| `Alt+A`                      | Move to start of visual line      |
| `Alt+E`                      | Move to end of visual line        |
| `Home`                       | Move to start of buffer           |
| `End`                        | Move to end of buffer             |

## 9. Input Editing — Select Text

| Keys                          | Action                         |
| ----------------------------- | ------------------------------ |
| `Shift+←` / `Shift+→`         | Select character left / right  |
| `Shift+↑` / `Shift+↓`         | Select line up / down          |
| `Alt+Shift+F` / `Alt+Shift+→` | Select word forward            |
| `Alt+Shift+B` / `Alt+Shift+←` | Select word backward           |
| `Ctrl+Shift+A`                | Select to start of line        |
| `Ctrl+Shift+E`                | Select to end of line          |
| `Alt+Shift+A`                 | Select to start of visual line |
| `Alt+Shift+E`                 | Select to end of visual line   |
| `Shift+Home`                  | Select to start of buffer      |
| `Shift+End`                   | Select to end of buffer        |
| `Super+A`                     | Select all                     |

## 10. Input Editing — Delete

| Keys                                          | Action                    |
| --------------------------------------------- | ------------------------- |
| `Backspace` / `Shift+Backspace`               | Delete character backward |
| `Ctrl+D` / `Delete` / `Shift+Delete`          | Delete character forward  |
| `Ctrl+K`                                      | Delete to end of line     |
| `Ctrl+U`                                      | Delete to start of line   |
| `Ctrl+Shift+D`                                | Delete entire line        |
| `Alt+D` / `Alt+Delete` / `Ctrl+Delete`        | Delete word forward       |
| `Ctrl+W` / `Ctrl+Backspace` / `Alt+Backspace` | Delete word backward      |

## 11. Input Editing — Undo / History

| Keys                               | Action                 |
| ---------------------------------- | ---------------------- |
| `Ctrl+Z` \* / `Ctrl+-` / `Super+Z` | Undo                   |
| `Ctrl+.` / `Super+Shift+Z`         | Redo                   |
| `↑` (in empty input)               | Previous history entry |
| `↓` (in empty input)               | Next history entry     |

\* `Ctrl+Z` is added to `input_undo` by default **only on Windows**, since Windows terminals don't support POSIX suspend.

## 12. Input Editing — Submit & Newline

| Keys                                                  | Action                                           |
| ----------------------------------------------------- | ------------------------------------------------ |
| `Enter`                                               | Submit prompt                                    |
| `Shift+Enter` / `Ctrl+Enter` / `Alt+Enter` / `Ctrl+J` | Insert newline (see Windows Terminal note below) |
| `Ctrl+C`                                              | Clear input                                      |
| `Ctrl+V`                                              | Paste                                            |

---

## 13. Dialogs & Autocomplete

| Keys                    | Action                              |
| ----------------------- | ----------------------------------- |
| `↑` / `Ctrl+P`          | Previous item in list dialog        |
| `↓` / `Ctrl+N`          | Next item in list dialog            |
| `Page Up` / `Page Down` | Page through dialog list            |
| `Home` / `End`          | Jump to top / bottom of dialog list |
| `Enter`                 | Confirm selection                   |
| `Space`                 | Toggle item (MCP list, plugin list) |
| `Escape`                | Hide autocomplete                   |
| `Tab`                   | Complete autocomplete suggestion    |
| `Shift+I`               | Install plugin (plugin dialog)      |
| `Ctrl+F`                | Fullscreen permission prompt        |

---

## 14. Which-Key Menu

| Keys                        | Action                      |
| --------------------------- | --------------------------- |
| `Ctrl+Alt+K`                | Toggle which-key menu       |
| `Ctrl+Alt+Shift+K`          | Toggle which-key layout     |
| `Ctrl+Alt+Shift+P`          | Toggle pending keys display |
| `Ctrl+Alt+←` / `Ctrl+Alt+[` | Previous key group          |
| `Ctrl+Alt+→` / `Ctrl+Alt+]` | Next key group              |
| `Ctrl+Alt+↑` / `Ctrl+Alt+P` | Scroll up                   |
| `Ctrl+Alt+↓` / `Ctrl+Alt+N` | Scroll down                 |
| `Ctrl+Alt+Page Up/Down`     | Page through which-key      |
| `Ctrl+Alt+Home/End`         | Jump to top / bottom        |

---

## 15. Windows-Specific Notes

- **Leader key** default is `Ctrl+X` — same on Windows as elsewhere.
- **`terminal_suspend`** is disabled (`none`) by default on Windows, since native Windows terminals don't support POSIX process suspend.
- **`input_undo`** includes an extra `Ctrl+Z` binding on Windows only (in addition to `Ctrl+-` and `Super+Z`).
- **Shift+Enter for newline** doesn't work out of the box in some terminals. To fix it in **Windows Terminal**:
   1. Open `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json`
   2. Add to the root-level `actions` array:

      ```json
      {
         "command": { "action": "sendInput", "input": "\u001b[13;2u" },
         "id": "User.sendInput.ShiftEnterCustom"
      }
      ```

   3. Add to the root-level `keybindings` array:

      ```json
      { "keys": "shift+enter", "id": "User.sendInput.ShiftEnterCustom" }
      ```

   4. Save and restart Windows Terminal (or open a new tab).
    - Alternatively, use `Ctrl+Enter`, `Alt+Enter`, or `Ctrl+J` for a newline without any config changes.

---

## Customizing Keybinds

Edit `tui.json` in your OpenCode config directory. Example:

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

---

## Working in VS Code's Integrated Terminal

VS Code's integrated terminal intercepts some keystrokes before they reach OpenCode. The most commonly affected default bindings are:

| Key | VS Code default | OpenCode action |
|---|---|---|
| `Ctrl+F` | Terminal find | Toggle model favorite |
| `Alt+←` / `Alt+→` | Navigate back / forward | Word backward / forward |
| `Ctrl+G` | Terminal find (focused) | Jump to first message |
| `Ctrl+K` | Chord prefix / clear | Delete to end of line |

**Recommended workarounds (pick one):**

1. **Use the leader key** — Most affected bindings have a leader-prefixed equivalent (e.g. `Ctrl+X M` instead of `Ctrl+A` for model list). Prefer these in VS Code's terminal.

2. **Override VS Code shortcuts** — Forward the keys to the terminal by adding to VS Code's `keybindings.json`:
   ```jsonc
   {
     "key": "ctrl+f",
     "command": "-workbench.action.terminal.focusFind",
     "when": "terminalFocus"
   },
   {
     "key": "alt+left",
     "command": "-workbench.action.navigateBack",
     "when": "terminalFocus"
   },
   {
     "key": "alt+right",
     "command": "-workbench.action.navigateForward",
     "when": "terminalFocus"
   },
   {
     "key": "ctrl+g",
     "command": "-workbench.action.terminal.focusFind",
     "when": "terminalFocus"
   }
   ```

3. **Remap in `tui.json`** — Move conflict-prone direct keys behind the leader:
   ```json
   {
     "keybinds": {
       "model_favorite_toggle": "<leader>f",
       "input_word_forward": "<leader>w",
       "input_word_backward": "<leader>b"
     }
   }
   ```

To find out what VS Code is doing with a specific keypress, run **Developer: Toggle Keyboard Shortcuts Troubleshooting** from the VS Code command palette and watch the output panel.

Edit `tui.json` in your OpenCode config directory. Example:

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

_Version: 2026-07-05 · OpenCode v1.17.13 | Source: [opencode.ai/docs/keybinds](https://opencode.ai/docs/keybinds) — verify against your installed version, as defaults can change between releases._

_© 2026 Robert H. Engelhardt · Apache 2.0 License_
_Latest version: [https://github.com/rheone/miscellaneous-agentic-tooling](https://github.com/rheone/miscellaneous-agentic-tooling)_
