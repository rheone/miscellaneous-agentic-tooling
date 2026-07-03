# Frontmatter and Hooks — `tp.frontmatter`, `tp.hooks`

## `tp.frontmatter`

Access YAML frontmatter variables of the current file.

### Syntax

```markdown
<% tp.frontmatter.variable_name %>
<% tp.frontmatter["variable with spaces"] %>
```

Frontmatter:
```yaml
---
alias: myfile
note type: seedling
categories:
  - book
  - movie
---
```

Usage:
```markdown
Alias: <% tp.frontmatter.alias %>
Type: <% tp.frontmatter["note type"] %>
Categories: <% tp.frontmatter.categories.map(c => `- ${c}`).join("\n") %>
```

Lists support JavaScript array methods (`map`, `filter`, `join`, etc.).

### Editing Frontmatter via `tp.app.fileManager.processFrontMatter()`

```markdown
<%*
const file = tp.file.find_tfile(tp.file.path(true));
await tp.app.fileManager.processFrontMatter(file, (fm) => {
  fm["status"] = "updated";
});
%>
```

## `tp.hooks`

Lifecycle hooks for post-processing after all templates finish executing.

### `tp.hooks.on_all_templates_executed(callback)`

| Param | Type | Description |
|-------|------|-------------|
| `callback` | `() => any` | Function to run after all templates finish |

**Async — requires `await`**. Multiple calls run callbacks in parallel.

```markdown
<%*
tp.hooks.on_all_templates_executed(async () => {
  const file = tp.file.find_tfile(tp.file.path(true));
  await tp.app.fileManager.processFrontMatter(file, (fm) => {
    fm["processed"] = tp.date.now();
  });
});
%>
```

Common use cases:
- Updating frontmatter after template insertion
- Triggering another plugin's command (e.g., linter, formatter)
- Creating related files after the main template finishes
- Running calculations based on the final file state
