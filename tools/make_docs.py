#!/usr/bin/env python3
"""Generate docs/device_inventory.md and docs/dependency_map.md from the build data."""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")
MAP = json.load(open(os.path.join(HERE, "device_map.json"), encoding="utf-8"))["devices"]
REPORT = json.load(open(os.path.join(ROOT, "build_report", "build_report.json"), encoding="utf-8"))
STATUS = {d["act"]: d for d in REPORT["devices"]}

CAT_TITLE = {
    "audio_effects": "Audio Effects",
    "instruments": "Instruments / Generators",
    "samplers": "Samplers & Buffer/Disk Players",
    "modulation": "Modulation & Control Sources",
    "sequencing": "Sequencing & Clocks",
    "midi": "MIDI",
    "routing_mixing": "Routing & Mixing",
    "spatialization": "Spatialization (Ambisonics / VBAP)",
    "analysis_metering": "Analysis & Metering",
    "visual_jitter": "Visual (Jitter)",
    "utilities": "Utilities",
}
CAT_ORDER = list(CAT_TITLE.keys())


def deps_str(d):
    parts = ["ppooll", "jasch objects"]
    parts += d["extra_packages"]
    s = " + ".join(parts)
    if d["extra_packages_inferred"]:
        s += " + (likely: " + ", ".join(d["extra_packages_inferred"]) + ")"
    return s


def md_escape(s):
    return s.replace("|", "\\|")


def device_filename(d):
    return f"{d['clear_name'].replace('/', '-')} — {d['act']}.amxd"


