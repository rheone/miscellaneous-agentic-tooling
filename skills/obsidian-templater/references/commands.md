# Commands Reference

## Command Syntax

All commands use opening tag `<%...` and closing tag `%>`.

### Interpolation `<% expression %>`

Evaluates the expression and outputs the result:

```markdown
Today: <% tp.date.now() %>
File: <% tp.file.title %>
```

### Execution `<%* code %>`

Executes JavaScript code. Outputs nothing by default — use the `tR` variable:

```markdown
<%* tR += "Hello from JS"; %>
```

Overwrite `tR` to discard everything generated so far:

```markdown
<%* tR = ""; %>
---
clean: frontmatter
---
```

### Dynamic `<%+ expression %>`

Resolved in preview mode only. Has known issues — **deprecated**. Use Dataview instead.

## Whitespace Control

Control characters go inside the tag, before `%>` or after `<%`:

| Syntax | Effect |
|--------|--------|
| `-%>` | Trim **one** newline **after** the command |
| `<%-` | Trim **one** newline **before** the command |
| `_%>` | Trim **all** whitespace **after** the command |
| `<%_` | Trim **all** whitespace **before** the command |

Without whitespace control, execution commands leave blank lines in the output:

```markdown
<%* if (x) { -%>
Visible
<%* } -%>
```

The `-%>` removes the newline from the `}` line, collapsing output cleanly.

## tR Variable

`tR` is the internal replacement string. The engine collects all interpolation output into `tR`, then writes it to the file.

- **Append**: `tR += "some text";`
- **Overwrite**: `tR = "new content";`
- Overwriting discards everything the engine has already accumulated

## await Requirement

These functions are async and require `await`:

| Module | Functions |
|--------|-----------|
| `tp.file` | `create_new()`, `include()`, `exists()`, `move()`, `rename()` |
| `tp.system` | `prompt()`, `suggester()`, `multi_suggester()` |
| `tp.web` | `daily_quote()`, `random_picture()`, `request()` |
| `tp.hooks` | `on_all_templates_executed()` |
| `tp.obsidian` | `requestUrl()` |

Forgetting `await` silently returns a Promise object instead of the expected value.

## Argument Types

| Type | Example |
|------|---------|
| `string` | `"value"` or `'value'` |
| `number` | `7`, `-3` |
| `boolean` | `true`, `false` |

## Function Signatures

Documentation uses this form: `tp.func(arg1: type, arg2?: type, arg3: type = default)`. When calling, pass **only values**:

```markdown
<% tp.date.now("YYYY-MM-DD", 7) %>
```
