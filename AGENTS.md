# AGENTS.md — miscellaneous-agentic-tooling

Agentic AI skills for Home Assistant automation and Obsidian knowledge management.

## Repository structure

```
├── skills/                       # AI agent skills (SKILL.md per directory)
│   ├── homeassistant-awtrix/     # AWTRIX 3 pixel clock control
│   ├── homeassistant-pixoo64/    # Divoom Pixoo 64 display control
│   └── obsidian-ics-sync/        # ICS calendar sync into Obsidian daily notes
└── README.md                     # Skills catalog and install instructions
```

## Skills

Skills live under `skills/` — each has a `SKILL.md`. Install via:

```bash
npx skills add rheone/miscellaneous-agentic-tooling
```
