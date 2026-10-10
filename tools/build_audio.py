#!/usr/bin/env python3
"""Build every audio stem for a Short in one pass (reference implementation from the Emu War demo), to the approved BRIEF mix targets.
VO   : HPF 90 Hz, +2 dB @3 kHz (Q1.2), 3:1 compression, make-up to VO_TARGET dBFS RMS per line, -3 dBFS limiter -> assets/voice-mix/
BED  : pizz (beats 1-2) | tuba march + marching snare (beat 3-4, dead stop at "jammed") | silence (white hold) | klezmer (beat 5-end, 1.5 s fade)
       sidechain duck from the VO (depth DUCK_DB, attack 80 ms, hold 700 ms, release 600 ms, look-ahead 150 ms)
       + dynamic carve -3.5 dB @2.5 kHz Q1 while speech is active -> assets/bgm/bed.wav
SFX  : each cue trimmed/faded, global -4 dB SFX duck keyed from VO, gain = min(free-level target, word-safe level) -> assets/sfx/NN-*.wav
Run from the project root (needs .hyperframes/timeline.json, audio_meta.json, tools/cues.json, tools/beds.json).
Sounds are YOUR files: every cue "src" and bed path is relative to $OVS_SOUNDS_DIR (default ./sounds).
Usage: python tools/build_audio.py [--vo -16.3] [--duck 9.5] [--bed-gap -20] [--dry-run]
  --dry-run  check that the project files and every referenced sound exist, then exit"""
import json, subprocess, sys, os
if '-h' in sys.argv or '--help' in sys.argv: print(__doc__); sys.exit(0)
SR = 48000
P = os.path.abspath(os.path.expanduser(os.environ.get('OVS_SOUNDS_DIR', 'sounds')))
CUES_PATH = os.environ.get('OVS_CUES', 'tools/cues.json'); BEDS_PATH = os.environ.get('OVS_BEDS', 'tools/beds.json')
args = sys.argv[1:]
if '--dry-run' in args:
    miss = [p for p in ('.hyperframes/timeline.json', 'audio_meta.json', CUES_PATH, BEDS_PATH) if not os.path.exists(p)]
    if os.path.exists(CUES_PATH) and os.path.exists(BEDS_PATH):
        B = json.load(open(BEDS_PATH)); srcs = [B[k] for k in ('setup', 'march', 'march_snare', 'after')] + [c['src'] for c in json.load(open(CUES_PATH))]
        miss += [f'{P}/{x}' for x in dict.fromkeys(srcs) if not os.path.exists(f'{P}/{x}')]
    print(f'sounds dir: {P}'); print('missing:' if miss else 'all inputs present', *miss, sep='\n  ')
    sys.exit(1 if miss else 0)
import numpy as np, soundfile as sf
def arg(k, d): return float(args[args.index(k)+1]) if k in args else d
VO_TARGET = arg('--vo', -16.3); DUCK_DB = arg('--duck', 9.5); BED_GAP = arg('--bed-gap', -20.0)
SFX_DUCK_DB = 4.0; CARVE_DB = -3.5
T = json.load(open('.hyperframes/timeline.json')); FR = {f['frame']: f for f in T['frames']}; TOTAL = T['total']
N = int(round(TOTAL*SR))
m = json.load(open('audio_meta.json'))

def ff(cmd_in, af=None, ch=2, extra_in=()):
    cmd = ['ffmpeg', '-v', 'error', *extra_in, '-i', cmd_in]
    if af: cmd += ['-af', af]
    cmd += ['-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).copy()
    return x.reshape(-1, ch) if ch > 1 else x
def db(x): return 20*np.log10(np.sqrt(np.mean(np.square(x))) + 1e-12) if len(x) else -120
def rms_win(x, t0, t1):
    a, b = max(0, int(t0*SR)), min(len(x), int(t1*SR)); return db(x[a:b]) if b > a else -120
def ffilter(x, af, ch):
    """run a float buffer through an ffmpeg filter chain"""
    p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', str(ch), '-i', '-', '-af', af,
                        '-f', 'f32le', '-ar', str(SR), '-ac', str(ch), '-'], input=x.astype(np.float32).tobytes(), capture_output=True, check=True).stdout
    y = np.frombuffer(p, dtype=np.float32).copy()
    y = y.reshape(-1, ch) if ch > 1 else y
    if len(y) < len(x): y = np.concatenate([y, np.zeros((len(x)-len(y),) + y.shape[1:], np.float32)])
    return y[:len(x)]

