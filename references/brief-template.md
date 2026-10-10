# BRIEF.md template — the shape that passed on the first render (Emu War, 2026-10-10)

Copy everything. Replace `<...>`. Keep every section; the subagent reads all of it.

```markdown
---
workflow: faceless-explainer
flow: automation
storyboard: no
message: "<one sentence: the whole joke/fact, with a number in it>"
destination: shorts
aspect: 1080x1920
language: en
audience: general YouTube Shorts / Reels viewers, zero history background, 8–80
length: 32-38s
angle: narrative (comedy, deadpan documentary; jokes target decisions and hubris, never victims)
voice: kokoro af_heart
series: "Bad Days in History" — episode <N> (ep 1 = ../dino-extinction-short, ep 2 = ../emu-war-short)
---

## Intent
Episode <N> of **Bad Days in History**: a ~35 s funny faceless explainer on <event, place, dates>.
Comedy engine: a calm, deadpan documentary narrator states facts while the cartoon cast panics,
stays smugly oblivious, or never reacts. Every joke is a visual gag pinned to a spoken word.
Viewer should laugh, learn the real sequence, and share.

## Assets
- none generated; reuse the previous episode's character-kit *approach* (frame.md atoms: ink
  8–12 px outlines, hard offset shadows, Fredoka 700 cream captions, dot/round eyes,
  squash-and-stretch). New characters: <CAST: name, size, 2–3 defining shapes each>. Props: <...>.
- Series tag: small cream text "BAD DAYS IN HISTORY · No. <N>" top-left in the hook, inside the
  safe zone, gone by 2.5 s.

## Customizations
- English VO: local Kokoro af_heart at 1.08×, comedy pauses spliced (tools/splice_vo.py pattern),
  burned-in kinetic captions: one big word/phrase per beat, slams in on the word, holds still.
- Visual lane: "<series family> — <variant>". Palette: canvas <#hex>, ground <#hex>, accent <#hex>,
  cast colours <...>, cream text #FFF4D6, pure white #FFFFFF reserved for ONE hold.
- Motion vocabulary: squash-and-stretch springs; hard cuts, zero crossfades; <signature move of this
  cast>; one smash-zoom; one 1 s dead-silent white hold on <the moment>; slow Ken Burns push on
  "documentary" shots; 2–3 s hold on the punchline card.
- Beat sheet (target; VO drives exact timing):
  1. 0–3 s   Hook. "<line>" beat "<two-word punch>". Series tag visible. <visual>
  2. 3–8 s   Setup. "<line>" <visual gag on word>
  3. 8–13 s  <escalation> "<line>" Caption: "<numbers>"
  4. 13–19 s <the failure> "<line>" → white hold, silence → caption "<WORD>."
  5. 19–26 s <they try again> "<line>"
  6. 26–32 s <round two / numbers> "<line>"
  7. 32–36 s Punchline card: "<Final score — X: 1. Y: 0.>" beat "<last line>". Hold 2–3 s.
- Sound: cartoon-orchestra kit from your own library in $OVS_SOUNDS_DIR (see references/mix-and-sound.md
  for the sound roles that worked). Ideas per beat: <slide whistle on dashes, womp on the failure, tada on the
  score, clown horn on the vehicle...>. Music: pizzicato bed for setup → <pompous/march> for the
  antagonist → dead stop into the white hold → klezmer after. One bed at a time, never two.
- Mix: build to the APPROVED targets from the start (do not deliver a buried or a loud-music mix):
  VO −16 dBFS RMS per line, 3:1 compression, HPF 90 Hz, +2 dB @ 3 kHz; music ~10 dB under the
  voice while speaking (sidechain duck ≈ −10 dB, attack 80 ms, hold 700 ms, release 600 ms,
  look-ahead 150 ms, −3.5 dB @ 2.5 kHz carve during speech), swelling to −20…−24 dBFS between
  lines; SFX on words ≥ 7 dB under the voice plus a global −4 dB SFX duck; master −14 LUFS /
  −1 dBTP. Verify with tools/level_check.py (bed-during-speech threshold −25, bed-not-buried ≥ −31).

## Notes
- Facts to use (only these): <8–15 verified facts with dates, places, counts; the quotable line
  if any>.
- Keep it concept-led and neutral; no creator identity, no channel branding beyond the series tag.
- Phone-readable at all times: captions inside the 9:16 safe zone, big type.
- No stock-photo look, no purple-blue "AI" gradients, no crossfades, no realistic violence,
  nothing grim: <what must never be on screen>; tallies are numbers.
- Deliverable: renders/video.mp4 (1080x1920, H.264) — send to the user immediately, no self-review
  commentary; they dictate corrections.

## Status (<date>)
- <filled on "done. save this.">
```

## Why each part is there (measured)
- `storyboard: no` + `flow: automation` → the subagent goes straight to a render; the user reviews renders, not storyboards.
- Beat sheet with target seconds → the VO is trimmed to fit before animation; Emu War script went 42 s → 37 s with years on screen only.
- Mix paragraph → one pass instead of five.
- Facts line → no invented numbers; "only these" is the fence.
- Negative list → kills the generic "AI explainer" look the research warned about.
