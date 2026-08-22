# Google Calendar — Read Operations

## 1. Get Events (`calendar.get_events`)

Retrieves events from one or more calendars within a date range. Returns a `response_variable` you can use in later steps.

### YAML Syntax

```yaml
action: calendar.get_events
target:
  entity_id:
    - calendar.{calendar_name}
data:
  start_date_time: "2026-07-16 00:00:00"   # optional, defaults to now
  end_date_time: "2026-07-17 00:00:00"     # optional, exclusive
  # OR use duration (mutually exclusive with end_date_time):
  duration:
    hours: 24
response_variable: agenda
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date_time` | string | No | Return events after this time. Format: `"YYYY-MM-DD HH:MM:SS"`. Defaults to now. |
| `end_date_time` | string | No | Return events before this time (exclusive). Cannot be used with `duration`. |
| `duration` | map | No | Return events from start for this duration, e.g. `hours: 24`. Cannot be used with `end_date_time`. |

### Response Format

The response is keyed by calendar entity ID, each containing an `events` list:

```yaml
calendar.{calendar_name}:
  events:
    - summary: "Team standup"
      start: "2026-07-16 09:00:00"
      end: "2026-07-16 09:15:00"
      location: "Conference Room A"
      description: "Weekly sync"
```

Each event object:
| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Event title |
| `description` | string | Event description (if set) |
| `start` | string | Start date/time or date |
| `end` | string | End date/time or date (exclusive) |
| `location` | string | Location (if set) |

### Multi-calendar Read

```yaml
action: calendar.get_events
target:
  entity_id:
    - calendar.{calendar_name}
    - calendar.{other_calendar}
    - calendar.{yet_another_calendar}
response_variable: all_calendars
```

### Looping Over Events in a Template

```yaml
action: persistent_notification.create
data:
  title: "Today's Agenda"
  message: >-
    {% for cal in agenda %}
    **{{ cal }}:**
    {% for event in agenda[cal].events %}
    - {{ event.summary }} ({{ event.start }} - {{ event.end }})
    {% endfor %}
    {% endfor %}
```

---

## 2. Calendar Entity Attributes

Each calendar entity exposes attributes for the **next upcoming event**. State is `on` (active event) or `off` (no event).

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `state` | string | `on` if an event is active, `off` otherwise |
| `message` | string | Title/summary of the next event |
| `description` | string | Description of the next event |
| `location` | string | Location of the next event |
| `start_time` | string | Start time of the next event |
| `end_time` | string | End time of the next event |
| `all_day` | boolean | Whether the next event is an all-day event |
| `offset_reached` | boolean | Whether the offset trigger has fired |

### Example State Check

```yaml
condition: state
entity_id: calendar.{calendar_name}
state: "on"
```

### Example Attribute Check

```yaml
condition: template
value_template: "{{ state_attr('calendar.{calendar_name}', 'message') == 'Team Meeting' }}"
```

> **Limitation**: Entity attributes only track a single next event. For multiple events or precise matching, use `calendar.get_events` instead.

---

## 3. Calendar Triggers

Calendar triggers fire automations when events start or end. This is the **preferred** way to automate based on calendar events.

### YAML Syntax

```yaml
automation:
  - alias: "Calendar Event Automation"
    triggers:
      - trigger: calendar
        event: start          # "start" or "end"
        entity_id: calendar.{calendar_name}
        offset: "-00:15:00"   # optional: fire 15 min before start
    actions:
      # ...
```

### Trigger Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `trigger` | Yes | Must be `calendar` |
| `event` | Yes | `start` or `end` |
| `entity_id` | Yes | Calendar entity to watch |
| `offset` | No | Timedelta offset, e.g. `"-00:15:00"` (before) or `"00:05:00"` (after) |

### Important Notes

- Calendar data is polled every **15 minutes**. Events less than 15 minutes away may not trigger.
- Use automation mode `queued` or `parallel` instead of `single` to handle simultaneous event starts.
- The offset must be in `HH:MM:SS` format with sign: `"-00:15:00"` or `"+00:05:00"`.

