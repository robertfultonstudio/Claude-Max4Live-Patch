# ppooll → Max for Live — Standalone Device Suite

131 modules from the **ppooll** live-performance environment, re-packaged as individually
named, category-sorted, path-clean **Max for Live** devices for Ableton Live — together with
the bundled ppooll runtime they need, and full documentation.

- **131 devices**, each derived 1:1 from an original ppooll *act* (no missing sources, no duplicates).
- **Renamed** `Clear Function Name — originalname.amxd` so they are readable in Live's browser.
- **Sorted** into 11 functional categories under [`devices/`](devices).
- **Portable**: every machine-specific absolute path (`~/Desktop/ppooll/…`) was removed — devices
  resolve entirely through the installed ppooll **Max Package** (262 path entries stripped in total).
- **Originals preserved** untouched in [`original_ppooll_sources/`](original_ppooll_sources).
- **Reproducible**: the whole suite is rebuilt by `tools/build_devices.py` (see [tools/](tools)).

> Source: **ppooll 8.6.9** by Klaus Filip & contributors — MIT licensed
> (<http://ppooll.klingt.org>, <https://github.com/ppooll-dev/ppooll>). This project re-packages
> and documents it; all credit for the modules belongs to the ppooll authors.

---

## ⚠️ Read this first — build status & honest scope

This suite was **assembled and statically validated in a headless Linux environment that has
neither Max nor Ableton Live**. That has two concrete consequences you must know:

1. **Every device still needs a functional test inside Ableton Live (macOS/Windows).**
   It was *not possible* to open, audition, or visually verify any device here. What *was* verified
   for all 131 (see [`build_report/build_report.json`](build_report/build_report.json)):
   the `.amxd` re-packs to a structurally valid file, its patcher JSON round-trips, **no
   machine-specific paths remain**, and the matching ppooll act exists in the bundled runtime.
   Follow [`docs/testing.md`](docs/testing.md) to complete functional testing — that step is yours.

2. **"Independent" here means "independent of the original author's machine", not "one
   self-contained file with zero dependencies."** ppooll is a *shared-runtime* modular system:
   every device loads `ppooll_host.maxpat` + its act + shared abstractions/externals. True
   single-file embedding ("Freeze") is a Max-only operation, is impractical here (it would bake the
   whole runtime into each of 131 files and stay platform-locked), and could not be performed
   without Max. The correct, supported model — and the one this suite uses — is: **install the
   bundled `ppooll` package once**, after which all 131 devices work with no per-user setup.

See [`docs/known_issues.md`](docs/known_issues.md) for the full, candid list of caveats
(device type, third-party packages, Jitter/video acts, GUI/parameter renaming scope).

---

## Install (3 steps)

1. **Install the ppooll runtime package.** Copy the folder [`dependencies/ppooll/`](dependencies/ppooll)
   into your Max Packages folder:
   - macOS: `~/Documents/Max 9/Packages/` (or `Max 8`)
   - Windows: `Documents\Max 9\Packages\`
2. **Install `jasch objects`** (required by *all* acts) via Max's **Package Manager**, plus any
   extra packages for the specific devices you use (13–17 devices — see
   [`docs/dependency_map.md`](docs/dependency_map.md)). Restart Max/Live.
3. **Add the devices to Live.** Either drop a `.amxd` from [`devices/`](devices) straight onto a
   track, or copy the category folders into your Ableton **User Library → Presets → … →** Max
   for Live folder so they appear in the browser.

Full, screenshot-level instructions: [`docs/installation.md`](docs/installation.md).

---

## Repository layout

```
.
├── README.md
├── devices/                     # the 131 converted devices, by function
│   ├── audio_effects/           (35)
│   ├── instruments/             (15)
│   ├── samplers/                (13)
│   ├── modulation/              (16)
│   ├── sequencing/              (7)
│   ├── midi/                    (2)
│   ├── routing_mixing/          (5)
│   ├── spatialization/          (9)
│   ├── analysis_metering/       (5)
│   ├── visual_jitter/           (16)
│   └── utilities/               (8)
├── dependencies/
│   ├── ppooll/                  # full ppooll 8.6.9 runtime (install as a Max Package)
│   └── README.md                # what to install + where to get extra packages
├── original_ppooll_sources/
│   ├── devices_amxd/            # the original 131 .amxd, untouched (preserved)
│   └── README.md
├── docs/
│   ├── device_inventory.md      # the full 131-row table (original → new → category → fn → deps → status)
│   ├── conversion_report.md     # exactly what the build did, and what it deliberately did not
│   ├── known_issues.md          # candid caveats + what still needs Max/Live
│   ├── dependency_map.md        # per-device dependency / package requirements
│   ├── installation.md          # install in Ableton Live
│   └── testing.md               # per-device test procedure + the testing-status reality
├── tools/
│   ├── amxd_lib.py              # byte-faithful .amxd reader/writer
│   ├── device_map.json          # single source of truth (names, categories, deps, types)
│   ├── make_device_map.py       # regenerates device_map.json from ppooll's own metadata
│   ├── build_devices.py         # builds devices/ from originals (rename + path-clean + repack)
│   └── make_docs.py             # regenerates the inventory + dependency map
└── build_report/
    └── build_report.json        # per-device build/validation status
```

## Rebuild from scratch

```bash
python3 tools/make_device_map.py     # (re)generate the curated map from ppooll metadata
python3 tools/build_devices.py        # build devices/ (preserves original Live device type)
# optional: re-tag each device's Live type (Audio Effect / Instrument / MIDI Effect) by category
#   python3 tools/build_devices.py --retag --clean   # then TEST in Live before relying on it
python3 tools/make_docs.py            # regenerate inventory + dependency map
```

## License & credits

- The **ppooll** modules and runtime are © Klaus Filip & contributors, **MIT** licensed
  (see [`dependencies/ppooll/LICENSE.md`](dependencies/ppooll/LICENSE.md)). MIT permits this
  redistribution and modification provided the copyright notice is retained — it is.
- Third-party packages (jasch objects, CNMAT Externals, ICST Ambisonics, karma, link, LowkeyNW,
  PeRColate, cv.jit, MuBu) are **not** redistributed here; install them yourself via the Max
  Package Manager. Each carries its own license.
- The packaging/renaming/documentation tooling in [`tools/`](tools) is provided as-is for this suite.
