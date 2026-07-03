# Testing User Scripts

Testing strategy for Templater user scripts (CommonJS modules). Inline template code (`<%* %>`) cannot be tested outside Obsidian — extract complex logic into user scripts and test those.

## Test Setup

Use [Jest](https://jestjs.io/) with Node.js. Create a standard `package.json` and install:

```bash
npm init -y
npm install --save-dev jest
```

In `package.json`, add:

```json
{
  "scripts": { "test": "jest" },
  "type": "module"
}
```

> Use `"type": "commonjs"` or omit the field if your user scripts use `require()` instead of `import`.

## Project Structure

```
vault/Scripts/
├── callout.js              # User script
├── __tests__/
│   └── callout.test.js     # Jest test
└── __mocks__/
    └── tp.js               # Shared tp mock
```

## Mocking `tp`

Create `__mocks__/tp.js` to simulate Templater's `tp` object:

```javascript
const tp = {
  file: {
    title: "Test-Note",
    folder: (absolute) => absolute ? "Folder/Sub" : "Sub",
    creation_date: (fmt) => "2026-01-01 12:00",
    last_modified_date: (fmt) => "2026-07-03 14:30",
    content: "# Test\nContent here",
    tags: ["#test", "#demo"],
    path: (relative) => relative ? "Folder/Test-Note.md" : "/vault/Folder/Test-Note.md",
    selection: () => "selected text",
    find_tfile: (name) => ({ basename: name, path: `Folder/${name}.md` }),
    exists: async (path) => path === "Folder/Existing.md",
  },
  date: {
    now: (fmt, offset) => "2026-07-03",
    tomorrow: (fmt) => "2026-07-04",
    yesterday: (fmt) => "2026-07-02",
    weekday: (fmt, day) => "2026-07-06",
  },
  system: {
    prompt: async () => "mock value",
    clipboard: () => "mock clipboard",
  },
  frontmatter: {
    type: "note",
    status: "active",
  },
};

module.exports = tp;
```

## Example Test

```javascript
const callout = require('../callout.js');

describe('callout', () => {
  test('creates a note callout', () => {
    const result = callout('Hello world', 'note');
    expect(result).toContain('> [!note]');
    expect(result).toContain('> Hello world');
  });

  test('creates a warning callout with title', () => {
    const result = callout('Be careful', 'warning', 'Caution');
    expect(result).toContain('> [!warning] Caution');
    expect(result).toContain('> Be careful');
  });

  test('handles multi-line content', () => {
    const result = callout('Line 1\nLine 2', 'tip');
    expect(result).toContain('> Line 1');
    expect(result).toContain('> Line 2');
  });
});
```

## Running Tests

```bash
npm test
```

## Mocking `app`

For scripts that access the Obsidian App object, extend the mock:

```javascript
const tp = {
  app: {
    vault: {
      getMarkdownFiles: () => [
        { basename: "Note1", path: "Note1.md" },
        { basename: "Note2", path: "Note2.md" },
      ],
      getAllLoadedFiles: () => [],
      getAbstractFileByPath: (path) => null,
    },
    metadataCache: {
      getTags: () => ({}),
    },
    fileManager: {
      processFrontMatter: async (file, fn) => {
        const fm = {};
        fn(fm);
      },
    },
    commands: {
      executeCommandById: async (id) => {},
    },
  },
  // ... other modules
};
```
