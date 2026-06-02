#!/usr/bin/env python3
"""
Build a self-contained Granular Delay Max for Live AUDIO EFFECT device.

Design goals (after the ppooll collisions): ZERO external dependencies — the whole DSP
is one inline gen~ codebox (no buffer~ names, no packages, nothing that can shadow or be
shadowed). plugin~ -> gen~ -> plugout~. Six clearly-labelled controls.

NOTE: built blind (no Max here). Structure + JSON are validated; the audio must be verified
in Live — see the companion runbook. Iterate by editing GEN_CODE and re-running.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amxd_lib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "devices", "_standalone")
OUT = os.path.join(OUTDIR, "Granular Delay.amxd")

APPVERSION = {"major": 9, "minor": 0, "revision": 8, "architecture": "x64", "modernui": 1}

# ---------------- gen~ DSP ----------------
GEN_CODE = r"""// Granular Delay — self-contained gen~ (no buffer~, no externals)
Param mix(35., min=0., max=100.);
Param delay(300., min=1., max=2000.);
Param grain(120., min=20., max=500.);
Param pitch(0., min=-24., max=24.);
Param feedback(30., min=0., max=95.);
Param spray(0., min=0., max=100.);

Data buf(960000);
n = dim(buf);
srms = samplerate / 1000.;

mixw  = slide(mix * 0.01, 1000, 1000);
dly   = slide(delay, 2000, 2000) * srms;
grs   = max(128., slide(grain, 2000, 2000) * srms);
fb    = min(0.95, slide(feedback * 0.01, 1000, 1000));
ratio = pow(2., slide(pitch, 500, 500) / 12.);
spr   = slide(spray * 0.01, 1000, 1000) * dly;

x = (in1 + in2) * 0.5;

History wp(0);
w = wp;

History fbprev(0);
poke(buf, x + tanh(fbprev * fb), w);

History ph(0);
inc = 1. / grs;
p1 = wrap(ph + inc, 0., 1.);
ph = p1;
p2 = wrap(p1 + 0.5, 0., 1.);

ng1 = p1 < inc;
ng2 = p2 < inc;

History o1(0);
History o2(0);
o1 = ng1 ? (noise() * 0.5 + 0.5) * spr : o1;
o2 = ng2 ? (noise() * 0.5 + 0.5) * spr : o2;

span = grs * ratio;
r1 = w - dly - o1 - (1. - p1) * span;
r2 = w - dly - o2 - (1. - p2) * span;

i1 = floor(r1); f1 = r1 - i1;
a1 = peek(buf, wrap(i1, 0, n));
b1 = peek(buf, wrap(i1 + 1, 0, n));
g1 = a1 + f1 * (b1 - a1);

i2 = floor(r2); f2 = r2 - i2;
a2 = peek(buf, wrap(i2, 0, n));
b2 = peek(buf, wrap(i2 + 1, 0, n));
g2 = a2 + f2 * (b2 - a2);

twopi = 6.28318530717959;
win1 = 0.5 - 0.5 * cos(p1 * twopi);
win2 = 0.5 - 0.5 * cos(p2 * twopi);

wet = g1 * win1 + g2 * win2;
fbprev = wet;

wp = wrap(w + 1., 0., n);