# ---------------- VO ----------------
os.makedirs('assets/voice-mix', exist_ok=True)
vo_stem = np.zeros(N, np.float32); vo_report = []
for v in m['voices']:
    f = v['frame']; src = f'assets/voice/{f:02d}.wav'
    x = ff(src, ch=1)
    w = v['words']; t0, t1 = w[0]['start'], w[-1]['end']
    if 'raw_words' not in v: v['raw_words'] = [dict(q) for q in w]
    w = v['words'] = [dict(q) for q in v['raw_words']]; t0, t1 = w[0]['start'], w[-1]['end']
    pre = rms_win(x, t0, t1)
    thr = 10**((pre + 4)/20)   # compress the louder half of the speech 3:1
    y = ffilter(x, f'highpass=f=90,equalizer=f=3000:width_type=q:w=1.2:g=2,acompressor=threshold={thr:.5f}:ratio=3:attack=5:release=80:makeup=1', 1)
    y *= 10**((VO_TARGET - rms_win(y, t0, t1))/20)
    y = ffilter(y, 'alimiter=limit=0.6683:attack=2:release=40:level=disabled', 1)   # -3 dBFS ceiling
    y *= 10**((VO_TARGET - rms_win(y, t0, t1))/20)
    # refine Parakeet word edges to the voiced energy (Parakeet starts can sit up to 0.2 s early in spliced pauses)
    hop10 = int(0.01*SR); lvl = lambda t: db(y[int(t*SR):int(t*SR)+hop10])
    for k, wd in enumerate(w):
        nxt = w[k+1]['start'] if k+1 < len(w) else len(y)/SR
        lo = max(0.0, wd['start'] - 0.06); hi = max(wd['end'], lo + 0.02)
        ts = [round(lo + j*0.01, 3) for j in range(int((hi-lo)/0.01)+1)]
        on = [t for t in ts if lvl(t) > -36]
        if on:
            st = on[0]
            te = max([t for t in ts if t >= st and lvl(t) > -36]) + 0.01
            wd['start'] = round(st, 3); wd['end'] = round(min(max(te, st + 0.06), nxt + 0.05), 3)
    out = f'assets/voice-mix/{f:02d}.wav'; sf.write(out, y, SR, subtype='PCM_24')
    v['path'] = out; v['duration_s'] = round(len(y)/SR, 3)
    s0 = int(round(FR[f]['start']*SR)); vo_stem[s0:s0+len(y)] += y[:N-s0]
    vo_report.append((f, round(rms_win(y, t0, t1), 2), round(20*np.log10(np.max(np.abs(y))+1e-9), 2)))

# ---------------- key / envelopes ----------------
hop = int(0.001*SR)                               # 1 ms control rate
nh = N//hop + 1
fr_rms = np.array([db(vo_stem[i*hop:i*hop+10*hop]) for i in range(nh)])  # 10 ms window
active = fr_rms > -40
la = 150; ahead = active.copy()
for k in range(1, la+1): ahead[:-k] |= active[k:]          # look-ahead 150 ms
held = ahead.copy(); last = -10**9
for i in range(nh):                                         # hold 700 ms
    if ahead[i]: last = i
    elif i - last <= 700: held[i] = True
def envelope(depth_db, att_ms=80, rel_ms=600):
    g = np.zeros(nh); cur = -depth_db if held[0] else 0.0
    for i in range(nh):
        tgt = -depth_db if held[i] else 0.0
        if tgt < cur: cur = max(tgt, cur - depth_db/att_ms)
        elif tgt > cur: cur = min(tgt, cur + depth_db/rel_ms)
        g[i] = cur
    return g
def to_samples(e): return np.interp(np.arange(N)/hop, np.arange(nh), e).astype(np.float32)
duck_bed = to_samples(envelope(DUCK_DB)); duck_sfx = to_samples(envelope(SFX_DUCK_DB))
carve_mix = to_samples(envelope(1.0))*-1.0          # 0..1, same ballistics

