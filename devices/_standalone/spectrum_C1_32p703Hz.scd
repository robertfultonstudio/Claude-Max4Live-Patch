// spectrum_C1_32p703Hz.scd  —  EXACT just-intonation spectral drone (auto-generated)
// Fundamental f0 = 32.703 Hz   |   partials 1..16  (selection: all)
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
s.waitForBoot({
    SynthDef(\spectralDrone, { |freq=110, amp=0.1, gate=1, fadeIn=20, fadeOut=25, pan=0|
        var env = EnvGen.kr(Env.asr(fadeIn, 1, fadeOut), gate, doneAction: 2);
        var sig = SinOsc.ar(freq) * amp;
        Out.ar(0, Pan2.ar(sig * env, pan));
    }).add;
    s.sync;

    ~f0      = 32.703000;
    ~master  = 0.14;                 // headroom: sum of 1/n can exceed 1
    ~stagger = 4;                  // beats between partial entries (Radigue accumulation)
    ~partials = [
        // [ n, freqHz (= n*f0, exact), amp (1/n), pan ]
        [1, 32.703000, 1.000000, -0.600000],
        [2, 65.406000, 0.500000, -0.520000],
        [3, 98.109000, 0.333333, -0.440000],
        [4, 130.812000, 0.250000, -0.360000],
        [5, 163.515000, 0.200000, -0.280000],
        [6, 196.218000, 0.166667, -0.200000],
        [7, 228.921000, 0.142857, -0.120000],
        [8, 261.624000, 0.125000, -0.040000],
        [9, 294.327000, 0.111111, 0.040000],
        [10, 327.030000, 0.100000, 0.120000],
        [11, 359.733000, 0.090909, 0.200000],
        [12, 392.436000, 0.083333, 0.280000],
        [13, 425.139000, 0.076923, 0.360000],
        [14, 457.842000, 0.071429, 0.440000],
        [15, 490.545000, 0.066667, 0.520000],
        [16, 523.248000, 0.062500, 0.600000],
    ];
    ~clock  = LinkClock(2.0).latency_(0.2);   // beats/sec; enables Ableton Link
    ~voices = ();

    ~clock.schedAbs(~clock.beats.ceil, {
        ~partials.do { |row, i|
            ~clock.sched(i * ~stagger, {
                var n = row[0], freq = row[1], amp = row[2] * ~master, pan = row[3];
                ~voices[n] = Synth(\spectralDrone, [\freq, freq, \amp, amp, \pan, pan, \fadeIn, 20]);
                nil
            });
        };
        nil
    });
    ("spectralDrone: " ++ ~partials.size ++ " partials scheduled on LinkClock @ f0=" ++ ~f0 ++ " Hz").postln;
});
)

// STOP — slow release of every voice:
// ( ~voices.do { |syn| syn.set(\gate, 0) }; ~voices = (); )
