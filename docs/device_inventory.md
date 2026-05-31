# Device Inventory — 131 ppooll Max for Live Devices

Generated from `tools/device_map.json` + `build_report/build_report.json`. Do not edit by hand; run `python3 tools/make_docs.py`.

**Total devices: 131**  •  Source: ppooll 8.6.9 (MIT)  •  All map 1:1 to an original ppooll act — no missing sources.

## Status legend

- **Static-OK** — re-packs to a structurally valid `.amxd`, JSON round-trips, all machine-specific paths removed, source act present in the bundled runtime.
- ⚠ **Verify** — additionally needs a third-party Max package, or has another note.
- **Functional testing in Ableton Live (Mac/Win) is still required for every device** — it could not be performed in the build environment (no Max/Live). See [testing.md](testing.md) and [known_issues.md](known_issues.md).

## Summary by category

| Category | Count |
|---|---:|
| Audio Effects | 35 |
| Instruments / Generators | 15 |
| Samplers & Buffer/Disk Players | 13 |
| Modulation & Control Sources | 16 |
| Sequencing & Clocks | 7 |
| MIDI | 2 |
| Routing & Mixing | 5 |
| Spatialization (Ambisonics / VBAP) | 9 |
| Analysis & Metering | 5 |
| Visual (Jitter) | 16 |
| Utilities | 8 |
| **Total** | **131** |

## Audio Effects  (35)

| Original (ppooll) | New device name | Function | Dependencies | Status | Notes |
|---|---|---|---|---|---|
| `wrapfilter` | 1-4 Band Stereo Filter | 1 - 4 band stereo filter/eq | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by noid) |
| `threekomp` | 3-Band Compressor | ppooll port of 3komp from the max demo patches | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by hausch/cycling'74) |
| `delayloops` | 3-Line Delay | 3 delay lines | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by Antonio DellaMarina) |
| `pHARM4@` | 4-Band Harmonizer | 4 band harmonizer | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by Paulo Raposo) |
| `TFF` | 4-Band Resonant Filter | 4 band resonant filter | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by Léo Dupleix) |
| `feedbacker` | Audio Feedback Generator | feedback generator for audio-inputs | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by noid) |
| `morph` | Audio Morpher (MC) | morphing between two audio signals (mc) | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by Taku Unami) |
| `arpanner` | Audio-Rate Auto-Panner | audiorate panner | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by Antonio DellaMarina) |
| `distort@` | Bitcrusher / Sample-Rate Reducer | degrade sample-rate & bit-resolution | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip/hausch) |
| `chebyshev@` | Chebyshev Distortion | distortion unit | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by hausch) |
| `x_filter` | Chebyshev/Butterworth Filter | cheyshev & butterworth filter | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by noid/hausch) |
| `kompressor` | Compressor | audio compressor | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by cycling'74) |
| `prdelay@` | Delay with Feedback | simple delay with feedback | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by Paulo Raposo) |
| `beauty` | Delay-Feedback Machine | delay-feedback machine | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by noid) |
| `peakfinder` | Dynamic Gate | dynamic gate | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by noid) |
| `LFFO` | Dynamic Ring Modulator | dynamic ring modulator | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by Antonio DellaMarina) |
| `fffb@` | Fixed Filter Bank | filter bank | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `munger@` | Granulator (Munger) | granulator plugin | ppooll + jasch objects + PeRColate | ⚠ Verify | 3rd-party pkg required; live_type=aaaa (Audio Effect) (by noid/hausch) |
| `eq@` | Graphic EQ (Crossover) | crossover-filter based graphic equalizer | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by hausch/cycling'74) |
| `multitap` | Multitap Delay | delay bank | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by noid) |
| `w_filter` | N-Band Filter / EQ | n-band filter/eq | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `overdrive@` | Overdrive | audio overdrive | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `limi` | Peak Limiter | peak limiter | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by hausch/cycling'74) |
| `normalize` | Peak Normalizer | get maximum level of audio | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by noid) |
| `mcpanner` | Random MC Panner | simple random panner for mc signals | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `freeverb@` | Reverb (Freeverb) | reverb | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by noid) |
| `gverb@` | Reverb (GVerb) | reverb plugin | ppooll + jasch objects + LowkeyNW | ⚠ Verify | 3rd-party pkg required; live_type=aaaa (Audio Effect) (by noid) |
| `rm@` | Ring Modulator | ring modulator | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `forbiddenP` | Spectral Filter / Vocoder | spectral filter or vocoder | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip/cycling'74) |
| `pr.spectfreeze` | Spectral Freeze | spectrum freezer | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by Paulo Raposo) |
| `gizmo@` | Spectral Pitch Shifter | pitch shifter | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by noid) |
| `pr.spectplay` | Spectral Player | spectrum player | ppooll + jasch objects + CNMAT Externals | ⚠ Verify | 3rd-party pkg required; live_type=aaaa (Audio Effect) (by Paulo Raposo) |
| `svf2@` | State-Variable Filter | cutoff filter | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip/hausch) |
| `bildsynthi` | Video-Driven Bandpass Filter | video driven bandpass filter | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip/nicolaj kirisits) |
| `waveshapers@` | Waveshaper | waveshaping functions and demos | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by hausch) |