# ---------------- BED ----------------
def loop_to(x, n):
    reps = int(np.ceil(n/len(x))); return np.concatenate([x]*reps)[:n]
def fade(x, fin=0.005, fout=0.005):
    x = x.copy(); a = int(fin*SR); b = int(fout*SR)
    if a: x[:a] *= np.linspace(0, 1, a)[:, None]
    if b: x[-b:] *= np.linspace(1, 0, b)[:, None]
    return x
def set_rms(x, target): return x*10**((target - db(x))/20)
def tame(x):
    r = db(x); thr = 10**((r + 2)/20)
    return ffilter(x, f'acompressor=threshold={thr:.5f}:ratio=4:attack=3:release=120:makeup=1,alimiter=limit=0.5:attack=1:release=50:level=disabled', 2)
t_march = FR[3]['start']; t_white = round(FR[4]['start'] + 3.33, 3); t_klez = FR[5]['start']
BEDS = json.load(open(BEDS_PATH))
bed = np.zeros((N, 2), np.float32)
pizz = ff(f"{P}/{BEDS['setup']}")
n1 = int(t_march*SR); seg = set_rms(tame(loop_to(pizz, n1)), BED_GAP); bed[:n1] += fade(seg, 0.0, 0.012)
tuba = ff(f"{P}/{BEDS['march']}")
snare = ff(f"{P}/{BEDS['march_snare']}", af=f"atempo={BEDS.get('march_snare_atempo', 1.0)}")
n2 = int(t_white*SR) - n1
march = set_rms(loop_to(tuba, n2), BED_GAP - 1.0) + set_rms(loop_to(snare, n2), BED_GAP - 7.0)
march = set_rms(tame(march), BED_GAP); bed[n1:n1+n2] += fade(march, 0.004, 0.004)       # dead stop into the white hold
klez = ff(f"{P}/{BEDS['after']}")
n3s = int(t_klez*SR); n3 = N - n3s
kseg = set_rms(tame(loop_to(klez, n3)), BED_GAP - 1.0)
fo = int(1.5*SR); kseg[-fo:] *= np.linspace(1, 0, fo)[:, None]
bed[n3s:] += fade(kseg, 0.004, 0.0)
carved = ffilter(bed, f'equalizer=f=2500:width_type=q:w=1:g={CARVE_DB}', 2)
bed = bed*(1 - carve_mix[:, None]) + carved*carve_mix[:, None]
bed *= (10**(duck_bed/20))[:, None]
bm0 = bed.sum(1)*0.70710678
protect = np.zeros(N, np.float32); dips = 0
for v in m['voices']:
    for wd in v['words']:
        w0 = FR[v['frame']]['start'] + wd['start']; w1 = FR[v['frame']]['start'] + wd['end']
        if w1 - w0 < 0.05: continue
        need = (rms_win(bm0, w0, w1) + 9.5) - rms_win(vo_stem, w0, w1)
        if need > 0:
            a0, a1 = int((w0-0.05)*SR), int((w1+0.05)*SR); r = int(0.05*SR)
            env = np.full(a1-a0, -need, np.float32); env[:r] *= np.linspace(0, 1, r); env[-r:] *= np.linspace(1, 0, r)
            protect[a0:a1] = np.minimum(protect[a0:a1], env); dips += 1
bed *= (10**(protect/20))[:, None]
print('vocal-protect dips on', dips, 'words')
bed[int(t_white*SR):n3s] = 0.0                       # measured dead silence through the white hold
os.makedirs('assets/bgm', exist_ok=True); sf.write('assets/bgm/bed.wav', bed, SR, subtype='PCM_24')
m['bgm'] = {'path': 'assets/bgm/bed.wav', 'source': 'host', 'volume': 1, 'duration_s': round(N/SR, 3)}
bed_mono = bed.sum(1)*0.70710678   # same stereo->mono convention as ffmpeg/level_check