---

## 4. Trigger Variables

When a calendar trigger fires, these variables are available in templates via `trigger.calendar_event`:

| Variable | Type | Description |
|----------|------|-------------|
| `trigger.platform` | string | Always `calendar` |
| `trigger.event` | string | `start` or `end` |
| `trigger.calendar_event.summary` | string | Event title |
| `trigger.calendar_event.start` | string | Start date/time (e.g. `"2026-07-16"` or `"2026-07-16 09:00:00-07:00"`) |
| `trigger.calendar_event.end` | string | End date/time (UTC) |
| `trigger.calendar_event.all_day` | boolean | Whether it's an all-day event |
| `trigger.calendar_event.description` | string | Event description |
| `trigger.calendar_event.location` | string | Event location |
| `trigger.offset` | timedelta | The offset value from the trigger config |

### Example: Notify with Event Details

```yaml
actions:
  - action: persistent_notification.create
    data:
      title: "Event Starting"
      message: >-
        {{ trigger.calendar_event.summary }}
        at {{ trigger.calendar_event.start }}
        {% if trigger.calendar_event.location %}
        Location: {{ trigger.calendar_event.location }}
        {% endif %}
```

### Mixed-Trigger Safety

When combining calendar triggers with event/state/time triggers, `trigger.calendar_event`
is undefined for non-calendar triggers. Attribute access raises `UndefinedError`.

**Cache and guard pattern:**
```yaml
variables:
  cal_event: '{{ trigger.calendar_event | default(none) }}'
  title: '{{ cal_event.summary if cal_event is not none else "Test Event" }}'
  start_ts: '{{ as_timestamp(cal_event.start) if cal_event is not none else now().timestamp() }}'
  end_ts: '{{ as_timestamp(cal_event.end) if cal_event is not none else now().timestamp() + 3600 }}'
```

**Safe all-day condition:**
```yaml
conditions:
  - condition: template
    value_template: '{{ cal_event is none or not cal_event.all_day }}'
```

**Testing with manual triggers:**
```yaml
triggers:
  - trigger: calendar
    entity_id: calendar.{calendar_name}
    event: start
    id: reminder
  - trigger: event
    event_type: my_test_event
    id: manual
```

When the manual trigger fires, `trigger.calendar_event` is undefined. The `| default(none)`
catches this, and the `if cal_event is not none` guards fall back to safe defaults.

---

## 5. Calendar Condition

Tests whether one or more calendars have an active event.

```yaml
condition: calendar.is_event_active
entity_id: calendar.{calendar_name}
```

### Multi-calendar Condition

```yaml
condition: calendar.is_event_active
entity_id:
  - calendar.{calendar_name}
  - calendar.{other_calendar}
```

---

## 6. Filtering Events by Summary

Use a template condition to match specific event titles:

```yaml
triggers:
  - trigger: calendar
    event: start
    entity_id: calendar.{calendar_name}
conditions:
  - condition: template
    value_template: >
      {{ trigger.calendar_event.summary == 'Team Standup' }}
```

### Partial Match

```yaml
conditions:
  - condition: template
    value_template: >
      {{ 'Meeting' in trigger.calendar_event.summary }}
```

---

## 7. Combined Read Example: Daily Agenda Notification

```yaml
alias: "Daily Agenda Summary"
triggers:
  - trigger: time
    at: "07:00:00"
actions:
  - action: calendar.get_events
    target:
      entity_id: calendar.{calendar_name}
    data:
      duration:
        hours: 12
    response_variable: agenda
  - action: persistent_notification.create
    data:
      title: "Today's Agenda"
      message: >-
        {% set events = agenda['calendar.{calendar_name}'].events %}
        {% if events %}
        {% for e in events %}
        - {{ e.summary }} ({{ e.start }} - {{ e.end }})
        {% endfor %}
        {% else %}
        No events today.
        {% endif %}
```
