# Original ppooll sources (preserved — do not edit)

This folder preserves the **original, unmodified** inputs so nothing is lost and every
transformation is auditable and reversible.

## `devices_amxd/`

The **131 original** `live.ppooll.<act>.amxd` Max for Live wrappers exactly as received. These are
the inputs to `tools/build_devices.py`. They are kept verbatim:

- to satisfy the rule "never delete the originals / never lose original names & references";
- so you can always diff a converted device against its source;
- so the build can be re-run from a clean source at any time.

The **only** differences between these and the devices in `../devices/` are:
(1) the two `~/Desktop/ppooll/…` machine-specific dependency-cache paths were removed, and
(2) the file was renamed and sorted into a category folder. No patch logic, parameters, GUI, or
device type were changed by the default build.

## The original ppooll runtime

The full upstream **ppooll 8.6.9** package is vendored, unmodified, at
[`../dependencies/ppooll/`](../dependencies/ppooll) (it doubles as both the dependency you install
and the pristine upstream source — including ppooll's own generator script at
`dependencies/ppooll/tools/generate_per_act_amxd.py` and its metadata in
`dependencies/ppooll/misc/`). It is MIT licensed; see its `LICENSE.md`.