## Instruments / Generators  (15)

| Original (ppooll) | New device name | Function | Dependencies | Status | Notes |
|---|---|---|---|---|---|
| `brown` | Brownian Noise Generator | brownian noise generator | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by noid) |
| `demosound@` | Demo Sound Generator | cycling's demosound to ppooll | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by cycling'74) |
| `fmrm` | FM Synth & Ring Modulator | fm synt & ring modulator | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by filip/hausch/cycling'74) |
| `noize@` | Noise Generator | noise-generator | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by filip/noid) |
| `cll_cltl@` | Ondo Noise Synth | ondomusic noise | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by filip/uhito kiyosue) |
| `cloud` | Oscillator Bank (Pitch Cloud) | oscillator bank with pitch distribution system | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by Taku Unami) |
| `paf@` | PAF Formant Synth | Phase Aligned Formant Synthesizer | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by filip/noid/hausch) |
| `sinsE` | Sine Bank with Envelopes | sinus bank with envelopes | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by filip) |
| `oscbank@` | Sine Oscillator Bank | multiple sinus generator | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by filip) |
| `sinus` | Sine Tone Generator | sinus tone generator | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by filip) |
| `rez@` | Spectral Resonators | spectral rezonators | ppooll + jasch objects + CNMAT Externals | ⚠ Verify | 3rd-party pkg required; live_type=iiii (Instrument) (by hausch) |
| `spectral_sins` | Spectral Sine Resynthesis | sinwaves following incoming audio | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by filip) |
| `TSSSF` | Subtractive Synth | substractive synthesis | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by Léo Dupleix) |
| `frequenzteiler` | Trautonium Synth | trautonium synthesizer | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by filip) |
| `wavelets` | Wavelet Oscillator | time based oscilator | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by noid) |

## Samplers & Buffer/Disk Players  (13)

| Original (ppooll) | New device name | Function | Dependencies | Status | Notes |
|---|---|---|---|---|---|
| `simproov` | 4-Fold Sample Player | simple 4 fold sample player | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by filip) |
| `pr.6groov` | 6-Voice Sample Player | multiple sample player | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by Paulo Raposo) |
| `beast` | Buffer Machine | non-trivial buffer machine | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by noid) |
| `buffub` | Buffer Recorder | records into buffers | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip/hausch) |
| `mubugrain@` | Granular Player (MuBu) | granular player | ppooll + jasch objects + MuBu For Max | ⚠ Verify | 3rd-party pkg required; live_type=iiii (Instrument) (by Joe Steccato) |
| `gg.rainer` | Granular Sample Player (gg) | granular sample player | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by noid) |
| `kk.rainer` | Granular Sample Player (kk) | granular sample player | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by noid) |
| `hardplay` | Hard Disk Player | plays soundfiles from hd or cd | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by filip/noid) |
| `rec@` | Hard Disk Recorder | record to harddisc | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `flop` | Sample Looper | sample looper | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by filip) |
| `xgroove@` | Sample Player (XGroove) | sample player | ppooll + jasch objects | Static-OK | live_type=iiii (Instrument) (by filip/Joe Steccato) |
| `SDIFter` | SDIF Soundfile Player | SDIF soundfile player | ppooll + jasch objects + CNMAT Externals | ⚠ Verify | 3rd-party pkg required; live_type=iiii (Instrument) (by filip/noid/bill d) |
| `karma@` | Varispeed Looper (Karma) | Varispeed audio looper | ppooll + jasch objects + karma | ⚠ Verify | 3rd-party pkg required; live_type=iiii (Instrument) (by raja) |

