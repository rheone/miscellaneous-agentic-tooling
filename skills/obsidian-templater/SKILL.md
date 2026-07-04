---
name: obsidian-templater
description: Create Obsidian templates with Templater syntax (tp.date, tp.file, tp.system, tp.web, tp.frontmatter, tp.hooks, tp.obsidian, tp.app, tp.config, tp.user). Interpolation (<% %>), execution (<%* %>), dynamic (<%+ %>), whitespace control, tR output, user scripts (CommonJS), system command functions, and plugin configuration. Use when the user asks to create or modify an Obsidian template, needs Templater syntax help, wants dynamic templates with dates/prompts/web data, or mentions Templater commands like tp.date.now(), tp.file.cursor(), tp.file.include(), tp.file.create_new(), tp.system.suggester(), tp.system.prompt(), tp.web.daily_quote(), tp.hooks.on_all_templates_executed(), or tp.user.*. Also for template automation, interactive templates, file creation workflows, and vault organization through Templater.
license: Apache-2.0
user-invocable: true
metadata:
  source: https://github.com/rheone/miscellaneous-agentic-tooling
  author: Robert Engelhardt <rheone@gmail.com>
  version: "0.0.0"
---

# Obsidian Templater

## Terminology

- **Template**: a file containing **commands** wrapped in `<% %>` tags.
- **Command**: a text snippet between `<%` and `%>` that produces output or executes code.
- **Function**: an object invoked inside a command that returns a value. All functions live under the `tp` object (e.g. `tp.date.now`).

All function documentation uses this syntax: `tp.func(arg1: type, arg2?: type)`. Only pass values, never the name/type/default — see `references/commands.md`.

## Command Types

| Tag           | Type          | Behavior                                                    |
| ------------- | ------------- | ----------------------------------------------------------- |
| `<% expr %>`  | Interpolation | Outputs the expression result                               |
| `<%* code %>` | Execution     | Runs JS code, outputs nothing by default (use `tR`)         |
| `<%+ expr %>` | Dynamic       | Resolves in preview mode (**deprecated** — prefer Dataview) |

Whitespace control: `-%>` trims one newline after, `<%-` trims one before. `_%>` and `<%_` trim all whitespace. See `references/commands.md`.

## Quick Start

This template creates a daily note with frontmatter, navigation, and a cursor:

```markdown
---
created: <% tp.file.creation_date() %>
modified: <% tp.file.last_modified_date("YYYY-MM-DD HH:mm") %>
tags: daily
---

# <% tp.file.title %>

<< [[<% tp.date.now("YYYY-MM-DD", -1) %>]] | [[<% tp.date.now("YYYY-MM-DD", 1) %>]] >>

## Notes

<% tp.file.cursor() %>
```

Save this in your Templater templates folder, then use it via hotkey or the Templater ribbon icon.

## Gotchas

| #   | Issue                                                                                                                                                                       |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **`await` required** — `tp.file.create_new()`, `tp.file.include()`, `tp.system.*`, `tp.web.*`, `tp.file.exists()` are async. Forgetting `await` silently returns a Promise. |
| 2   | **`create_new(true)` ordering** — `open_new: true` opens the new file immediately; remaining commands then append to that _new_ file, not the current one.                  |
| 3   | **`tR` is the only output channel** — `<%* "hello" %>` outputs nothing. You must write `tR += "hello"`.                                                                     |
| 4   | **`tp` is not in scope for user scripts** — Pass it explicitly: `tp.user.my_func(tp)`.                                                                                      |
| 5   | **User functions (scripts + system commands) don't work on mobile.**                                                                                                        |
| 6   | **Dynamic commands (`<%+ %>`) deprecated** — Use Dataview for live-updating values.                                                                                         |
| 7   | **System command args are environment variables** — `tp.user.echo({a: 1})` → `$a` in shell, not stdin.                                                                      |

## Workflows

### Workflow: Interactive Template

