# Inline act layout inside the device (no external window) — prototype plan

Goal: show each act's panel **inside** the M4L device box instead of opening a separate window.

## Why it's feasible (verified from the patchers)
- ppooll acts are **compact** patches; the act's patching window *is* its UI (e.g. `freeverb@`
  ≈ 159×133, `overdrive@` ≈ 159×96, `eq@` ≈ 300×157). See `tools/act_embed_info.json` for all 131.
- Acts have **0 inlets / 0 outlets** — they connect themselves via `send`/`receive`
  (`live.stereo_in` / `live.stereo_out`) and `pattr`. So an embedded view needs **no patch cords**;
  a `bpatcher` purely for display is enough.
- ppooll already ships the pattern: `patchers/abstractions/misc/demosound@bp.maxpat` embeds acts
  as `bpatcher` + `presentation:1` with the wrapper `openinpresentation:1`.
- Only **2 / 131** acts have a dedicated Presentation layout, so the bpatcher shows the act's
  patching canvas (which is the intended UI for ppooll acts).

## The one unknown (why we prototype on 1 device first)
Today the act is created/displayed by `p create-act-bpatcher` (inside `p LIVE_PPOOLL_ENVIRONMENT`),
which `ppooll_host` drives. If we display the act with our own top-level bpatcher we must keep
**exactly one** act instance (two would collide on `send/receive` + `pattr`, re-creating the
stack-overflow class of bug), **and** confirm `ppooll_host` still registers the act's parameters
(the 8 `live.param` knobs / preset recall) when it didn't spawn it itself. That can only be
confirmed in Max/Live — hence: prototype `freeverb@`, verify, then auto-scale to all 131.

## Prompt for Claude Code on your Mac (Max 9 + Live 12)

```text
Sei Claude Code sul mio Mac (Max 9 + Ableton Live 12). Obiettivo: mostrare il pannello dell'act
DENTRO il device Max for Live (niente finestra esterna), partendo da UN device come prototipo:
"Reverb (Freeverb) — freeverb@.amxd".

Fatti verificati:
- Gli act ppooll non hanno layout di Presentation: il loro pannello È la finestra di patching
  (compatta). freeverb@ ~159x133 px.
- IMPORTANTE: gli act hanno 0 inlet e 0 outlet; si collegano da soli via send/receive
  (live.stereo_in / live.stereo_out) e pattr. Per mostrarli NON servono cavi: basta un bpatcher
  dell'act, solo per visualizzazione.
- Oggi l'act viene creato/mostrato in finestra esterna dal subpatcher "p create-act-bpatcher"
  dentro "p LIVE_PPOOLL_ENVIRONMENT".

0) Fai una COPIA di backup del .amxd prima di modificarlo.
1) Apri il device in Max (in Live: pulsante Edit ✎ sulla barra del device).

2) APPROCCIO A (prova prima questo - il piu' semplice):
   a. Nel patch top-level del device crea un oggetto "bpatcher". Inspector -> Patcher File =
      freeverb@.maxpat (numinlets/numoutlets = 0). Mostra il pannello dell'act.
   b. Tasto destro -> Add to Presentation. Vai in Presentation (vista del device box) e
      posiziona/ridimensiona il bpatcher ~159x133 sotto l'header.
   c. Evita la DOPPIA istanza: dentro "p LIVE_PPOOLL_ENVIRONMENT" togli il cavo da
      "loadmess ppooll_host.maxpat" -> "p create-act-bpatcher" (cosi' non crea una seconda
      istanza ne' porta in primo piano una finestra). Cancella anche l'oggetto statico
      "freeverb@.maxpat" li' dentro. Deve restare UNA sola istanza dell'act = il bpatcher.
   d. Salva. In Live re-inserisci il device e fai la VERIFICA qui sotto.

3) Se passa audio e si vede il pannello MA i parametri non rispondono o i preset non si
   richiamano (ppooll_host non "registra" l'act perche' non l'ha creato lui), passa
   all'APPROCCIO B:
   - Rimetti il cavo loadmess -> create-act-bpatcher (lascia che sia ppooll_host a creare/
     registrare l'act), ma modifica "p create-act-bpatcher" perche' l'act venga mostrato nel
     pannello del device invece di aprire una finestra in primo piano (togli/cambia la parte
     "script ... front"). Obiettivo: 1 sola istanza, registrata da ppooll_host, visibile inline.

VERIFICA (traccia audio con audio in loop):
   [ ] il pannello dell'act si vede DENTRO il device (niente finestra esterna)
   [ ] nessun "stack overflow" in Max Console
   [ ] l'audio passa, il riverbero si sente
   [ ] manopole/parametri rispondono
   [ ] salva il set, riapri -> il device ricarica con lo stato

Quando un approccio funziona: salva il .amxd e DAMMELO (oppure dimmi la ricetta esatta: oggetti
aggiunti/rimossi, attributi del bpatcher, modifiche a create-act-bpatcher). Non toccare i file
dentro Packages/ppooll: lavora solo sul .amxd del device.
```

## After the prototype works → auto-scale to all 131
Send the working `freeverb@` device (or the exact recipe) back. The build pipeline will then:
- add the display `bpatcher` for each act, sized per `tools/act_embed_info.json`
  (per-act window size; bpatcher I/O = 0/0),
- apply the same single-instance change, and
- set the device `openinpresentation` so the embedded panel is what Live shows,
across all 131 in one pass (with the same static validation already in place).
