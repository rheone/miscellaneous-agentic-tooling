# Templater Examples

Six progressively complex templates demonstrating core Templater capabilities.

## 1. Daily Journal

Creates a daily journal with dates, navigation, and a quote.

```markdown
---
created: <% tp.file.creation_date() %>
modified: <% tp.file.last_modified_date("YYYY-MM-DD HH:mm") %>
tags: [daily]
week: <% moment(tp.file.title, "YYYY-MM-DD").isoWeek() %>
---

# <% tp.date.now("dddd, MMMM Do YYYY") %>

<< [[<% tp.date.now("YYYY-MM-DD", -1) %>]] | [[<% tp.date.now("YYYY-MM-DD", 1) %>]] >>

<% await tp.web.daily_quote() %>

## Gratitude

1. <% tp.file.cursor(1) %>
2. <% tp.file.cursor(1) %>
3. <% tp.file.cursor(1) %>

## Notes

<% tp.file.cursor() %>
```

## 2. Meeting Note with Suggester

Interactive template that asks for attendees and captures notes.

```markdown
---
created: <% tp.file.creation_date() %>
type: meeting
attendees:
---
<%*
let project = await tp.system.suggester(
  ["Alpha", "Beta", "Gamma"],
  ["alpha", "beta", "gamma"]
);
let attendees = await tp.system.multi_suggester(
  (item) => item.basename,
  tp.app.vault.getMarkdownFiles().filter(f => f.path.startsWith("People/"))
);
%>
# Meeting: <% tp.file.title %>

**Project**: <% project %>
**Date**: <% tp.date.now("MMMM Do YYYY") %>
**Attendees**: <% attendees.map(f => `[[${f.basename}]]`).join(", ") %>

## Agenda

<% tp.file.cursor() %>

## Action Items

- [ ] <% tp.file.cursor(1) %>
```

## 3. Project Tracker

Creates a project note and a linked project board folder.

```markdown
---
created: <% tp.file.creation_date() %>
status: active
type: project
---
<%*
let name = await tp.system.prompt("Project name?", tp.file.title);
%>
# <% name %>

## Goals

<% tp.file.cursor() %>

## Tasks

- [ ] Setup
- [ ] Research
- [ ] Build
- [ ] Review

## Resources

[[_resources/<% name %>|Project Resources]]

<%*
await tp.file.create_new(
  "# Resources for " + name + "\n\n",
  "_resources/" + name,
  false,
  tp.file.folder(true)
);
%>
```

## 4. Zettelkasten / Literature Note

Creates a note with ID, source metadata, and backlinks.

```markdown
---
created: <% tp.file.creation_date() %>
id: <% tp.date.now("YYYYMMDDHHmmss") %>
source:
author:
rating:
tags: [literature, seedling]
---

# <% tp.file.title.split(" ").slice(1).join(" ") %>

**Source**: <% tp.file.cursor(1) %>
**Author**: <% tp.file.cursor(1) %>
**ZID**: <% tp.date.now("YYYYMMDDHHmmss") %>

## Highlights

> <% tp.file.cursor() %>

## Summary



## Connected To

- [[]]
```

## 5. Interactive Task with Prompt

Creates a task card with user-provided details.

```markdown
---
created: <% tp.file.creation_date() %>
deadline: <% tp.date.now("YYYY-MM-DD", 7) %>
---
<%*
let task = await tp.system.prompt("What needs to be done?");
let priority = await tp.system.suggester(
  ["High", "Medium", "Low"],
  ["high", "medium", "low"]
);
%>
# <% task %>

**Priority**: <% priority %>
**Deadline**: [[<% tp.date.now("YYYY-MM-DD", 7) %>]]
**Created**: <% tp.date.now() %>

## Checklist

- [ ] <% tp.file.cursor() %>

## Notes

<% tp.file.cursor() %>
```

## 6. User Script — Callout Formatter

User script (`Scripts/callout.js`) and its template.

**Script file** (`Scripts/callout.js`):

```javascript
/**
 * Wraps text in an Obsidian callout block.
 * @param {string} text - The callout content
 * @param {string} type - Callout type (note, tip, warning, danger, info)
 * @param {string} title - Optional callout title
 * @returns {string} Formatted callout markdown
 */
module.exports = function (text, type = "note", title = "") {
  const header = `> [!${type}]${title ? " " + title : ""}`;
  const body = text.split("\n").map(l => `> ${l}`).join("\n");
  return `${header}\n${body}`;
};
```

**Template** (`Templates/callout-demo.md`):

```javascript
<% tp.user.callout("This is important", "warning", "Heads up") %>
```

Output:

```markdown
> [!warning] Heads up
> This is important
```
