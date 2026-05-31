# Known Issues & Caveats

Candid list of everything that is unverified, limited, or needs your attention. Nothing here is
hidden in order to make the suite look more finished than it is.

## 1. Functional testing was not possible in this environment — **highest priority**

The suite was built on a headless Linux server with **no Max and no Ableton Live**. Therefore
**no device was opened, loaded into Live, or auditioned.** Each device passed only *static*
validation (valid `.amxd` structure, JSON round-trip, no machine paths, source act present in the
runtime). You **must** run the functional tests in [`testing.md`](testing.md) on macOS/Windows
before relying on any device. Treat every "Static-OK" status as "structurally sound, **awaiting
your functional test**."

## 2. "Independence" = no per-user paths, **not** a zero-dependency single file

ppooll is a shared-runtime system. Each device loads `ppooll_host.maxpat` + its act + shared
abstractions/externals **by name**. This suite makes the devices independent of *where you keep
files* (all absolute paths removed; resolution via the installed package). It does **not** turn
each `.amxd` into a self-contained island — that would require Max's "Freeze/Consolidate"
(unavailable here), would bloat each of 131 files with the whole runtime, and would still be
platform-locked by the compiled externals. **The single install requirement is: the bundled
`ppooll` package in your Max Packages folder.**

## 3. Third-party Max packages are required by some devices (not bundled)

- **`jasch objects` — required by *every* device.** Without it, devices may not function at all.
  Install via Max Package Manager.
- **17 devices need an additional package** (CNMAT Externals, ICST Ambisonics, karma, link,
  LowkeyNW, PeRColate, cv.jit, MuBu For Max). The exact package-per-device list is in
  [`dependency_map.md`](dependency_map.md). These packages have their own licenses and are **not**
  redistributed here. A device whose package is missing will load but its core object(s) will be
  absent (you'll see errors in the Max console).
- 3 ambisonics converters (`spat.abba@`, `spat.ambitransform@`, `spat.uhj2b@`) are **likely** to
  need ICST Ambisonics too; this is inferred (not stated upstream) — verify in Max.

## 4. All devices are tagged as **Instrument** (`iiii`) — this is inherited, and may not be ideal

Every original wrapper is a Live **Instrument**. For sound generators/synths/samplers that's
natural. For **audio processors** (reverb, EQ, delay, distortion, dynamics, filters…) an
Instrument does **not** receive the track's audio input in Live the way an **Audio Effect** does —
so used as a plain insert they may produce no processed output unless fed through ppooll's own
routing. We **preserved the original type** to avoid shipping untested behavioural changes.

- The inventory lists a **suggested** type per device (`live_type`), and the build supports
  re-tagging: `python3 tools/build_devices.py --retag --clean`. This only changes the 4-byte type
  code; it does not rewire anything.
- **Re-tagging is unverified** — only switch a device's type if you then confirm it in Live.
  See [`testing.md`](testing.md) §Device type.

## 5. GUI layout & parameter renaming were not performed

The wrapper's own panel is generic; each module's real controls/parameters live inside the shared
ppooll act patchers, loaded at runtime. Renaming cryptic parameters or redesigning a module's
layout means editing those shared `.maxpat` files **in Max and verifying visually in Live** — not
safely doable in a headless batch over 131 devices. So:

- The **device names** are clear and the **inventory** documents each module's function.
- The **internal** parameter labels and panel layouts remain as ppooll ships them.
- Doing the deep per-module GUI/parameter polish is a clearly-scoped follow-up that needs Max +
  Live (and ideally per-module judgement). The maintainers' own act layout tool (`tetris@`) is
  included to help.

## 6. Jitter / video acts (16) have special needs

Devices in `visual_jitter/` process **video**, not audio, and several need a camera, a movie file,
GPU/OpenGL, or screen-capture permissions (e.g. `jit.grab@` camera, `jit.player` movie,
`jit.copyprot.act` screen grab, `jit.blobs` needs **cv.jit**). They will not "pass audio" — judge
them by their video behaviour. Expect macOS to prompt for Camera/Screen-Recording permission.

## 7. Function uncertainty on a couple of acts

- `equalAmp` — upstream description is literally "????"; named "Equal Amplitude Utility" from the
  name. Verify its real function in Max.
- `buffer_host`, `mc.random@` — no upstream description; named from evident function.

## 8. Platform / version notes

- Requires **Max 8.6.1+ / Max 9** (Live 11/12 with Max for Live). The bundled externals cover
  **macOS (`.mxo`, x64 + Apple Silicon)** and **Windows (`.mxe64`, x64)**. There is **no Linux**
  Max runtime — these cannot run on Linux (which is also why they couldn't be tested here).
- The devices were generated with Max 9.0.8 (`appversion` in the patcher). Opening in an older Max
  may prompt to convert.

## 9. Repository size

The bundled ppooll runtime (~57 MB) plus originals plus built devices make this a "heavy" repo. It
is intentional: it keeps the suite self-contained and the build reproducible. If you only need the
devices, you still need the `ppooll` package installed — it is not optional.
