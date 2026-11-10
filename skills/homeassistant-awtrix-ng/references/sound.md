# Sound

What the clock can play depends on hardware. Check `audio` on the retained `<P>/state/capabilities` topic.

| Clock | Can play |
|---|---|
| ESP32 with a buzzer | RTTTL melodies. DFPlayer tracks if fitted. One sound at a time |
| ESP32-S3 with I2S and PSRAM | Also MP3, songs, internet radio |
| Speaker clocks such as the TC002 | MP3 (also from a URL), melodies, songs, speech, radio, several at once |

## The sound object

Same value in a notification's `sound` and on `<P>/cmd/audio/play`.

| Form | Plays |
|---|---|
| `"ding"` or `{"file":"ding"}` | Stored sound, by name, no extension |
| `{"rtttl":"bell:d=4,o=5,b=120:c,e,g"}` | Melody in the message |
| `{"track":3}` | DFPlayer track 1 to 2999 |
| `{"song":"..."}` | Synthesizer text (S3, TC002) |
| `{"speech":"..."}` | Read aloud (TC002 with a voice) |
| `{"station":"SWR3"}` | Radio. On `audio/play` only, alone |
| `[{...},"ding"]` | First of 1 to 4 entries the clock can play |

Add `"loop": true` beside the key to repeat. In a notification the loop ends when the notice leaves the display. `"loop"` with `"hold"` makes an alarm.

A plain name resolves to `/MP3/<name>.mp3` first (where MP3 exists), then `/MELODIES/<name>.txt`.

## RTTTL

`name:defaults:notes`. All three parts are required, and the name must not be empty.

- Defaults: `d` length (1, 2, 4, 8, 16, 32; default 4), `o` octave (4 to 7; default 6), `b` tempo (10 to 300; default 63).
- Notes: optional length, letter `a`-`g` or `p` (pause), optional `#`, optional `.`, optional octave. `16c6` is a 16th note C in octave 6.
- Refused: `b#`, `e#`, a sharp on a pause, a length such as 3. At most 512 characters.

Examples to reuse:

```
bell:d=4,o=5,b=100:e,c
lose:d=8,o=5,b=120:16c,16b,16a,4g
jackpot:d=8,o=5,b=120:16c,16e,16g,c6,16p,16c6,16e6,4g6
siren:d=8,o=5,b=200:c,g,c,g
```

## Stored melodies

Over HTTP only: `PUT /api/v1/audio/melodies/doorbell` with `{"rtttl":"d=4,o=5,b=100:e,c"}` (a stored melody may omit the name). List with `GET /api/v1/audio/melodies`. The web UI's **Audio** tab has an editor. Names: 1 to 24 characters of letters, digits, `_`, `-`.

## Volume

What you hear is `volume x group volume / 100`.

| Setting | Default | Covers |
|---|---|---|
| `volume` | 60 (TC002 90) | Everything |
| `alertVolume` | 100 | Notification sounds and `audio/play` |
| `appVolume` | 100 | Scripts |
| `radioVolume` | 80 | Radio |

All four are HA number entities where the hardware has them. `volume: 0` silences all sound.

## What plays over what

- A new alert replaces the alert playing.
- A script's single sound is not played while an alert plays.
- A notice without `loop` lets its sound finish after it leaves. With `loop`, the sound stops at once.
- An alert pauses the radio, which then resumes.

## Stopping

Press the HA **Stop sound** button, or publish empty or `{"group":"alert"}` to `<P>/cmd/audio/stop`.

## Internet radio

Needs `radio` in the capabilities. Publish to `<P>/cmd/audio/play`:

| Payload | Plays |
|---|---|
| `{"station":"SWR3"}` | The station with that name |
| `{"station":0}` | A list position from 0. The list is sorted A to Z |
| `{"station":"https://example.com/live.mp3"}` | A stream not in the list |

- `<P>/cmd/audio/stations` with `{"stations":[{"name":"SWR3","url":"https://..."}]}` **replaces the whole list**, so send every station you want to keep. Up to 32; names 24 characters, URLs 255.
- A station goes alone: it is refused inside a sound list or a notification's `sound`.
- MP3 streams only. A station that sends AAC reports `not playable MP3`. `.m3u` and `.pls` playlist URLs work and are read again at each reconnect.
- The clock retries a dropped stream by itself until you stop it.
- The radio never shows a title on the display. Read `radio.title` from `<P>/state/audio`, and push it as an app.

`<P>/state/audio` is retained and published on every change:

```json
{"radio":{"playing":true,"station":"SWR3","title":"Kraftwerk - Das Model","error":"","underruns":0,"starvedMs":0},
 "app":{"playing":false,"name":"","error":""},
 "alert":{"playing":false,"name":"","error":""},
 "stations":[{"name":"SWR3","url":"https://..."}]}
```

A growing `underruns` or `starvedMs` means the stream arrives too slowly, usually weak Wi-Fi.

## Speech

Needs `speech` in the capabilities. Displayed and spoken text are separate, and a list gives a fallback for clocks without a voice:

```json
{"text":"Door open","sound":[{"speech":"The front door is open."},"ding"]}
```

Up to 512 bytes, and accented letters count for more. The built-in voice is English. It reads numbers, times such as `7:05`, and `%`, `&`, `°` aloud, pauses at punctuation, and skips emoji. Write the text in the voice's language. A voice pack replaces the built-in voice.

## Songs

Needs `song` in the capabilities. A song is text played on the built-in synthesizer, so it takes no storage. `;` separates statements, which suits JSON:

```json
{"song":"bpm 120; inst lead wave=pulse volume=75; lead: c4 e g c5"}
```

Statements, keys, and note letters are lower case. Without `"loop": true` it plays once. Over MQTT it must fit the 8192-byte limit. The full language is at `https://blueforcer.github.io/awtrix-ng/reference/songs/`.

## Failures

| Result | Cause |
|---|---|
| `{"ok":true}`, silence | A volume is 0, or a script sound met an alert |
| Notice shows, no sound | The stored name does not exist. This is not an error for a notification |
| `validationFailed`, field `sound...` | Bad melody or two source keys. The notice is not shown |
| `notFound`, `nothing called "x"` | `audio/play` with an unknown name |
| `unavailable` | No hardware for that kind of sound |
