# Dependencies

## `ppooll/` — the runtime (bundled, install this)

The complete, unmodified **ppooll 8.6.9** Max package (Klaus Filip & contributors, MIT). The 131
devices load `ppooll_host.maxpat`, their act patcher, and shared abstractions/externals from this
package **by name**, via the Max search path.

**Install it as a Max Package** (copy into `…/Documents/Max 9/Packages/`) — see
[`../docs/installation.md`](../docs/installation.md). It includes the externals for **macOS
(`.mxo`, x64 + Apple Silicon)** and **Windows (`.mxe64`, x64)**.

## Third-party packages (NOT bundled — install via Max Package Manager)

These are required by some devices and are **not** redistributed here (each has its own license).
Full per-device mapping: [`../docs/dependency_map.md`](../docs/dependency_map.md).

| Package | Needed by | Notes |
|---|---|---|
| **jasch objects** | **all devices** | install before anything else |
| CNMAT Externals | `rez@`, `pr.spectplay`, `SDIFter` | |
| ICST Ambisonics | the `spat.ambi*@` family (and likely `spat.abba@`, `spat.ambitransform@`, `spat.uhj2b@`) | |
| karma | `karma@` | |
| link | `link@` | Ableton Link |
| LowkeyNW | `gverb@` | |
| PeRColate | `munger@` | |
| cv.jit | `jit.blobs` | |
| MuBu For Max | `mubugrain@` | |

All are installable from Max → **Window ▸ Package Manager**.
