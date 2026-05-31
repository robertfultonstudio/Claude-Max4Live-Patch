#!/usr/bin/env python3
"""
Build tools/device_map.json — the single source of truth for the conversion.

For each of the 131 ppooll acts it records:
  act            original ppooll act name (== source .maxpat basename, == device suffix)
  clear_name     human-readable function name (curated from ppooll's own descriptions)
  category       functional folder (derived from ppooll's own act_overview tags + curation)
  description    ppooll's official one-line description (verbatim where available)
  authors        ppooll author(s)
  tags           ppooll tag names
  extra_packages third-party Max packages required (authoritative, from package_dependencies.json)
  extra_packages_inferred  likely-but-unconfirmed extra packages
  live_type      SUGGESTED Live device 4CC (aaaa/iiii/mmmm) — used only by build --retag
The script reads ppooll's own metadata so descriptions/tags/authors are never invented.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PPOOLL = os.path.join(ROOT, "dependencies", "ppooll")
ACT_OVERVIEW = os.path.join(PPOOLL, "misc", "act_overview.json")
PKG_DEPS = os.path.join(PPOOLL, "misc", "package_dependencies.json")
OUT = os.path.join(HERE, "device_map.json")

# --- curated human-readable names (function-first), keyed by ppooll act name ---
CLEAR_NAMES = {
    "2Dsliders": "XY Control Pad",
    "INmulti": "Multi Audio Input",
    "LFFO": "Dynamic Ring Modulator",
    "SDIFter": "SDIF Soundfile Player",
    "TFF": "4-Band Resonant Filter",
    "TSSSF": "Subtractive Synth",
    "amxd@": "Max for Live Device Host",
    "analyze@": "Audio Analyzer (Loudness/Brightness)",
    "animator@": "5-Band LFO",
    "arpanner": "Audio-Rate Auto-Panner",
    "autocount@": "Number / Counter Generator",
    "bandfollower": "Multiband Envelope Follower",
    "banger": "Sync Bang Generator",
    "beast": "Buffer Machine",
    "beauty": "Delay-Feedback Machine",
    "bildsynthi": "Video-Driven Bandpass Filter",
    "brown": "Brownian Noise Generator",
    "buffer_host": "Shared Buffer Host",
    "buffub": "Buffer Recorder",
    "chaos": "Lorenz/Roessler Chaos Generator",
    "chebyshev@": "Chebyshev Distortion",
    "cll_cltl@": "Ondo Noise Synth",
    "clocker@": "Event Sequencer",
    "cloud": "Oscillator Bank (Pitch Cloud)",
    "control@": "External Control Input (MIDI/OSC)",
    "delayloops": "3-Line Delay",
    "demosound@": "Demo Sound Generator",
    "distort@": "Bitcrusher / Sample-Rate Reducer",
    "envM": "Multi-Envelope (MC)",
    "envMM": "Multi-Envelope Generator",
    "eq@": "Graphic EQ (Crossover)",
    "equalAmp": "Equal Amplitude Utility",
    "euclid": "Euclidean LFO Sequencer",
    "feedbacker": "Audio Feedback Generator",
    "fffb@": "Fixed Filter Bank",
    "flop": "Sample Looper",
    "fmrm": "FM Synth & Ring Modulator",
    "forbiddenP": "Spectral Filter / Vocoder",
    "frack": "Parameter Motion Recorder",
    "freeverb@": "Reverb (Freeverb)",
    "frequenzteiler": "Trautonium Synth",
    "gg.rainer": "Granular Sample Player (gg)",
    "gizmo@": "Spectral Pitch Shifter",
    "gverb@": "Reverb (GVerb)",
    "hardplay": "Hard Disk Player",
    "jit.2oscbank": "Video-to-Oscillator Bank",
    "jit.3m@": "Image Analyzer",
    "jit.blobs": "Blob Tracker",
    "jit.brcosa@": "Video Brightness/Contrast/Saturation",
    "jit.buf": "Image Buffer / Texture Player",
    "jit.buffer@": "Image Buffer Recorder",
    "jit.copyprot.act": "Screen Grabber",
    "jit.display@": "Video Display / Recorder",
    "jit.grab@": "Camera Input",
    "jit.lcd@": "Drawing Canvas",
    "jit.op@": "Image Operator",
    "jit.player": "Movie Player",
    "jit.slide@": "Texture Slide / Reposition",
    "jit.videoplanes": "Video Mixer / Positioner",
    "jit.videoplanesP": "Video Mixer (List)",
    "jit.world@": "Texture World / Movie Recorder",
    "kaos@": "Random Mouse-Click Generator",
    "karma@": "Varispeed Looper (Karma)",
    "kk.rainer": "Granular Sample Player (kk)",
    "kompressor": "Compressor",
    "limi": "Peak Limiter",
    "link@": "Ableton Link Sync",
    "matriarch@": "Audio Matrix (Matriarch)",
    "matrix@": "Audio Matrix",
    "mc.random@": "Random Generator (MC)",
    "mcpanner": "Random MC Panner",
    "midikeys": "MIDI Keyboard Parser",
    "mixer@": "Audio Mixer",
    "modul.ator": "Universal Modulator",
    "morph": "Audio Morpher (MC)",
    "mubugrain@": "Granular Player (MuBu)",
    "multitap": "Multitap Delay",
    "munger@": "Granulator (Munger)",
    "noize@": "Noise Generator",
    "normalize": "Peak Normalizer",
    "notepad@": "Notepad",
    "op@": "Signal / Number Operator",
    "oscbank@": "Sine Oscillator Bank",
    "overdrive@": "Overdrive",
    "pHARM4@": "4-Band Harmonizer",
    "paf@": "PAF Formant Synth",
    "peakfinder": "Dynamic Gate",
    "peakfollow@": "Envelope Follower",
    "period": "Signal Step Sequencer",
    "pr.6groov": "6-Voice Sample Player",
    "pr.spectfreeze": "Spectral Freeze",
    "pr.spectplay": "Spectral Player",
    "prdelay@": "Delay with Feedback",
    "pulse@": "LFO Pulse Generator",
    "pulsegen": "Pulse Wave Generator",
    "quant": "Frequency / Rhythm Quantizer",
    "random0_1-": "Random Bit Generator (0/1)",
    "random@": "Parameter Randomizer",
    "rec@": "Hard Disk Recorder",
    "rec_events": "Parameter Event Recorder",
    "rez@": "Spectral Resonators",
    "rm@": "Ring Modulator",
    "scope@": "Oscilloscope",
    "signaltocontrol": "Signal-to-Control Converter",
    "simproov": "4-Fold Sample Player",
    "sinsE": "Sine Bank with Envelopes",
    "sinus": "Sine Tone Generator",
    "snap@": "Preset Snapshot",
    "sonogram@": "Sonogram (Spectral View)",
    "spat.abba@": "Ambisonics A/B Converter",
    "spat.ambicontrol@": "Ambisonics Monitor Control",
    "spat.ambidecode@": "Ambisonics B-Format Decoder",
    "spat.ambiencode@": "Ambisonics B-Format Encoder",
    "spat.ambimonitor@": "Ambisonics Monitor",
    "spat.ambipanning@": "Ambisonics Panner",
    "spat.ambitransform@": "Ambisonics Soundfield Transform",
    "spat.uhj2b@": "Ambisonics UHJ-to-B Converter",
    "spectral_sins": "Spectral Sine Resynthesis",
    "svf2@": "State-Variable Filter",
    "tetris@": "Act Layout Editor",
    "threekomp": "3-Band Compressor",
    "timeline@": "Parameter Timeline Sequencer",
    "vbap@": "VBAP Multi-Speaker Panner",
    "vst@": "VST Plugin Host",
    "w_filter": "N-Band Filter / EQ",
    "walk": "Random Walk Modulator",
    "wavelets": "Wavelet Oscillator",
    "waveshapers@": "Waveshaper",
    "wrapfilter": "1-4 Band Stereo Filter",
    "x_filter": "Chebyshev/Butterworth Filter",
    "xgroove@": "Sample Player (XGroove)",
}

# --- functional category per act (folder) ---
CATEGORY = {
    # audio effects
    "freeverb@": "audio_effects", "gverb@": "audio_effects", "eq@": "audio_effects",
    "w_filter": "audio_effects", "x_filter": "audio_effects", "wrapfilter": "audio_effects",
    "svf2@": "audio_effects", "TFF": "audio_effects", "fffb@": "audio_effects",
    "chebyshev@": "audio_effects", "distort@": "audio_effects", "overdrive@": "audio_effects",
    "waveshapers@": "audio_effects", "rm@": "audio_effects", "LFFO": "audio_effects",
    "gizmo@": "audio_effects", "pHARM4@": "audio_effects", "forbiddenP": "audio_effects",
    "pr.spectfreeze": "audio_effects", "pr.spectplay": "audio_effects",
    "delayloops": "audio_effects", "multitap": "audio_effects", "prdelay@": "audio_effects",
    "beauty": "audio_effects", "feedbacker": "audio_effects", "munger@": "audio_effects",
    "morph": "audio_effects", "kompressor": "audio_effects", "threekomp": "audio_effects",
    "limi": "audio_effects", "normalize": "audio_effects", "peakfinder": "audio_effects",
    "arpanner": "audio_effects", "mcpanner": "audio_effects", "bildsynthi": "audio_effects",
    # instruments / generators
    "sinus": "instruments", "sinsE": "instruments", "oscbank@": "instruments",
    "cloud": "instruments", "noize@": "instruments", "brown": "instruments",
    "wavelets": "instruments", "frequenzteiler": "instruments", "TSSSF": "instruments",
    "fmrm": "instruments", "paf@": "instruments", "rez@": "instruments",
    "cll_cltl@": "instruments", "spectral_sins": "instruments", "demosound@": "instruments",
    # samplers / buffer & disk players / recorders
    "flop": "samplers", "beast": "samplers", "gg.rainer": "samplers", "kk.rainer": "samplers",
    "xgroove@": "samplers", "simproov": "samplers", "pr.6groov": "samplers",
    "karma@": "samplers", "mubugrain@": "samplers", "hardplay": "samplers",
    "buffub": "samplers", "rec@": "samplers", "SDIFter": "samplers",
    # modulation / control sources
    "animator@": "modulation", "chaos": "modulation", "walk": "modulation",
    "random@": "modulation", "random0_1-": "modulation", "envM": "modulation",
    "envMM": "modulation", "pulse@": "modulation", "pulsegen": "modulation",
    "kaos@": "modulation", "autocount@": "modulation", "modul.ator": "modulation",
    "op@": "modulation", "quant": "modulation", "2Dsliders": "modulation",
    "mc.random@": "modulation",
    # sequencing
    "clocker@": "sequencing", "timeline@": "sequencing", "euclid": "sequencing",
    "period": "sequencing", "banger": "sequencing", "frack": "sequencing",
    "rec_events": "sequencing",
    # midi
    "midikeys": "midi", "control@": "midi",
    # routing / mixing
    "matrix@": "routing_mixing", "matriarch@": "routing_mixing", "mixer@": "routing_mixing",
    "INmulti": "routing_mixing", "signaltocontrol": "routing_mixing",
    # spatialization
    "spat.abba@": "spatialization", "spat.ambicontrol@": "spatialization",
    "spat.ambidecode@": "spatialization", "spat.ambiencode@": "spatialization",
    "spat.ambimonitor@": "spatialization", "spat.ambipanning@": "spatialization",
    "spat.ambitransform@": "spatialization", "spat.uhj2b@": "spatialization",
    "vbap@": "spatialization",
    # analysis / metering
    "analyze@": "analysis_metering", "bandfollower": "analysis_metering",
    "peakfollow@": "analysis_metering", "scope@": "analysis_metering",
    "sonogram@": "analysis_metering",
    # visual / jitter
    "jit.2oscbank": "visual_jitter", "jit.3m@": "visual_jitter", "jit.blobs": "visual_jitter",
    "jit.brcosa@": "visual_jitter", "jit.buf": "visual_jitter", "jit.buffer@": "visual_jitter",
    "jit.copyprot.act": "visual_jitter", "jit.display@": "visual_jitter",
    "jit.grab@": "visual_jitter", "jit.lcd@": "visual_jitter", "jit.op@": "visual_jitter",
    "jit.player": "visual_jitter", "jit.slide@": "visual_jitter",
    "jit.videoplanes": "visual_jitter", "jit.videoplanesP": "visual_jitter",
    "jit.world@": "visual_jitter",
    # utilities
    "amxd@": "utilities", "vst@": "utilities", "notepad@": "utilities", "snap@": "utilities",
    "tetris@": "utilities", "link@": "utilities", "buffer_host": "utilities",
    "equalAmp": "utilities",
}

# default suggested Live device type per category
DEFAULT_TYPE = {
    "audio_effects": "aaaa", "instruments": "iiii", "samplers": "iiii",
    "modulation": "aaaa", "sequencing": "aaaa", "midi": "mmmm",
    "routing_mixing": "aaaa", "spatialization": "aaaa", "analysis_metering": "aaaa",
    "visual_jitter": "aaaa", "utilities": "aaaa",
}
# per-act type overrides (recorders need track audio input -> Audio Effect)
TYPE_OVERRIDE = {"buffub": "aaaa", "rec@": "aaaa", "INmulti": "aaaa"}

# extra packages NOT bundled in the zip — must be installed via Max Package Manager.
# Authoritative list comes from ppooll/misc/package_dependencies.json (loaded below).
# These 3 ambisonics converters very likely also need ICST Ambisonics (not listed upstream):
EXTRA_INFERRED = {
    "spat.abba@": ["ICST Ambisonics"],
    "spat.ambitransform@": ["ICST Ambisonics"],
    "spat.uhj2b@": ["ICST Ambisonics"],
}


def main():
    ov = json.load(open(ACT_OVERVIEW, encoding="utf-8"))
    tags, authors, acts = ov["tags"], ov["authors"], ov["acts"]
    pkgdeps = json.load(open(PKG_DEPS, encoding="utf-8"))

    # invert package_dependencies -> act: [packages]
    act_pkgs = {}
    for pkg, who in pkgdeps.items():
        if pkg == "comments":
            continue
        targets = who if isinstance(who, list) else [who]
        for t in targets:
            if t == "all":
                continue
            act_pkgs.setdefault(t, []).append(pkg)

    def tagnames(t):
        if t is None:
            return []
        if not isinstance(t, list):
            t = [t]
        return [tags.get(str(x), "?") for x in t]

    def authname(a):
        if a is None:
            return ["unknown"]
        if not isinstance(a, list):
            a = [a]
        return [authors.get(str(x), ["?"])[0] for x in a]

    # the authoritative device list = the 131 original .amxd files
    src_dir = os.path.join(ROOT, "original_ppooll_sources", "devices_amxd")
    act_list = sorted(
        f[len("live.ppooll."):-len(".amxd")]
        for f in os.listdir(src_dir)
        if f.endswith(".amxd")
    )

    entries = []
    problems = []
    for act in act_list:
        meta = acts.get(act, {})
        cat = CATEGORY.get(act)
        if cat is None:
            problems.append(f"no category for {act}")
            cat = "utilities"
        name = CLEAR_NAMES.get(act)
        if name is None:
            problems.append(f"no clear_name for {act}")
            name = act
        extra = sorted(set(act_pkgs.get(act, [])))
        entries.append({
            "act": act,
            "clear_name": name,
            "category": cat,
            "description": meta.get("description", "(no upstream description)"),
            "authors": authname(meta.get("authors")),
            "tags": tagnames(meta.get("tags")),
            "requires_all": ["jasch objects"],          # every act needs jasch
            "extra_packages": extra,                      # authoritative
            "extra_packages_inferred": EXTRA_INFERRED.get(act, []),
            "live_type": TYPE_OVERRIDE.get(act, DEFAULT_TYPE[cat]),
            "has_upstream_metadata": act in acts,
        })

    json.dump({"version": "1.0", "source": "ppooll 8.6.9", "devices": entries},
              open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"wrote {OUT} with {len(entries)} devices")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  -", p)
    else:
        print("all 131 acts have a curated clear_name and category.")


if __name__ == "__main__":
    main()
