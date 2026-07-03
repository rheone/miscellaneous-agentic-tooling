# App, Config, and Obsidian API — `tp.app`, `tp.config`, `tp.obsidian`

Gateway modules for accessing the Obsidian application internals. Useful in user scripts and execution commands.

## `tp.app`

The full Obsidian [App instance](https://docs.obsidian.md/Reference/TypeScript+API/App).

| Property | Description |
|----------|-------------|
| `tp.app.vault` | Vault API (create, read, write files) |
| `tp.app.fileManager` | File management (processFrontMatter, rename, etc.) |
| `tp.app.metadataCache` | Metadata and link cache |
| `tp.app.commands` | Execute any Obsidian command by ID |

```javascript
<% tp.app.vault.getAllLoadedFiles().filter(x => x instanceof tp.obsidian.TFolder).map(x => x.name) %>

<%*
const file = tp.file.find_tfile(tp.file.path(true));
await tp.app.fileManager.processFrontMatter(file, (fm) => {
  fm["status"] = "processed";
});
%>

<%*
tp.app.commands.executeCommandById("obsidian-linter:lint-file");
%>
```

## `tp.config`

Templater's current execution context.

| Property | Type | Description |
|----------|------|-------------|
| `tp.config.active_file` | TFile\|null | Active file when Templater launched (may differ from target) |
| `tp.config.run_mode` | RunMode | `Create`, `Append`, `Overwrite`, `Rename` — how Templater was invoked |
| `tp.config.target_file` | TFile | File being written to |
| `tp.config.template_file` | TFile | The template file being processed |

Useful in user scripts to understand invocation context.

## `tp.obsidian`

Exposes Obsidian API classes and utility functions.

| Function | Description |
|----------|-------------|
| `tp.obsidian.normalizePath(path)` | Normalizes path separators |
| `tp.obsidian.htmlToMarkdown(html)` | Converts HTML string to Markdown |
| `tp.obsidian.requestUrl(config)` | HTTP request. **Async — requires `await`**. Returns `{ json, text, status, headers }` |

Classes: `tp.obsidian.TFile`, `tp.obsidian.TFolder`, `tp.obsidian.TAbstractFile`, etc.

```javascript
<% tp.obsidian.normalizePath("Path\\to\\file.md") %>
<% tp.obsidian.htmlToMarkdown("<h1>Title</h1><p>Text</p>") %>
<%*
const resp = await tp.obsidian.requestUrl({ url: "https://api.example.com/data" });
tR += resp.json.title;
%>
```

> **Security**: `tp.obsidian` provides full access to the Obsidian API. Be cautious with templates from untrusted sources.
