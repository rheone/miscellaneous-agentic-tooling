# User Functions — `tp.user`

Two types: **script user functions** (JavaScript files) and **system command user functions** (shell commands).

> **No mobile support**: User functions are unavailable on Obsidian for mobile.

## Script User Functions

### Setup

1. Set a Scripts folder in Templater settings (must be inside the vault).
2. Place `.js` files there. Create them outside Obsidian (Obsidian only creates `.md` files).
3. Files are loaded as CommonJS modules.

### Module Format

Export a single function:

```javascript
module.exports = function (msg) {
  return `Script says: ${msg}`;
};
```

Export an object of functions:

```javascript
module.exports = {
  note: (text) => `> [!note]\n> ${text}`,
  warn: (text) => `> [!warning]\n> ${text}`,
};
```

### Invocation

```markdown
<% tp.user.my_script("hello") %>
<% tp.user.my_script.note("Important") %>
```

### `tp` Scope

`tp` is NOT available in user scripts by default. Pass it as an argument:

```markdown
<% tp.user.my_script(tp) %>
```

```javascript
module.exports = function (tp) {
  return `File: ${tp.file.title}`;
};
```

### Documentation (TSDoc)

Add TSDoc at the top of the script for intellisense in Templater:

```javascript
/**
 * Formats text as an Obsidian callout.
 * @param {string} text - The callout content
 * @param {string} type - Callout type (note, tip, warning)
 * @returns {string} Formatted callout
 */
module.exports = function (text, type = "note") {
  return `> [!${type}]\n> ${text.split("\n").join("\n> ")}`;
};
```

### Available Globals

- `app` — Obsidian App instance
- `moment` — Moment.js
- `tp` — Only if passed as argument

## System Command User Functions

### Setup

1. Enable in Templater settings.
2. Add a user function: define a **name** and **system command**.

### Invocation

```markdown
<% tp.user.echo() %>
```

### Arguments

Pass as a single object `{key: value}`. Values become environment variables:

```markdown
<% tp.user.echo({a: "hello", b: "world"}) %>
```

Shell side: `$a` → `hello`, `$b` → `world`.

### Internal Function Resolution

Internal functions are resolved BEFORE the system command runs:

| Config | Resolves to |
|--------|-------------|
| `cat <% tp.file.path() %>` | `cat /path/to/file` |

```markdown
<% tp.user.cat_file() %>  <!-- e.g. command: cat <% tp.file.path() %> -->
```

> **Security**: System commands execute arbitrary shell commands. Only use from trusted sources.

## Settings Reference

| Setting | Purpose |
|---------|---------|
| Template folder location | Folder scanned for template files |
| Trigger Templater on new file creation | Auto-apply templates to new files |
| Folder Templates | Rule: folder → template (deepest match wins) |
| File Regex Templates | Rule: regex → template (first match wins) |
| Startup Templates | Run on Templater startup (no output) |
| Template Hotkeys | Bind templates to keyboard shortcuts |
| User Script Functions | Folder of CommonJS `.js` files |
| User System Command Functions | Name + command pairs |

Folder Templates and Regex Templates are mutually exclusive. Use `.*` (regex) or `/` (folder) as catch-all.
