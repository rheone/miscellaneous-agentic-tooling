# System Module — `tp.system`

Interactive prompts and clipboard access. All functions are **async — require `await`**.

## Functions

### `tp.system.clipboard()`

Reads the system clipboard. No arguments.

```markdown
Clipboard: <% tp.system.clipboard() %>
```

### `tp.system.prompt(prompt_text?, default_value?, throw_on_cancel?, multiline?)`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `prompt_text` | string | — | Label shown above the input |
| `default_value` | string | — | Pre-filled value |
| `throw_on_cancel` | boolean | `false` | If `true`, throws error on cancel instead of returning `null` |
| `multiline` | boolean | `false` | If `true`, shows a textarea |

```markdown
<% await tp.system.prompt("Enter your name") %>
<% await tp.system.prompt("What is your mood?", "happy") %>
<% await tp.system.prompt("Write notes", null, false, true) %>
```

Reuse the value:

```markdown
<%*
let name = await tp.system.prompt("What is your name?");
%>
# Hello, <% name %>
```

> **Cancellation**: `prompt()`, `suggester()`, and `multi_suggester()` return `null` when the user cancels (unless `throw_on_cancel: true`). Guard with `if (!result) return;` or use optional chaining: `<% (await tp.system.suggester(...))?.basename %>`.

### `tp.system.suggester(text_items, items, throw_on_cancel?, placeholder?, limit?, default_value?)`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `text_items` | string[] \| (item) => string | — | Display texts or mapping function |
| `items` | T[] | — | Values underlying each choice |
| `throw_on_cancel` | boolean | `false` | Throw on cancel instead of returning `null` |
| `placeholder` | string | `""` | Placeholder text |
| `limit` | number | — | Max items rendered at once (performance) |
| `default_value` | T | — | Pre-selected item |

```markdown
<% await tp.system.suggester(["A", "B"], ["a", "b"]) %>
<% await tp.system.suggester((item) => item.basename, tp.app.vault.getMarkdownFiles()) %>
[[<% (await tp.system.suggester((item) => item.basename, tp.app.vault.getMarkdownFiles())).basename %>]]
```

### `tp.system.multi_suggester(text_items, items, throw_on_cancel?, title?, limit?, default_values?)

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `text_items` | string[] \| (item) => string | — | Display texts or mapping function |
| `items` | T[] | — | Values |
| `throw_on_cancel` | boolean | `false` | Throw on cancel |
| `title` | string | `""` | Modal title |
| `limit` | number | — | Max items rendered |
| `default_values` | T[] | — | Pre-selected items |

```markdown
<% (await tp.system.multi_suggester((item) => item.basename, tp.app.vault.getMarkdownFiles())).map(f => `[[${f.basename}]]`) %>
<% await tp.system.multi_suggester(["Happy","Sad"], ["happy","sad"], false, "Choose moods", undefined, ["happy"]) %>
```
