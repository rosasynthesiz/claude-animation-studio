# Mix targets, sound kit, cue sheet — what was approved (2026-10-10)

## Mix targets (locked over dino v3 → v5, confirmed first-render on Emu War)
| layer | while VO speaks | gaps |
|---|---|---|
| voice | −16 dBFS RMS per line (−16.7 ± 2 so the master lands on −14 LUFS), 3:1 comp, HPF 90 Hz, +2 dB @ 3 kHz Q1.2, −3.5 dBFS limiter | — |
| music bed | **~10 dB under voice**: sidechain duck −9.5…−10 dB keyed from the VO stem, attack 80 ms, hold 700 ms, release 600 ms, look-ahead 150 ms; dynamic carve −3.5 dB @ 2.5 kHz Q1 during speech; measured −28.5…−29.6 dBFS RMS per line (≤ −25, ≥ −31) | −20 to −24 dBFS RMS |
| SFX on words | ≥ 7 dB under the word it overlaps, peak ≤ −6 dBFS, global −4 dB duck keyed from VO; hero hits (impact, tada) free in gaps | free |
| white hold | bed and SFX zeroed; measured RMS −88 dBFS | |
| master | −14 LUFS, −1 … −2 dBTP | |

Rejected: music 18–25 dB under (dino v3: "so down"); music 9 dB under with unducked SFX (v2: "not hearable"). Quiet words sit at 5–6 dB margin at the final level — ride them +2 dB if they blur. A word-level "vocal protect" dip on words where a loop transient would sit < 9.5 dB under them fixed the last fails.

## Comedy sound kit — bring your own (`$OVS_SOUNDS_DIR`, default `./sounds`)
No audio ships with this skill. The demo used a commercial sample library whose licence allows use in
your own productions but **not redistribution of the files**, so `tools/cues.json` and `tools/beds.json`
are templates with placeholder paths (`sfx/<role>.wav`, `music/<role>.wav`). Drop your own licensed or
royalty-free files at those paths, or edit the paths. Good free sources: Freesound (check each file's
licence), the YouTube Audio Library, or any sample pack whose licence covers your use.

One sonic family per film: "cartoon orchestra". No synth beeps, no corporate whooshes, no realistic war audio.

| job | placeholder file (under `$OVS_SOUNDS_DIR`) | what to look for |
|---|---|---|
| dash / swish | sfx/swish.wav | short cartoon foley swish |
| creature stare | sfx/bird-call.wav | calm bird call, 2–3 s |
| stroll / fat walk | sfx/fat-walk.wav | comedic heavy footsteps |
| things vanish | sfx/xylophone-run.wav | fast xylophone run |
| blink / shrug | sfx/xylophone-blink.wav | single xylophone blip (pitch +3 st for tiny things) |
| land / fall / fence | sfx/tympani-bounce.wav | bouncy tympani hit |
| ding (phone) | sfx/ding.wav | typewriter or bell ding |
| ding (counter) | sfx/counter-ding.wav | slot-machine / arcade ding |
| stamp / slap | sfx/slap.wav | dry slap |
| pop / rimshot | sfx/cartoon-pop.wav | cartoon percussion pop |
| run away | sfx/run-away.wav | cartoon scramble |
| slide whistle up / down | sfx/slide-whistle-up.wav · sfx/slide-whistle-down.wav · sfx/slide-down.wav | slide whistle |
| cartoon machine gun | sfx/snare-roll.wav | long acoustic snare roll (sliced) |
| jam / bend | sfx/boing-bend.wav | metal bend / boing |
| womp (failure) | sfx/womp.wav | "wrong" womp |
| clown horn (vehicle) | sfx/clown-horn.wav | bike/clown horn |
| honk (crowd laughs) | sfx/honk.wav | honk |
| soldier footsteps | sfx/marching-steps.wav | marching boots |
| tada | sfx/tada.wav | kids-game fanfare |
| glock medal | sfx/glockenspiel.wav | glockenspiel hit |
| extras for other casts | — | sad trombone, violin squeak (shiver), boings, goofy crash, goofy roar (+4 st), slurp, chicken |

Music beds (`tools/beds.json`; one at a time, hard switch on a cut, dead stop into the white hold):
- `setup`: idyll — pizzicato / acoustic folk loop (~100 bpm, looped, 4:1 tamed)
- `march` + `march_snare`: pompous army / authority — tuba loop + marching-snare loop (`march_snare_atempo` matches the snare tempo to the tuba, −6 dB under it)
- `after`: after the disaster — klezmer clarinet loop (looped, 1.5 s fade at the end)
- optional sting: a 1.6 s accordion flourish; fallback bed if the clarinet fights the VO: a goofy fretless-guitar riff

Search your library for a new cast with e.g. `rg -i "march|military|brass|tuba|fanfare|whistle|boing|womp" "$OVS_SOUNDS_DIR" --files`,
and check everything resolves with `python3 tools/build_audio.py --dry-run`.

## Cue sheet pattern (SOUND.md, written from `tools/cues.json`)
One row per cue: `# | time s | frame +offset | name | file | length | gain`. Music table above it with windows, source, treatment (gap level, duck, dead stop). VO block: splices (+0.45 s before the punch word, 1.0 s silent tail = the white hold), EQ/comp, measured RMS per line. "Not used" line: what was rejected (synth beeps, whooshes, realistic gunfire).

`cues.json` entry: `{"frame": 4, "t": 2.96, "name": "gun-jam-bend", "src": "sfx/boing-bend.wav", "start": 0.0, "len": 0.36, "fade": 0.05, "free": -22}` — `free` is the level when no word overlaps; the build picks min(free, word-safe).

## LISTEN.md pattern (ships with every render)
Five timestamps the user should ear-check, one line each: what happens, which cue, what must be true ("16.24–17.32 pure white, must be silent, measured −88.6 dBFS").

## Comedy pauses (`tools/splice_vo.py`)
Cut at the quietest 10 ms point in the inter-word gap, insert digital silence, 5 ms fades. Typical: +0.45 s before the two-word punch ("On birds."), +0.40 s before the kicker number, 1.0 s tail after the failure word (= the white hold). Word timings re-run after splicing.
