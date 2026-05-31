# Known Issues & Caveats

Candid list of everything that is unverified, limited, or needs your attention. Nothing here is
hidden in order to make the suite look more finished than it is.

## 0. Fixed in v1.1 — act-creation "half-swap" (caused the `stack overflow` blocker)

An end-user reported `Reverb (Freeverb)` failing on insertion with
`prepend: stack overflow -- outlets are disabled until this message is cleared`, no act UI, and
no audio. Investigation found the root cause — **a bug in the upstream `generate_per_act_amxd.py`**:

- The ppooll-for-Live template names the loaded act in **two** places, kept identical
  (both `demosound@.maxpat`): (1) a static abstraction, and (2) the message inside
  `p create-act-bpatcher` that `ppooll_host` bangs (via `r live.load_act`,
  `thispatcher script newdefault`) to **dynamically spawn** the act.
- The upstream generator rewrote only **(1)**. So every generated device **statically loaded
  `<act>`** while `ppooll_host` **dynamically spawned `demosound@`** — two different acts
  colliding over the shared `pattr`/`pattrstorage` state → the stack overflow, and the wrong
  act being managed (hence no audio / no correct UI). This was present in all 131 and is exactly
  why the bare `live.ppooll.amxd` could also exhibit it.

**Fix (v1.1):** `tools/build_devices.py` now rewrites *both* references, restoring the template's
invariant (verified: 130/131 corrected; the `demosound@` device legitimately keeps the
placeholder; 0 residual mismatches). This is a high-confidence structural fix that makes each
device internally consistent with the original template's own pattern.

> ⚠️ Honest status: this fix is **statically verified** (the patcher is now consistent) but, as
> with everything here, it was **not run in Max/Live** in the build environment. Please re-test in
> Live (it's the first thing to check). If any residual Max-runtime issue remains, use
> [`debugging.md`](debugging.md) to iterate locally where Max can actually run it.

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

## 4. Device types are assigned **per category** (was: all Instrument)

As of v1.1 the shipped devices are typed by function (`build_devices.py --retag`):

- **Audio Effect** (`aaaa`) — audio processors: `audio_effects`, `modulation`, `sequencing`,
  `routing_mixing`, `spatialization`, `analysis_metering`, `visual_jitter`, `utilities`, plus the
  audio recorders `buffub`/`rec@` (they need track input). Drop these on an **Audio track**.
- **Instrument** (`iiii`) — `instruments` and the sample/buffer **players** (`samplers`). Drop
  these on a **MIDI track**.
- **MIDI Effect** (`mmmm`) — `midikeys`, `control@`.

This matches the original request (audio FX as Audio Effects, samplers/synths as Instruments).
The type is the 4-byte header code only; it does not rewire the patch. If a specific device's
type still feels wrong in your workflow, you can rebuild preserving the original type
(`build_devices.py` without `--retag`) or adjust `live_type` in `tools/device_map.json`. The
type↔track behaviour is the kind of thing to confirm in Live — see [`testing.md`](testing.md).

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
