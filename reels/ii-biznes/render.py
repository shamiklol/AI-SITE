#!/usr/bin/env python3
"""Fast-cut BIRFOIZ-style reel: AI in business (RU, 45 s).
Usage: python3 render.py <workdir> <out.mp4> [scale]
workdir must contain p/*.png panels, voice.wav, music.wav (optional), sfx.wav.
Writes raw frames to ffmpeg (video only) -> <out>.video.mp4; audio is mixed separately.
"""
import sys, math, subprocess, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WD = sys.argv[1]
OUT = sys.argv[2]
SC = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
W, H = int(1080 * SC) // 2 * 2, int(1920 * SC) // 2 * 2
FPS = 30
TOTAL = 45.0
TEMPO = 1.03
LEAD = 0.2

def R(t):  # raw voice time -> video time
    return t / TEMPO + LEAD

BLACK = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'
XB = '/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf'

# ---------------- shots ----------------
# (start, panel, zoom0, zoom1, fx, fy, transition)
S = []
def shot(t, panel, z0=1.0, z1=1.12, fx=0.5, fy=0.55, tr='punch'):
    S.append(dict(t=t, panel=panel, z0=z0, z1=z1, fx=fx, fy=fy, tr=tr))

shot(0.0,        '21', 1.25, 1.05, .5, .5, 'none')
shot(R(1.75),    '11', 1.0, 1.15, .35, .5, 'slide')
shot(R(3.70),    '16', 1.05, 1.2, .5, .6, 'punch')
shot(R(5.70),    'card:СМОТРИТЕ:#FFD43B', tr='punch')
shot(R(6.60),    '12', 1.0, 1.18, .45, .5, 'slide')
shot(R(9.20),    '13', 1.1, 1.0, .6, .45, 'punch')
shot(R(11.0),    '14', 1.0, 1.2, .55, .5, 'slide')
shot(R(12.70),   'num:01:СКОРОСТЬ:#3B82F6', tr='punch')
shot(R(14.60),   '15', 1.0, 1.12, .55, .5, 'slide')
shot(R(16.0),    '15', 1.45, 1.6, .3, .48, 'punch')
shot(R(17.60),   'num:02:ЭКОНОМИЯ:#22C55E', tr='punch')
shot(R(19.50),   '17', 1.0, 1.15, .4, .7, 'slide')
shot(R(21.0),    '16', 1.15, 1.0, .6, .5, 'punch')
shot(R(22.50),   'num:03:ПРОДАЖИ:#F43F5E', tr='punch')
shot(R(24.40),   '23', 1.0, 1.15, .5, .5, 'slide')
shot(R(25.80),   '24', 1.1, 1.0, .4, .6, 'punch')
shot(R(27.0),    '18', 1.0, 1.15, .5, .55, 'slide')
shot(R(28.05),   '19', 1.0, 1.15, .4, .6, 'punch')
shot(R(29.60),   '26', 1.0, 1.18, .5, .55, 'slide')
shot(R(31.05),   '25', 1.0, 1.12, .5, .45, 'punch')
shot(R(33.25),   '27', 1.0, 1.15, .45, .55, 'slide')
shot(R(35.40),   '28', 1.0, 1.12, .5, .6, 'punch')
shot(R(36.95),   'type:БИЗНЕС:#7C3AED', tr='punch')
shot(R(38.05),   '22', 1.0, 1.12, .55, .5, 'slide')
shot(R(39.4),    '29', 1.0, 1.1, .45, .5, 'punch')
shot(41.3,       'final', tr='punch')
for i, s in enumerate(S):
    s['end'] = S[i + 1]['t'] if i + 1 < len(S) else TOTAL

# ---------------- captions ----------------
# (t0, t1, text, style, y) style: white|yellow|box|big
C = []
def cap(t0, t1, text, style='white', y=0.17, size=96, count=None):
    C.append(dict(t0=t0, t1=t1, text=text, style=style, y=y, size=size, count=count))

