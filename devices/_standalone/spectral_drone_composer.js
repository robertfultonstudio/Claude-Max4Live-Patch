// spectral_drone_composer.js  —  engine for the "Spectral Drone Composer" M4L device.
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
