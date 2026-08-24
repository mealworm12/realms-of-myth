#!/usr/bin/env python3
"""
Realms of Myth — audio suite generator.

Deterministic pure-Python/numpy synthesis of every game sound + both music loops.
Outputs PCM 22050 Hz mono 16-bit WAVs into realms_of_myth_RP/sounds/.
Re-run any time to regenerate byte-identical audio (numpy seeded RNG).

Usage:  python3 audio-sources/gen_audio_suite.py   (from repo root)
"""
import os, wave, json
import numpy as np

SR = 22050
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "realms_of_myth_RP", "sounds")

rng = np.random.default_rng(1337)

# ---------------------------------------------------------------- core utils
def t(dur): return np.arange(int(SR * dur)) / SR

def env_ad(n, a=0.01, r=0.3, curve=3.0):
    """Attack/release envelope over n samples."""
    e = np.ones(n)
    na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    na = min(na, n); nr = min(nr, n)
    e[:na] = np.linspace(0, 1, na)
    e[n - nr:] *= np.linspace(1, 0, nr) ** curve
    return e

def env_exp(n, k=6.0):
    return np.exp(-k * np.arange(n) / n)

def osc(freq, dur, shape="sin", detune=0.0, fm=None):
    tt = t(dur)
    ph = 2 * np.pi * freq * tt
    if detune:
        ph += 2 * np.pi * freq * (1 + detune) * tt
    if fm is not None:
        ph += fm
    if shape == "sin":
        w = np.sin(ph)
    elif shape == "square":
        w = np.sign(np.sin(ph)) * 0.7
    elif shape == "saw":
        w = 2 * ((freq * tt) % 1) - 1
    elif shape == "tri":
        w = 2 * np.abs(2 * ((freq * tt) % 1) - 1) - 1
    else:
        w = np.sin(ph)
    return w

def noise(dur):
    return rng.uniform(-1, 1, int(SR * dur))

def lowpass(x, cutoff):
    """Simple one-pole lowpass with time-varying cutoff array or scalar."""
    n = len(x)
    if np.isscalar(cutoff):
        co = np.full(n, cutoff)
    else:
        co = np.interp(np.arange(n) / n, np.linspace(0, 1, len(cutoff)), cutoff)
    a = np.exp(-2 * np.pi * co / SR)
    y = np.empty(n); acc = 0.0
    for i in range(n):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y

def highpass(x, cutoff):
    return x - lowpass(x, cutoff)

def bandpass(x, lo, hi):
    return highpass(lowpass(x, hi), lo)

def reverb(x, mix=0.35, times=(0.031, 0.047, 0.061, 0.089), fb=0.42, damp=5500):
    """Feedback delay-network reverb tail."""
    n = len(x)
    wet = np.zeros(n)
    for d in times:
        nd = int(d * SR)
        buf = np.zeros(n + nd + int(0.8 * SR))
        sig = x.copy()
        pos = nd
        for rep in range(int(len(buf) / max(nd, 1))):
            end = min(pos + n, len(buf))
            if pos >= len(buf): break
            buf[pos:end] += sig[:end - pos]
            sig = lowpass(sig, damp) * fb
            pos += nd
        wet += buf[nd:nd + n] if len(buf) >= nd + n else np.pad(buf[nd:], (0, n))
    wet /= len(times)
    out = x * (1 - mix) + wet * mix
    # let the tail breathe past the dry end: append decayed tail
    tail_len = int(1.2 * SR)
    tail = np.zeros(tail_len)
    src = np.concatenate([x, np.zeros(tail_len)])
    twet = np.zeros(len(src))
    for d in times:
        nd = int(d * SR)
        shifted = np.zeros_like(src)
        shifted[nd:] = src[:-nd]
        twet += shifted
    twet /= len(times)
    full = src * (1 - mix) + lowpass(twet, damp) * mix * fb * 4
    return full[:len(x) + tail_len]

def pitch_env_mult(n, f0, f1, k=3.0):
    """Multiplicative glide factor array from f0->f1."""
    x = np.arange(n) / n
    return f0 * (f1 / f0) ** (x ** (1 / k))

def save(name, data, gain=0.9):
    path = os.path.join(RP, name + ".wav")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = np.asarray(data, dtype=np.float64)
    peak = np.max(np.abs(data)) or 1.0
    data = data / peak * gain
    pcm = (data * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"  {name}.wav  {len(pcm)/SR:.2f}s")