## Modulation & Control Sources  (16)

| Original (ppooll) | New device name | Function | Dependencies | Status | Notes |
|---|---|---|---|---|---|
| `animator@` | 5-Band LFO | 5 band lfo | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by hausch) |
| `quant` | Frequency / Rhythm Quantizer | signal based frequency/rhythm quantizer | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by hausch) |
| `pulse@` | LFO Pulse Generator | lfo pulse generator | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by hausch) |
| `chaos` | Lorenz/Roessler Chaos Generator | lorenz-roessler generator | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip/noid) |
| `envM` | Multi-Envelope (MC) | mc version of multiple envelopes | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `envMM` | Multi-Envelope Generator | multiple envelopes | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `autocount@` | Number / Counter Generator | number generator | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by Paulo Raposo) |
| `random@` | Parameter Randomizer | randomize parameters | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `pulsegen` | Pulse Wave Generator | pulse wave generator | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by romain macagni) |
| `random0_1-` | Random Bit Generator (0/1) | simple ranomizer spitting 0 and 1 | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `mc.random@` | Random Generator (MC) | (no upstream description) | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by unknown) |
| `kaos@` | Random Mouse-Click Generator | random mouse clicks | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `walk` | Random Walk Modulator | random walk a parameter | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `op@` | Signal / Number Operator | signal/number operator | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by hausch) |
| `modul.ator` | Universal Modulator | modulates anything | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `2Dsliders` | XY Control Pad | control parameters by dragging points | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |

## Sequencing & Clocks  (7)

| Original (ppooll) | New device name | Function | Dependencies | Status | Notes |
|---|---|---|---|---|---|
| `euclid` | Euclidean LFO Sequencer | LFO with Euclidean sequencer | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by Taku Unami) |
| `clocker@` | Event Sequencer | event sequencer | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `rec_events` | Parameter Event Recorder | records parameter events | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `frack` | Parameter Motion Recorder | record parameter movements | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by boris hauf) |
| `timeline@` | Parameter Timeline Sequencer | graphical timeline sequencer for parameters | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `period` | Signal Step Sequencer | signal-based step sequencer | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by hausch) |
| `banger` | Sync Bang Generator | send synchronized bangs | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |

## MIDI  (2)

| Original (ppooll) | New device name | Function | Dependencies | Status | Notes |
|---|---|---|---|---|---|
| `control@` | External Control Input (MIDI/OSC) | external device input (midi-osc-etc) | ppooll + jasch objects | Static-OK | live_type=mmmm (MIDI Effect) (by filip) |
| `midikeys` | MIDI Keyboard Parser | midi keyboard parser | ppooll + jasch objects | Static-OK | live_type=mmmm (MIDI Effect) (by filip) |

## Routing & Mixing  (5)

| Original (ppooll) | New device name | Function | Dependencies | Status | Notes |
|---|---|---|---|---|---|
| `matrix@` | Audio Matrix | audio matrix | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `matriarch@` | Audio Matrix (Matriarch) | audio matrix on steroids | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by Joe Steccato) |
| `mixer@` | Audio Mixer | audio mixer | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `INmulti` | Multi Audio Input | (multiple) audio input | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `signaltocontrol` | Signal-to-Control Converter | signals to control@ | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |

## Spatialization (Ambisonics / VBAP)  (9)

