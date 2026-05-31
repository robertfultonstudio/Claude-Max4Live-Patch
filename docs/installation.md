# Installation — using the devices in Ableton Live

Requires **Ableton Live 11 or 12 with Max for Live**, and **Max 8.6.1+ / Max 9** installed
(Live's bundled Max is fine). macOS or Windows. (There is no Linux build of Max for Live.)

## Step 1 — Install the ppooll runtime package (required)

The devices load the ppooll host + their act from the **ppooll Max Package**. Install it once:

1. Copy the folder `dependencies/ppooll/` from this repo into your Max **Packages** folder:
   - **macOS:** `~/Documents/Max 9/Packages/` (or `~/Documents/Max 8/Packages/`)
   - **Windows:** `C:\Users\<you>\Documents\Max 9\Packages\`
   - The result should be `…/Packages/ppooll/` containing `package-info.json`, `patchers/`,
     `extras/ppooll_host.maxpat`, `externals/`, etc.
2. **Restart** Max and Ableton Live so the package is indexed.

> Tip: to find the exact folder, open Max → **Options ▸ File Preferences**, or
> **Max ▸ Show Package Manager ▸ (gear) ▸ Open Packages Folder**.

## Step 2 — Install the third-party packages

Open Max → **Window ▸ Package Manager** and install:

- **`jasch objects`** — **required by all devices**.
- Any extra packages for the specific devices you intend to use (see
  [`dependency_map.md`](dependency_map.md)): CNMAT Externals, ICST Ambisonics, karma, link,
  LowkeyNW, PeRColate, cv.jit, MuBu For Max.

Restart Live after installing. (You can skip a package if you won't use the devices that need it;
those devices will still load but their core object(s) will be missing.)

## Step 3 — Make the devices available in Live

Pick **one**:

**A. Quick (drag & drop).** Drag any `.amxd` from `devices/<category>/` directly onto an
appropriate Live track. Good for trying one device.

**B. Browser integration (recommended).** Copy the `devices/` category folders into your Ableton
**User Library** so they show up in Live's browser:

- **macOS:** `~/Music/Ableton/User Library/Presets/`
- **Windows:** `…\Documents\Ableton\User Library\Presets\`

You can keep the category subfolders — Live shows the folder tree in the browser. The device name
shown is the file name (e.g. *Reverb (Freeverb) — freeverb@*).

## Which track does a device go on?

All devices are currently **Instrument**-type (see [`known_issues.md`](known_issues.md) §4):

- **Instruments / generators / samplers / synths** → drop on a **MIDI track** (instrument slot).
- **Audio effects, filters, dynamics, spatialization, analysis** → these are *also* tagged
  Instrument right now. If, in testing, a processor doesn't receive your track's audio, either
  (a) route audio into it via ppooll's own input acts (e.g. `INmulti`), or (b) rebuild that device
  as an Audio Effect: `python3 tools/build_devices.py --retag --clean`, then re-test (this re-tags
  by the suggested type in the inventory). See [`testing.md`](testing.md) §Device type.

## First-launch notes

- The **first** time a device opens it loads the ppooll host environment; this can take a few
  seconds and may print informational messages in the Max console — that's normal.
- macOS may ask for **Microphone / Camera / Screen-Recording** permission for input/Jitter acts.
- If a device shows missing-object errors, the usual cause is a not-yet-installed package
  (Step 2) or the ppooll package not being in the Packages folder (Step 1).
