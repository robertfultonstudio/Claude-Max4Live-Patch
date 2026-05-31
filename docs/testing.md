# Testing Guide

## Status: what has and hasn't been tested

| Check | Done here? | How |
|---|---|---|
| Valid `.amxd` structure (header + `ptch` + JSON) | ✅ | `tools/amxd_lib.read` on every output |
| JSON round-trips after repack (no corruption) | ✅ | self-check in `repack_file` |
| **No** machine-specific / absolute paths remain | ✅ | regex scan, all 131 clean |
| Source act `.maxpat` exists in bundled runtime | ✅ | filesystem check, all 131 present |
| Opens in Max for Live without error | ❌ **you** | no Max in build env — see below |
| Loads in Ableton Live | ❌ **you** | no Live in build env |
| Audio/MIDI/video actually passes | ❌ **you** | requires audio hardware + Live |
| Controls behave; no Max-console errors | ❌ **you** | requires Live |
| Saves & recalls correctly in a Live set | ❌ **you** | requires Live |

Per-device static results: [`build_report/build_report.json`](../build_report/build_report.json).
The functional rows are **yours to complete** — that is unavoidable, since Max for Live only runs
inside Max/Ableton on macOS/Windows.

## Per-device functional test (do this in Ableton Live)

For each device (start with one per category, then the ones you care about):

1. **Open** — drag the `.amxd` onto a track. The device title bar should show the clear name.
2. **Console** — open Max's console (in Live: device titlebar ▸ **Edit** opens the patch; or
   Max ▸ Window ▸ Max Console). Note any **error** (missing object/file = a package or the ppooll
   package isn't installed; see [`installation.md`](installation.md)). Informational messages on
   first load are normal.
3. **Signal** —
   - *Instrument / generator / synth / sampler:* play MIDI (or its trigger) → expect audio out.
   - *Audio effect / filter / dynamics / spatial:* feed audio → expect processed audio out. If
     nothing comes through, see **§Device type** below.
   - *Modulation / sequencing / control:* map a control to a Live parameter → expect it to move.
   - *Visual (Jitter):* expect a video window / texture; grant camera/screen permission if asked.
     These do **not** pass audio.
4. **Controls** — move the main controls; confirm audible/visible change and no console errors.
5. **Persistence** — save the Live set, close, reopen → device should reload with its state.
6. **Record the result** in the inventory's Status column (or your own copy): OK / issue + note.

## §Device type (Instrument vs Audio Effect)

All devices currently load as **Instrument**. If an audio *processor* doesn't receive the track's
input audio when used as an insert:

- Quick test of the alternative tagging:
  ```bash
  python3 tools/build_devices.py --retag --clean
  ```
  This re-tags each device with the **suggested** type from `tools/device_map.json`
  (Audio Effect for processors, Instrument for generators, MIDI Effect for the 2 MIDI acts),
  changing only the 4-byte type code. Re-test in Live.
- Or keep Instrument tagging and route audio in through a ppooll input act (e.g. `INmulti`).
- Decide per device which behaviour you want; both builds are reproducible.

## Batch sanity re-check (no Max needed)

You can re-run the static validation at any time:

```bash
python3 tools/build_devices.py     # rebuilds + re-validates all 131; prints OK/WARN/ERROR counts
```

Expected: `Built 131 devices: 131 OK, 0 WARN, 0 ERROR`.

## Suggested test order

1. Simple audio FX first — `freeverb@`, `eq@`, `overdrive@`, `prdelay@` — to confirm the ppooll
   package + jasch objects are correctly installed and audio flows.
2. A generator — `sinus`, `noize@` — to confirm instrument behaviour.
3. A modulator — `LFFO`/`animator@` — mapped to a Live parameter.
4. Then the devices needing extra packages (verify each package is installed first).
5. Jitter acts last (they need cameras/movies/permissions).