cap(R(0.35), R(1.75), '{n} ИЗ 10', 'big', .16, 230, count=(1, 8, .6))
cap(R(1.0),  R(1.75), 'КОМПАНИЙ', 'box', .29, 92)
cap(R(1.85), R(3.70), 'УЖЕ ВНЕДРИЛИ ИИ', 'white', .12, 92)
cap(R(3.85), R(4.6),  'СПОЙЛЕР:', 'box', .12, 84)
cap(R(4.6),  R(5.70), 'ДЕЛО В ДЕНЬГАХ', 'yellow', .21, 110)
cap(R(6.75), R(9.20), 'МЕНЕДЖЕР', 'white', .10, 90)
cap(R(7.9),  R(9.20), '{n} МИНУТ', 'big', .18, 190, count=(1, 20, .7))
cap(R(9.30), R(11.0), 'ИИ', 'box', .10, 100)
cap(R(9.9),  R(11.0), '{n} СЕКУНДЫ', 'big', .19, 170, count=(20, 3, .35))
cap(R(11.1), R(12.7), 'НОЧЬЮ', 'yellow', .10, 120)
cap(R(11.8), R(12.7), 'И В ВЫХОДНЫЕ', 'white', .18, 96)
cap(R(14.7), R(16.0), 'ДЕНЬ РАБОТЫ', 'white', .11, 100)
cap(R(16.05), R(17.6), '→ МИНУТЫ', 'yellow', .11, 140)
cap(R(19.6), R(21.0), 'РУТИНА → МАШИНЕ', 'white', .10, 88)
cap(R(21.05), R(22.5), 'ЛЮДИ → ДЕНЬГИ', 'yellow', .11, 100)
cap(R(24.5), R(25.8), 'ПОМНИТ КАЖДОГО', 'white', .10, 92)
cap(R(25.85), R(27.9), '0 ПОТЕРЯННЫХ', 'big', .10, 140)
cap(R(26.5), R(27.9), 'ЗАЯВОК', 'box', .19, 92)
cap(R(28.1), R(29.6), 'ПОКА ВЫ ДУМАЕТЕ…', 'white', .10, 88)
cap(R(29.65), R(31.05), 'КОНКУРЕНТ УЖЕ ВНЕДРИЛ', 'yellow', .10, 80)
cap(R(31.1), R(33.25), 'НУЖЕН ЛИ ИИ?', 'strike', .11, 110)
cap(R(33.3), R(35.40), 'КОГДА ВЫ НАЧНЁТЕ?', 'yellow', .11, 100)
cap(R(35.5), R(36.95), 'НАПИШИТЕ', 'white', .10, 120)
cap(R(36.0), R(36.95), 'В КОММЕНТАРИЯХ', 'box', .18, 84)
cap(R(36.95), R(38.05), 'СЛОВО', 'white', .28, 110)
cap(R(38.1), R(39.4), 'ПОДБЕРЁМ РЕШЕНИЯ', 'white', .10, 90)
cap(R(39.45), 41.3, 'ДЛЯ ВАШЕГО', 'white', .09, 96)
cap(R(39.9), 41.3, 'БИЗНЕСА', 'yellow', .16, 150)

# ---------------- helpers ----------------
_font = {}
def font(path, size):
    k = (path, size)
    if k not in _font:
        _font[k] = ImageFont.truetype(path, max(8, int(size * SC)))
    return _font[k]

