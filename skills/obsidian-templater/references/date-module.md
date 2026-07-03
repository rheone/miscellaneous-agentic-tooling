# Date Module — `tp.date`

Uses [Moment.js](https://momentjs.com/docs/#/displaying/format/) format strings.

## Functions

### `tp.date.now(format?, offset?, reference?, reference_format?)`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `format` | string | `"YYYY-MM-DD"` | Moment.js output format |
| `offset` | number\|string | — | Days (number) or ISO 8601 duration (string) |
| `reference` | string | today | Base date instead of today |
| `reference_format` | string | — | Format of the reference date |

Offset as number (days): `7`, `-1`. As ISO 8601 string: `"P1Y"`, `"P-1M"`, `"P3D"`.

```markdown
<% tp.date.now("Do MMMM YYYY") %>
<% tp.date.now("YYYY-MM-DD", -7) %>
<% tp.date.now("YYYY-MM-DD", "P1Y") %>
<% tp.date.now("YYYY-MM-DD", 1, tp.file.title, "YYYY-MM-DD") %>
```

### `tp.date.tomorrow(format?)`

| Param | Type | Default |
|-------|------|---------|
| `format` | string | `"YYYY-MM-DD"` |

```markdown
<% tp.date.tomorrow() %>
<% tp.date.tomorrow("dddd") %>
```

### `tp.date.yesterday(format?)`

| Param | Type | Default |
|-------|------|---------|
| `format` | string | `"YYYY-MM-DD"` |

```markdown
<% tp.date.yesterday() %>
```

### `tp.date.weekday(format?, weekday, reference?, reference_format?)`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `format` | string | `"YYYY-MM-DD"` | Output format |
| `weekday` | number | — | `0` = first day of week (locale-dependent, usually Monday), `7` = next week's, `-7` = last week's |
| `reference` | string | today | Base date |
| `reference_format` | string | — | Format of reference |

```markdown
<% tp.date.weekday("YYYY-MM-DD", 0) %>    <!-- This Monday -->
<% tp.date.weekday("YYYY-MM-DD", 7) %>    <!-- Next Monday -->
<% tp.date.weekday("YYYY-MM-DD", -7) %>   <!-- Last Monday -->
```

## moment.js

`moment` is globally available in all command types. Set locale for non-English dates:

```markdown
<%*
moment.locale("fr");
%>
<% moment(tp.file.title, "YYYY-MM-DD").startOf("month").format("YYYY-MM-DD") %>
<% moment(tp.file.title, "YYYY-MM-DD").endOf("month").format("YYYY-MM-DD") %>
```