| Original (ppooll) | New device name | Function | Dependencies | Status | Notes |
|---|---|---|---|---|---|
| `spat.abba@` | Ambisonics A/B Converter | ambisonics a-to-b/b-to-a format converter | ppooll + jasch objects + (likely: ICST Ambisonics) | ⚠ Verify | 3rd-party pkg required; live_type=aaaa (Audio Effect) (by hausch) |
| `spat.ambidecode@` | Ambisonics B-Format Decoder | ambisonics b-format decoder | ppooll + jasch objects + ICST Ambisonics | ⚠ Verify | 3rd-party pkg required; live_type=aaaa (Audio Effect) (by hausch) |
| `spat.ambiencode@` | Ambisonics B-Format Encoder | ambisonics b-format encoder | ppooll + jasch objects + ICST Ambisonics | ⚠ Verify | 3rd-party pkg required; live_type=aaaa (Audio Effect) (by hausch) |
| `spat.ambimonitor@` | Ambisonics Monitor | monitor for ambisonics encoder | ppooll + jasch objects + ICST Ambisonics | ⚠ Verify | 3rd-party pkg required; live_type=aaaa (Audio Effect) (by filip/hausch) |
| `spat.ambicontrol@` | Ambisonics Monitor Control | ambimonitor controller | ppooll + jasch objects + ICST Ambisonics | ⚠ Verify | 3rd-party pkg required; live_type=aaaa (Audio Effect) (by filip/hausch) |
| `spat.ambipanning@` | Ambisonics Panner | ambisonics panner | ppooll + jasch objects + ICST Ambisonics | ⚠ Verify | 3rd-party pkg required; live_type=aaaa (Audio Effect) (by hausch) |
| `spat.ambitransform@` | Ambisonics Soundfield Transform | ambisonics soundfield transform | ppooll + jasch objects + (likely: ICST Ambisonics) | ⚠ Verify | 3rd-party pkg required; live_type=aaaa (Audio Effect) (by hausch) |
| `spat.uhj2b@` | Ambisonics UHJ-to-B Converter | ambisonics uhj-to-b format converter | ppooll + jasch objects + (likely: ICST Ambisonics) | ⚠ Verify | 3rd-party pkg required; live_type=aaaa (Audio Effect) (by hausch) |
| `vbap@` | VBAP Multi-Speaker Panner | multi-speaker-spat or plugin-router | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |

## Analysis & Metering  (5)

| Original (ppooll) | New device name | Function | Dependencies | Status | Notes |
|---|---|---|---|---|---|
| `analyze@` | Audio Analyzer (Loudness/Brightness) | loudness, brightness of audio | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `peakfollow@` | Envelope Follower | envelope follower | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by noid) |
| `bandfollower` | Multiband Envelope Follower | generate loudness data from filters | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `scope@` | Oscilloscope | view audio signal | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip/hausch) |
| `sonogram@` | Sonogram (Spectral View) | audio signal viewer | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |

## Visual (Jitter)  (16)

| Original (ppooll) | New device name | Function | Dependencies | Status | Notes |
|---|---|---|---|---|---|
| `jit.blobs` | Blob Tracker | outputs a list with blobs tracked in an image | ppooll + jasch objects + cv.jit | ⚠ Verify | 3rd-party pkg required; live_type=aaaa (Audio Effect) (by filip) |
| `jit.grab@` | Camera Input | camera input | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `jit.lcd@` | Drawing Canvas | draft drawing | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `jit.3m@` | Image Analyzer | cheap image analyser | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `jit.buf` | Image Buffer / Texture Player | store images and play (textures) | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `jit.buffer@` | Image Buffer Recorder | store images and play later | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `jit.op@` | Image Operator | image operater | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `jit.player` | Movie Player | qt movie player | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `jit.copyprot.act` | Screen Grabber | grab video from screen | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `jit.slide@` | Texture Slide / Reposition | slide and repositin incoming texture | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `jit.world@` | Texture World / Movie Recorder | texture host to movie rec | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `jit.brcosa@` | Video Brightness/Contrast/Saturation | video brcosa settings | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `jit.display@` | Video Display / Recorder | video screening and recording | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `jit.videoplanesP` | Video Mixer (List) | mix and position video (list-version) | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `jit.videoplanes` | Video Mixer / Positioner | mix and position video | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip/noid) |
| `jit.2oscbank` | Video-to-Oscillator Bank | video to oscilator bank | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |

## Utilities  (8)

| Original (ppooll) | New device name | Function | Dependencies | Status | Notes |
|---|---|---|---|---|---|
| `link@` | Ableton Link Sync | ableton link sync interface | ppooll + jasch objects + link | ⚠ Verify | 3rd-party pkg required; live_type=aaaa (Audio Effect) (by hausch) |
| `tetris@` | Act Layout Editor | customize your act layout (and act-building) | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `equalAmp` | Equal Amplitude Utility | ???? | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by Taku Unami) |
| `amxd@` | Max for Live Device Host | host for max for live devices | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip/hausch/Joe Steccato) |
| `notepad@` | Notepad | write something to yourself | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip/hausch) |
| `snap@` | Preset Snapshot | snapshot all parameters as preset | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip) |
| `buffer_host` | Shared Buffer Host | (no upstream description) | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by unknown) |
| `vst@` | VST Plugin Host | host for vst plugins | ppooll + jasch objects | Static-OK | live_type=aaaa (Audio Effect) (by filip/hausch) |
