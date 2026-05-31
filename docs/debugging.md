# Debugging in Max/Live (for runtime issues a headless build can't catch)

This suite is assembled and **statically** validated without Max/Live. Runtime bugs (audio not
flowing, Max-console errors, GUI glitches) can only be found and fixed where Max actually runs —
your machine. This doc records the diagnosis already done and gives you a ready-to-paste prompt to
iterate locally.

## Root cause already found & fixed (v1.1): the "stack overflow" on insertion

**Symptom:** dropping a device (e.g. `Reverb (Freeverb)`) printed
`prepend: stack overflow -- outlets are disabled until this message is cleared`, showed only the
wrapper shell (no act UI), and passed no audio.

**Diagnosis (from the patcher JSON):** the ppooll-for-Live template names the act in two places —
a static abstraction *and* the dynamic spawner message in `p create-act-bpatcher` (banged by
`ppooll_host` via `r live.load_act` → `thispatcher script newdefault`). The upstream
`generate_per_act_amxd.py` rewrote only the static one, so each device **statically loaded `<act>`
but dynamically spawned `demosound@`** — two acts colliding over the shared `pattr`/`pattrstorage`
state. `tools/build_devices.py` now rewrites both (verified consistent).

**Verify the fix in your copy (no Max needed):**
```bash
python3 - <<'PY'
import json,glob,os,sys; sys.path.insert(0,'tools'); import amxd_lib
for f in glob.glob('devices/**/*.amxd',recursive=True):
    _,_,j=amxd_lib.read(f); s=json.dumps(j,ensure_ascii=False)
    act=os.path.basename(f).split(' — ')[-1][:-5]
    if act!='demosound@' and '"demosound@.maxpat"' in s:
        print("MISMATCH still present:", f)
print("check done")
PY
```
Expect only `check done`.

## If a stack overflow (or no audio) still happens after v1.1

Then there is a *second*, deeper interaction that needs Max to resolve. Ranked suspects:

1. **`envi_name` pattr ↔ pattrstorage feedback.** Top level has
   `r envi_name → tosymbol → pattr envi_name → prepend set`. If `ppooll_host`'s `pattrstorage`
   re-emits `envi_name` on store/recall, this can self-retrigger. Try gating it with
   `t b` + `onebang`, or a `change`/`deferlow` before `pattr envi_name`, so it can't re-enter.
2. **Static + dynamic double instance.** The act is created *both* as a static `newobj`
   abstraction (varname `<act>1`, in `p LIVE_PPOOLL_ENVIRONMENT`) *and* dynamically by
   `create-act-bpatcher`. Now they're the same act, but having both may still double-register with
   `ppooll_host`. Experiment: delete the static `<act>.maxpat` newobj (keep the dynamic creation),
   reload, test — or the reverse. Whichever is clean wins.
3. **`pattrstorage` initial state** baked into the device. Inspect `ppooll_host`'s `pattrstorage`
   for a stored default that collides on a blank set.

## Copy-paste prompt for Claude Code on your Mac (has Max + Live)

```text
Sei Claude Code sul mio Mac, ho Max 9 e Ableton Live 12. Aiutami a debuggare un device Max for Live.

Repo già installato; i device sono in .../ppooll M4L/ e il pacchetto ppooll è in
~/Documents/Max 9/Packages/ppooll.

Contesto: ho applicato un fix (v1.1) all'errore "prepend: stack overflow -- outlets are disabled".
Verifica prima che il fix sia presente: nel file
devices/audio_effects/"Reverb (Freeverb) — freeverb@.amxd" sia il newobj statico SIA il messaggio
dentro "p create-act-bpatcher" devono dire "freeverb@.maxpat" (non "demosound@.maxpat").

Poi:
1) Apri Ableton Live, crea una traccia AUDIO con dell'audio in loop.
2) Trascina "Reverb (Freeverb)" sulla traccia. Apri l'editor del device (Edit) e la Max Console.
3) Dimmi ESATTAMENTE cosa compare in console all'inserimento (copia i messaggi).
4) Se NON c'è più stack overflow e passa audio: ottimo, conferma e prova anche "Overdrive" (audio)
   e "Sine Tone Generator" su traccia MIDI.
5) Se c'è ANCORA stack overflow, indaga in quest'ordine, testando l'audio dopo ogni tentativo
   (fai una copia di backup del .amxd prima di modificarlo):
   a) Catena envi_name: trova "pattr envi_name" e la "pattrstorage" dentro ppooll_host; cerca un
      loop di feedback; prova a inserire un [onebang] o [change] prima di "pattr envi_name".
   b) Doppia istanza dell'act: dentro "p LIVE_PPOOLL_ENVIRONMENT" c'è sia il newobj statico
      "<act>.maxpat" sia la creazione dinamica in "create-act-bpatcher". Prova a cancellare il
      newobj statico (tieni solo la creazione dinamica), salva, ricarica, testa. Poi prova il
      contrario. Tienimi quello che funziona.
   c) Controlla "pattrstorage" in ppooll_host per uno stato di default che collide su un set vuoto.
6) Quando trovi la modifica che risolve, dimmi qual è in modo PRECISO (oggetto, connessione,
   messaggio) così la replico nello script di build per tutti i 131 device.

Non modificare i file dentro Packages/ppooll. Lavora solo sui .amxd e spiegami ogni passo.
```

Whatever change fixes it, tell me the exact object/connection and I'll fold it into
`tools/build_devices.py` so all 131 get it in one pass.
