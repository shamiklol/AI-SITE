#!/usr/bin/env python3
"""Build sfx.wav from cue json, then mix voice + music + sfx with ffmpeg."""
import sys, json, subprocess, wave
import numpy as np

WD = sys.argv[1]
VID = sys.argv[2] if len(sys.argv) > 2 else 'video.mp4'
VOICE = sys.argv[3] if len(sys.argv) > 3 else 'voice-1.mp3'
TEMPO_ARG = float(sys.argv[4]) if len(sys.argv) > 4 else 1.03
OUTWAV = sys.argv[5] if len(sys.argv) > 5 else 'mix.wav'
cues = json.load(open(f'{WD}/{VID}.cues.json'))
SR = 48000
TOTAL = 45.0
rng = np.random.default_rng(7)
out = np.zeros(int(SR * TOTAL))

def add(sig, t, g=1.0):
    i = int(t * SR)
    j = min(len(out), i + len(sig))
    if i < len(out):
        out[i:j] += sig[:j - i] * g

def whoosh(d=0.28):
    n = int(SR * d)
    x = rng.standard_normal(n)
    # sweep low-pass: running average with shrinking window
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t) ** 1.5
    y = np.convolve(x, np.ones(12) / 12, 'same') * env
    return y / np.abs(y).max() * 0.5

def pop(d=0.07):
    n = int(SR * d); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 30) + 300
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 55)
    return y * 0.6

def impact(d=0.45):
    n = int(SR * d); t = np.arange(n) / SR
    f = 120 * np.exp(-t * 8) + 45
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    y += rng.standard_normal(n) * np.exp(-t * 40) * 0.25
    return y * 0.8

def click():
    n = int(SR * .025); t = np.arange(n) / SR
    return rng.standard_normal(n) * np.exp(-t * 300) * 0.5

cards = set(round(c, 3) for c in cues['cards'])
for t in cues['cuts']:
    if round(t, 3) in cards:
        add(impact(), t, 0.9)
    else:
        add(whoosh(), max(t - 0.12, 0), 0.55)
for t in cues['caps']:
    add(pop(), t, 0.45)
# typing clicks on the БИЗНЕС card
typing_t = [c for c in cues['cards']][-2]
for k in range(6):
    add(click(), typing_t + 0.05 + k * 0.09, 0.8)

out = np.clip(out, -1, 1)
with wave.open(f'{WD}/sfx.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes())

TEMPO, LEAD = TEMPO_ARG, 0.2
fc = (
    f"[0:a]atempo={TEMPO},aresample=48000,adelay={int(LEAD*1000)}:all=1,loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000,apad,asplit=2[v][v2];"
    f"[1:a]aresample=48000,volume=0.22,afade=t=in:d=0.3,afade=t=out:st={TOTAL-1.5}:d=1.5[m];"
    f"[2:a]aresample=48000,volume=0.55[s];"
    f"[m][v]sidechaincompress=threshold=0.04:ratio=3:attack=20:release=300[md];"
    f"[v2][md][s]amix=inputs=3:normalize=0:duration=first,atrim=0:{TOTAL},alimiter=limit=0.95[a]"
)
subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                '-i', f'{WD}/{VOICE}', '-i', f'{WD}/music.mp3', '-i', f'{WD}/sfx.wav',
                '-filter_complex', fc, '-map', '[a]', '-ar', '48000', '-ac', '2', f'{WD}/{OUTWAV}'], check=True)
