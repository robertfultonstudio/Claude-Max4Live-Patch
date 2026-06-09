# Spectral Drone Composer — Max for Live MIDI device

Generates MIDI **clips tuned to the just-intonation (JI) harmonic spectrum** of a
fundamental — for drone / spectral composition — and always exports an **exact-JI
SuperCollider `.scd`** plus a **cents map** alongside it.

> **What this is / isn't.** This is a **Max for Live** device (`.amxd`, MIDI Effect),
> built the way everything else in this repo is built (Python emits the patcher JSON +
> a companion `js` engine; `tools/amxd_lib.py` packs it). It is **not** an Ableton
> *Extensions* `.ablx` — that SDK (TypeScript, `api/`, `extensions-cli`) is a different
> project and is **not present in this repository**, so a real `.ablx` could not be built
> here without inventing its API. This is the faithful reframing onto *this repo's actual
> technology*. See `tools/make_spectral_drone.py`.

---

## ⚠️ Built blind — verify in Live (same caveat as the rest of the suite)

Assembled and statically validated in a headless Linux environment **with neither Max nor
Ableton Live**. What *was* verified here:

- the `.amxd` packs to a structurally valid **MIDI Effect** and its patcher JSON round-trips;
- the `js` engine passes a JavaScript syntax check (`node --check`);
- the `.scd` partial frequencies are **exactly** `fn = n·f0` and amplitudes are **exactly** `1/n`
  (all rows cross-checked); the partial-table cents match the spec (7th = −31.2¢, 11th = −48.7¢);
- the Live note API used (`create_clip`, `add_new_notes`) is the **documented** LOM API.

What you must still do: **open it in Live and test it.** No clip was actually generated, no
audio auditioned, no SuperCollider session run.

---

## The honest part: which detune strategy is active, and why

The brief lists three detune strategies in order of preference. The **Live Object Model has no
per-note pitch-bend / micro-tuning field** — `add_new_notes` accepts only
`pitch / start_time / duration / velocity / mute`, and MPE/microtuning data cannot be written
into a clip (it is even excluded from MIDI export). That rules out Strategy #1 (per-note bend in
one clip) and a clean Strategy #2 (clip-baked channel-bend envelopes) **via the LOM**.

**→ Active strategy = #3 (declared).** The generated **clip notes are nearest 12-TET**. The
**true, uncompromised just intonation** is written to two side files, every time:

| file | what it is |
|---|---|
| `spectrum_<f0>.scd` | SuperCollider drone — sines at `fn = n·f0` (no quantization), amps `1/n`, slow fades, on a **LinkClock** (Ableton Link). This is the real JI. |
| `detune_map_<f0>.txt` | exact **cents** per partial, to apply in **Live 12 "Tuning Systems"**, an MPE synth, a Sub 37, or SC. |

**The clip notes are never presented as JI.** To actually *hear* JI you run the `.scd`, or apply
the cents map to an MPE-capable instrument (in Live 12: *Tuning Systems* on an MPE device with
pitch-bend range 48 st), or use the `tracks` layout (below) and tune each partial's synth.

---

## JI partial table — f0 = C1 = 32.703 Hz, partials 1…16

```
 n   freq(Hz)  MIDI note    cents  vel
 1     32.703    24   C1     +0.0  100
 2     65.406    36   C2     +0.0   50
 3     98.109    43   G2     +1.9   33
 4    130.812    48   C3     +0.0   25
 5    163.515    52   E3    -13.7   20
 6    196.218    55   G3     +1.9   17
 7    228.921    58  A#3    -31.2   14
 8    261.624    60   C4     +0.0   12
 9    294.327    62   D4     +3.9   11
10    327.030    64   E4    -13.7   10
11    359.733    66  F#4    -48.7   10
12    392.436    67   G4     +1.9   10
13    425.139    68  G#4    +40.5   10
14    457.842    70  A#4    -31.2   10
15    490.545    71   B4    -11.7   10
16    523.248    72   C5     +0.0   10
```

Math: `fn = n·f0`; `m = 69 + 12·log2(fn/440)`; `note = round(m)`; `cents = (m − round(m))·100`.
Velocity `1/n` (parts roll off naturally); `equal` = flat 100.

---

## Use

1. **Install the `js` next to the device.** Keep `spectral_drone_composer.js` in the **same
   folder** as `Spectral Drone Composer.amxd` (or anywhere on Max's search path). When you later
   **Freeze** the device in Live, the `.js` is embedded and it becomes a single self-contained
   file. (Headless, it can't be frozen for you — same reason the rest of the suite ships unfrozen.)
2. **Drop the device on a MIDI track** in Live.
3. **Set parameters** (f0 Hz, partial from/to, duration, stagger) in the device UI, then click
   **Generate**.
4. You get: a **MIDI clip** on the track (one note per partial, staggered entries, `1/n`
   velocity, 12-TET nearest) **+** `spectrum_<f0>.scd` **+** `detune_map_<f0>.txt`.
5. The **Max Console** prints the full partial table, the active strategy, and where the files
   were written.

### Parameters

Defaults live as **editable constants at the top of `spectral_drone_composer.js`** (the spec asks
for this); the five most-used are also exposed as device dials. Everything is also settable by
message into the `js` inlet.

| constant / message | default | meaning |
|---|---|---|
| `F0_HZ` / `f0 <hz>` | `32.703` | fundamental in Hz (C1) |
| `F0_MIDI` / `f0midi <m>` | `-1` (off) | alt: fundamental as a MIDI note (overrides Hz) |
| `PARTIAL_FROM..TO` / `pfrom`,`pto` | `1..16` | partial range |
| `SELECTION` / `selection ...` | `all` | `all` \| `odd` \| `even` \| `primes` \| `1 3 5 7` |
| `DURATION_BEATS` / `dur` | `64` | note length (drone) |
| `STAGGER_BEATS` / `stagger` | `4` | entry offset per partial (Radigue accumulation; `0` = unison) |
| `VELOCITY_CURVE` / `velcurve` | `1/n` | `1/n` \| `equal` |
| `REGISTER_FOLD` / `fold` | `0` | fold partials above `MAX_MIDI` down by octaves |
| `LAYOUT` / `layout` | `clip` | `clip` (one staggered clip on this track) \| `tracks` (one MIDI track per partial) |
| `EXPORT_DIR` / `exportdir` | `""` | absolute folder for the `.scd`/`.txt` (`""` = Max default dir) |
| `USE_LEGACY_NOTES` / `legacy` | `0` | `0` = `add_new_notes` (Live 11+) · `1` = `set_notes/note/done` (older) |

`LAYOUT=tracks` creates one MIDI track per partial (named with its cents offset) so you can route
each to its **own synth tuned by the cents map** — that is the practical way to get true JI
*inside Live*.

---

## Run the true-JI render in SuperCollider

Open `spectrum_<f0>.scd`, put the cursor inside the `( … )` block, evaluate it (Cmd/Ctrl +
Enter). It boots the server, defines a sine-drone `SynthDef`, and stacks the partials with
staggered entries on a `LinkClock` (so SC locks to Live's transport via Ableton Link). Evaluate
the `STOP` line at the bottom for a slow release.

---

## Rebuild

```bash
python3 tools/make_spectral_drone.py
```

Regenerates the `.amxd`, the `js`, and the default-f0 `.scd` + cents map into
`devices/_standalone/`, and prints the validation report + partial table. Edit the `DEF` dict
(or the constants at the top of the embedded `JS_SOURCE`) and re-run.
