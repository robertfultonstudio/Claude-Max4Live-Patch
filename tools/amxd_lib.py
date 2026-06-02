#!/usr/bin/env python3
"""
amxd_lib — minimal, byte-faithful reader/writer for Max for Live `.amxd` devices.

An .amxd file is:

    'ampf'  (4 bytes magic)
    version (4 bytes, little-endian, = 4)
    type    (4 bytes 4CC)  ->  'aaaa' Audio Effect | 'iiii' Instrument | 'mmmm' MIDI Effect
    'meta'  (4 bytes) + chunk-size(4 LE = 4) + meta-value(4 LE = 1)
    'ptch'  (4 bytes) + payload-size(4 LE)
    payload (UTF-8 JSON Max patcher, `payload-size` bytes, optional trailing NULs)

This module never re-orders or re-formats JSON keys destructively: it parses the
patcher to a Python object, lets a caller mutate it, then re-packs while preserving
the *original* header bytes (magic/version/type/meta) verbatim. Only the `ptch`
size field and the payload are rewritten. This matches what Max itself writes
(tab-indented, UTF-8) and what ppooll's own generator script produced.
"""
import json
import struct

MAGIC = b"ampf"

# Live device 4CC type codes (the 4 bytes at offset 8).
TYPE_AUDIO_EFFECT = b"aaaa"
TYPE_INSTRUMENT = b"iiii"
TYPE_MIDI_EFFECT = b"mmmm"

TYPE_NAMES = {
    b"aaaa": "Audio Effect",
    b"iiii": "Instrument",
    b"mmmm": "MIDI Effect",
}


class AmxdError(Exception):
    pass


def _find_ptch(data: bytes) -> int:
    idx = data.find(b"ptch")
    if idx < 0:
        raise AmxdError("no 'ptch' chunk found — not a valid .amxd")
    return idx


def read(path: str):
    """Return (raw_bytes, ptch_offset, patcher_dict)."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] != MAGIC:
        raise AmxdError(f"{path}: missing 'ampf' magic — not an .amxd")
    idx = _find_ptch(data)
    size = struct.unpack("<I", data[idx + 4 : idx + 8])[0]
    payload = data[idx + 8 : idx + 8 + size].rstrip(b"\x00")
    try:
        obj = json.loads(payload.decode("utf-8"))
    except UnicodeDecodeError:
        obj = json.loads(payload.decode("utf-8", errors="replace"))
    return data, idx, obj


def device_type(path: str) -> bytes:
    with open(path, "rb") as f:
        head = f.read(12)
    return head[8:12]


def serialize_payload(obj) -> bytes:
    """Serialize a patcher dict the way Max writes it: tab indent, UTF-8, trailing newline."""
    return json.dumps(obj, indent="\t", ensure_ascii=False).encode("utf-8") + b"\n"


def pack(original_bytes: bytes, ptch_offset: int, obj, new_type: bytes = None) -> bytes:
    """
    Re-pack a patcher dict into a valid .amxd, preserving the original header
    bytes (everything up to and including the 'ptch' tag). Optionally overrides
    the 4CC device type (4 bytes at offset 8).
    """
    header = bytearray(original_bytes[: ptch_offset + 4])  # through 'ptch' tag
    if new_type is not None:
        if len(new_type) != 4:
            raise AmxdError("device type must be 4 bytes")
        header[8:12] = new_type
    payload = serialize_payload(obj)
    return bytes(header) + struct.pack("<I", len(payload)) + payload


def repack_file(src_path: str, dst_path: str, mutate=None, new_type: bytes = None):
    """
    Read src_path, optionally mutate the patcher dict via `mutate(obj)->obj`,
    re-pack and write to dst_path. Returns the new patcher dict.
    Verifies the result round-trips (re-parses to an equal object).
    """
    data, idx, obj = read(src_path)
    if mutate is not None:
        obj = mutate(obj)
    blob = pack(data, idx, obj, new_type=new_type)
    with open(dst_path, "wb") as f:
        f.write(blob)
    # round-trip self-check
    _, _, check = read(dst_path)
    if json.dumps(check, sort_keys=True) != json.dumps(obj, sort_keys=True):
        raise AmxdError(f"{dst_path}: round-trip mismatch after repack")
    return obj


def build_amxd(obj, dst_path: str, type_bytes: bytes = TYPE_AUDIO_EFFECT):
    """Build a brand-new .amxd from a patcher dict (not derived from an existing device)."""
    import struct as _struct
    payload = serialize_payload(obj)
    header = (
        MAGIC
        + _struct.pack("<I", 4)
        + type_bytes
        + b"meta" + _struct.pack("<I", 4) + _struct.pack("<I", 1)
        + b"ptch" + _struct.pack("<I", len(payload))
    )
    with open(dst_path, "wb") as f:
        f.write(header + payload)
    _, _, check = read(dst_path)  # round-trip validation
    if json.dumps(check, sort_keys=True) != json.dumps(obj, sort_keys=True):
        raise AmxdError(f"{dst_path}: round-trip mismatch after build")
    return dst_path


if __name__ == "__main__":
    import sys

    d, i, o = read(sys.argv[1])
    print(f"type={device_type(sys.argv[1])!r} ({TYPE_NAMES.get(device_type(sys.argv[1]), '?')})")
    print(f"ptch@{i}  payload-objects={len(o['patcher'].get('boxes', []))} top-level boxes")
