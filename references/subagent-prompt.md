# Dispatch prompt — one Opus subagent, high effort, builds the whole Short

Fill `<...>`, send as the Agent prompt. Model: opus (another model only if the user asked). Run it in the background.

```
You are building episode <N> of "Bad Days in History", a ~35 s 9:16 comedy explainer, in
<PROJECT_ROOT> (already initialised with HyperFrames, skill faceless-explainer). Read, in order:
BRIEF.md (the contract — every section), frame.md (series design atoms; reuse
../<prev>-short/frame.md atoms, new cast), ~/.claude/skills/opus-video-short/references/mix-and-sound.md,
and the previous episode's SOUND.md + tools/ in ../<prev>-short/ (copy tools/, adapt cue list and
frame table).

Build everything in one pass, in this order, and do not stop to ask:
1. SCRIPT.md: 7 VO lines from the beat sheet, deadpan documentary delivery notes, total ≤ 36 s at
   Kokoro af_heart 1.08×. If over length, move years/counts to on-screen captions; never speed the
   voice further. Use only the facts in BRIEF.md.
2. VO: Kokoro af_heart 1.08× → assets/voice_raw/NN.wav; splice comedy pauses with tools/splice_vo.py
   (pause before the punch words, 1.0 s silent tail after the failure word = the white hold);
   Parakeet word timings → audio_meta.json; .hyperframes/timeline.json from the spliced durations.
3. STORYBOARD.md: 7 frames, each change pinned to a spoken word (frame-local word times), the one
   smash-zoom, the one dead-silent pure-white hold, 2–3 s punchline card, captions law
   (one big phrase per beat, slam 0.18 s on the word, dead still, hard-cut swap, safe zone).
4. Frames: compositions/frames/NN-*.html, flat 2D SVG cast per frame.md, squash-and-stretch,
   hard cuts, no crossfades/gradients/purple-blue/Math.random/Date.now/rAF/CSS transitions.
5. Sound: tools/cues.json from the user's own sounds only ($OVS_SOUNDS_DIR; the table in
   mix-and-sound.md names the sound roles that worked; run `tools/build_audio.py --dry-run` first), one bed at a time with a dead stop into the hold;
   tools/build_audio.py to the BRIEF mix targets → assets/voice-mix, assets/bgm/bed.wav, assets/sfx.
6. Assemble, `npx hyperframes check`, contact sheet, fix the top 3 visual problems, render
   `--quality looks` → renders/video.mp4 (1080x1920 H.264).
7. `python3 -I tools/level_check.py renders/video.mp4` must print RESULT: PASS (update its hold
   window). Measure −14 LUFS / ≤ −1 dBTP. If anything fails, fix the audio build and re-render; do
   not deliver a failing mix.
8. Write SOUND.md (cue sheet actually used, music windows, VO processing, "not used"), LISTEN.md
   (5 timestamps to ear-check), and the Status block in BRIEF.md.

Report back with: the MP4 path, duration, LUFS/dBTP, level_check result, and the three agent
calls you made that changed the brief (script trims, on-screen-only numbers, cast changes).
Nothing else — no self-review of the picture; the user reviews.
```

After it returns: send `renders/video.mp4` (compress under 30 MiB if needed) + the LISTEN.md lines. One line. Stop.