# ---------------- SFX ----------------
# (frame, local_t, name, source, src_start, length, fade_out, free_target_dB)
CUES = json.load(open(CUES_PATH))
os.makedirs('assets/sfx', exist_ok=True)
for fn in os.listdir('assets/sfx'): os.remove('assets/sfx/' + fn)
words_global = [(FR[v['frame']]['start']+w['start'], FR[v['frame']]['start']+w['end'], w['text'], v['frame']) for v in m['voices'] for w in v['words']]
sfx_meta = []; sfx_stem = np.zeros(N, np.float32); rep = []
for i, c in enumerate(CUES):
    f, lt, name, src, s0, ln, fo_s, free = c['frame'], c['t'], c['name'], c['src'], c.get('start', 0.0), c['len'], c.get('fade', 0.05), c.get('free', -20.0)
    x = ff(f'{P}/{src}', af=c.get('af'))
    x = x[int(s0*SR):int((s0+ln)*SR)]
    x = fade(x, 0.003, fo_s)
    g0 = FR[f]['start'] + lt; a = int(round(g0*SR)); L = min(len(x), N-a)
    x = x[:L] * (10**(duck_sfx[a:a+L]/20))[:, None]
    # peak-window loudness (loudest 100 ms)
    mono = x.sum(1)*0.70710678; h = int(0.1*SR)
    pk = max(db(mono[j:j+h]) for j in range(0, max(1, L-h), int(0.02*SR)))
    gain = free - pk
    for (w0, w1, txt, wf) in words_global:            # word-safe limit
        if w1 - w0 < 0.08 or w1 <= g0 or w0 >= g0 + L/SR: continue
        vo_w = rms_win(vo_stem, w0, w1)
        if vo_w < -40: continue
        sfx_w = db(mono[max(0, int((w0-g0)*SR)):max(0, int((w1-g0)*SR))])
        bed_w = rms_win(bed_mono, w0, w1)
        lim1 = (vo_w - 7.5) - sfx_w                                  # >= 7.5 dB under the word
        # combined (bed+sfx) margin >= 6.6
        room = 10**((vo_w - 7.6)/10) - 10**(bed_w/10)
        lim2 = (10*np.log10(room) - sfx_w) if room > 0 else -60
        gain = min(gain, lim1, lim2)
    gain = min(gain, -6.0 - 20*np.log10(np.max(np.abs(x)) + 1e-9))
    x *= 10**(gain/20)
    out = f'assets/sfx/{i:02d}-{name}.wav'; sf.write(out, x, SR, subtype='PCM_24')
    sfx_stem[a:a+L] += x.sum(1)*0.70710678
    sfx_meta.append({'frame': f, 'file': out, 'offset_s': lt, 'duration_s': round(L/SR, 3), 'volume': 1, 'source': 'host', 'src': src})
    rep.append(f'{i:02d} {g0:6.2f}s {name:18s} gain {gain:6.1f} dB  peak100ms {pk+gain:6.1f}')
m['sfx'] = sfx_meta
json.dump(m, open('audio_meta.json', 'w'), indent=1)

# ---------------- offline mix for loudness ----------------
mix = vo_stem[:, None] + bed + sfx_stem[:, None]*0  # placeholder (sfx stereo added below)
mix = np.repeat(vo_stem[:, None], 2, 1) + bed
for s in sfx_meta:
    y, _ = sf.read(s['file'], dtype='float32'); a = int(round((FR[s['frame']]['start']+s['offset_s'])*SR)); mix[a:a+len(y)] += y[:N-a]
os.makedirs('.hyperframes/level-analysis', exist_ok=True)
sf.write('.hyperframes/level-analysis/offline_mix.wav', mix, SR, subtype='FLOAT')
r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', '.hyperframes/level-analysis/offline_mix.wav', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = [l for l in r.splitlines() if l.strip().startswith('I:')][-1].split()[1]; TP = [l for l in r.splitlines() if 'Peak:' in l][-1].split()[1]
print('VO lines (frame, RMS over words, peak):', vo_report)
print('\n'.join(rep))
print(f'BED gap target {BED_GAP}, duck {DUCK_DB} dB | white hold {t_white}-{t_klez}')
print(f'OFFLINE MIX: I {I} LUFS  TP {TP} dBTP')
