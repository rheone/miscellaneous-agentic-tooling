---
name: homeassistant-google-calendar
description: "Read and write Google Calendar (gcal, google cal) from Home Assistant automations and scripts. Use when creating calendar events (google.create_event), fetching events (calendar.get_events), triggering automations on calendar event start/end, or building calendar-based logic. Covers both google-specific and generic calendar actions."
user-invocable: true
metadata: 
  skill: homeassistant-google-calendar
  author: "Robert H. Engelhardt"
  version: 1.0.0
  see also:
    - "https://www.home-assistant.io/integrations/calendar.google/"
    - "https://www.home-assistant.io/integrations/calendar/"
---

# Google Calendar Skill

Read and write Google Calendar via Home Assistant actions and automations.

## Quick Start

### Get today's events

```yaml
action: calendar.get_events
target:
  entity_id: calendar.{calendar_name}
data:
  duration:
    hours: 12
response_variable: agenda
```

### Create an event

```yaml
action: google.create_event
target:
  entity_id: calendar.{calendar_name}
data:
  summary: "Team Standup"
  start_date_time: "2026-07-16 09:00:00"
  end_date_time: "2026-07-16 09:15:00"
```

## Actions Reference

| Action | Purpose | Requires |
|--------|---------|----------|
| `google.create_event` | Create event on Google Calendar | Read-write OAuth access |
| `calendar.create_event` | Create event on any calendar | Read-write OAuth access |
| `calendar.get_events` | Read events from calendar(s) | Read access (default) |

## Workflows

### Read calendar events
1. Use `calendar.get_events` with a target entity and time range
2. Store result in `response_variable`
3. Loop over `response_variable.<entity_id>.events` in templates

### Create calendar events
1. Use `google.create_event` (Google-specific) or `calendar.create_event` (generic)
2. Target a calendar entity
3. Provide `summary` + one of: `start_date_time`/`end_date_time`, `start_date`/`end_date`, or `in`

### Automate on calendar events
1. Use `trigger: calendar` with `event: start` or `event: end`
2. Set `entity_id` and optional `offset` (e.g. `"-00:15:00"` for 15 min before)
3. Access event details via `trigger.calendar_event.summary`, `.start`, `.end`, `.location`, `.description`

### Mixed-trigger automations (calendar + event/state triggers)

When combining calendar triggers with other trigger types (event, state, time),
`trigger.calendar_event` is undefined for non-calendar triggers. Direct attribute
access raises `UndefinedError`.

**Safe variable pattern:**
```yaml
variables:
  cal_event: '{{ trigger.calendar_event | default(none) }}'
  title: '{{ cal_event.summary if cal_event is not none else "Default" }}'
```

**Safe all-day condition:**
```yaml
conditions:
  - condition: template
    value_template: '{{ cal_event is none or not cal_event.all_day }}'
```

## Key Concepts

- **`google.create_event`** is Google-specific; **`calendar.create_event`** is the generic building-block — both work the same way
- All-day event `end_date` is **exclusive** — single-day event on July 25 needs `end_date: "2026-07-26"`
- Calendar triggers poll every **15 minutes** — events <15 min away may not fire
- Use `queued` or `parallel` automation mode for calendar triggers to handle simultaneous starts
- **Mixed-trigger safety**: `trigger.calendar_event` is undefined for non-calendar triggers. Cache with `| default(none)` and use conditional checks in variables and conditions.
- **Manual testing**: Add an `event` trigger with a custom event type (e.g. `calendar_test`) for easy testing. Ensure variables use safe defaults when `trigger.calendar_event` doesn't exist.
- **`| default()` chain trap**: `trigger.calendar_event.all_day | default(false)` fails if `trigger.calendar_event` is undefined — the error occurs before `default` can catch it. Always cache the object first, then check attributes.
- **"Run Actions" ≠ real trigger**: The "Run Actions" button in the automation editor skips triggers and conditions entirely. If actions reference `trigger.*`, test with the actual trigger instead.
- **0.00s trace = template failure**: When an automation trace shows 0.00s runtime with "stopped for unknown reason", a condition or variable template failed silently — not an action.

## Reference Files

- [Read Operations](READ-OPERATIONS.md) — get_events, entity attributes, triggers, conditions, trigger variables
- [Write Operations](WRITE-OPERATIONS.md) — create_event params, all-day events, relative timing, templates, error handling
