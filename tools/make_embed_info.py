#!/usr/bin/env python3
"""
Collect, for every act, the data needed to embed it as an inline bpatcher in the
M4L device (so the act's GUI shows inside the device box instead of a separate window):
  - window/canvas size (the act's Max layout = its UI, since ppooll acts are compact)
  - inlet / outlet counts (a bpatcher must declare these correctly)
  - whether it already has a Presentation layout
Writes tools/act_embed_info.json.
"""
import json
import os
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ACTS = os.path.join(ROOT, "dependencies", "ppooll", "patchers", "ppooll.acts")
SRC = os.path.join(ROOT, "original_ppooll_sources", "devices_amxd")


def act_info(act):
    p = json.load(open(os.path.join(ACTS, f"{act}.maxpat")))["patcher"]
    boxes = [b["box"] for b in p.get("boxes", [])]
    n_in = sum(1 for b in boxes if b.get("maxclass") == "inlet")
    n_out = sum(1 for b in boxes if b.get("maxclass") == "outlet")
    rect = p.get("rect", [0, 0, 0, 0])
    n_pres = sum(1 for b in boxes if b.get("presentation") == 1)
    return {
        "act": act,
        "win_w": int(rect[2]),
        "win_h": int(rect[3]),
        "n_inlets": n_in,
        "n_outlets": n_out,
        "n_boxes": len(boxes),
        "openinpresentation": p.get("openinpresentation", 0),
        "n_presentation_objs": n_pres,
    }


def main():
    acts = sorted(
        os.path.basename(f)[len("live.ppooll."):-len(".amxd")]
        for f in glob.glob(os.path.join(SRC, "*.amxd"))
    )
    rows = []
    for a in acts:
        try:
            rows.append(act_info(a))
        except Exception as e:  # noqa
            rows.append({"act": a, "error": str(e)})
    out = os.path.join(HERE, "act_embed_info.json")
    json.dump({"count": len(rows), "acts": rows}, open(out, "w"), indent=1)

    # summary
    ok = [r for r in rows if "win_h" in r]
    buckets = {"compact(<=120h)": 0, "medium(<=200h)": 0, "large(<=350h)": 0, "xl(>350h)": 0}
    for r in ok:
        h = r["win_h"]
        if h <= 120:
            buckets["compact(<=120h)"] += 1
        elif h <= 200:
            buckets["medium(<=200h)"] += 1
        elif h <= 350:
            buckets["large(<=350h)"] += 1
        else:
            buckets["xl(>350h)"] += 1
    with_pres = sum(1 for r in ok if r["openinpresentation"] == 1)
    print(f"wrote {out} ({len(rows)} acts)")
    print("acts with a Presentation layout (openinpresentation=1):", with_pres, "/", len(ok))
    print("native-size buckets:", json.dumps(buckets))
    print("widest:", max(ok, key=lambda r: r["win_w"])["act"],
          max(r["win_w"] for r in ok), "px")
    print("tallest:", max(ok, key=lambda r: r["win_h"])["act"],
          max(r["win_h"] for r in ok), "px")


if __name__ == "__main__":
    main()
