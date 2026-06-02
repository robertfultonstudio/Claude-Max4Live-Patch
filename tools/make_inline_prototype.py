#!/usr/bin/env python3
"""
Build the Approach-A inline-panel PROTOTYPE for one device (freeverb@), per the runbook:
  - add a top-level referenced bpatcher of the act (0 in / 0 out, embed OFF) in Presentation,
  - remove the duplicate static act newobj in p LIVE_PPOOLL_ENVIRONMENT,
  - cut the loadmess -> create-act-bpatcher cord (stop the 2nd instance / external window).
Starts from the shipped device (so it keeps the v1.1 fix, path-strip and Audio-Effect type).
Output is STRUCTURAL only — it must be verified in Live (param registration is the open question).
"""
import os
import sys

sys.path.insert(0, "tools")
import amxd_lib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "devices", "audio_effects", "Reverb (Freeverb) — freeverb@.amxd")
OUTDIR = os.path.join(ROOT, "devices", "_prototype_inline")
OUT = os.path.join(OUTDIR, "Reverb (Freeverb) INLINE — freeverb@.amxd")
ACT = "freeverb@.maxpat"
PANEL_W, PANEL_H = 159.0, 133.0  # freeverb@ native window size


def find_env(patcher):
    for b in patcher.get("boxes", []):
        bo = b["box"]
        if bo.get("varname") == "LIVE_PPOOLL_ENVIRONMENT":
            return bo["patcher"]
        if "patcher" in bo:
            r = find_env(bo["patcher"])
            if r:
                return r
    return None


def mutate(obj):
    p = obj["patcher"]

    # unique id for the new bpatcher
    existing = {b["box"].get("id", "") for b in p["boxes"]}
    nid = "obj-9001"
    while nid in existing:
        nid = "obj-" + str(int(nid.split("-")[1]) + 1)

    # 1) add top-level referenced bpatcher of the act, in presentation, below the shell content
    bpatcher = {"box": {
        "maxclass": "bpatcher",
        "name": ACT,
        "id": nid,
        "numinlets": 0,
        "numoutlets": 0,
        "embed": 0,
        "bgmode": 0,
        "offset": [0.0, 0.0],
        "viewvisibility": 1,
        "presentation": 1,
        "presentation_rect": [6.0, 165.0, PANEL_W, PANEL_H],
        "patching_rect": [6.0, 640.0, PANEL_W, PANEL_H],
        "varname": "inline_act",
    }}
    p["boxes"].append(bpatcher)

    # 2) edit the environment subpatcher
    env = find_env(p)
    assert env is not None, "env subpatcher not found"
    # remove the static act newobj (the duplicate instance)
    before = len(env["boxes"])
    env["boxes"] = [
        b for b in env["boxes"]
        if not (b["box"].get("maxclass") == "newobj" and b["box"].get("text", "") == ACT)
    ]
    removed_static = before - len(env["boxes"])
    # cut the loadmess(ppooll_host) -> create-act-bpatcher cord (stop auto 2nd instance + window)
    def is_loadmess_to_create(line):
        s, d = line["patchline"]["source"][0], line["patchline"]["destination"][0]
        ids = {b["box"].get("id"): b["box"] for b in env["boxes"]}
        sb = ids.get(s, {}); db = ids.get(d, {})
        return sb.get("text", "").startswith("loadmess") and "create-act-bpatcher" in db.get("text", "")
    before_l = len(env.get("lines", []))
    env["lines"] = [l for l in env.get("lines", []) if not is_loadmess_to_create(l)]
    cut_cord = before_l - len(env["lines"])

    print(f"  added bpatcher id={nid} name={ACT} (presentation 159x133)")
    print(f"  removed static act newobj: {removed_static}")
    print(f"  cut loadmess->create-act-bpatcher cords: {cut_cord}")
    return obj


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    amxd_lib.repack_file(SRC, OUT, mutate=mutate)  # preserves Audio-Effect type
    # validate
    _, _, chk = amxd_lib.read(OUT)
    top = chk["patcher"]["boxes"]
    has_bp = any(b["box"].get("maxclass") == "bpatcher" and b["box"].get("name") == ACT for b in top)
    print(f"  wrote {OUT}")
    print(f"  validation: JSON ok, top-level bpatcher present = {has_bp}, "
          f"type = {amxd_lib.TYPE_NAMES.get(amxd_lib.device_type(OUT))}")


if __name__ == "__main__":
    main()
