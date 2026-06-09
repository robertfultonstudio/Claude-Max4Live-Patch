#!/usr/bin/env python3
"""
Build the "Spectral Drone Composer" — a self-contained Max for Live MIDI device that
generates MIDI clips tuned to the JUST-INTONATION harmonic spectrum of a fundamental,
for drone / spectral composition, plus an EXACT-JI SuperCollider `.scd` export.

This is the Max-for-Live reframing of an Ableton-Extensions-SDK idea: this repository is
an M4L device suite (it has NO Extensions SDK / `api/` / `.ablx` toolchain), so the device
is built the repo's proven way — Python emits the patcher JSON + a companion `js` engine,
and `amxd_lib` packs a round-trip-validated `.amxd`. It is NOT an `.ablx`.

------------------------------------------------------------------------------------------
HONEST DETUNE STRATEGY  ——  ACTIVE = #3 (temperato + cents map).   WHY:
  The Live Object Model has NO per-note pitch-bend / micro-tuning field. `add_new_notes`
  accepts only pitch / start_time / duration / velocity / mute (verified against the
  Cycling '74 LOM docs + community reference; MPE/microtuning is not writable to a clip,
  and is excluded from MIDI export). So Strategy #1 (per-note bend in one clip) and a clean
  Strategy #2 (clip-baked channel bend envelopes) are NOT available via the LOM.

  Therefore the generated CLIP notes are nearest-12-TET. TRUE just intonation is delivered
  EXACTLY, with no MIDI compromise, in two always-written side files:
    * spectrum_<f0>.scd     — SuperCollider drone, fn = n*f0 (no quantization), amps ~ 1/n,
                              slow fades, on a LinkClock (Ableton Link). Runs the real JI.
    * detune_map_<f0>.txt   — exact cents per partial, to apply via Live 12 "Tuning Systems",
                              an MPE synth, a Sub 37, or SuperCollider.
  The clip notes are NEVER presented as JI.  (Built blind — no Max here; verify in Live.)
------------------------------------------------------------------------------------------

Math (exact, no hidden approximations):
    fn    = n * f0
    m     = 69 + 12*log2(fn/440)
    note  = round(m)
    cents = (m - round(m)) * 100        # e.g. 7th partial -31.2c, 11th -48.7c

Run:  python3 tools/make_spectral_drone.py
Outputs into devices/_standalone/:  the .amxd, spectral_drone_composer.js,
spectrum_<tag>.scd, detune_map_<tag>.txt  (all round-trip / sanity validated here).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amxd_lib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "devices", "_standalone")
DEVICE_NAME = "Spectral Drone Composer"
JS_NAME = "spectral_drone_composer.js"

APPVERSION = {"major": 9, "minor": 0, "revision": 8, "architecture": "x64", "modernui": 1}

# ---- defaults (mirrored as editable constants at the top of the .js engine) ----
DEF = dict(
    f0_hz=32.703,        # C1 — cello open-C, 12-TET reference
    partial_from=1,
    partial_to=16,
    selection="all",     # all | odd | even | primes | "1 3 5 7"
    duration_beats=64,   # long drone
    stagger_beats=4,     # Radigue-style staggered entries (0 = unison)
    velocity_curve="1/n",
    register_fold=False,
    max_midi=96,
    tempo_bps=2.0,       # .scd LinkClock tempo (beats/sec); 2.0 = 120 BPM
)

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


# ============================ shared math core ============================
def note_name(midi):
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def is_prime(k):
    if k < 2:
        return False
    d = 2
    while d * d <= k:
        if k % d == 0:
            return False
        d += 1
    return True


def select_n(n, selection):
    if selection == "all":
        return True
    if selection == "odd":
        return n % 2 == 1
    if selection == "even":
        return n % 2 == 0
    if selection == "primes":
        return is_prime(n)
    return n in {int(x) for x in selection.split() if x.strip().isdigit()}


def partial_table(f0, partial_from, partial_to, selection="all",
                  velocity_curve="1/n", register_fold=False, max_midi=96):
    """Return the list of partial rows (the single source of truth for every output)."""
    nsel = [n for n in range(partial_from, partial_to + 1) if select_n(n, selection)]
    count = len(nsel)
    rows = []
    for idx, n in enumerate(nsel):
        fn = n * f0
        m = 69 + 12 * math.log2(fn / 440.0)
        near = round(m)
        while register_fold and near > max_midi:
            near -= 12
        near = max(0, min(127, near))
        cents = (m - round(m)) * 100.0
        vel = 100 if velocity_curve == "equal" else max(10, round(100.0 / n))
        amp = 1.0 / n
        pan = (idx / (count - 1)) * 1.2 - 0.6 if count > 1 else 0.0
        rows.append(dict(n=n, freq=fn, midi=near, name=note_name(near),
                         cents=cents, vel=vel, amp=amp, pan=pan, idx=idx))
    return rows


def f0_tag(f0):
    m = round(69 + 12 * math.log2(f0 / 440.0))
    return note_name(m).replace("#", "s") + "_" + f"{f0:.3f}".replace(".", "p") + "Hz"


# ============================ .scd renderer ============================
def scd_text(f0, rows, stagger_beats, tempo_bps, selection, partial_from, partial_to):
    part_lines = "\n".join(
        f"        [{r['n']}, {r['freq']:.6f}, {r['amp']:.6f}, {r['pan']:.6f}],"
        for r in rows
    )
    return f"""// spectrum_{f0_tag(f0)}.scd  —  EXACT just-intonation spectral drone (auto-generated)
