# Conversion Report

What this project received, what the build does to each device, and — just as important —
what it deliberately does **not** do.

## 1. What was provided

| Input | Contents |
|---|---|
| `ppooll.zip` (small) | **131** auto-generated Max for Live wrappers `live.ppooll.<act>.amxd` |
| `ppooll.zip` (large) | the full **ppooll 8.6.9** Max package (1045 files: acts, host, abstractions, JS, media, externals for macOS+Windows, and the generator script `tools/generate_per_act_amxd.py`) |

Analysis established the following facts (all reproducible from the data in this repo):

- The 131 wrappers are **identical** except for one bpatcher inside their
  `LIVE_PPOOLL_ENVIRONMENT` sub-patcher, which names the act to load
  (e.g. `freeverb@.maxpat`). This is exactly what ppooll's own
  `tools/generate_per_act_amxd.py` produces.
- Each wrapper's audio path is `mc.plugin~ 1…16 → mc.live.gain~ → mc.send~ live.stereo_in`
  and `mc.receive~ live.stereo_out → mc.live.gain~ → mc.plugout~ 1…16`; it loads
  `ppooll_host.maxpat` and the act **by name** (resolved via the Max search path).
- All 131 device files are Live device type **`iiii` (Instrument)**.
- Every device name maps **1:1** to an existing `<act>.maxpat` in
  `patchers/ppooll.acts/` — **no missing sources, no duplicates.** (The two acts present
  in the package but *not* wrapped, `benjolino` and `_act_overview`, are correctly absent.)
- The only machine-specific paths anywhere in the 131 files were **two** dependency-cache
  bootpaths per file, both rooted at `~/Desktop/ppooll/…` (262 entries total).

## 2. Phase 1–2 — Inventory & classification

- Built [`tools/device_map.json`](../tools/device_map.json): one row per device with the
  original act name, a curated human-readable **clear name**, a functional **category**, the
  official **description / tags / authors** (read verbatim from the package's own
  `misc/act_overview.json` — never invented), the **third-party packages** required (from the
  package's own `misc/package_dependencies.json`), and a **suggested** Live device type.
- 129/131 acts carried an upstream description; the two without (`buffer_host`, `mc.random@`)
  were named from their evident function and flagged.
- Categories were assigned from ppooll's own 15 tags plus curation, into 11 folders. The full
  table is [`device_inventory.md`](device_inventory.md).

## 3. Phase 3 — Conversion (what the build changes)

`tools/build_devices.py` performs a **minimal, safe, reversible** transform per device:

1. **Remove machine-specific paths.** Dependency-cache entries whose `bootpath` pointed at
   `~/Desktop/ppooll/…` are dropped (they are `implicit` — Max regenerates them from the search
   path on load). Result: **0 absolute/local paths** remain in any device (verified). The act,
   host, and abstraction references were already by-name, so nothing about *resolution* breaks —
   it now happens purely through the installed ppooll package.
2. **Rename + categorize.** The output filename is `Clear Name — <act>.amxd`, written into the
   correct `devices/<category>/` folder. In Max for Live the device's display name comes from the
   filename, so this *is* the rename — done without touching internal patch data.
3. **Fix the act-creation half-swap (v1.1).** The upstream generator rewrote only the *static*
   act reference and left the *dynamic* spawner (`create-act-bpatcher`) pointing at the placeholder
   `demosound@.maxpat` — so devices loaded `<act>` statically but spawned `demosound@` dynamically,
   colliding over `pattr`/`pattrstorage` (the `stack overflow` blocker). The build now rewrites
   both references (130/131 corrected; `demosound@` keeps the placeholder; 0 residual mismatches).
   See [`known_issues.md`](known_issues.md) §0 and [`debugging.md`](debugging.md).
4. **Set Live device type by category (`--retag`).** Audio processors → Audio Effect (`aaaa`),
   generators/sample-players → Instrument (`iiii`), MIDI acts → MIDI Effect (`mmmm`). This is the
   4-byte header code only; it does not rewire the patch.
5. **Re-pack byte-faithfully.** The original header (magic / version / meta chunk) is preserved;
   only the device-type 4CC (step 4), the `ptch` payload and its size are rewritten, exactly as
   Max writes them (tab-indented UTF-8). Each output is re-read and its JSON asserted equal to the
   in-memory patcher (round-trip check), with zero machine paths and zero act mismatches.

The shipped build is produced with `build_devices.py --retag`. The act-creation fix is **always**
applied; without `--retag` the original device type is preserved instead of the per-category type.

## 4. Phase 4–5 — Layout, parameters, testing (scope & status)

These three areas are where a headless environment hits hard limits. Being explicit:

- **GUI layout & parameter renaming.** The `.amxd` wrapper's own visible UI is generic and
  identical across all devices (8 dials, show/hide, console, info, audio I/O). The *real*
  per-module interface and its parameters live **inside the ppooll act patchers**, which are
  loaded at runtime from the shared package — they are **not** present in the wrapper to edit.
  Redesigning a module's panel or renaming its cryptic parameters therefore means editing shared
  `.maxpat` files **in Max, with visual verification in Live** — which cannot be done here without
  risking 131 untested, possibly-broken patches. This work is **documented but not performed**;
  the inventory gives the function and (where upstream provides it) the description to guide it.
  See [`known_issues.md`](known_issues.md) §GUI.
- **Functional testing.** No Max, no Ableton in the build environment → **no device was opened,
  loaded, or auditioned.** Only *static* validation was done (structure, round-trip, paths,
  source presence). Per the task's own rule ("don't deliver untested files without flagging it"),
  this is flagged loudly here, in the README, and per-row in the inventory. The exact functional
  test procedure for you to run in Live is in [`testing.md`](testing.md).

## 5. Phase 6 — Delivery

- 131 devices in `devices/<category>/`, originals preserved in `original_ppooll_sources/`,
  runtime in `dependencies/ppooll/`, docs in `docs/`, reproducible tooling in `tools/`.
- Build status for every device: [`build_report/build_report.json`](../build_report/build_report.json).

## 6. Summary

| Phase | Status |
|---|---|
| 1 — Analysis | ✅ Complete (131 mapped, dependencies + paths characterized) |
| 2 — Classification & naming | ✅ Complete (clear names + 11 categories, from ppooll metadata) |
| 3 — Conversion (portability + rename + repack) | ✅ Complete (131 built, statically validated) |
| 4 — Deep GUI/parameter redesign | ⏸ Documented, **requires Max + Live** (not done headless) |
| 5 — Functional testing in Live | ⏸ Procedure provided, **requires Ableton Live** (your step) |
| 6 — Delivery (repo + docs) | ✅ Complete |