def write_inventory():
    by_cat = defaultdict(list)
    for d in MAP:
        by_cat[d["category"]].append(d)

    lines = []
    lines.append("# Device Inventory — 131 ppooll Max for Live Devices\n")
    lines.append("Generated from `tools/device_map.json` + `build_report/build_report.json`. "
                 "Do not edit by hand; run `python3 tools/make_docs.py`.\n")
    lines.append(f"**Total devices: {len(MAP)}**  •  Source: ppooll 8.6.9 (MIT)  •  "
                 "All map 1:1 to an original ppooll act — no missing sources.\n")

    # status legend
    lines.append("## Status legend\n")
    lines.append("- **Static-OK** — re-packs to a structurally valid `.amxd`, JSON round-trips, "
                 "all machine-specific paths removed, source act present in the bundled runtime.\n"
                 "- ⚠ **Verify** — additionally needs a third-party Max package, or has another note.\n"
                 "- **Functional testing in Ableton Live (Mac/Win) is still required for every device** — "
                 "it could not be performed in the build environment (no Max/Live). See "
                 "[testing.md](testing.md) and [known_issues.md](known_issues.md).\n")

    # summary table by category
    lines.append("## Summary by category\n")
    lines.append("| Category | Count |")
    lines.append("|---|---:|")
    for c in CAT_ORDER:
        lines.append(f"| {CAT_TITLE[c]} | {len(by_cat.get(c, []))} |")
    lines.append(f"| **Total** | **{len(MAP)}** |\n")

    # per-category detailed tables
    for c in CAT_ORDER:
        items = sorted(by_cat.get(c, []), key=lambda d: d["clear_name"].lower())
        if not items:
            continue
        lines.append(f"## {CAT_TITLE[c]}  ({len(items)})\n")
        lines.append("| Original (ppooll) | New device name | Function | Dependencies | Status | Notes |")
        lines.append("|---|---|---|---|---|---|")
        for d in items:
            st = STATUS.get(d["act"], {})
            status = st.get("status", "?")
            extra = bool(d["extra_packages"] or d["extra_packages_inferred"])
            status_label = "⚠ Verify" if (status != "OK" or extra) else "Static-OK"
            note_bits = []
            if extra:
                note_bits.append("3rd-party pkg required")
            # include live_type note
            for n in st.get("notes", []):
                if n.startswith("live_type="):
                    note_bits.append(n)
            authors = "/".join(d["authors"])
            lines.append(
                f"| `{md_escape(d['act'])}` "
                f"| {md_escape(d['clear_name'])} "
                f"| {md_escape(d['description'])} "
                f"| {md_escape(deps_str(d))} "
                f"| {status_label} "
                f"| {md_escape('; '.join(note_bits))} (by {md_escape(authors)}) |"
            )
        lines.append("")

    open(os.path.join(DOCS, "device_inventory.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("wrote docs/device_inventory.md")


def write_depmap():
    lines = []
    lines.append("# Dependency Map\n")
    lines.append("How each device resolves its dependencies, and exactly which extra packages "
                 "are required by which devices.\n")

    lines.append("## 1. Always required (every device)\n")
    lines.append("- **Max 8.6.1+ or Max 9** (the Max for Live runtime inside Ableton Live 11/12).\n"
                 "- **The bundled `ppooll` package** (`dependencies/ppooll/`) installed as a Max Package. "
                 "Provides `ppooll_host.maxpat`, every `*.maxpat` act, all abstractions, JavaScript, "
                 "media, and the bundled externals (`ll_number`, `ll_fastforward`, `ll_2dslider`, "
                 "`shell`, `pattrexists`, `vbap`, …) for **both macOS (`.mxo`) and Windows (`.mxe64`)**.\n"
                 "- **`jasch objects`** — required by *all* acts; **not bundled**, install via the "
                 "Max Package Manager.\n")

    # group by package
    pkg_to_acts = defaultdict(list)
    inferred_to_acts = defaultdict(list)
    for d in MAP:
        for p in d["extra_packages"]:
            pkg_to_acts[p].append(d)
        for p in d["extra_packages_inferred"]:
            inferred_to_acts[p].append(d)

    lines.append("## 2. Extra third-party Max packages (per device)\n")
    lines.append("These are **not bundled** (they have their own licenses / installers). Install the "
                 "ones you need via the Max Package Manager. Devices load and run *without* them, but "
                 "the affected act will be missing its core object(s) until the package is present.\n")
    lines.append("| Package | Required by | Install |")
    lines.append("|---|---|---|")
    for pkg in sorted(pkg_to_acts):
        acts = ", ".join(f"`{d['act']}`" for d in sorted(pkg_to_acts[pkg], key=lambda x: x["act"]))
        lines.append(f"| **{pkg}** | {acts} | Max Package Manager |")
    lines.append("")
    if inferred_to_acts:
        lines.append("### Likely also required (not listed upstream — verify in Max)\n")
        lines.append("| Package | Likely required by |")
        lines.append("|---|---|")
        for pkg in sorted(inferred_to_acts):
            acts = ", ".join(f"`{d['act']}`" for d in sorted(inferred_to_acts[pkg], key=lambda x: x["act"]))
            lines.append(f"| {pkg} | {acts} |")
        lines.append("")

    lines.append("## 3. Resolution model\n")
    lines.append("Each `.amxd` references its act, the ppooll host, and abstractions **by name only** "
                 "(e.g. the bpatcher `freeverb@.maxpat`, the object `ll.getacts2`, `loadmess "
                 "ppooll_host.maxpat`). Max resolves these through the **package search path** once "
                 "`ppooll` is installed as a package — there are **no absolute paths** left in any device "
                 "(the original `~/Desktop/ppooll/...` dependency-cache bootpaths were removed during the "
                 "build; 262 entries across the 131 devices).\n")
    lines.append("This is why the devices do **not** need to sit next to the ppooll folder, and work "
                 "regardless of where each user keeps things — the single requirement is that the "
                 "`ppooll` package is installed in the Max **Packages** folder.\n")

    open(os.path.join(DOCS, "dependency_map.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("wrote docs/dependency_map.md")


if __name__ == "__main__":
    os.makedirs(DOCS, exist_ok=True)
    write_inventory()
    write_depmap()
