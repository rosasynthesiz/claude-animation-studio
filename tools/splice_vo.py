#!/usr/bin/env python3
"""Splice comedy pauses into Kokoro VO lines (method: cut at the
quietest 10 ms point in the inter-word gap, insert digital silence, 5 ms fades).
Reads assets/voice_raw/NN.wav + audio_meta.json (raw word times), writes assets/voice/NN.wav.
Edit SPLICES below per project (the values are from the Emu War demo). Run from the project root."""
import sys
if '-h' in sys.argv or '--help' in sys.argv: print(__doc__); sys.exit(0)
import json, numpy as np, soundfile as sf
m = json.load(open('audio_meta.json'))
# (frame, index of the word the pause goes BEFORE (or 'end'), seconds)
SPLICES = {1: [('on', 0, 0.45)], 6: [('ten', 1, 0.40)], 7: [('the', 2, 0.45)], 4: [('END', 0, 1.0)]}
for v in m['voices']:
    f = v['frame']; raw = f'assets/voice_raw/{f:02d}.wav'
    x, sr = sf.read(raw, dtype='float32')
    if x.ndim > 1: x = x.mean(1)
    pieces = []; cur = 0
    for word, nth, secs in SPLICES.get(f, []):
        if word == 'END':
            continue
        hits = [i for i, w in enumerate(v['words']) if w['text'].lower().strip('.,:') == word]
        i = hits[nth]
        a = v['words'][i-1]['end'] - 0.06; b = v['words'][i]['start'] + 0.04
        a_i, b_i = int(a*sr), int(b*sr); win = int(0.01*sr)
        best, bt = 1e9, a_i
        for s in range(a_i, max(a_i+1, b_i-win), int(0.002*sr)):
            e = float(np.sqrt(np.mean(x[s:s+win]**2)))
            if e < best: best, bt = e, s + win//2
        print(f'frame {f}: pause {secs}s before "{v["words"][i]["text"]}" at {bt/sr:.3f}s (rms {20*np.log10(best+1e-9):.1f} dB)')
        pieces.append(x[cur:bt].copy()); cur = bt
        pieces.append(np.zeros(int(secs*sr), dtype='float32'))
    pieces.append(x[cur:].copy())
    # 5 ms fades around every cut
    fade = int(0.005*sr)
    for p in pieces:
        if len(p) > 2*fade and np.any(p):
            p[:fade] *= np.linspace(0, 1, fade); p[-fade:] *= np.linspace(1, 0, fade)
    y = np.concatenate(pieces)
    for word, nth, secs in SPLICES.get(f, []):
        if word == 'END':
            y = np.concatenate([y, np.zeros(int(secs*sr), dtype='float32')])
            print(f'frame {f}: {secs}s silent tail after "{v["words"][-1]["text"]}"')
    sf.write(f'assets/voice/{f:02d}.wav', y, sr, subtype='PCM_16')
    print(f'{f:02d}: {len(x)/sr:.3f}s -> {len(y)/sr:.3f}s')
