#!/usr/bin/env python3
"""
Diagnostic: a minimal M4L audio effect = plugin~ -> gen~ (passthrough) -> plugout~.
No dials, no params. Purpose: isolate whether the gen~ codebox embedding + audio path
work at all. If THIS passes audio, the structure is fine and any silence in the granular
delay is a DSP-code bug; if this is also silent, the structure/embedding is the problem.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amxd_lib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "devices", "_standalone", "Passthrough Test (gen).amxd")
APPVERSION = {"major": 9, "minor": 0, "revision": 8, "architecture": "x64", "modernui": 1}

GEN_CODE = "// passthrough diagnostic\nout1 = in1;\nout2 = in2;\n"


def gen_sub():
    boxes = [
        {"box": {"maxclass": "newobj", "text": "in 1", "id": "in1", "numinlets": 0,
                 "numoutlets": 1, "outlettype": ["signal"], "patching_rect": [40, 40, 32, 22]}},
        {"box": {"maxclass": "newobj", "text": "in 2", "id": "in2", "numinlets": 0,
                 "numoutlets": 1, "outlettype": ["signal"], "patching_rect": [80, 40, 32, 22]}},
        {"box": {"maxclass": "codebox", "code": GEN_CODE, "id": "cb", "numinlets": 2,
                 "numoutlets": 2, "outlettype": ["signal", "signal"],
                 "patching_rect": [40, 80, 240, 120]}},
        {"box": {"maxclass": "newobj", "text": "out 1", "id": "out1", "numinlets": 1,
                 "numoutlets": 0, "patching_rect": [40, 220, 36, 22]}},
        {"box": {"maxclass": "newobj", "text": "out 2", "id": "out2", "numinlets": 1,
                 "numoutlets": 0, "patching_rect": [84, 220, 36, 22]}},
    ]
    lines = [
        {"patchline": {"source": ["in1", 0], "destination": ["cb", 0]}},
        {"patchline": {"source": ["in2", 0], "destination": ["cb", 1]}},
        {"patchline": {"source": ["cb", 0], "destination": ["out1", 0]}},
        {"patchline": {"source": ["cb", 1], "destination": ["out2", 0]}},
    ]
    return {"fileversion": 1, "appversion": APPVERSION, "classnamespace": "dsp.gen",
            "rect": [0, 0, 400, 300], "boxes": boxes, "lines": lines}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    boxes = [
        {"box": {"maxclass": "newobj", "text": "plugin~", "id": "obj-1", "numinlets": 1,
                 "numoutlets": 2, "outlettype": ["signal", "signal"], "patching_rect": [40, 60, 60, 22]}},
        {"box": {"maxclass": "newobj", "text": "gen~", "id": "obj-2", "numinlets": 2,
                 "numoutlets": 2, "outlettype": ["signal", "signal"],
                 "patching_rect": [40, 120, 100, 22], "patcher": gen_sub()}},
        {"box": {"maxclass": "newobj", "text": "plugout~", "id": "obj-3", "numinlets": 2,
                 "numoutlets": 0, "patching_rect": [40, 180, 64, 22]}},
        {"box": {"maxclass": "comment", "text": "Passthrough test: if you hear audio, the gen~ structure is OK.",
                 "id": "obj-4", "numinlets": 1, "numoutlets": 0, "presentation": 1,
                 "presentation_rect": [8.0, 8.0, 260.0, 34.0], "patching_rect": [160, 60, 240, 34]}},
    ]
    lines = [
        {"patchline": {"source": ["obj-1", 0], "destination": ["obj-2", 0]}},
        {"patchline": {"source": ["obj-1", 1], "destination": ["obj-2", 1]}},
        {"patchline": {"source": ["obj-2", 0], "destination": ["obj-3", 0]}},
        {"patchline": {"source": ["obj-2", 1], "destination": ["obj-3", 1]}},
    ]
    patcher = {"fileversion": 1, "appversion": APPVERSION, "classnamespace": "box",
               "rect": [80.0, 120.0, 480.0, 300.0], "openinpresentation": 1,
               "default_fontsize": 10.0, "default_fontname": "Arial",
               "gridsize": [8.0, 8.0], "boxes": boxes, "lines": lines, "is_mpe": 0}
    amxd_lib.build_amxd({"patcher": patcher}, OUT, type_bytes=amxd_lib.TYPE_AUDIO_EFFECT)
    print("wrote", OUT, "| type", amxd_lib.TYPE_NAMES[amxd_lib.device_type(OUT)])


if __name__ == "__main__":
    main()
