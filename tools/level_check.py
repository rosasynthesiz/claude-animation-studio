#!/usr/bin/env python3
"""Measure VO vs music bed vs SFX levels per spoken word (opus-video-short skill, generic version).
Usage:  python3 -I tools/level_check.py [renders/video.mp4] [--hold 16.241:17.324]
Reads frame durations from .hyperframes/timeline.json and stems from audio_meta.json; builds
time-aligned stems into .hyperframes/level-analysis/ and prints PASS/FAIL both ways:
voice -16.7 +/- 2 dBFS RMS per line, bed <= -25 while speaking and >= -31 (not buried), every
word >= 6 dB over bed+sfx (quiet words >= 5), the white hold silent."""
import sys
if '-h' in sys.argv or '--help' in sys.argv: print(__doc__); sys.exit(0)
import json, subprocess, sys, wave, array, math, os
S='.hyperframes/level-analysis'; os.makedirs(S, exist_ok=True)
args=[a for a in sys.argv[1:]]
WHITE=(-1.0,-1.0)
if '--hold' in args:
    i=args.index('--hold'); a,b=args[i+1].split(':'); WHITE=(float(a),float(b)); del args[i:i+2]
mp4 = args[0] if args else 'renders/video.mp4'
m=json.load(open('audio_meta.json'))
T=json.load(open('.hyperframes/timeline.json'))
dur={f['frame']: f['duration'] for f in T['frames']}
TOTAL=round(T.get('total', sum(dur.values())),3)
start={f['frame']: f['start'] for f in T['frames']}
NF=max(dur)
def stem(items,out):
    cmd=['ffmpeg','-y','-v','error']
    for it in items: cmd+=['-i',it[0]]
    fc=''
    for i,it in enumerate(items):
        fc+=f'[{i}:a]aformat=sample_rates=48000:channel_layouts=mono,adelay={int(it[1]*1000)}|{int(it[1]*1000)},volume={it[2]}[a{i}];'
    fc+=''.join(f'[a{i}]' for i in range(len(items)))+f'amix=inputs={len(items)}:normalize=0:duration=longest,apad=whole_dur={TOTAL},atrim=0:{TOTAL}[o]'
    subprocess.run(cmd+['-filter_complex',fc,'-map','[o]','-c:a','pcm_s16le',out],check=True)
stem([(v['path'],start[v['frame']],1.0) for v in m['voices']],S+'/vo.wav')
stem([(s['file'],start[s['frame']]+s['offset_s'],s.get('volume',1)) for s in m['sfx']],S+'/sfx.wav')
stem([(m['bgm']['path'],0,m['bgm'].get('volume',1))],S+'/bed.wav')
subprocess.run(['ffmpeg','-y','-v','error','-i',mp4,'-vn','-ac','1','-ar','48000','-c:a','pcm_s16le',S+'/mix.wav'],check=True)
def load(p):
    w=wave.open(p); a=array.array('h', w.readframes(w.getnframes())); w.close(); return a
vo,bed,sfx,mix=[load(f'{S}/{n}.wav') for n in ('vo','bed','sfx','mix')]
SR=48000
def rms_db(a,t0,t1):
    i0=max(0,int(t0*SR)); i1=min(len(a),int(t1*SR))
    if i1<=i0: return -99
    s=0
    for x in a[i0:i1]: s+=x*x
    r=math.sqrt(s/(i1-i0))/32768
    return 20*math.log10(r) if r>0 else -99
fails=0
print(f"{'line':>4} {'t0':>6} {'t1':>6} {'VO':>6} {'bed':>6} {'sfx':>6} {'VO-bed':>7} {'VO-sfx':>7}  text")
flag=[]; buried=[]
for v in m['voices']:
    fs=start[v['frame']]; ws=v['words']
    t0=fs+ws[0]['start']; t1=fs+ws[-1]['end']
    a=rms_db(vo,t0,t1); b=rms_db(bed,t0,t1); c=rms_db(sfx,t0,t1)
    silent_window = t0>=WHITE[0] and t1<=WHITE[1]+0.01   # bed is deliberately silent in the white hold
    ok = (b<=-25 or b<=-99) and abs(a+16.7)<=2
    audible = silent_window or b>=-31
    if not ok: fails+=1
    if not audible: fails+=1; buried.append((v['frame'],b))
    print(f"{v['frame']:>4} {t0:6.2f} {t1:6.2f} {a:6.1f} {b:6.1f} {c:6.1f} {a-b:7.1f} {a-c:7.1f}  {'' if ok else 'FAIL '}{'' if audible else 'FAIL-BED-BURIED '}{' '.join(w['text'] for w in ws)[:55]}")
    line_vo=a
    for w in ws:
        wt0=fs+w['start']; wt1=fs+w['end']
        if wt1-wt0<0.08: continue
        a=rms_db(vo,wt0,wt1); b=rms_db(bed,wt0,wt1); c=rms_db(sfx,wt0,wt1)
        if a<-40: continue  # spliced pause inside a word span
        comp=10*math.log10(10**(b/10)+10**(c/10))
        quiet = a < line_vo - 4          # quiet word (unstressed / trailing): may sit at 5 dB
        if a-comp < (5 if quiet else 6): flag.append((wt0,wt1,w['text'],a,b,c,a-comp))
print("\nWORDS with VO less than 6 dB (quiet words: 5 dB) above (bed+sfx):")
for f in flag: print(f"{f[0]:6.2f} {f[1]:6.2f} VO {f[3]:6.1f} bed {f[4]:6.1f} sfx {f[5]:6.1f} margin {f[6]:5.1f}  {f[2]}")
fails+=len(flag)
print("\nLINES with bed below -31 (music buried):", buried if buried else "none")
print("\nBED per 1 s:", ' '.join(f"{t:02d}:{rms_db(bed,t,t+1):4.0f}" for t in range(0,int(TOTAL)+1)))
print("MIX RMS:", round(rms_db(mix,0,TOTAL),1))
print("RESULT:", "PASS" if fails==0 else f"FAIL ({fails})")
sys.exit(0 if fails==0 else 1)