// Fundamental f0 = {f0:.3f} Hz   |   partials {partial_from}..{partial_to}  (selection: {selection})
//
// PURE JI: each voice is a sine at fn = n*f0  — NO MIDI quantization, no cent rounding.
// Amplitudes ~ 1/n (natural spectral roll-off). Slow fades. LinkClock locks SC to Ableton Link.
// This file is the TRUE just-intonation rendering; the Live clip is only 12-TET nearest.
//
// HOW TO RUN (SuperCollider):
//   1) evaluate the (...) block below  (place cursor inside, Cmd/Ctrl + Enter)
//   2) it boots the server, defines the drone, and stacks the partials (staggered entries)
//   3) evaluate the STOP line at the bottom for a slow release.

(
s.waitForBoot({{
    SynthDef(\\spectralDrone, {{ |freq=110, amp=0.1, gate=1, fadeIn=20, fadeOut=25, pan=0|
        var env = EnvGen.kr(Env.asr(fadeIn, 1, fadeOut), gate, doneAction: 2);
        var sig = SinOsc.ar(freq) * amp;
        Out.ar(0, Pan2.ar(sig * env, pan));
    }}).add;
    s.sync;

    ~f0      = {f0:.6f};
    ~master  = 0.14;                 // headroom: sum of 1/n can exceed 1
    ~stagger = {stagger_beats};                  // beats between partial entries (Radigue accumulation)
    ~partials = [
        // [ n, freqHz (= n*f0, exact), amp (1/n), pan ]
{part_lines}
    ];
    ~clock  = LinkClock({tempo_bps}).latency_(0.2);   // beats/sec; enables Ableton Link
    ~voices = ();

    ~clock.schedAbs(~clock.beats.ceil, {{
        ~partials.do {{ |row, i|
            ~clock.sched(i * ~stagger, {{
                var n = row[0], freq = row[1], amp = row[2] * ~master, pan = row[3];
                ~voices[n] = Synth(\\spectralDrone, [\\freq, freq, \\amp, amp, \\pan, pan, \\fadeIn, 20]);
                nil
            }});
        }};
        nil
    }});
    ("spectralDrone: " ++ ~partials.size ++ " partials scheduled on LinkClock @ f0=" ++ ~f0 ++ " Hz").postln;
}});
)

