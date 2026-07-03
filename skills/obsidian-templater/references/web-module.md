# Web Module — `tp.web`

HTTP requests and web content. All functions are **async — require `await`**.

## Functions

### `tp.web.daily_quote()`

Fetches a random quote from a curated database. Returns an Obsidian callout:

```markdown
<% await tp.web.daily_quote() %>
```

Output:

```markdown
> [!quote]- Daily Quote
> The best time to plant a tree was 20 years ago. The second best time is now.
> &mdash; <cite>Chinese Proverb</cite>
```

### `tp.web.random_picture(size?, query?, include_size?)`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `size` | string | — | Format `<width>x<height>` (e.g. `"800x600"`) |
| `query` | string | — | Search term (comma-separated for multiples) |
| `include_size` | boolean | `false` | Include size in the markdown |

Returns markdown: `![description](url)`.

```markdown
<% await tp.web.random_picture() %>
<% await tp.web.random_picture("200x200", "landscape,water") %>
```

### `tp.web.request(url, path?)`

| Param | Type | Description |
|-------|------|-------------|
| `url` | string | HTTP request URL |
| `path` | string | Dot-notation path into the JSON response (e.g. `"0.title"`) |

```markdown
<% await tp.web.request("https://api.example.com/data") %>
<% await tp.web.request("https://api.example.com/data", "results.0.name") %>
```