def ease_out(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3

def pop(x):  # 0..1 -> scale with overshoot
    x = min(max(x, 0), 1)
    return 1 + 0.15 * math.sin(x * math.pi) if x < 1 else 1.0

_txt = {}
def text_img(text, style, size, maxw):
    k = (text, style, size)
    if k in _txt:
        return _txt[k]
    f = font(BLACK, size)
    while True:
        bb = f.getbbox(text)
        if bb[2] - bb[0] <= maxw or f.size < 20:
            break
        f = ImageFont.truetype(BLACK, f.size - 4)
    bb = f.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = int(30 * SC)
    stroke = max(2, int(f.size * 0.11))
    im = Image.new('RGBA', (tw + 2 * pad + 2 * stroke, th + 2 * pad + 2 * stroke), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = pad + stroke - bb[0], pad + stroke - bb[1]
    if style == 'box':
        d.rounded_rectangle((stroke, stroke, im.width - stroke, im.height - stroke), radius=int(24 * SC), fill=(17, 17, 17, 255))
        d.text((ox, oy), text, font=f, fill=(255, 255, 255, 255))
    else:
        fill = {'white': (255, 255, 255), 'yellow': (255, 214, 10), 'big': (255, 255, 255), 'strike': (255, 255, 255)}[style]
        # soft shadow
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((ox + 6 * SC, oy + 10 * SC), text, font=f, fill=(0, 0, 0, 140), stroke_width=stroke, stroke_fill=(0, 0, 0, 140))
        sh = sh.filter(ImageFilter.GaussianBlur(8 * SC))
        im.alpha_composite(sh)
        d.text((ox, oy), text, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=(15, 15, 15, 255))
    _txt[k] = im
    return im

_pan = {}
def panel(name):
    if name not in _pan:
        im = Image.open(f'{WD}/p/{name}.png').convert('RGB')
        if im.size != (W, H):
            im = im.resize((W, H), Image.LANCZOS)
        _pan[name] = im
    return _pan[name]

def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def grad_bg(color):
    c = np.array(hexrgb(color), float)
    y = np.linspace(0, 1, H)[:, None, None]
    top = np.clip(c * 1.15 + 20, 0, 255)
    bot = c * 0.65
    arr = (top * (1 - y) + bot * y).repeat(W, axis=1)
    return Image.fromarray(arr.astype(np.uint8))

def draw_rays(im, t, color=(255, 255, 255, 40)):
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    cx, cy = W / 2, H * 0.48
    L = H * 1.2
    for i in range(16):
        a0 = (i / 16) * 2 * math.pi + t * 0.6
        a1 = a0 + math.pi / 16
        d.polygon([(cx, cy), (cx + L * math.cos(a0), cy + L * math.sin(a0)), (cx + L * math.cos(a1), cy + L * math.sin(a1))], fill=color)
    im.paste(Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'))

def center_text(im, text, size, y, color=(255, 255, 255), stroke_col=(15, 15, 15), scale=1.0, path=BLACK):
    f = ImageFont.truetype(path, max(8, int(size * SC * scale)))
    bb = f.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    st = max(2, int(f.size * 0.09))
    ImageDraw.Draw(im).text((W / 2 - tw / 2 - bb[0], y * H - th / 2 - bb[1]), text, font=f, fill=color, stroke_width=st, stroke_fill=stroke_col)

def render_card(spec, lt, dur):
    kind = spec.split(':')[0]
    if kind == 'card':
        _, word, col = spec.split(':')
        im = grad_bg(col); draw_rays(im, lt, (255, 255, 255, 50))
        center_text(im, word, 150, .47, scale=pop(lt / .22) * (1 + 0.06 * lt))
        return im
    if kind == 'num':
        _, num, word, col = spec.split(':')
        im = grad_bg(col); draw_rays(im, lt)
        p = ease_out(lt / .25)
        center_text(im, f'ПРИЧИНА', 70, .30 - (1 - p) * .1, color=(255, 255, 255))
        center_text(im, num, 420, .45, color=(255, 214, 10), scale=pop(lt / .25) * (1 + 0.05 * lt))
        p2 = ease_out((lt - .2) / .25)
        if p2 > 0:
            center_text(im, word, 140, .64 + (1 - p2) * .06, scale=p2 * 0.3 + 0.7)
        return im
    if kind == 'type':
        _, word, col = spec.split(':')
        im = grad_bg(col); draw_rays(im, lt)
        return comment_box(im, word, lt, typing=True)
    if kind == 'final':
        im = grad_bg('#7C3AED'); draw_rays(im, lt)
        center_text(im, 'НАПИШИТЕ', 110, .2, scale=pop(lt / .2))
        im = comment_box(im, 'БИЗНЕС', 10, typing=False, pulse=lt)
        center_text(im, 'и получите решения', 84, .62, color=(255, 255, 255))
        center_text(im, 'для своего бизнеса', 84, .675, color=(255, 214, 10))
        # bouncing arrow
        d = ImageDraw.Draw(im)
        by = H * (.78 + .02 * math.sin(lt * 7))
        cx = W / 2; s = 95 * SC
        d.polygon([(cx - s, by), (cx + s, by), (cx, by + s * 1.2)], fill=(255, 214, 10), outline=(15, 15, 15), width=int(6 * SC))
        d.rectangle((cx - s * .35, by - s * 1.1, cx + s * .35, by), fill=(255, 214, 10), outline=(15, 15, 15), width=int(6 * SC))
        return im

def comment_box(im, word, lt, typing=True, pulse=None):
    n = len(word) if not typing else min(len(word), int(max(lt - .05, 0) / .09) + 1)
    sc = 1.0
    if pulse is not None:
        sc = 1 + 0.04 * math.sin(pulse * 6)
    bw, bh = W * .84 * sc, H * .13 * sc
    x0, y0 = W / 2 - bw / 2, H * .42 - bh / 2
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0 + 10 * SC, y0 + 14 * SC, x0 + bw + 10 * SC, y0 + bh + 14 * SC), radius=int(60 * SC), fill=(20, 10, 40))
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=int(60 * SC), fill=(255, 255, 255), outline=(15, 15, 15), width=int(8 * SC))
    f = ImageFont.truetype(BLACK, int(128 * SC * sc))
    txt = word[:n]
    bb = f.getbbox(word)
    tx = x0 + 60 * SC * sc - bb[0]
    ty = H * .42 - (bb[3] - bb[1]) / 2 - bb[1]
    d.text((tx, ty), txt, font=f, fill=(124, 58, 237))
    if typing and (n < len(word) or int(lt * 3) % 2 == 0):
        cb = f.getbbox(txt) if txt else (0, 0, 0, 0)
        cxp = tx + cb[2] + 14 * SC
        d.rectangle((cxp, ty + bb[1], cxp + 10 * SC, ty + bb[3]), fill=(124, 58, 237))
    # send button
    r = bh * .32
    bx, byy = x0 + bw - r * 1.6, H * .42
    d.ellipse((bx - r, byy - r, bx + r, byy + r), fill=(124, 58, 237))
    d.polygon([(bx - r * .4, byy - r * .5), (bx + r * .55, byy), (bx - r * .4, byy + r * .5)], fill=(255, 255, 255))
    return im