// STOP — slow release of every voice:
// ( ~voices.do {{ |syn| syn.set(\\gate, 0) }}; ~voices = (); )
"""


# ============================ detune map renderer ============================
def map_text(f0, rows, selection, partial_from, partial_to):
    head = (
        f"# detune_map_{f0_tag(f0)}.txt  —  EXACT just-intonation cent offsets (auto-generated)\n"
        f"# f0 = {f0:.3f} Hz   partials {partial_from}..{partial_to}  (selection: {selection})\n"
        f"#\n"
        f"# The Live clip plays the 'nearMIDI' column (12-TET). To hear TRUE JI, apply the\n"
        f"# 'cents' offset to each note in an MPE synth / Live 12 Tuning System / Sub 37 / SC,\n"
        f"# or just run the companion spectrum_{f0_tag(f0)}.scd.\n"
        f"#\n"
        f"# n   freqHz       nearMIDI  note   cents     velocity\n"
    )
    body = "\n".join(
        f"{r['n']:<4}{r['freq']:<13.4f}{r['midi']:<10}{r['name']:<7}{r['cents']:<+10.2f}{r['vel']}"
        for r in rows
    )
    return head + body + "\n"


# ============================ the embedded js engine ============================
JS_SOURCE = r"""// spectral_drone_composer.js  —  engine for the "Spectral Drone Composer" M4L device.
//
// Generates MIDI clips on the JI harmonic spectrum of a fundamental, and ALWAYS writes an
// exact-JI SuperCollider .scd + a cents map.  Keep this math in sync with its build-time
// twin, tools/make_spectral_drone.py.
//
// ACTIVE DETUNE STRATEGY = #3 (temperato + cents map).  WHY:
//   The Live Object Model has NO per-note pitch-bend / micro-tuning field — add_new_notes
//   takes only pitch/start_time/duration/velocity/mute. So the generated CLIP notes are
//   nearest-12-TET.  TRUE just intonation is written exactly to:
//     - spectrum_<f0>.scd   (SuperCollider, fn = n*f0, no quantization)
//     - detune_map_<f0>.txt (cents per partial: Live 12 Tuning Systems / MPE synth / Sub 37 / SC)
//   The clip notes are NEVER treated as JI.   (Built blind — verify in Live.)

autowatch = 1;
inlets = 1;
outlets = 1;

// ---------------- editable constants (top of file, per spec) ----------------
var F0_HZ            = 32.703;   // fundamental (C1 — cello open-C, 12-TET reference)
var F0_MIDI          = -1;       // alt: if >= 0, overrides F0_HZ  =>  440 * 2^((m-69)/12)
var PARTIAL_FROM     = 1;
var PARTIAL_TO       = 16;
var SELECTION        = "all";    // "all" | "odd" | "even" | "primes" | "1 3 5 7" (space list)
var DURATION_BEATS   = 64;       // long drone
var STAGGER_BEATS    = 4;        // staggered entries (0 = unison attack)
var VELOCITY_CURVE   = "1/n";    // "1/n" | "equal"
var REGISTER_FOLD    = 0;        // 1 = fold partials above MAX_MIDI down by octaves
var MAX_MIDI         = 96;
var BEND_RANGE       = 2;        // st — declared for the downstream synth (NOT written to clip)
var LAYOUT           = "clip";   // "clip" = one clip, staggered notes | "tracks" = one track/partial
var EXPORT_DIR       = "";       // absolute folder for .scd/.txt ; "" => Max default dir
var USE_LEGACY_NOTES = 0;        // 0 = add_new_notes (Live 11+) ; 1 = set_notes/note/done (older)
var TEMPO_BPS        = 2.0;      // .scd LinkClock tempo (beats/sec) ; 2.0 = 120 BPM
// ---------------------------------------------------------------------------

function log2(x)  { return Math.log(x) / Math.LN2; }
function isPrime(k){ if (k < 2) return false; for (var d = 2; d * d <= k; d++) if (k % d === 0) return false; return true; }
function noteName(m){
    var N = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"];
    return N[((m % 12) + 12) % 12] + (Math.floor(m / 12) - 1);
}
function pad(v, w){ var s = "" + v; while (s.length < w) s = " " + s; return s; }
function fundamental(){ return (F0_MIDI >= 0) ? 440 * Math.pow(2, (F0_MIDI - 69) / 12) : F0_HZ; }

