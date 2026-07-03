# File Module — `tp.file`

## Properties (no `()` needed)

| Property | Returns | Description |
|----------|---------|-------------|
| `tp.file.content` | string | File content at the time Templater ran |
| `tp.file.tags` | string[] | All tags in the file |
| `tp.file.title` | string | File title (basename without extension) |

## Functions

### `tp.file.create_new(template, filename?, open_new?, folder?)`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `template` | TFile\|string | — | Template TFile, filepath, or raw content string |
| `filename` | string | `"Untitled"` | New filename (without extension) |
| `open_new` | boolean | `false` | Open the new file after creation |
| `folder` | TFolder\|string | vault root | Target folder |

Returns a `TFile` object. **Async — requires `await`**.

> **Gotcha**: `open_new: true` opens the new file *before* remaining commands finish. Subsequent `<%* %>` commands will write to the new file, not the current one.

```markdown
<%* await tp.file.create_new("content", "MyNote") %>
<%* await tp.file.create_new(tp.file.find_tfile("Template"), "MyNote", true) %>
<%* await tp.file.create_new("content", "MyNote", false, tp.file.folder(true)) %>
[[<% (await tp.file.create_new("content", "MyNote")).basename %>]]
```

### `tp.file.creation_date(format?)`

| Param | Type | Default |
|-------|------|---------|
| `format` | string | `"YYYY-MM-DD HH:mm"` |

### `tp.file.cursor(order?)`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `order` | number | — | Jump order. Same order = multi-cursor |

```markdown
<% tp.file.cursor() %>
<% tp.file.cursor(1) %>content<% tp.file.cursor(1) %>  <!-- multi-cursor -->
```

### `tp.file.cursor_append(content)`

```markdown
<% tp.file.cursor_append("appended text") %>
```

### `tp.file.exists(filepath)`

**Async — requires `await`**. Full vault-relative path including extension.

```markdown
<% await tp.file.exists("Folder/MyFile.md") %>
```

### `tp.file.find_tfile(filename)`

Search vault for a file by name. Returns `TFile`.

```markdown
<% tp.file.find_tfile("MyFile").basename %>
```

### `tp.file.folder(absolute?)`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `absolute` | boolean | `false` | `true` = vault-absolute path, `false` = basename only |

### `tp.file.include(include_link)`

**Async — requires `await`**. Includes content from another file. Templates in included content are resolved.

```markdown
<% await tp.file.include("[[Template1]]") %>
<% await tp.file.include("[[MyFile#Section1]]") %>
<% await tp.file.include(tp.file.find_tfile("MyFile")) %>
```

### `tp.file.last_modified_date(format?)`

| Param | Type | Default |
|-------|------|---------|
| `format` | string | `"YYYY-MM-DD HH:mm"` |

### `tp.file.move(new_path, file_to_move?)`

**Async — requires `await`**.

| Param | Type | Default |
|-------|------|---------|
| `new_path` | string | — | Vault-relative path WITHOUT extension (e.g. `"/Folder/NewName"`) |
| `file_to_move` | TFile | current file |

### `tp.file.path(relative?)`

| Param | Type | Default |
|-------|------|---------|
| `relative` | boolean | `false` | `true` = vault-relative path |

### `tp.file.rename(new_title)`

**Async — requires `await`**.

```markdown
<%* await tp.file.rename(tp.file.title + " (updated)") %>
```

### `tp.file.selection()`

Returns the currently selected text in the active editor.
