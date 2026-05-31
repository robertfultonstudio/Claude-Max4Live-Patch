#!/usr/bin/env python3
"""Generate per-act .amxd devices from live.ppooll.amxd template."""
import json, os, re, struct, sys, shutil

SRC = '/Users/RF/Desktop/ppooll/devices/live.ppooll.amxd'
ACTS_DIR = '/Users/RF/Desktop/ppooll/patchers/ppooll.acts'
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else '/tmp/ppooll/build/out'

os.makedirs(OUT_DIR, exist_ok=True)

# --- read source ---
with open(SRC, 'rb') as f:
    src_bytes = f.read()

# header = ampf + ver(4) + type(4) + meta-chunk(4+4+4) + ptch tag(4) + ptch size(4)
# patcher payload follows. trailing nulls may exist.
HEADER_LEN = 32
src_header = src_bytes[:HEADER_LEN]
src_patch = src_bytes[HEADER_LEN:].rstrip(b'\x00')

# Validate header
assert src_header[:4] == b'ampf', 'not amxd'
device_type = src_header[8:12]  # iiii / aaaa / mmmm

# parse json
template = json.loads(src_patch.decode())

# --- helpers ---
def list_acts():
    res = []
    for f in sorted(os.listdir(ACTS_DIR)):
        if not f.endswith('.maxpat'):
            continue
        if f.startswith('_'):
            continue
        name = f[:-len('.maxpat')]
        # require actmaker registration
        try:
            with open(os.path.join(ACTS_DIR, f)) as fp:
                txt = fp.read()
        except:
            continue
        if re.search(r'actmaker\s+' + re.escape(name), txt):
            res.append(name)
    return res

def safe_filename(actname):
    # Live filename: live.<actname>.amxd
    # sanitize: keep @ # etc removed for Live compatibility
    s = actname
    # Live's preset browser does fine with most chars; '@' is OK in macOS but spaces are risky
    s = s.replace(' ', '_')
    return f'live.ppooll.{s}.amxd'

def make_amxd_for(actname):
    # deep-copy template
    d = json.loads(json.dumps(template))
    p = d['patcher']
    # find env subpatcher
    env_sub = None
    for b in p['boxes']:
        box = b.get('box', {})
        if box.get('varname') == 'LIVE_PPOOLL_ENVIRONMENT':
            env_sub = box['patcher']
            break
    assert env_sub, 'no env subpatcher'

    new_boxes = []
    for b in env_sub['boxes']:
        box = b.get('box', {})
        # KEEP LFFO
        if False and box.get("varname") == "LFFO1":
            continue
        # replace demosound bpatcher
        if box.get('varname') == 'demosound@1':
            box['text'] = f'{actname}.maxpat'
            box['varname'] = f'{actname}1'
            # patching_rect kept as-is so layout stays
        new_boxes.append(b)
    env_sub['boxes'] = new_boxes

    return d

def pack_amxd(json_data, type_bytes=device_type):
    payload = json.dumps(json_data, separators=(', ', ' : ')).encode()
    # Match Max's formatting more closely: use indent w/ tabs
    payload = json.dumps(json_data, indent='\t').encode() + b'\n'
    # Header: ampf(4) + ver(4 LE) + type(4) + 'meta' + chunk_size(4 LE = 4) + meta_val(4 LE = 1) + 'ptch' + size(4 LE)
    header = (
        b'ampf' +
        struct.pack('<I', 4) +
        type_bytes +
        b'meta' +
        struct.pack('<I', 4) +
        struct.pack('<I', 1) +
        b'ptch' +
        struct.pack('<I', len(payload))
    )
    return header + payload

# --- run ---
acts = list_acts()
print(f'Generating {len(acts)} devices into {OUT_DIR}')
for i, a in enumerate(acts):
    d = make_amxd_for(a)
    blob = pack_amxd(d)
    out_path = os.path.join(OUT_DIR, safe_filename(a))
    with open(out_path, 'wb') as f:
        f.write(blob)
    if i < 3 or i == len(acts)-1:
        print(f'  -> {safe_filename(a)} ({len(blob)} bytes)')
print('Done.')