// ---- message inlets: live UI / patch wiring set these, then 'bang' generates ----
function f0(v)        { F0_HZ = v; F0_MIDI = -1; }
function f0midi(v)    { F0_MIDI = v; }
function pfrom(v)     { PARTIAL_FROM = Math.max(1, Math.round(v)); }
function pto(v)       { PARTIAL_TO = Math.max(1, Math.round(v)); }
function dur(v)       { DURATION_BEATS = Math.max(0.25, v); }
function stagger(v)   { STAGGER_BEATS = Math.max(0, v); }
function velcurve(s)  { VELOCITY_CURVE = (s == "equal") ? "equal" : "1/n"; }
function fold(v)      { REGISTER_FOLD = v ? 1 : 0; }
function layout(s)    { LAYOUT = (s == "tracks") ? "tracks" : "clip"; }
function selection()  { SELECTION = arrayfromargs(arguments).join(" "); }
function exportdir()  { EXPORT_DIR = arrayfromargs(arguments).join(" "); }
function legacy(v)    { USE_LEGACY_NOTES = v ? 1 : 0; }

function selectN(n){
    if (SELECTION == "all")    return true;
    if (SELECTION == "odd")    return (n % 2) == 1;
    if (SELECTION == "even")   return (n % 2) == 0;
    if (SELECTION == "primes") return isPrime(n);
    var parts = SELECTION.split(/\s+/);
    for (var i = 0; i < parts.length; i++) if (parseInt(parts[i], 10) === n) return true;
    return false;
}

function partialTable(){
    var f0v = fundamental();
    var nsel = [];
    for (var n = PARTIAL_FROM; n <= PARTIAL_TO; n++) if (selectN(n)) nsel.push(n);
    var count = nsel.length;
    var rows = [];
    for (var idx = 0; idx < count; idx++){
        var nn = nsel[idx];
        var fn = nn * f0v;
        var m  = 69 + 12 * log2(fn / 440);
        var near = Math.round(m);
        while (REGISTER_FOLD && near > MAX_MIDI) near -= 12;
        if (near < 0) near = 0;
        if (near > 127) near = 127;
        var cents = (m - Math.round(m)) * 100;
        var vel = (VELOCITY_CURVE == "equal") ? 100 : Math.max(10, Math.round(100 / nn));
        var pan = (count > 1) ? (idx / (count - 1)) * 1.2 - 0.6 : 0.0;
        rows.push({ n: nn, freq: fn, midi: near, name: noteName(near),
                    cents: cents, vel: vel, amp: 1.0 / nn, pan: pan, idx: idx });
    }
    return rows;
}

// ------------------------------ entry point ------------------------------
function bang(){ generate(); }
function generate(){
    var rows = partialTable();
    if (rows.length === 0){ error("Spectral Drone: no partials selected\n"); return; }
    postTable(rows);
    try {
        if (LAYOUT == "tracks") generateTracks(rows); else generateClip(rows);
    } catch (e) {
        error("Spectral Drone: clip generation failed — " + e + "\n");
    }
    writeFile("spectrum_" + tag() + ".scd", scdText(rows));
    writeFile("detune_map_" + tag() + ".txt", mapText(rows));
    post("Spectral Drone: done. Strategy #3 — clips are 12-TET nearest; TRUE JI is in the .scd + cents map.\n\n");
}

// ---- one clip on this device's track, notes staggered (default) ----
function generateClip(rows){
    var track = new LiveAPI("this_device canonical_parent");
    var base  = track.unquotedpath;                 // e.g. "live_set tracks 2"
    var nSlots = track.getcount("clip_slots");
    var slot = -1;
    for (var s = 0; s < nSlots; s++){
        var cs = new LiveAPI(base + " clip_slots " + s);
        if (parseInt(cs.get("has_clip"), 10) === 0){ slot = s; break; }
    }
    if (slot < 0){ error("Spectral Drone: no empty clip slot on this track — add a scene.\n"); return; }
    var total = STAGGER_BEATS * (rows.length - 1) + DURATION_BEATS;
    if (total < 0.25) total = 0.25;
    var cs = new LiveAPI(base + " clip_slots " + slot);
    cs.call("create_clip", total);
    var clip = new LiveAPI(base + " clip_slots " + slot + " clip");
    var notes = [];
    for (var i = 0; i < rows.length; i++){
        notes.push({ pitch: rows[i].midi, start_time: rows[i].idx * STAGGER_BEATS,
                     duration: DURATION_BEATS, velocity: rows[i].vel, mute: 0 });
    }
    addNotes(clip, notes);
    clip.set("name", "JI spectrum " + fundamental().toFixed(2) + "Hz (12-TET)");
    post("  wrote clip: " + base + " clip_slots " + slot + "  (" + notes.length + " partials, 12-TET nearest)\n");
}

