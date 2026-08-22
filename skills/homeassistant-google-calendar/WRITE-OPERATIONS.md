# Google Calendar — Write Operations

## 1. Create Event — Google-specific (`google.create_event`)

The Google Calendar integration's own action. **Requires read-write access** granted in the integration options (Settings > Integrations > Google Calendar > Options).

### YAML Syntax

```yaml
action: google.create_event
target:
  entity_id: calendar.{calendar_name}
data:
  summary: "Team Standup"
  start_date_time: "2026-07-16 09:00:00"
  end_date_time: "2026-07-16 09:15:00"
  description: "Weekly team sync"
  location: "Conference Room A"
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `summary` | string | Yes | Event title |
| `description` | string | No | Event description |
| `start_date_time` | string | No* | Start date+time, format `"YYYY-MM-DD HH:MM:SS"` |
| `end_date_time` | string | No* | End date+time (exclusive), format `"YYYY-MM-DD HH:MM:SS"` |
| `start_date` | string | No* | Start date for all-day events, format `"YYYY-MM-DD"` |
| `end_date` | string | No* | End date for all-day events (exclusive), format `"YYYY-MM-DD"` |
| `in` | map | No* | Relative timing: `{ days: 2 }` or `{ weeks: 2 }` |
| `location` | string | No | Event location |

**Timing**: Set event time using exactly one of three methods:
1. `start_date_time` + `end_date_time` — timed event
2. `start_date` + `end_date` — all-day event
3. `in` — relative from now

### Create Timed Event

```yaml
action: google.create_event
target:
  entity_id: calendar.{calendar_name}
data:
  summary: "Doctor Appointment"
  start_date_time: "2026-07-18 14:30:00"
  end_date_time: "2026-07-18 15:30:00"
  location: "123 Main St"
  description: "Annual checkup"
```

### Create All-Day Event

```yaml
action: google.create_event
target:
  entity_id: calendar.{calendar_name}
data:
  summary: "Day Off"
  start_date: "2026-07-25"
  end_date: "2026-07-26"        # exclusive — one day uses next day
```

### Create Event in N Days

```yaml
action: google.create_event
target:
  entity_id: calendar.{calendar_name}
data:
  summary: "Follow up with dentist"
  in:
    days: 2
  start_date_time: "2026-07-18 10:00:00"
  end_date_time: "2026-07-18 10:30:00"
```

### Create Event in N Weeks

```yaml
action: google.create_event
target:
  entity_id: calendar.{calendar_name}
data:
  summary: "Quarterly Review"
  in:
    weeks: 3
```

---

## 2. Create Event — Generic (`calendar.create_event`)

The building-block calendar action. Works with **any** calendar integration (Google, CalDAV, Local Calendar, etc.).

### YAML Syntax

```yaml
action: calendar.create_event
target:
  entity_id: calendar.{calendar_name}
data:
  summary: "Quick Meeting"
  start_date_time: "2026-07-16 11:00:00"
  end_date_time: "2026-07-16 11:30:00"
```

### Parameters

Identical to `google.create_event`:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `summary` | string | Yes | Event title |
| `description` | string | No | Event description |
| `start_date_time` | string | No* | Start date+time |
| `end_date_time` | string | No* | End date+time (exclusive) |
| `start_date` | string | No* | Start date (all-day) |
| `end_date` | string | No* | End date (all-day, exclusive) |
| `in` | map | No* | Relative timing |
| `location` | string | No | Event location |

### When to Use Which

| Use `google.create_event` when | Use `calendar.create_event` when |
|--------------------------------|----------------------------------|
| You know it's a Google Calendar | You want integration-agnostic code |
| Need Google-specific features | Targeting any calendar entity |
| Working with Google OAuth setup | Simpler, more portable |

> **Note**: `calendar.create_event` is not available for the Google integration unless read-write access is enabled in the integration options. Both actions require the same OAuth scope.

---

## 3. Logging/Recording Events

Use a quick 1-second event to record that something happened:

```yaml
alias: "Log washing machine finish"
triggers:
  - trigger: state
    entity_id: sensor.washing_machine_status
    to: idle
actions:
  - action: google.create_event
    target:
      entity_id: calendar.{calendar_name}
    data:
      summary: "Laundry finished"
      start_date_time: "{{ now().strftime('%Y-%m-%d %H:%M:%S') }}"
      end_date_time: "{{ (now() + timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S') }}"
```

---

## 4. Dynamic Event Creation from Templates

Use Jinja2 templates for dynamic summaries, times, and descriptions:

```yaml
action: google.create_event
target:
  entity_id: calendar.{calendar_name}
data:
  summary: "{{ trigger.to_state.attributes.friendly_name }} finished"
  description: >
    Status changed from {{ trigger.from_state.state }}
    to {{ trigger.to_state.state }} at {{ now().strftime('%H:%M') }}
  start_date_time: "{{ now().strftime('%Y-%m-%d %H:%M:%S') }}"
  end_date_time: "{{ (now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S') }}"
```

---

## 5. Error Handling

### Missing read-write access
If `google.create_event` fails with a permissions error:
1. Go to Settings > Integrations > Google Calendar
2. Click Options
3. Enable read-write access
4. Re-authorize if needed

### Invalid date format
Always use `"YYYY-MM-DD HH:MM:SS"` for timed events or `"YYYY-MM-DD"` for all-day events.

### End time must be after start time
The `end_date_time` / `end_date` is exclusive and must be after the start.

### All-day event end date is exclusive
For a single all-day event on July 25, use `start_date: "2026-07-25"` and `end_date: "2026-07-26"`.

---

## 6. Target Options

Both create-event actions support flexible targeting:

```yaml
# Single entity
target:
  entity_id: calendar.{calendar_name}

# Multiple entities
target:
  entity_id:
    - calendar.{calendar_name}
    - calendar.{other_calendar}

# By device
target:
  device_id: "google-calendar-device-id"

# By area
target:
  area_id: "office"

# By label
target:
  label_id: "personal"
```
