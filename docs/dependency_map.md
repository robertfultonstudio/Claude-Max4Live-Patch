# Dependency Map

How each device resolves its dependencies, and exactly which extra packages are required by which devices.

## 1. Always required (every device)

- **Max 8.6.1+ or Max 9** (the Max for Live runtime inside Ableton Live 11/12).
- **The bundled `ppooll` package** (`dependencies/ppooll/`) installed as a Max Package. Provides `ppooll_host.maxpat`, every `*.maxpat` act, all abstractions, JavaScript, media, and the bundled externals (`ll_number`, `ll_fastforward`, `ll_2dslider`, `shell`, `pattrexists`, `vbap`, …) for **both macOS (`.mxo`) and Windows (`.mxe64`)**.
- **`jasch objects`** — required by *all* acts; **not bundled**, install via the Max Package Manager.

## 2. Extra third-party Max packages (per device)

These are **not bundled** (they have their own licenses / installers). Install the ones you need via the Max Package Manager. Devices load and run *without* them, but the affected act will be missing its core object(s) until the package is present.

| Package | Required by | Install |
|---|---|---|
| **CNMAT Externals** | `SDIFter`, `pr.spectplay`, `rez@` | Max Package Manager |
| **ICST Ambisonics** | `spat.ambicontrol@`, `spat.ambidecode@`, `spat.ambiencode@`, `spat.ambimonitor@`, `spat.ambipanning@` | Max Package Manager |
| **LowkeyNW** | `gverb@` | Max Package Manager |
| **MuBu For Max** | `mubugrain@` | Max Package Manager |
| **PeRColate** | `munger@` | Max Package Manager |
| **cv.jit** | `jit.blobs` | Max Package Manager |
| **karma** | `karma@` | Max Package Manager |
| **link** | `link@` | Max Package Manager |

### Likely also required (not listed upstream — verify in Max)

| Package | Likely required by |
|---|---|
| ICST Ambisonics | `spat.abba@`, `spat.ambitransform@`, `spat.uhj2b@` |

## 3. Resolution model

Each `.amxd` references its act, the ppooll host, and abstractions **by name only** (e.g. the bpatcher `freeverb@.maxpat`, the object `ll.getacts2`, `loadmess ppooll_host.maxpat`). Max resolves these through the **package search path** once `ppooll` is installed as a package — there are **no absolute paths** left in any device (the original `~/Desktop/ppooll/...` dependency-cache bootpaths were removed during the build; 262 entries across the 131 devices).

This is why the devices do **not** need to sit next to the ppooll folder, and work regardless of where each user keeps things — the single requirement is that the `ppooll` package is installed in the Max **Packages** folder.