// ---- one MIDI track per partial (advanced: route each to a synth tuned by the cents map) ----
function generateTracks(rows){
    var ls = new LiveAPI("live_set");
    for (var i = 0; i < rows.length; i++){
        var before = ls.getcount("tracks");
        ls.call("create_midi_track", -1);
        var tp = "live_set tracks " + before;
        var t = new LiveAPI(tp);
        var sign = (rows[i].cents >= 0) ? "+" : "";
        t.set("name", "P" + rows[i].n + " " + rows[i].name + " " + sign + rows[i].cents.toFixed(1) + "c");
        var cs = new LiveAPI(tp + " clip_slots 0");
        cs.call("create_clip", Math.max(0.25, DURATION_BEATS));
        var clip = new LiveAPI(tp + " clip_slots 0 clip");
        addNotes(clip, [{ pitch: rows[i].midi, start_time: 0, duration: DURATION_BEATS,
                          velocity: rows[i].vel, mute: 0 }]);
    }
    post("  created " + rows.length + " partial tracks — route each to a synth tuned by detune_map for TRUE JI.\n");
}

function addNotes(clip, notes){
    if (USE_LEGACY_NOTES){                          // older API (Live 9/10; deprecated in 11+)
        clip.call("set_notes");
        clip.call("notes", notes.length);
        for (var i = 0; i < notes.length; i++){
            var nt = notes[i];
            clip.call("note", nt.pitch, nt.start_time, nt.duration, nt.velocity, nt.mute);
        }
        clip.call("done");
    } else {                                        // modern API (Live 11+)
        var d = new Dict();
        d.parse(JSON.stringify({ notes: notes }));
        clip.call("add_new_notes", d);
    }
}

// ------------------------------ file exports ------------------------------
function tag(){
    var f0v = fundamental();
    var m = Math.round(69 + 12 * log2(f0v / 440));
    return noteName(m).replace("#", "s") + "_" + f0v.toFixed(3).replace(".", "p") + "Hz";
}
function resolvePath(fname){
    if (EXPORT_DIR && EXPORT_DIR.length){
        var sep = (EXPORT_DIR.charAt(EXPORT_DIR.length - 1) == "/") ? "" : "/";
        return EXPORT_DIR + sep + fname;
    }
    return fname;                                   // Max default search dir
}
function writeFile(fname, content){
    var path = resolvePath(fname);
    var f = new File(path, "write", "TEXT");
    if (!f.isopen){ error("Spectral Drone: cannot open for write: " + path + "\n"); return; }
    f.writestring(content);
    f.close();
    post("  wrote " + f.foldername + f.filename + "\n");
}

