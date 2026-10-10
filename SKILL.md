---
name: opus-video-short
description: >
  Make a ~35 s 9:16 comedy explainer Short the way the "Bad Days in History" episodes were made
  (dino extinction, Great Emu War, Titanic): Claude writes the brief, one Opus subagent builds
  picture + local voice + comedy sound + measured mix in a single pass with HyperFrames, the MP4
  is delivered without commentary, the user dictates the next pass. Use when the user says "opus video",
  "code video", "make a short", "next episode", "bad days in history", names a catastrophe/topic
  for the series, or asks for a funny faceless explainer. Not for live-action, generative-video
  models, or long-form (use the HyperFrames skills directly for other shapes).
---

# opus-video-short — the code-rendered comedy Short, the way that worked

"Opus video" is not a video model. The model writes deterministic animation code (HyperFrames
HTML/GSAP), a headless browser screenshots every frame, ffmpeg encodes. Quality comes from the
process below, not from a one-line "go all out" prompt. Proven: dino v5 (5 passes), Emu War
(**first render accepted** once the mix targets were in the brief), Titanic (in build).

Model routing: the build runs as **one Opus subagent at high effort**. Use another model only when the user asks.
Budget: **$0** — local Kokoro voice, Parakeet timings, sound files the user already owns or licensed (in `$OVS_SOUNDS_DIR`). Nothing downloaded,
nothing paid, ever, without the user saying so.

## Files this skill ships
- `references/brief-template.md` — the BRIEF.md that produced a first-render pass. Copy, fill, keep every section.
- `references/mix-and-sound.md` — the approved mix targets, the comedy sound kit, cue-sheet and LISTEN.md patterns, the rejected mixes.
- `references/subagent-prompt.md` — the dispatch prompt for the build subagent.
- `tools/level_check.py` — per-word VO vs bed+SFX measurement, PASS/FAIL both ways (generic: reads `.hyperframes/timeline.json`).
- `tools/build_audio.py`, `tools/splice_vo.py` — the audio build and comedy-pause splicer from the Emu War project, as reference implementations (cue list in `tools/cues.json`, music beds in `tools/beds.json`, both relative to `$OVS_SOUNDS_DIR`; edit per project).

## The process (7 steps, in order)

1. **Topic → facts line.** Research the event; write 8–15 verified facts with numbers and dates. Only these facts go in the script. Comedy targets decisions and hubris, never victims (Titanic rule).
2. **Write BRIEF.md yourself** from `references/brief-template.md`: message, beat sheet with target times (hook ≤ 3 s, one dead-silent white hold on the punch moment, 2–3 s punchline card), palette, motion vocabulary, cast, sound ideas, **mix targets written in**, facts, negatives. `storyboard: no`, `flow: automation` — straight to a render ([deliver, don't narrate](#review-rule)).
3. **Project.** `$OVS_PROJECTS_DIR/<topic>-short/` (default `./videos`), `npx hyperframes init` with `--skill=faceless-explainer`, series frame.md reused from the previous episode (new cast, same atoms: ink outlines, hard offset shadows, Fredoka cream captions, squash-and-stretch).
4. **Dispatch one Opus subagent** (high effort) with `references/subagent-prompt.md`. It runs: frame packets → 7 frame HTMLs → Kokoro VO at 1.08× with spliced comedy pauses → Parakeet word timings → cue sheet from the user's own sounds → `build_audio.py` to the targets → assemble → lint/check → contact sheet → fix top 3 → `--quality looks` → `tools/level_check.py` PASS.
5. **Deliver** `renders/video.mp4` (1080×1920, H.264, ≤ 30 MiB) with LISTEN.md's 5 spots. One-line caption. Stop.
6. **The user's pass.** They dictate corrections ("music +2 dB", "voice not hearable at 0:12"). Each pass = one measured change, new LEVELS-Vn.md, re-run `level_check.py`, redeliver. Keep v1…vN in `renders/`.
7. **Save.** On "done. save this": copy to `renders/final.mp4`, write the Status block into BRIEF.md, and (optionally) log the episode in your own notes/series queue. The next topic reuses this project as `../<prev>-short` reference.

## Review rule
When a render completes: compress under 30 MiB if needed → send the file → one line → **stop**. No self-review, no "I noticed". The user is the editor. Silent QC of inputs (facts, character consistency, `level_check` PASS) is fine because it gates the build.

## Gates that must pass before delivery
- `level_check.py` → `RESULT: PASS` (VO −16.7 ± 2 dBFS RMS per line; bed ≤ −25 while speaking and ≥ −31 so it is not buried; every word ≥ 6 dB over bed+SFX, quiet words ≥ 5; white hold silent).
- Master −14 LUFS, −1 … −2 dBTP (`ffmpeg -af loudnorm=print_format=json` or `ebur128`).
- Captions inside the 9:16 safe zone, one big phrase per beat, slams on the spoken word, dead still while read.
- No crossfades, gradients, purple-blue "AI" look, synth beeps, corporate whooshes, realistic violence, stock photos. One sonic family per film.
- Facts on screen match the facts line; years and counts shown, not spoken, when the VO is over length.

## What breaks it (measured)
- Mix targets missing from the brief → 5 passes (dino). With them → 1 pass (emu). Always write them in.
- One-line prompts → generic showreel. The 10k-char brief with beats, facts and motion vocabulary is the work.
- Opus can't hear: synth-beep defaults unless the kit paths and the cue-sheet pattern are given.
- Music 18–25 dB under = "so down"; music 9 dB under with unducked SFX = "voice not hearable". ~10 dB under with the sidechain + 2.5 kHz carve is the approved window.
- VO over length → trim the script (numbers on screen only), never speed the voice past 1.08×.

## Configuration
- `OVS_SOUNDS_DIR` — root of your sound library (default `./sounds`). Every `src` in `tools/cues.json` and every bed in `tools/beds.json` is relative to it. No sounds ship with this skill.
- `OVS_PROJECTS_DIR` — where episode projects live (default `./videos`).
- `OVS_CUES`, `OVS_BEDS` — override the cue/bed file paths for `build_audio.py`.