NOTE = {n: 440.0 * 2 ** ((i - 9) / 12) for i, n in enumerate(
    ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"])}
def freq(name, octave): return NOTE[name] * 2 ** (octave - 4)

def pluck(f, dur, bright=3000):
    """Karplus-strong-ish pluck string."""
    n = int(SR * dur)
    period = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, period) * env_exp(period, 1.5)
    out = np.zeros(n)
    damp = np.exp(-2 * np.pi * bright / SR)
    idx = 0; acc = 0.0
    for i in range(n):
        nxt = (idx + 1) % period
        acc = (buf[idx] + buf[nxt]) * 0.5
        buf[idx] = acc * damp
        out[i] = buf[idx]
        idx = nxt
    return out * env_ad(n, 0.002, dur * 0.6, 2)

# ================================================================ MOB SOUNDS
def dragon_roar():
    print("mob/dragon_roar")
    dur = 3.2
    tt = t(dur)
    # sub growl: FM'd low saw with slow vibrato
    vib = 40 * np.sin(2 * np.pi * 11 * tt)
    sub = osc(55, dur, "saw", detune=0.01, fm=vib * 0.02) * 0.8 \
        + osc(41, dur, "square") * 0.35
    sub = lowpass(sub, [900, 1400, 700, 400])
    # screech harmonics: detuned high formant sweep down
    f = pitch_env_mult(len(tt), 900, 320, 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    scr = (np.sin(ph) + 0.5 * np.sin(2.02 * ph) + 0.25 * np.sin(3.01 * ph))
    scr = bandpass(scr, 500, 3800)
    # breath layer
    br = bandpass(noise(dur), 300, 2500) * env_exp(len(tt), 4)
    e = env_ad(len(tt), 0.15, 1.6, 2)
    raw = (sub * 0.75 + scr * 0.45 + br * 0.25) * e
    save("mob/dragon_roar", reverb(raw, 0.45), 0.95)

def dragon_roar_frost():
    print("mob/dragon_frost_hurt (cold variant source)")
    dur = 2.6
    tt = t(dur)
    vib = 34 * np.sin(2 * np.pi * 13 * tt)
    sub = osc(62, dur, "saw", detune=-0.012, fm=vib * 0.02)
    sub = lowpass(sub, [1100, 1500, 600])
    f = pitch_env_mult(len(tt), 1150, 420, 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    scr = np.sin(ph) + 0.4 * np.sin(2.5 * ph)          # colder interval
    # frost shimmer: sparse high sines with random-ish (seeded) gating
    shim = sum(np.sin(2 * np.pi * fr * tt + i) * env_exp(len(tt), 3 + i * 2)
               for i, fr in enumerate((5200, 6600, 7900)))
    e = env_ad(len(tt), 0.12, 1.3, 2)
    raw = (sub * 0.7 + bandpass(scr, 600, 4500) * 0.5 + shim * 0.12) * e
    save("mob/dragon_frost_hurt", reverb(raw, 0.4), 0.9)

def dragon_wing_flap():
    print("mob/dragon_wing_flap")
    dur = 0.9
    n = int(SR * dur)
    nz = noise(dur)
    cut = np.array([300, 2200, 900, 250])
    whoosh = lowpass(nz, cut)
    whoosh *= env_ad(n, 0.18, 0.45, 2)
    # membrane thump at flap start
    thump = osc(pitch_env_mult(int(0.12 * SR), 120, 45)[None][0] * 0 + 70,
                0.12) * 0
    th_n = int(0.14 * SR)
    thump = osc(80, 0.14) * env_exp(th_n, 8) * 0.5
    thump[-1] = 0
    out = whoosh.copy()
    out[:th_n] += thump
    save("mob/dragon_wing_flap", out, 0.8)

def giant_stomp():
    print("mob/giant_stomp")
    dur = 1.4
    n = int(SR * dur)
    th_n = int(0.35 * SR)
    sub = osc(pitch_env_mult(th_n, 90, 28, 2) * 0 + 55, 0.35)
    sub = lowpass(sub, [200, 120]) * env_exp(th_n, 7)
    # debris crackle
    deb = bandpass(noise(dur), 1500, 8000) * env_ad(n, 0.005, 1.0, 4) * 0.35
    gate = (rng.uniform(0, 1, n) > 0.995).astype(float)
    gate = lowpass(gate, 800)
    out = np.zeros(n)
    out[:th_n] += sub
    out += deb * (0.3 + gate * 2)
    save("mob/giant_stomp", reverb(out, 0.3), 0.95)

def troll_grunt():
    print("mob/troll_grunt")
    dur = 0.8
    tt = t(dur)
    f = pitch_env_mult(len(tt), 130, 85, 1.5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    v = np.sign(np.sin(ph)) * 0.4 + np.sin(ph) * 0.6      # vocal-fold grit
    v = bandpass(v, 180, 1600)                             # guttural formants
    grit = bandpass(noise(dur), 800, 3000) * 0.2
    e = env_ad(len(tt), 0.05, 0.35, 2)
    save("mob/troll_grunt", (v + grit) * e, 0.85)

def troll_bark():
    print("mob/troll_bark (hurt)")
    dur = 0.5
    tt = t(dur)
    f = pitch_env_mult(len(tt), 170, 100, 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    v = (np.sin(ph) + 0.6 * np.sin(2 * ph)) * 0.7
    v = bandpass(v, 250, 2200)
    snap = bandpass(noise(0.5), 1200, 5000) * env_exp(len(tt), 10) * 0.5
    e = env_ad(len(tt), 0.01, 0.22, 3)
    save("mob/troll_bark", (v + snap) * e, 0.85)

def troll_death():
    print("mob/troll_death")
    dur = 1.6
    tt = t(dur)
    f = pitch_env_mult(len(tt), 120, 40, 2.5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    v = np.sign(np.sin(ph)) * 0.5 + np.sin(ph) * 0.5
    v = bandpass(v, 120, 1200)
    gurgle = lowpass(noise(dur), 700) * 0.4 * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * tt))
    e = env_ad(len(tt), 0.05, 0.9, 2.5)
    save("mob/troll_death", reverb((v + gurgle) * e, 0.3), 0.85)

def elf_hum():
    print("mob/elf_warrior hum (ambient)")
    dur = 1.8
    tt = t(dur)
    base = freq("E", 5)
    v = sum(np.sin(2 * np.pi * base * h * tt + i) / (h * 1.5)
            for i, h in enumerate((1, 2, 3, 4)))
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * tt)
    v *= vib
    air = bandpass(noise(dur), 3000, 8000) * 0.05
    e = env_ad(len(tt), 0.4, 0.7, 2)
    save("mob/elf_hum", reverb((v + air) * e, 0.5), 0.6)

def elf_hurt():
    print("mob/elf_hurt")
    dur = 0.45
    tt = t(dur)
    f = pitch_env_mult(len(tt), 700, 480, 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    v = np.sin(ph) + 0.3 * np.sin(3 * ph)
    v = bandpass(v, 600, 3500)
    e = env_ad(len(tt), 0.005, 0.2, 3)
    save("mob/elf_hurt", v * e, 0.8)

def elf_death():
    print("mob/elf_death")
    dur = 1.5
    tt = t(dur)
    f = pitch_env_mult(len(tt), 520, 260, 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    v = np.sin(ph) * 0.7 + np.sin(2 * ph) * 0.15
    chime = np.sin(2 * np.pi * freq("B", 5) * tt) * env_exp(len(tt), 4) * 0.15
    e = env_ad(len(tt), 0.05, 0.9, 2)
    save("mob/elf_death", reverb((v + chime) * e, 0.55), 0.7)

def colossus_voice():
    print("mob/giant_colossus voice (ambient rumble)")
    dur = 2.4
    tt = t(dur)
    f = pitch_env_mult(len(tt), 46, 38, 1.5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    v = np.sin(ph) + 0.5 * np.sin(2.02 * ph) + 0.25 * np.sin(3.04 * ph)
    rumble = lowpass(noise(dur), 180) * 0.5
    e = env_ad(len(tt), 0.5, 0.9, 1.6)
    save("mob/colossus_voice", reverb((v + rumble) * e, 0.4), 0.85)

def colossus_hurt():
    print("mob/giant_colossus hurt")
    dur = 1.2
    tt = t(dur)
    f = pitch_env_mult(len(tt), 60, 42, 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    v = np.sign(np.sin(ph)) * 0.6 + np.sin(ph) * 0.4
    v = lowpass(v, [500, 350])
    crack = bandpass(noise(1.2), 900, 4000) * env_exp(len(tt), 9) * 0.5
    e = env_ad(len(tt), 0.02, 0.6, 2)
    save("mob/colossus_hurt", reverb((v + crack) * e, 0.35), 0.95)

def colossus_death():
    print("mob/giant_colossus death")
    dur = 2.8
    tt = t(dur)
    f = pitch_env_mult(len(tt), 55, 24, 3)
    ph = 2 * np.pi * np.cumsum(f) / SR
    v = np.sin(ph) * 0.8
    collapse = bandpass(noise(dur), 200, 2500) * env_exp(len(tt), 3) * 0.6
    e = env_ad(len(tt), 0.1, 1.6, 2)
    save("mob/colossus_death", reverb((v + collapse) * e, 0.45), 0.95)

def whelp_chirp():
    print("mob/dragon_whelp chirp (ambient)")
    dur = 0.5
    tt = t(dur)
    f = pitch_env_mult(len(tt), 1400, 2100, 1.2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    c = np.sin(ph) + 0.2 * np.sin(2.5 * ph)
    trill = 0.6 + 0.4 * np.sin(2 * np.pi * 26 * tt)
    e = env_ad(len(tt), 0.01, 0.18, 2.5)
    save("mob/whelp_chirp", c * trill * e, 0.7)

def whelp_screech():
    print("mob/dragon_whelp screech (hurt)")
    dur = 0.6
    tt = t(dur)
    f = pitch_env_mult(len(tt), 2400, 1100, 1.6)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)
    s = bandpass(s, 900, 6500)
    e = env_ad(len(tt), 0.01, 0.25, 3)
    save("mob/whelp_screech", s * e, 0.75)

def whelp_death():
    print("mob/dragon_whelp death")
    dur = 1.1
    tt = t(dur)
    f = pitch_env_mult(len(tt), 1800, 500, 2.5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * 0.8
    wob = 0.7 + 0.3 * np.sin(2 * np.pi * 14 * tt)
    e = env_ad(len(tt), 0.02, 0.6, 2.5)
    save("mob/whelp_death", reverb(s * wob * e, 0.35), 0.7)

def altar_drone():
    print("block/ancient_altar ambience")
    dur = 6.0
    tt = t(dur)
    chord = [freq(n, 2) for n in ("D", "A", "D")] + [freq("E", 3)]
    v = np.zeros(len(tt))
    for i, f in enumerate(chord):
        det = 1 + 0.002 * np.sin(2 * np.pi * (0.07 + i * 0.03) * tt + i)
        v += np.sin(2 * np.pi * f * det * tt + i) / (i + 2)
    breath = lowpass(noise(dur), 400) * 0.12
    swell = 0.6 + 0.4 * np.sin(2 * np.pi * 0.12 * tt - 1)
    e = env_ad(len(tt), 1.2, 1.2, 1.2)
    save("block/altar_drone", (v + breath) * swell * e, 0.5)

# ============================================================== WEAPONS / UI
def sword_swing():
    print("weapons/sword_swing")
    dur = 0.4
    nz = noise(dur)
    sw = bandpass(nz, 900, 6500)
    n = len(sw)
    cut = np.array([1200, 5000, 2500, 800])
    sw = lowpass(sw, cut) * env_ad(n, 0.03, 0.18, 2)
    ring = np.sin(2 * np.pi * 3400 * t(dur)) * env_exp(n, 14) * 0.12
    save("weapons/sword_swing", sw + ring, 0.75)

def staff_cast():
    print("weapons/staff_cast")
    dur = 0.9
    tt = t(dur)
    f = pitch_env_mult(len(tt), 300, 1200, 1.5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    z = np.sin(ph) + 0.5 * np.sin(1.98 * ph) + 0.3 * np.sin(3.01 * ph)
    spark = bandpass(noise(dur), 4000, 10000) * env_exp(len(tt), 6) * 0.3
    e = env_ad(len(tt), 0.02, 0.4, 2)
    save("weapons/staff_cast", reverb((z + spark) * e, 0.35), 0.75)

def bow_release():
    print("weapons/bow_release")
    dur = 0.5
    n = int(SR * dur)
    twang = pluck(196, 0.35, 2200) * 0.6
    whoosh = bandpass(noise(dur), 1500, 7000) * env_ad(n, 0.01, 0.3, 3) * 0.7
    out = np.zeros(n)
    out[:min(len(twang), n)] += twang[:n]
    out += whoosh
    save("weapons/bow_release", out, 0.75)

def ui_class_select():
    print("ui/class_select_open (harp arpeggio)")
    notes = [("A", 4), ("C", 5), ("E", 5), ("A", 5)]
    step = 0.09
    total = step * (len(notes) - 1) + 1.0
    out = np.zeros(int(SR * total))
    for i, (nm, oc) in enumerate(notes):
        p = pluck(freq(nm, oc), 1.0, 4500)
        s = int(i * step * SR)
        out[s:s + len(p)] += p * (0.9 - i * 0.1)
    save("ui/class_select_open", reverb(out, 0.4), 0.7)

def ui_ability_ready():
    print("ui/ability_ready (shimmering chime)")
    dur = 1.2
    tt = t(dur)
    out = np.zeros(len(tt))
    for i, (nm, oc, dl) in enumerate((("E", 6, 0.0), ("B", 6, 0.07), ("E", 7, 0.14))):
        s = int(dl * SR)
        seg = tt[:len(tt) - s]
        out[s:] += np.sin(2 * np.pi * freq(nm, oc) * seg) * env_exp(len(seg), 5) * (0.6 - i * 0.15)
    sparkle = bandpass(noise(dur), 6000, 12000) * env_exp(len(tt), 8) * 0.08
    save("ui/ability_ready", out + sparkle, 0.6)

# ================================================================ ABILITIES
def ab_fireball():
    dur = 1.4
    tt = t(dur)
    whoosh = bandpass(noise(dur), 400, 3500)
    whoosh = lowpass(whoosh, np.array([600, 2800, 1400])) * env_ad(len(tt), 0.25, 0.5, 1.5)
    boom_n = int(0.5 * SR)
    boom = lowpass(noise(0.5), 250) * env_exp(boom_n, 6) * 1.2
    sub = osc(60, 0.5) * env_exp(boom_n, 7) * 0.8
    out = whoosh
    out[int(0.7 * SR):int(0.7 * SR) + boom_n] += boom + sub
    save("ability/fireball_cast", reverb(out, 0.35), 0.9)

def ab_ice_shield():
    dur = 1.5
    tt = t(dur)
    crys = np.zeros(len(tt))
    for i, f in enumerate((2600, 3300, 4100, 5200)):
        crys += np.sin(2 * np.pi * f * tt + i * 1.3) * env_exp(len(tt), 3 + i) * 0.3
    crackle = bandpass(noise(dur), 3000, 9000)
    gate = (rng.uniform(0, 1, len(tt)) > 0.998).astype(float)
    gate = lowpass(gate, 1500)
    rise = lowpass(noise(dur), [400, 2000, 3000]) * env_ad(len(tt), 0.5, 0.4, 1.5) * 0.5
    save("ability/ice_shield_cast", reverb(crys + crackle * gate * 2 + rise, 0.4), 0.8)

def ab_arcane_teleport():
    dur = 0.7
    tt = t(dur)
    up = pitch_env_mult(len(tt), 400, 3600, 1.3)
    ph = 2 * np.pi * np.cumsum(up) / SR
    z = np.sin(ph) + 0.4 * np.sin(2.02 * ph)
    zipn = bandpass(noise(dur), 2000, 8000) * env_exp(len(tt), 5) * 0.5
    e = env_ad(len(tt), 0.005, 0.2, 2.5)
    save("ability/arcane_teleport_cast", (z + zipn) * e, 0.8)

def ab_multishot():
    total = 0.8
    out = np.zeros(int(SR * total))
    for i, dl in enumerate((0.0, 0.11, 0.22)):
        s = int(dl * SR)
        ln = int(0.25 * SR)
        w = bandpass(noise(0.25), 1500, 7000) * env_ad(ln, 0.005, 0.15, 3)
        out[s:s + ln] += w * (1 - i * 0.2)
        tw = pluck(220 + i * 30, 0.2, 2500) * 0.4
        out[s:s + len(tw)] += tw[:max(0, len(out) - s)][:len(tw)] * 0
    save("ability/multi_shot_cast", out, 0.8)

def ab_shadow_step():
    dur = 0.8
    tt = t(dur)
    dark = bandpass(lowpass(noise(dur), [2500, 600, 300]), 100, 1200)
    dark *= env_ad(len(tt), 0.1, 0.45, 1.6)
    whisper = bandpass(noise(dur), 2500, 6000) * env_ad(len(tt), 0.2, 0.4, 2) * 0.3
    tone = np.sin(2 * np.pi * 110 * tt) * env_ad(len(tt), 0.05, 0.4, 2) * 0.25
    save("ability/shadow_step_cast", reverb(dark + whisper + tone, 0.4), 0.75)

def ab_eagle_eye():
    dur = 1.3
    tt = t(dur)
    f = pitch_env_mult(len(tt), 1600, 2400, 1.2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    cry = np.sin(ph) + 0.3 * np.sin(2 * ph)
    cry = bandpass(cry, 1000, 5500)
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * 18 * tt)
    e = env_ad(len(tt), 0.06, 0.6, 2)
    save("ability/eagle_eye_cast", reverb(cry * trem * e, 0.4), 0.7)

def ab_rage():
    dur = 1.2
    tt = t(dur)
    f = pitch_env_mult(len(tt), 110, 190, 1.5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    roar = np.sign(np.sin(ph)) * 0.5 + np.sin(2 * ph) * 0.4
    roar = bandpass(roar, 150, 1800)
    breath = bandpass(noise(dur), 500, 2500) * 0.3
    e = env_ad(len(tt), 0.08, 0.5, 1.8)
    save("ability/rage_cast", (roar + breath) * e, 0.9)

def ab_ground_slam():
    dur = 1.6
    n = int(SR * dur)
    impact = lowpass(noise(1.6), 300) * env_exp(n, 5)
    sub = osc(pitch_env_mult(int(0.4 * SR), 80, 26, 2) * 0 + 50, 0.4) * env_exp(int(0.4 * SR), 6)
    shake = lowpass(noise(dur), 120) * env_exp(n, 2.5) * 0.8
    out = impact + shake
    out[:int(0.4 * SR)] += sub
    save("ability/ground_slam_cast", reverb(out, 0.35), 0.95)

def ab_bloodlust():
    dur = 1.8
    out = np.zeros(int(SR * dur))
    for beat, dl in enumerate((0.0, 0.32, 0.72, 1.04)):
        s = int(dl * SR)
        ln = int(0.18 * SR)
        lub = lowpass(osc(58, 0.18), 150) * env_exp(ln, 7) * (1 if beat % 2 == 0 else 0.7)
        out[s:s + ln] += lub
    sheen = bandpass(noise(dur), 2000, 6000) * env_ad(len(out), 0.5, 0.6, 1.5) * 0.06
    save("ability/bloodlust_cast", out + sheen, 0.85)

def ab_holy_light():
    dur = 1.8
    tt = t(dur)
    choir = np.zeros(len(tt))
    for i, (nm, oc) in enumerate((("C", 4), ("E", 4), ("G", 4), ("C", 5))):
        f = freq(nm, oc) * (1 + 0.003 * np.sin(2 * np.pi * (4 + i) * tt))
        choir += np.sin(2 * np.pi * f * tt + i) / (i + 2)
    hit = np.zeros(len(tt)); hn = int(0.15 * SR)
    hit[:hn] = bandpass(noise(1.8)[:hn], 800, 4000) * env_exp(hn, 8) * 0.3
    e = env_ad(len(tt), 0.05, 1.0, 1.6)
    save("ability/holy_light_cast", reverb((choir + hit) * e, 0.5), 0.8)

def ab_divine_shield():
    dur = 1.6
    tt = t(dur)
    bell_f = freq("G", 5)
    partials = [(1, 1.0), (2.76, 0.4), (5.4, 0.18), (8.9, 0.08)]
    bell = sum(np.sin(2 * np.pi * bell_f * h * tt) * a * env_exp(len(tt), 2.5 + i)
               for i, (h, a) in enumerate(partials))
    shimmer = bandpass(noise(dur), 5000, 11000) * env_exp(len(tt), 6) * 0.1
    save("ability/divine_shield_cast", reverb(bell + shimmer, 0.45), 0.8)

def ab_smite():
    dur = 1.8
    n = int(SR * dur)
    clap = noise(dur)
    clap = highpass(clap, 800) * env_exp(n, 4) * 1.2
    thunder = lowpass(noise(dur), [900, 400, 150]) * env_exp(n, 1.8) * 1.0
    crack_n = int(0.06 * SR)
    crack = noise(1.8)[:crack_n] * env_exp(crack_n, 3) * 0.8
    out = clap * 0.6 + thunder + np.pad(crack, (0, n - crack_n))
    save("ability/smite_cast", reverb(out, 0.4), 0.95)

def ab_wolf_form():
    dur = 1.6
    tt = t(dur)
    f = pitch_env_mult(len(tt), 320, 480, 2.5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    howl = np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph)
    howl = bandpass(howl, 300, 2500)
    vib = 1 + 0.01 * np.sin(2 * np.pi * 6 * tt)
    e = env_ad(len(tt), 0.25, 0.7, 1.8)
    save("ability/wolf_form_cast", reverb(howl * vib * e, 0.5), 0.8)

def ab_entangling_roots():
    dur = 1.4
    n = int(SR * dur)
    crackle = bandpass(noise(dur), 700, 4500)
    gate = lowpass((rng.uniform(0, 1, n) > 0.997).astype(float), 900)
    groan = osc(pitch_env_mult(n, 90, 60, 1.5) * 0 + 75, 1.4)
    groan = lowpass(groan, 400) * env_ad(n, 0.3, 0.6, 1.5) * 0.6
    rustle = bandpass(noise(dur), 3000, 9000) * env_ad(n, 0.2, 0.5, 2) * 0.25
    save("ability/entangling_roots_cast", crackle * (0.3 + gate * 2.5) + groan + rustle, 0.8)

def ab_natures_blessing():
    dur = 2.0
    tt = t(dur)
    bloom = np.zeros(len(tt))
    for i, (nm, oc, dl) in enumerate((("C", 5, 0.0), ("E", 5, 0.12), ("G", 5, 0.24), ("C", 6, 0.36))):
        s = int(dl * SR)
        seg = tt[:len(tt) - s]
        tone = np.sin(2 * np.pi * freq(nm, oc) * seg) + 0.3 * np.sin(2 * np.pi * freq(nm, oc) * 2 * seg)
        bloom[s:] += tone * env_exp(len(seg), 4) * 0.35
    birds = bandpass(noise(dur), 4000, 9000)
    bgate = lowpass((rng.uniform(0, 1, len(tt)) > 0.999).astype(float), 1200)
    warm = lowpass(noise(dur), 600) * env_ad(len(tt), 0.6, 0.8, 1.3) * 0.15
    save("ability/natures_blessing_cast", reverb(bloom + birds * bgate * 1.5 + warm, 0.45), 0.75)

# ==================================================================== MUSIC
PENT = ["A", "C", "D", "E", "G"]   # A minor pentatonic

def realms_theme():
    print("music/realms_theme (45s seamless exploration loop)")
    dur = 45.0
    n = int(SR * dur)
    tt = t(dur)
    out = np.zeros(n)
    # --- drones: Am stack with slow beating
    for nm, oc, amp in (("A", 2, 0.30), ("E", 3, 0.20), ("A", 3, 0.14), ("C", 4, 0.07)):
        f = freq(nm, oc)
        det = 1 + 0.0015 * np.sin(2 * np.pi * 0.13 * tt)
        w = np.sin(2 * np.pi * f * det * tt) + 0.4 * np.sin(2 * np.pi * f * 2 * det * tt)
        swell = 0.75 + 0.25 * np.sin(2 * np.pi * dur / dur * np.pi * 0 + tt * 2 * np.pi / dur * 2)
        out += w * amp * swell
    # --- pad swells every 15s (chords: Am, F, C, G -> i VI III VII)
    chords = [(("A", 3), ("C", 4), ("E", 4)), (("F", 3), ("A", 3), ("C", 4)),
              (("C", 4), ("E", 4), ("G", 4)), (("G", 3), ("B", 3), ("D", 4))]
    for ci, ch in enumerate(chords):
        start = ci * 11.25
        seg_d = 12.0                      # overlaps next slightly
        s = int(start * SR); ln = int(seg_d * SR)
        seg_t = t(seg_d)
        pad = np.zeros(ln)
        for nm, oc in ch:
            f = freq(nm, oc)
            pad += np.sin(2 * np.pi * f * seg_t) / 3
            pad += np.sin(2 * np.pi * f * 1.003 * seg_t) / 5
        pe = env_ad(ln, 4.0, 4.0, 1.2) * 0.16
        end = min(s + ln, n)
        out[s:end] += pad[:end - s] * pe[:end - s]
    # --- pentatonic melody plucks (seeded pattern, phrase every 7.5s)
    melody = [
        ("E", 5), ("G", 5), ("A", 5), ("G", 5), ("E", 5), ("D", 5),
        ("C", 5), ("D", 5), ("E", 5), None, ("A", 4), None,
        ("A", 5), ("G", 5), ("E", 5), ("D", 5), ("C", 5), ("D", 5),
        ("E", 5), ("G", 5), ("E", 5), None, None, None,
    ]
    step = 45.0 / 24                     # even spacing so loop wraps cleanly
    for i, note in enumerate(melody):
        if note is None: continue
        nm, oc = note
        p = pluck(freq(nm, oc), 1.4, 2600) * 0.30
        s = int(i * step * SR) % n
        endi = min(s + len(p), n)
        out[s:endi] += p[:endi - s]
        if s + len(p) > n:               # wrap the tail for seamlessness
            wrap = (s + len(p)) - n
            out[:wrap] += p[len(p) - wrap:]
    # --- gentle high shimmer
    out += bandpass(noise(dur), 6000, 11000) * 0.012 * (0.6 + 0.4 * np.sin(2 * np.pi * tt / 9))
    # seamless loop: crossfade last 0.5s into first 0.5s
    xf = int(0.5 * SR)
    ramp = np.linspace(0, 1, xf)
    out[:xf] = out[:xf] * ramp + out[-xf:] * (1 - ramp)
    out = out[:-xf]
    save("music/realms_theme", out, 0.8)

def realms_battle():
    print("music/realms_battle (24s intense loop)")
    bpm = 140
    beat = 60.0 / bpm                    # 0.4286s
    bar = beat * 4
    bars = int(round(24.0 / bar))         # 14 bars = 24.0s
    dur = bars * bar
    n = int(SR * dur)
    tt = t(dur)
    out = np.zeros(n)
    # --- driving bass ostinato: A A E G | A A C B pattern in A minor
    ostinato = ["A2", "A2", "E2", "G2", "A2", "A2", "C3", "B2"]
    eighth = beat / 2
    for i in range(bars * 8):
        nm, oc = ostinato[i % 8][:-1], int(ostinato[i % 8][-1])
        f = freq(nm, oc)
        s = int(i * eighth * SR); ln = int(eighth * 0.9 * SR)
        seg = t(ln / SR)
        w = (np.sin(2 * np.pi * f * seg) + 0.5 * np.sign(np.sin(2 * np.pi * f * seg))) * 0.5
        w = lowpass(w, 700) * env_ad(ln, 0.004, ln / SR * 0.5, 2.5) * 0.4
        end = min(s + ln, n)
        out[s:end] += w[:end - s]
        if s + ln > n:
            wrap = s + ln - n
            out[:wrap] += w[end - s:]
    # --- drum pulses
    hits_per_bar = 8
    for i in range(bars * hits_per_bar):
        pos_in_bar = i % hits_per_bar
        s = int(i * (bar / hits_per_bar) * SR)
        ln = int(0.2 * SR)
        if pos_in_bar in (0, 4):                       # kick
            k = lowpass(osc(65, 0.2), 200) * env_exp(ln, 9) * 0.9
        elif pos_in_bar in (2, 6):                     # snare-ish
            k = bandpass(noise(0.2), 900, 5000) * env_exp(ln, 10) * 0.5
            k += lowpass(osc(180, 0.2), 400) * env_exp(ln, 12) * 0.3
        else:                                          # hats
            k = bandpass(noise(0.2), 6000, 12000) * env_exp(ln, 14) * 0.15
        end = min(s + ln, n)
        out[s:end] += k[:end - s]
        if s + ln > n:
            out[:s + ln - n] += k[end - s:]
    # --- tense high drone + minor-second grind
    out += np.sin(2 * np.pi * freq("A", 4) * tt) * 0.06
    out += np.sin(2 * np.pi * freq("A#", 4) * tt) * 0.05
    # rising peril sweep each 8 bars
    for rep in range(max(1, int(dur / 12))):
        s = int(rep * 12 * SR); ln = min(int(3 * SR), n - s)
        if ln <= 0: break
        fsw = pitch_env_mult(ln, 220, 880, 1.2)
        ph = 2 * np.pi * np.cumsum(fsw) / SR
        out[s:s + ln] += np.sin(ph) * env_ad(ln, 2.0, 0.8, 1.5) * 0.08
    xf = int(0.3 * SR)
    ramp = np.linspace(0, 1, xf)
    out[:xf] = out[:xf] * ramp + out[-xf:] * (1 - ramp)
    out = out[:-xf]
    save("music/realms_battle", out, 0.85)

def battle_sting(kind):
    print(f"music/battle_{kind}")
    dur = 1.5
    tt = t(dur)
    if kind == "start":
        # brass-ish stab: stacked saws hitting an A minor chord then swelling
        out = np.zeros(len(tt))
        for i, (nm, oc) in enumerate((("A", 2), ("E", 3), ("A", 3), ("C", 4))):
            f = freq(nm, oc)
            saw = 2 * ((f * tt) % 1) - 1
            out += lowpass(saw, [600, 1800, 1200]) / (i + 2)
        e = env_ad(len(tt), 0.02, 0.8, 1.5)
        out = out * e
    else:
        # stop: descending resolve, fading to silence
        out = np.zeros(len(tt))
        for i, (nm, oc, dl) in enumerate((("A", 4, 0.0), ("E", 4, 0.18), ("A", 3, 0.36))):
            s = int(dl * SR)
            seg = tt[:len(tt) - s]
            out[s:] += np.sin(2 * np.pi * freq(nm, oc) * seg) * env_exp(len(seg), 3) * 0.5 / (i + 1)
    save(f"music/battle_{kind}", reverb(out, 0.4), 0.8)

# ==================================================================== MAIN
def main():
    print("Generating Realms of Myth audio suite...\n--- mobs ---")
    dragon_roar(); dragon_roar_frost(); dragon_wing_flap(); giant_stomp()
    troll_grunt(); troll_bark(); troll_death()
    elf_hum(); elf_hurt(); elf_death()
    colossus_voice(); colossus_hurt(); colossus_death()
    whelp_chirp(); whelp_screech(); whelp_death()
    altar_drone()
    print("--- weapons/ui ---")
    sword_swing(); staff_cast(); bow_release()
    ui_class_select(); ui_ability_ready()
    print("--- abilities ---")
    ab_fireball(); ab_ice_shield(); ab_arcane_teleport(); ab_multishot()
    ab_shadow_step(); ab_eagle_eye(); ab_rage(); ab_ground_slam()
    ab_bloodlust(); ab_holy_light(); ab_divine_shield(); ab_smite()
    ab_wolf_form(); ab_entangling_roots(); ab_natures_blessing()
    print("--- music ---")
    realms_theme(); realms_battle(); battle_sting("start"); battle_sting("stop")
    print("\nDone.")

if __name__ == "__main__":
    main()