def render_shot(s, t):
    lt = t - s['t']
    dur = s['end'] - s['t']
    p = s['panel']
    if ':' in p or p == 'final':
        return render_card(p, lt, dur)
    base = panel(p)
    k = min(1.0, ease_out(lt / max(dur, .01)) * 0.6 + (lt / max(dur, .01)) * 0.4)
    z = s['z0'] + (s['z1'] - s['z0']) * k
    cw, ch = W / z, H / z
    cx = min(max(s['fx'] * W, cw / 2), W - cw / 2)
    cy = min(max(s['fy'] * H, ch / 2), H - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return base.resize((W, H), Image.BILINEAR, box=box)

# ---------------- stickers & motion ----------------
# sticker: (t0, t1, name, x, y, width_frac, rot, motion)  motion: wobble|float|spin|pulse
ST = []
def stk(t0, t1, name, x, y, w=.24, rot=0, mo='wobble', d=0.0):
    ST.append(dict(t0=t0 + d, t1=t1, name=name, x=x, y=y, w=w, rot=rot, mo=mo))

stk(R(0.9), R(1.75), 'A1', .82, .80, .26, 10)                     # robot: AI
stk(R(2.3), R(3.70), 'A4', .16, .36, .16, -12, 'pulse')           # shock lightning
stk(R(4.6), R(5.70), 'A3', .22, .36, .28, -14)                    # cash: «деньги»
stk(R(5.75), R(6.60), 'B8', .5, .70, .30, 0, 'pulse')             # look card
stk(R(7.0), R(9.20), 'A5', .82, .80, .24, 12, 'shake')            # alarm clock: slow manager
stk(R(9.9), R(11.0), 'A4', .85, .33, .16, 14, 'pulse')            # lightning: 3 s
stk(R(10.3), R(11.0), 'B4', .17, .80, .2, -8)                      # done
stk(R(11.1), R(12.7), 'A9', .83, .30, .24, 0, 'float')            # moon: night
stk(R(12.9), R(14.6), 'A4', .16, .80, .22, -15, 'spin')
stk(R(13.1), R(14.6), 'A2', .84, .82, .24, 12)
stk(R(16.1), R(17.6), 'A4', .82, .80, .2, 15, 'pulse')
stk(R(17.8), R(19.5), 'A3', .2, .82, .3, -12)
stk(R(18.0), R(19.5), 'A8', .82, .80, .22, 10, 'spin')
stk(R(19.7), R(21.0), 'B4', .84, .58, .16, 6)
stk(R(20.1), R(21.0), 'B4', .70, .50, .13, -6)
stk(R(21.1), R(22.5), 'A3', .2, .36, .26, -10)
stk(R(22.7), R(24.4), 'A6', .18, .82, .28, -8)
stk(R(22.9), R(24.4), 'B5', .84, .80, .24, 10)
stk(R(24.6), R(25.8), 'B1', .82, .24, .18, 8, 'float')
stk(R(25.0), R(25.8), 'B1', .17, .25, .15, -8, 'float')
stk(R(26.0), R(27.0), 'B4', .84, .86, .22, 8)
stk(R(27.1), R(28.05), 'B7', .82, .33, .2, 8, 'pulse')
stk(R(28.3), R(29.6), 'B9', .18, .30, .22, -10, 'shake')
stk(R(29.8), R(31.05), 'B7', .16, .30, .18, -8, 'pulse')
stk(R(31.4), R(33.25), 'B6', .14, .58, .14, -14)
stk(R(31.8), R(33.25), 'B6', .86, .62, .12, 14)
stk(R(33.5), R(35.4), 'B5', .84, .30, .22, 10, 'float')
stk(R(35.6), R(36.95), 'B1', .80, .27, .2, 8, 'float')
stk(R(37.65), R(38.05), 'B4', .84, .58, .18, 8)
stk(R(38.2), R(39.4), 'B8', .18, .32, .24, -8, 'float')
stk(R(39.6), 41.3, 'A6', .82, .30, .22, 8)
stk(41.5, TOTAL, 'A1', .18, .87, .30, -8, 'float')
stk(41.7, TOTAL, 'A7', .83, .87, .30, 10, 'float')

# particles: coin rain / flying docs / speed lines
PT = [dict(kind='coins', t0=R(4.4), t1=R(5.70), xr=(.04, .48)), dict(kind='coins', t0=R(21.05), t1=R(22.5), xr=(.04, .48)),
      dict(kind='coins', t0=R(17.6), t1=R(19.5)),
      dict(kind='docs', t0=R(14.6), t1=R(16.0)), dict(kind='speed', t0=R(29.6), t1=R(31.05)),
      dict(kind='speed', t0=R(33.25), t1=R(35.4)), dict(kind='speed', t0=R(9.2), t1=R(11.0))]
# camera shake windows: (t0, t1, amplitude px@1080)
SHAKE = [(R(7.9), R(8.5), 10), (R(28.1), R(28.6), 12), (R(29.6), R(31.05), 7), (R(33.25), R(33.9), 14),
         (R(4.6), R(5.0), 10)]

_st = {}
def sticker(name, w):
    k = (name, w)
    if k not in _st:
        im = Image.open(f'{WD}/st/{name}.png').convert('RGBA')
        tw = max(4, int(W * w))
        im = im.resize((tw, max(4, int(im.height * tw / im.width))), Image.LANCZOS)
        # drop shadow baked in
        sh = Image.new('RGBA', (im.width + 40, im.height + 40), (0, 0, 0, 0))
        a = im.split()[3].point(lambda v: v * 0.45)
        blk = Image.new('RGBA', im.size, (0, 0, 0, 255)); blk.putalpha(a)
        sh.alpha_composite(blk, (14, 22)); sh = sh.filter(ImageFilter.GaussianBlur(8))
        sh.alpha_composite(im, (6, 6))
        _st[k] = sh
    return _st[k]

def paste_center(im, spr, x, y, scale=1.0, rot=0.0):
    if scale <= 0.02:
        return
    s = spr
    if abs(scale - 1) > 1e-3:
        s = s.resize((max(2, int(s.width * scale)), max(2, int(s.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.2:
        s = s.rotate(rot, resample=Image.BILINEAR, expand=True)
    _safe_paste(im, s, int(x - s.width / 2), int(y - s.height / 2))

def _safe_paste(im, s, px, py):
    # alpha_composite needs non-negative dest; crop sprite when off-canvas
    sx, sy = max(0, -px), max(0, -py)
    if sx >= s.width or sy >= s.height or px >= im.width or py >= im.height:
        return
    s = s.crop((sx, sy, min(s.width, im.width - px + sx), min(s.height, im.height - py + sy)))
    im.alpha_composite(s, (max(px, 0), max(py, 0)))

def draw_stickers(im, t):
    for s in ST:
        if not (s['t0'] <= t < s['t1']):
            continue
        lt = t - s['t0']
        x = lt / .28
        sc = 0 if x <= 0 else (pop(x) * ease_out(x) if x < 1 else 1.0)
        rot = s['rot'] + (1 - ease_out(x)) * -35 * (1 if s['rot'] >= 0 else -1)
        dx = dy = 0
        mo = s['mo']
        if mo == 'wobble':
            rot += 4 * math.sin(lt * 6)
        elif mo == 'float':
            dy = 12 * SC * math.sin(lt * 4); rot += 3 * math.sin(lt * 3)
        elif mo == 'pulse':
            sc *= 1 + 0.08 * math.sin(lt * 14)
        elif mo == 'spin':
            rot += lt * 90
        elif mo == 'shake':
            rot += 9 * math.sin(lt * 40); dx = 4 * SC * math.sin(lt * 53)
        paste_center(im, sticker(s['name'], s['w']), s['x'] * W + dx, s['y'] * H + dy, sc, rot)

def draw_particles(im, t):
    for p in PT:
        if not (p['t0'] <= t < p['t1']):
            continue
        lt = t - p['t0']
        if p['kind'] == 'coins':
            rng = np.random.default_rng(int(p['t0'] * 100))
            for k in range(14):
                x0 = rng.uniform(*p.get('xr', (.05, .95))) * W; delay = rng.uniform(0, .6); spd = rng.uniform(.9, 1.5) * H
                y = -150 * SC + (lt - delay) * spd
                if lt < delay or y > H + 100: continue
                paste_center(im, sticker('A8', rng.uniform(.07, .11)), x0 + 30 * SC * math.sin(lt * 5 + k), y, 1.0, lt * rng.uniform(-300, 300))
        elif p['kind'] == 'docs':
            for k in range(4):
                q = ((lt - k * .25) / .7)
                if q <= 0 or q >= 1: continue
                x = (-.1 + 0.75 * q) * W; y = (.80 + .05 * math.sin(q * 3 + k) - .12 * q) * H
                paste_center(im, sticker('B3', .16), x, y, 1 - .4 * q, -30 + 60 * q)
        elif p['kind'] == 'speed':
            d = ImageDraw.Draw(im)
            rng = np.random.default_rng(int(p['t0'] * 10))
            for k in range(18):
                y = rng.uniform(.25, .95) * H; L = rng.uniform(.15, .4) * W
                x = ((rng.uniform(0, 1) + lt * rng.uniform(2.5, 4)) % 1.4 - .2) * W
                d.line((x, y, x + L, y), fill=(255, 255, 255, 150), width=max(2, int(rng.uniform(4, 9) * SC)))

def shake_offset(t):
    for t0, t1, a in SHAKE:
        if t0 <= t < t1:
            k = 1 - (t - t0) / (t1 - t0) * 0.5
            return int(a * SC * k * math.sin(t * 91)), int(a * SC * k * math.cos(t * 77))
    return 0, 0

def frame(t):
    i = max(j for j, s in enumerate(S) if s['t'] <= t + 1e-9)
    s = S[i]
    lt = t - s['t']
    im = render_shot(s, t)
    TR = 0.16
    if lt < TR and i > 0 and s['tr'] != 'none':
        p = ease_out(lt / TR)
        if s['tr'] == 'slide':
            prev = render_shot(S[i - 1], t)
            off = int(W * (1 - p))
            canvas = Image.new('RGB', (W, H))
            canvas.paste(prev, (off - W, 0))
            canvas.paste(im, (off, 0))
            im = canvas.filter(ImageFilter.BoxBlur(int(14 * SC * (1 - p)))) if p < .9 else canvas
        else:  # punch: zoom-in from 1.18 + white flash
            z = 1.18 - 0.18 * p
            cw, ch = W / z, H / z
            im = im.resize((W, H), Image.BILINEAR, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
            a = (1 - p) * 0.55
            im = Image.blend(im, Image.new('RGB', (W, H), (255, 255, 255)), a)
    im = im.convert('RGBA')
    draw_particles(im, t)
    draw_stickers(im, t)
    # captions
    for c in C:
        if c['t0'] <= t < c['t1']:
            x = (t - c['t0']) / .2
            txt = c['text']
            if c.get('count'):
                a, b, dd = c['count']
                txt = txt.format(n=int(round(a + (b - a) * ease_out((t - c['t0']) / dd))))
            ti = text_img(txt, c['style'], c['size'], W * .92)
            sc = pop(x) * (0.55 + 0.45 * ease_out(x))
            if sc != 1:
                ti2 = ti.resize((max(1, int(ti.width * sc)), max(1, int(ti.height * sc))), Image.BILINEAR)
            else:
                ti2 = ti
            px = int(W / 2 - ti2.width / 2)
            py = int(c['y'] * H - ti2.height / 2)
            im.alpha_composite(ti2, (max(px, -ti2.width), max(py, 0)))
            if c['style'] == 'strike' and t - c['t0'] > 1.0:
                q = ease_out((t - c['t0'] - 1.0) / .2)
                d = ImageDraw.Draw(im)
                y = c['y'] * H
                x0 = W / 2 - ti.width / 2 + 20 * SC
                d.line((x0, y + 10 * SC, x0 + (ti.width - 40 * SC) * q, y - 10 * SC), fill=(239, 68, 68, 255), width=int(18 * SC))
    dx, dy = shake_offset(t)
    if dx or dy:
        m = 18 * SC
        im = im.resize((W, H), Image.BILINEAR, box=(m + dx, m + dy, W - m + dx, H - m + dy))
    return im.convert('RGB')

if __name__ == '__main__':
    n = int(TOTAL * FPS)
    only = None
    if len(sys.argv) > 4:
        only = [float(x) for x in sys.argv[4].split(',')]
    if only:
        for t in only:
            frame(t).save(f'{OUT}_{t:05.2f}.jpg', quality=85)
        sys.exit()
    p = subprocess.Popen(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium',
                          '-crf', '16' if SC >= 1 else '26', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
    for k in range(n):
        p.stdin.write(frame(k / FPS).tobytes())
    p.stdin.close(); p.wait()
    # cut times for sfx
    json.dump(dict(cuts=[s['t'] for s in S[1:]], caps=[c['t0'] for c in C] + [x['t0'] for x in ST],
                   cards=[s['t'] for s in S if ':' in s['panel'] or s['panel'] == 'final']),
              open(OUT + '.cues.json', 'w'))