function scdText(rows){
    var f0v = fundamental();
    var L = [];
    L.push("// spectrum_" + tag() + ".scd  —  EXACT just-intonation spectral drone (auto-generated)");
    L.push("// f0 = " + f0v.toFixed(3) + " Hz | partials " + PARTIAL_FROM + ".." + PARTIAL_TO + " (selection: " + SELECTION + ")");
    L.push("// PURE JI: each voice = sine at fn = n*f0 (no MIDI quantization). Amps ~ 1/n. LinkClock = Ableton Link.");
    L.push("// Evaluate the (...) block; evaluate the STOP line for a slow release.");
    L.push("");
    L.push("(");
    L.push("s.waitForBoot({");
    L.push("    SynthDef(\\spectralDrone, { |freq=110, amp=0.1, gate=1, fadeIn=20, fadeOut=25, pan=0|");
    L.push("        var env = EnvGen.kr(Env.asr(fadeIn, 1, fadeOut), gate, doneAction: 2);");
    L.push("        var sig = SinOsc.ar(freq) * amp;");
    L.push("        Out.ar(0, Pan2.ar(sig * env, pan));");
    L.push("    }).add;");
    L.push("    s.sync;");
    L.push("");
    L.push("    ~f0      = " + f0v.toFixed(6) + ";");
    L.push("    ~master  = 0.14;");
    L.push("    ~stagger = " + STAGGER_BEATS + ";");
    L.push("    ~partials = [");
    for (var i = 0; i < rows.length; i++){
        var r = rows[i];
        L.push("        [" + r.n + ", " + r.freq.toFixed(6) + ", " + r.amp.toFixed(6) + ", " + r.pan.toFixed(6) + "],");
    }
    L.push("    ];");
    L.push("    ~clock  = LinkClock(" + TEMPO_BPS + ").latency_(0.2);");
    L.push("    ~voices = ();");
    L.push("    ~clock.schedAbs(~clock.beats.ceil, {");
    L.push("        ~partials.do { |row, i|");
    L.push("            ~clock.sched(i * ~stagger, {");
    L.push("                var n = row[0], freq = row[1], amp = row[2] * ~master, pan = row[3];");
    L.push("                ~voices[n] = Synth(\\spectralDrone, [\\freq, freq, \\amp, amp, \\pan, pan, \\fadeIn, 20]);");
    L.push("                nil");
    L.push("            });");
    L.push("        };");
    L.push("        nil");
    L.push("    });");
    L.push("});");
    L.push(")");
    L.push("");
    L.push("// STOP: ( ~voices.do { |syn| syn.set(\\gate, 0) }; ~voices = (); )");
    return L.join("\n") + "\n";
}

function mapText(rows){
    var f0v = fundamental();
    var L = [];
    L.push("# detune_map_" + tag() + ".txt  —  EXACT JI cent offsets (auto-generated)");
    L.push("# f0 = " + f0v.toFixed(3) + " Hz | partials " + PARTIAL_FROM + ".." + PARTIAL_TO + " (selection: " + SELECTION + ")");
    L.push("# The Live clip plays 'nearMIDI' (12-TET). Apply 'cents' in an MPE synth / Live 12 Tuning System / Sub 37 / SC.");
    L.push("# n   freqHz       nearMIDI  note   cents     velocity");
    for (var i = 0; i < rows.length; i++){
        var r = rows[i];
        var sign = (r.cents >= 0) ? "+" : "";
        L.push(pad(r.n, 4) + pad(r.freq.toFixed(4), 13) + pad(r.midi, 9) + "  " + pad(r.name, 5) + "  " + pad(sign + r.cents.toFixed(2), 8) + "  " + r.vel);
    }
    return L.join("\n") + "\n";
}