Use `tp.system.prompt()` and `tp.system.suggester()` to ask the user for input:

```markdown
<%\*
let mood = await tp.system.suggester(["Happy","Sad","Confused"], ["happy","sad","confused"]);
let note = await tp.system.prompt("What happened today?");
%>

- **Mood**: <% mood %>
- **Note**: <% note %>
  <% tp.file.cursor() %>
```

### Workflow: Post-Processing

Use `tR` to control output and hooks for side effects:

```markdown
<%\*
tR = "";
%>
---
generated: <% tp.date.now() %>
---
<% tp.file.cursor() %>

<%\*
tp.hooks.on_all_templates_executed(() => {
  tp.app.commands.executeCommandById("obsidian-linter:lint-file");
});
%>
```

### Workflow: Create a Note from Template

```markdown
[[<% (await tp.file.create_new("TemplateContent", tp.system.prompt("Note name?"), true)).basename %>]]
```

### Subagent: Template Generation

When the user says "create a template that does X":

1. Ask clarifying questions (purpose, vault structure, existing naming conventions, desired dynamic elements)
2. Read relevant reference docs from `references/`
3. If the vault path is accessible, write to their Templater template folder (default: `Templates/`). Offer to place elsewhere.
4. If the vault path is not accessible, output the template content with save instructions.
5. Optionally run `scripts/validate-template.*` on the result.
6. If the template uses a user script (CommonJS), offer to generate a Jest test in `testing/TESTING.md` style.

## User Scripts

Place `.js` files in the configured Scripts folder (setting in Templater). Follow CommonJS:

```javascript
module.exports = function (msg) {
   return `from script: ${msg}`;
};
```

Invoke as `<% tp.user.filename("hello") %>`. Pass `tp` if needed: `<% tp.user.filename(tp) %>`.

See `references/user-functions.md`.

## Checklist-Driven Execution

When this skill is invoked, create a `todowrite` checklist covering every phase below. Tick items off as you go; if blocked, note the blocker and ask the user.

1. **Clarify requirements** — confirm vault structure, naming conventions, desired dynamic elements, whether a user script is needed, and where to save the template.
2. **Study references** — read the relevant `references/*.md` files for each module you'll use.
3. **Write the template** — compose the `.md` file with correct `tp.*` calls and proper whitespace control.
4. **Validate syntax** — run `scripts/validate-template.*` on the result and fix any issues.
5. **Test user scripts** — if the template depends on a `.js` module, scaffold a Jest test using the style in `testing/TESTING.md`, run `npm test`, and fix failures.
6. **Final verification** — re-read the template once more to confirm all `tp.*` calls match reference docs, all `await` keywords are present where needed, and the output matches user intent.

### Example Checklist

```markdown
## todowrite
- [x] Clarify requirements — daily note with date nav, mood prompt, daily quote
- [x] Study references — read date-module.md, system-module.md, web-module.md
- [x] Write the template — daily-journal.md with frontmatter, nav links, prompt, quote, cursor
- [ ] Validate syntax — run validate-template.py Templates/daily-journal.md
- [ ] Test user scripts — no user scripts needed; skip
- [ ] Final verification — re-read template, confirm dates/prompt/quote all correct
```

## See Also

- `references/commands.md` — Full command syntax, whitespace control, tR
- `references/date-module.md` — tp.date, moment.js
- `references/file-module.md` — tp.file (16 functions)
- `references/system-module.md` — tp.system prompts and suggesters
- `references/web-module.md` — tp.web daily quote, images, requests
- `references/app-obsidian.md` — tp.app, tp.config, tp.obsidian
- `references/frontmatter-hooks.md` — tp.frontmatter, tp.hooks
- `references/user-functions.md` — scripts, system commands, settings
- `examples/EXAMPLES.md` — 6 practical templates
- `testing/TESTING.md` — Jest testing for user scripts
- `scripts/validate-template.ps1|py|sh` — Template syntax validation