out1 = x * (1. - mixw) + wet * mixw;
out2 = out1;
"""

# control: (gen param name, label, min, max, default, unit)
CONTROLS = [
    ("mix", "Mix", 0., 100., 35., "%"),
    ("delay", "Delay", 1., 2000., 300., "ms"),
    ("grain", "Grain Size", 20., 500., 120., "ms"),
    ("pitch", "Pitch", -24., 24., 0., "st"),
    ("feedback", "Feedback", 0., 95., 30., "%"),
    ("spray", "Spray", 0., 100., 0., "%"),
]

_id = [0]
def nid():
    _id[0] += 1
    return f"obj-{_id[0]}"


def gen_subpatcher():
    in1, in2, cb, out1, out2 = "in1", "in2", "cb", "out1", "out2"
    boxes = [
        {"box": {"maxclass": "newobj", "text": "in 1", "id": in1, "numinlets": 0,
                 "numoutlets": 1, "outlettype": ["signal"], "patching_rect": [40, 40, 32, 22]}},
        {"box": {"maxclass": "newobj", "text": "in 2", "id": in2, "numinlets": 0,
                 "numoutlets": 1, "outlettype": ["signal"], "patching_rect": [80, 40, 32, 22]}},
        {"box": {"maxclass": "codebox", "code": GEN_CODE, "id": cb, "numinlets": 2,
                 "numoutlets": 2, "outlettype": ["signal", "signal"],
                 "patching_rect": [40, 80, 520, 520], "fontname": "Courier New", "fontsize": 12.0}},
        {"box": {"maxclass": "newobj", "text": "out 1", "id": out1, "numinlets": 1,
                 "numoutlets": 0, "patching_rect": [40, 620, 36, 22]}},
        {"box": {"maxclass": "newobj", "text": "out 2", "id": out2, "numinlets": 1,
                 "numoutlets": 0, "patching_rect": [84, 620, 36, 22]}},
    ]
    lines = [
        {"patchline": {"source": [in1, 0], "destination": [cb, 0]}},
        {"patchline": {"source": [in2, 0], "destination": [cb, 1]}},
        {"patchline": {"source": [cb, 0], "destination": [out1, 0]}},
        {"patchline": {"source": [cb, 1], "destination": [out2, 0]}},
    ]
    return {"fileversion": 1, "appversion": APPVERSION, "classnamespace": "dsp.gen",
            "rect": [0, 0, 640, 680], "boxes": boxes, "lines": lines}


def live_dial(param, label, lo, hi, default, unit, prect):
    bid = nid()
    box = {
        "maxclass": "live.dial",
        "id": bid,
        "numinlets": 1,
        "numoutlets": 2,
        "outlettype": ["", "float"],
        "parameter_enable": 1,
        "patching_rect": [20 + 60 * _id[0], 60, 44, 48],
        "presentation": 1,
        "presentation_rect": prect,
        "saved_attribute_attributes": {"valueof": {
            "parameter_longname": label,
            "parameter_shortname": label,
            "parameter_mmin": lo,
            "parameter_mmax": hi,
            "parameter_initial": [default],
            "parameter_initial_enable": 1,
            "parameter_type": 0,
            "parameter_unitstyle": 1,
        }},
        "varname": param + "_dial",
    }
    return bid, {"box": box}


def label_comment(text, prect):
    return {"box": {"maxclass": "comment", "text": text, "id": nid(),
                    "numinlets": 1, "numoutlets": 0, "presentation": 1,
                    "presentation_rect": prect, "patching_rect": [20, 320, 80, 18],
                    "fontsize": 9.0, "textjustification": 1}}


def build():
    boxes = []
    lines = []

    # audio I/O + gen~
    plugin = nid()
    boxes.append({"box": {"maxclass": "newobj", "text": "plugin~", "id": plugin,
                          "numinlets": 1, "numoutlets": 2, "outlettype": ["signal", "signal"],
                          "patching_rect": [40, 60, 60, 22]}})
    gen = nid()
    boxes.append({"box": {"maxclass": "newobj", "text": "gen~", "id": gen, "numinlets": 2,
                          "numoutlets": 2, "outlettype": ["signal", "signal"],
                          "patching_rect": [40, 360, 120, 22], "patcher": gen_subpatcher()}})
    plugout = nid()
    boxes.append({"box": {"maxclass": "newobj", "text": "plugout~", "id": plugout,
                          "numinlets": 2, "numoutlets": 0, "patching_rect": [40, 420, 64, 22]}})

    lines.append({"patchline": {"source": [plugin, 0], "destination": [gen, 0]}})
    lines.append({"patchline": {"source": [plugin, 1], "destination": [gen, 1]}})
    lines.append({"patchline": {"source": [gen, 0], "destination": [plugout, 0]}})
    lines.append({"patchline": {"source": [gen, 1], "destination": [plugout, 1]}})

    # title
    boxes.append({"box": {"maxclass": "comment", "text": "GRANULAR DELAY", "id": nid(),
                          "numinlets": 1, "numoutlets": 0, "presentation": 1,
                          "presentation_rect": [8.0, 6.0, 160.0, 20.0],
                          "patching_rect": [200, 20, 160, 20], "fontsize": 12.0,
                          "fontface": 1}})

    # 6 controls in a 3x2 grid
    cols = [12.0, 96.0, 180.0]
    rows = [34.0, 104.0]   # label y per row
    for i, (param, label, lo, hi, default, unit) in enumerate(CONTROLS):
        cx = cols[i % 3]
        ly = rows[i // 3]
        boxes.append(label_comment(label, [cx, ly, 76.0, 16.0]))
        did, dbox = live_dial(param, label, lo, hi, default, unit,
                              [cx + 16.0, ly + 16.0, 44.0, 48.0])
        boxes.append(dbox)
        msg = nid()
        boxes.append({"box": {"maxclass": "message", "text": f"{param} $1", "id": msg,
                              "numinlets": 2, "numoutlets": 1, "outlettype": [""],
                              "patching_rect": [200 + 70 * i, 120, 80, 20]}})
        lines.append({"patchline": {"source": [did, 0], "destination": [msg, 0]}})
        lines.append({"patchline": {"source": [msg, 0], "destination": [gen, 0]}})

    patcher = {
        "fileversion": 1,
        "appversion": APPVERSION,
        "classnamespace": "box",
        "rect": [80.0, 120.0, 640.0, 520.0],
        "openinpresentation": 1,
        "default_fontsize": 10.0,
        "default_fontname": "Arial",
        "gridsize": [8.0, 8.0],
        "boxes": boxes,
        "lines": lines,
        "is_mpe": 0,
    }
    return {"patcher": patcher}


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    obj = build()
    amxd_lib.build_amxd(obj, OUT, type_bytes=amxd_lib.TYPE_AUDIO_EFFECT)
    _, _, chk = amxd_lib.read(OUT)
    p = chk["patcher"]
    n_dials = sum(1 for b in p["boxes"] if b["box"].get("maxclass") == "live.dial")
    has_gen = any(b["box"].get("text") == "gen~" for b in p["boxes"])
    print(f"wrote {OUT}")
    print(f"  type={amxd_lib.TYPE_NAMES[amxd_lib.device_type(OUT)]}, gen~={has_gen}, "
          f"live.dials={n_dials}, JSON round-trip OK")


if __name__ == "__main__":
    main()