function postTable(rows){
    post("\n=== Spectral Drone Composer — JI partial table ===\n");
    post("f0 = " + fundamental().toFixed(3) + " Hz   partials " + PARTIAL_FROM + ".." + PARTIAL_TO + "  (selection: " + SELECTION + ")\n");
    post(" n    freq(Hz)   MIDI note   cents   vel\n");
    for (var i = 0; i < rows.length; i++){
        var r = rows[i];
        var sign = (r.cents >= 0) ? "+" : "";
        post(pad(r.n, 2) + "   " + pad(r.freq.toFixed(3), 9) + "   " + pad(r.midi, 3) + "  " + pad(r.name, 4) + "   " + pad(sign + r.cents.toFixed(1), 6) + "  " + pad(r.vel, 4) + "\n");
    }
    post("Active strategy: #3  (clip = 12-TET nearest;  TRUE JI -> spectrum_*.scd + detune_map_*.txt)\n");
}
"""


# ============================ .amxd patcher builder ============================
_id = [0]
def nid():
    _id[0] += 1
    return f"obj-{_id[0]}"


def comment(text, prect, fontsize=9.0, bold=False, just=0):
    box = {"maxclass": "comment", "text": text, "id": nid(),
           "numinlets": 1, "numoutlets": 0, "presentation": 1,
           "presentation_rect": prect, "patching_rect": [20, 320, prect[2], prect[3]],
           "fontsize": fontsize, "textjustification": just}
    if bold:
        box["fontface"] = 1
    return {"box": box}


def live_numbox(varname, label, lo, hi, default, prect, is_int=False):
    bid = nid()
    box = {
        "maxclass": "live.numbox", "id": bid,
        "numinlets": 1, "numoutlets": 2, "outlettype": ["", "float"],
        "parameter_enable": 1, "presentation": 1, "presentation_rect": prect,
        "patching_rect": [20 + 70 * _id[0] % 400, 60, 50, 15],
        "saved_attribute_attributes": {"valueof": {
            "parameter_longname": label, "parameter_shortname": label,
            "parameter_mmin": lo, "parameter_mmax": hi,
            "parameter_initial": [default], "parameter_initial_enable": 1,
            "parameter_type": 0,
            "parameter_unitstyle": 0 if not is_int else 1,
        }},
        "varname": varname,
    }
    return bid, {"box": box}


def msg(text, patch_rect):
    bid = nid()
    return bid, {"box": {"maxclass": "message", "text": text, "id": bid,
                         "numinlets": 2, "numoutlets": 1, "outlettype": [""],
                         "patching_rect": patch_rect}}


def newobj(text, patch_rect, ins, outs, outlettype=None):
    bid = nid()
    box = {"maxclass": "newobj", "text": text, "id": bid,
           "numinlets": ins, "numoutlets": outs, "patching_rect": patch_rect}
    if outlettype is not None:
        box["outlettype"] = outlettype
    return bid, {"box": box}


def build_patcher():
    boxes, lines = [], []

    # --- title + honesty strip (presentation) ---
    boxes.append(comment("SPECTRAL DRONE COMPOSER", [8.0, 6.0, 220.0, 20.0], 12.0, bold=True))
    boxes.append(comment("JI harmonic-spectrum drone clip generator", [8.0, 24.0, 260.0, 16.0], 9.0))

    # --- Generate button (live.button -> bang) ---
    btn = nid()
    boxes.append({"box": {"maxclass": "live.button", "id": btn,
                          "numinlets": 1, "numoutlets": 1, "outlettype": ["bang"],
                          "parameter_enable": 0, "presentation": 1,
                          "presentation_rect": [300.0, 8.0, 30.0, 30.0],
                          "patching_rect": [40, 120, 24, 24]}})
    boxes.append(comment("Generate", [300.0, 40.0, 60.0, 14.0], 8.0))

    # --- the js engine ---
    js = nid()
    boxes.append({"box": {"maxclass": "newobj", "text": "js " + JS_NAME, "id": js,
                          "numinlets": 1, "numoutlets": 1, "outlettype": [""],
                          "patching_rect": [40, 200, 200, 22]}})
    lines.append({"patchline": {"source": [btn, 0], "destination": [js, 0]}})

    # --- parameter numboxes (UI -> message -> js) ---
    params = [
        ("p_f0",      "f0 (Hz)",   1.0, 8000.0, DEF["f0_hz"],          "f0 $1",      False),
        ("p_from",    "from",      1.0, 64.0,   DEF["partial_from"],   "pfrom $1",   True),
        ("p_to",      "to",        1.0, 64.0,   DEF["partial_to"],     "pto $1",     True),
        ("p_dur",     "dur(beats)",0.25, 512.0, DEF["duration_beats"], "dur $1",     False),
        ("p_stagger", "stagger",   0.0, 64.0,   DEF["stagger_beats"],  "stagger $1", False),
    ]
    x = 8.0
    msg_y = 150
    for i, (vn, label, lo, hi, dflt, m, is_int) in enumerate(params):
        boxes.append(comment(label, [x, 44.0, 64.0, 13.0], 8.0))
        did, dbox = live_numbox(vn, label, lo, hi, dflt, [x, 58.0, 50.0, 15.0], is_int)
        boxes.append(dbox)
        mid, mbox = msg(m, [40 + 70 * i, msg_y, 80, 20])
        boxes.append(mbox)
        lines.append({"patchline": {"source": [did, 0], "destination": [mid, 0]}})
        lines.append({"patchline": {"source": [mid, 0], "destination": [js, 0]}})
        x += 66.0

    # --- MIDI passthrough (well-behaved MIDI Effect) ---
    mi, mibox = newobj("midiin", [400, 120, 48, 22], 1, 1, ["int"])
    mo, mobox = newobj("midiout", [400, 200, 54, 22], 1, 0)
    boxes.append(mibox)
    boxes.append(mobox)
    lines.append({"patchline": {"source": [mi, 0], "destination": [mo, 0]}})

    # --- honesty note (presentation) ---
    boxes.append(comment(
        "Strategy #3: clips = nearest 12-TET (the Live API has no per-note JI tuning). "
        "TRUE just intonation is written to spectrum_<f0>.scd + detune_map_<f0>.txt. "
        "Built blind — verify in Live.",
        [8.0, 78.0, 332.0, 46.0], 8.0))

    patcher = {
        "fileversion": 1, "appversion": APPVERSION, "classnamespace": "box",
        "rect": [80.0, 120.0, 560.0, 360.0], "openinpresentation": 1,
        "default_fontsize": 10.0, "default_fontname": "Arial",
        "gridsize": [8.0, 8.0], "boxes": boxes, "lines": lines, "is_mpe": 0,
    }
    return {"patcher": patcher}


# ============================ main ============================
def main():
    os.makedirs(OUTDIR, exist_ok=True)
    f0 = DEF["f0_hz"]
    rows = partial_table(f0, DEF["partial_from"], DEF["partial_to"], DEF["selection"],
                         DEF["velocity_curve"], DEF["register_fold"], DEF["max_midi"])

    # 1) the .amxd device (MIDI Effect)
    amxd_path = os.path.join(OUTDIR, DEVICE_NAME + ".amxd")
    amxd_lib.build_amxd(build_patcher(), amxd_path, type_bytes=amxd_lib.TYPE_MIDI_EFFECT)

    # 2) the js engine
    js_path = os.path.join(OUTDIR, JS_NAME)
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(JS_SOURCE)

    # 3) exact-JI side files for the default f0 (verified artifacts, independent of Live)
    tag = f0_tag(f0)
    scd_path = os.path.join(OUTDIR, f"spectrum_{tag}.scd")
    map_path = os.path.join(OUTDIR, f"detune_map_{tag}.txt")
    with open(scd_path, "w", encoding="utf-8") as f:
        f.write(scd_text(f0, rows, DEF["stagger_beats"], DEF["tempo_bps"],
                         DEF["selection"], DEF["partial_from"], DEF["partial_to"]))
    with open(map_path, "w", encoding="utf-8") as f:
        f.write(map_text(f0, rows, DEF["selection"], DEF["partial_from"], DEF["partial_to"]))

    # ---- validation / report ----
    _, _, chk = amxd_lib.read(amxd_path)
    p = chk["patcher"]
    has_js = any(b["box"].get("text", "").startswith("js ") for b in p["boxes"])
    n_num = sum(1 for b in p["boxes"] if b["box"].get("maxclass") == "live.numbox")
    cents = {r["n"]: r["cents"] for r in rows}
    assert abs(cents.get(7, 0) - (-31.2)) < 0.1, "7th-partial cents drifted"
    assert abs(cents.get(11, 0) - (-48.7)) < 0.1, "11th-partial cents drifted"

    print(f"wrote {amxd_path}")
    print(f"  type={amxd_lib.TYPE_NAMES[amxd_lib.device_type(amxd_path)]}, js={has_js}, "
          f"live.numboxes={n_num}, JSON round-trip OK")
    print(f"wrote {js_path}  ({os.path.getsize(js_path)} bytes)")
    print(f"wrote {scd_path}")
    print(f"wrote {map_path}")
    print(f"\nActive detune strategy: #3 (clips = 12-TET nearest; TRUE JI in .scd + cents map)")
    print(f"\nJI partial table  (f0 = {f0:.3f} Hz, C1):")
    print(f"{'n':>2} {'freq(Hz)':>10} {'MIDI':>5} {'note':>5} {'cents':>8} {'vel':>4}")
    print("-" * 40)
    for r in rows:
        print(f"{r['n']:>2} {r['freq']:>10.3f} {r['midi']:>5} {r['name']:>5} {r['cents']:>+8.1f} {r['vel']:>4}")
    print("\nVerified: 7th partial -31.2c, 11th partial -48.7c (matches spec).")


if __name__ == "__main__":
    main()
