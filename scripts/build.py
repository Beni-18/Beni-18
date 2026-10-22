"""Render the profile: animated SVGs into assets/ and the README. Standard library only.

    python3 scripts/build.py

Live numbers (repo counts, languages, monthly activity) come from the GitHub API, using
$GITHUB_TOKEN or `gh auth token` when available. Words and facts live in content.py.
"""

import datetime as dt
import itertools
import json
import math
import os
import random
import subprocess
import textwrap
import urllib.request
from html import escape
from pathlib import Path

import content as c

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# matte black + blue
BG, PANEL, LINE, GRID = "#0A0C0F", "#0F1217", "#1C222B", "#12171E"
TEXT, MUTED, DIM, GHOST = "#E8EDF4", "#8B95A4", "#4A5361", "#222A35"
BLUE, BLUE2, ICE, DEEP, CYAN = "#2F6BFF", "#5C8DFF", "#A8C6FF", "#14306E", "#38BDF8"
MONO = "ui-monospace,'SF Mono',Menlo,'DejaVu Sans Mono','Courier New',monospace"
SANS = "'Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif"
CW = 0.6  # monospace advance, in font-size units

_ids = itertools.count()
random.seed(18)


# ------------------------------------------------------------------ github

def _token():
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip() or None
    except FileNotFoundError:
        return None


TOKEN = _token()


def api(path):
    req = urllib.request.Request(f"https://api.github.com/{path}",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "beni-18-profile"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def stats():
    user = api(f"users/{c.USER}")
    repos, page = [], 1
    while True:
        batch = api(f"users/{c.USER}/repos?per_page=100&type=owner&page={page}")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    langs = {}
    for r in repos:
        if r["fork"]:
            continue
        for name, size in api(f"repos/{c.USER}/{r['name']}/languages").items():
            langs[name] = langs.get(name, 0) + size
    return {
        "created": dt.datetime.fromisoformat(user["created_at"].replace("Z", "+00:00")),
        "public": len(repos),
        "own": sum(not r["fork"] for r in repos),
        "forks": sum(r["fork"] for r in repos),
        "repos": repos,
        "langs": langs,
        "now": dt.datetime.now(dt.timezone.utc),
    }


# ------------------------------------------------------------------ svg primitives

def svg(w, h, body, desc, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">\n'
            f"<desc>{escape(desc)}</desc>\n<style>\n"
            f"text{{font-family:{MONO}}} .s{{font-family:{SANS}}}\n"
            "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}\n"
            ".cur{animation:blink 1.06s steps(1) infinite}\n"
            "@keyframes fade{from{opacity:0}to{opacity:1}}\n"
            "@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}\n"
            ".fade{opacity:0;animation:fade .5s ease-out forwards}\n"
            ".rise{opacity:0;animation:rise .55s cubic-bezier(.2,.7,.2,1) forwards}\n"
            f"{css}</style>\n{body}\n</svg>\n")


def t(x, y, s, size=14, fill=TEXT, cls="", anchor="start", weight=400, extra=""):
    c_ = f' class="{cls}"' if cls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}"{c_} {extra} xml:space="preserve">{escape(s)}</text>')


def typed(x, y, s, size, fill, start=0.0, cps=24, cursor=True, weight=400, linger=False):
    """Typewriter text with a block cursor, like a terminal eyebrow."""
    n, cw = len(s), size * CW
    i, dur = next(_ids), max(len(s), 1) / cps
    widths = ";".join(f"{k * cw:.1f}" for k in range(n + 1))
    keys = ";".join(f"{k / n:.4f}" for k in range(n + 1))
    out = (f'<clipPath id="ty{i}"><rect x="{x}" y="{y - size * 1.1:.1f}" width="0" height="{size * 1.5:.1f}">'
           f'<animate attributeName="width" values="{widths}" keyTimes="{keys}" calcMode="discrete" '
           f'begin="{start:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
           f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" textLength="{n * cw:.1f}" '
           f'lengthAdjust="spacingAndGlyphs" clip-path="url(#ty{i})" xml:space="preserve">{escape(s)}</text>')
    if cursor:
        xs = ";".join(f"{x + k * cw + 2:.1f}" for k in range(n + 1))
        out += (f'<rect x="{x + 2}" y="{y - size * .8:.1f}" width="{cw * .85:.1f}" height="{size * .95:.1f}" fill="{BLUE}">'
                f'<animate attributeName="x" values="{xs}" keyTimes="{keys}" calcMode="discrete" begin="{start:.2f}s" '
                f'dur="{dur:.2f}s" fill="freeze"/>'
                f'<animate attributeName="opacity" values="1;0" keyTimes="0;0.5" calcMode="discrete" dur="1.06s" '
                f'begin="{start + dur:.2f}s" repeatCount="indefinite"/>')
        if not linger:
            out += f'<set attributeName="visibility" to="hidden" begin="{start + dur + 1.6:.2f}s" fill="freeze"/>'
        out += "</rect>"
    return out


def grid(w, h, step=40, color=GRID):
    return "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="{color}"/>' for x in range(step, w, step))


def pixels(x, y, rows, cell, colors, cls="", start=0.0, stagger=0.04):
    """Pixel cluster from strings of '1'/'0'. Colours cycle so the shape reads as noise."""
    out = []
    k = 0
    for r, row in enumerate(rows):
        for col, on in enumerate(row):
            if on != "1":
                continue
            fill = colors[(r * 7 + col * 3) % len(colors)]
            out.append(f'<rect x="{x + col * cell}" y="{y + r * cell}" width="{cell - 1}" height="{cell - 1}" '
                       f'fill="{fill}" class="{cls}" style="animation-delay:{start + k * stagger:.2f}s"/>')
            k += 1
    return "".join(out)


def ts(x, y, parts, size, cls="", weight=700):
    """One text run with differently coloured pieces, so suffixes like '/' sit exactly after the word."""
    spans = "".join(f'<tspan fill="{fill}">{escape(s)}</tspan>' for s, fill in parts)
    c_ = f' class="{cls}"' if cls else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}"{c_} xml:space="preserve">{spans}</text>'


def wrap(s, width):
    return textwrap.wrap(s, width)


# ------------------------------------------------------------------ hero

GLYPHS = {
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "I": ["111", "010", "010", "010", "010", "010", "111"],
    "-": ["0000", "0000", "1001", "1111", "0000", "0000", "0000"],  # a hyphen, or two ears
    "1": ["00100", "01100", "10100", "00100", "00100", "00100", "11111"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
}
SITTING = ["010001000", "011011000", "011111000", "010101000", "011111001",
           "001110001", "011111010", "011111100", "011111000"]
PAW = ["01010", "10101", "00000", "01110", "11111", "01110"]
FACE = ["1000001", "1100011", "1111111", "1010101", "1111111", "0111110"]


def hero(st):
    W, H = 1200, 480
    css = (".cell{opacity:0;animation:fade .3s ease-out forwards}\n"
           "@keyframes scan{from{transform:translateX(-80px)}to{transform:translateX(1240px)}}\n"
           ".scan{animation:scan 6.5s linear 1.8s infinite}\n"
           "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(var(--d))}}\n"
           ".bob{animation:bob var(--t) ease-in-out infinite}\n"
           "@keyframes shimmer{0%,100%{opacity:1}50%{opacity:.45}}\n"
           ".sh{animation:shimmer 2.8s ease-in-out infinite}\n")
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>', grid(W, H)]
    p.append(f'<line x1="0" y1="72" x2="{W}" y2="72" stroke="{LINE}"/><line x1="0" y1="{H - 78}" x2="{W}" y2="{H - 78}" stroke="{LINE}"/>')

    # eyebrow, like a terminal prompt
    p.append(typed(40, 46, "bennish-christopher/", 18, TEXT, start=.2, cursor=False, weight=600))
    p.append(typed(40 + 21 * 18 * CW, 46, f"{c.ROLE} · {c.PLACE}", 18, MUTED, start=1.1, linger=True))
    right = [("public-repos/", str(st["public"])), ("models-shipped/", str(len(c.ZOO))), ("since/", st["created"].strftime("%Y.%m"))]
    x = W - 40
    for label, val in reversed(right):
        p.append(t(x, 46, val, 18, BLUE2, anchor="end", weight=700))
        x -= len(val) * 18 * CW + 8
        p.append(t(x, 46, label, 15, DIM, anchor="end"))
        x -= len(label) * 15 * CW + 34

    # split letterforms
    word, cell, step, gap = "BENI-18", 20, 24, 2
    widths = [len(GLYPHS[ch][0]) for ch in word]
    total = (sum(widths) + gap * (len(word) - 1)) * step
    x0, y0 = (W - total) / 2, 128
    col = 0
    seps = []
    for i, ch in enumerate(word):
        fill = BLUE if ch in "18" else (DIM if ch == "-" else TEXT)
        for r, row in enumerate(GLYPHS[ch]):
            for k, on in enumerate(row):
                if on == "1":
                    delay = .5 + (col + k) * .028 + r * .012
                    p.append(f'<rect class="cell" style="animation-delay:{delay:.2f}s" x="{x0 + (col + k) * step:.1f}" '
                             f'y="{y0 + r * step}" width="{cell}" height="{cell}" fill="{fill}"/>')
        col += widths[i]
        if i < len(word) - 1:
            seps.append(x0 + (col + gap / 2) * step - (step - cell) / 2)
        col += gap
    for i, sx in enumerate(seps):
        top, bot = y0 - 30, y0 + 7 * step + 24
        p.append(f'<line x1="{sx:.1f}" y1="{top}" x2="{sx:.1f}" y2="{bot}" stroke="{BLUE}" stroke-width="2" opacity=".85"/>')
        d, tt = (-1) ** i * (14 + i * 5), 2.2 + i * .45
        p.append(f'<rect class="bob" style="--d:{d}px;--t:{tt:.2f}s" x="{sx - 4:.1f}" y="{y0 + 60 + (i % 3) * 22}" width="8" height="8" fill="{ICE}"/>')

    # scanning beam across the letters
    p.append('<defs><linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="#2F6BFF" stop-opacity="0"/>'
             '<stop offset=".85" stop-color="#2F6BFF" stop-opacity=".28"/><stop offset="1" stop-color="#A8C6FF" stop-opacity=".9"/>'
             '</linearGradient></defs>')
    p.append(f'<g class="scan"><rect x="0" y="{y0 - 30}" width="80" height="{7 * step + 54}" fill="url(#beam)"/></g>')

    # symbol trail
    trail = "-/).+=^.^=*&;~>"
    tones = [BLUE, BLUE2, CYAN, ICE, DEEP, BLUE2, BLUE]
    for i, ch in enumerate(trail):
        bx, by = 40 + i * 28, H - 52
        fill = tones[i % len(tones)]
        ink = ICE if fill == DEEP else BG
        p.append(f'<g class="rise" style="animation-delay:{2.0 + i * .06:.2f}s"><rect x="{bx}" y="{by}" width="26" height="26" fill="{fill}"/>'
                 + t(bx + 13, by + 18.5, ch, 16, ink, anchor="middle", weight=700) + "</g>")

    # uptime, like a countdown that only counts up
    age = st["now"] - st["created"]
    yrs, rem = divmod(age.days, 365)
    mos, days = divmod(rem, 30)
    ux = 40 + len(trail) * 28 + 40
    p.append(t(ux, H - 33, "uptime/", 15, DIM))
    p.append(t(ux + 8 * 15 * CW, H - 33, f"{yrs:02d}y", 20, TEXT, weight=700))
    p.append(t(ux + 8 * 15 * CW + 3.2 * 20 * CW, H - 33, ":", 20, BLUE, cls="cur", weight=700))
    p.append(t(ux + 8 * 15 * CW + 4.2 * 20 * CW, H - 33, f"{mos:02d}m", 20, TEXT, weight=700))
    p.append(t(ux + 8 * 15 * CW + 7.4 * 20 * CW, H - 33, ":", 20, BLUE, cls="cur", weight=700))
    p.append(t(ux + 8 * 15 * CW + 8.4 * 20 * CW, H - 33, f"{days:02d}d", 20, TEXT, weight=700))

    p.append(pixels(W - 96, H - 64, SITTING, 6, [BLUE, DEEP, BLUE2, "#1E4FC4", ICE], cls="rise sh", start=2.6, stagger=.015))
    return svg(W, H, "".join(p), "BENI-18. Bennish Christopher, ML and AI engineer, Coimbatore. =^..^=", css)


# ------------------------------------------------------------------ section header

def header(idx, title, eyebrow, fn, count=""):
    W, H = 1200, 104
    css = ("@keyframes slide{from{transform:translateX(0)}to{transform:translateX(1060px)}}\n"
           ".sl{animation:slide 5s cubic-bezier(.6,0,.4,1) infinite alternate}\n"
           "@keyframes pulse{0%,100%{opacity:.25}50%{opacity:1}}\n")
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    p.append(t(40, 30, idx, 16, BLUE, weight=700))
    p.append(typed(40 + 4 * 16 * CW, 30, eyebrow, 16, MUTED, start=.15, cps=30))
    p.append(f'<g class="rise" style="animation-delay:.1s">{ts(38, 76, [(title.rstrip("/"), TEXT), ("/", BLUE)], 40, cls="s")}</g>')
    fw = len(fn) * 14 * CW + 24
    p.append(f'<rect x="{W - 40 - fw:.1f}" y="52" width="{fw:.1f}" height="28" fill="none" stroke="{LINE}"/>')
    p.append(t(W - 40 - fw / 2, 71, fn, 14, ICE, anchor="middle"))
    if count:
        p.append(t(W - 52 - fw, 71, count, 13, DIM, anchor="end"))
    p.append(f'<line x1="40" y1="{H - 6}" x2="{W - 40}" y2="{H - 6}" stroke="{LINE}"/>')
    p.append(f'<rect class="sl" x="40" y="{H - 7}" width="100" height="3" fill="{BLUE}"/>')
    for i in range(4):
        p.append(f'<rect x="{W - 40 - 10 * (i + 1)}" y="{H - 18}" width="7" height="7" fill="{[BLUE, ICE, BLUE2, DEEP][i]}" '
                 f'style="animation:pulse 1.8s ease-in-out {i * .3:.1f}s infinite"/>')
    return svg(W, H, "".join(p), f"{idx} {title}", css)


# ------------------------------------------------------------------ whoami

def whoami():
    W, H = 1200, 380
    css = "@keyframes ping{0%{r:5;opacity:.9}100%{r:16;opacity:0}}\n.ping{animation:ping 1.6s ease-out infinite}\n"
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    p.append(f'<rect x="40" y="10" width="720" height="{H - 20}" fill="{PANEL}" stroke="{LINE}"/>')
    p.append(t(64, 46, "model_card.yaml", 14, MUTED))
    p.append(t(736, 46, "v2026.10", 13, DIM, anchor="end"))
    p.append(f'<line x1="40" y1="62" x2="760" y2="62" stroke="{LINE}"/>')
    y = 96
    for i, (k, v) in enumerate(c.MODEL_CARD):
        p.append(f'<g class="rise" style="animation-delay:{.15 + i * .08:.2f}s">'
                 + t(64, y, f"{k}:", 15, BLUE2) + t(214, y, v, 15, TEXT) + "</g>")
        y += 29
    p.append(f'<g class="rise" style="animation-delay:{.15 + len(c.MODEL_CARD) * .08:.2f}s">' + t(64, y, "status:", 15, BLUE2)
             + f'<circle cx="222" cy="{y - 5}" r="5" fill="{BLUE}"/><circle class="ping" cx="222" cy="{y - 5}" r="5" fill="none" stroke="{BLUE}" stroke-width="2"/>'
             + t(236, y, c.STATUS, 15, TEXT, weight=700) + "</g>")

    p.append(f'<rect x="790" y="10" width="370" height="{H - 20}" fill="{PANEL}" stroke="{LINE}"/>')
    p.append(t(814, 46, "recent-wins/", 14, MUTED))
    p.append(f'<line x1="790" y1="62" x2="1160" y2="62" stroke="{LINE}"/>')
    p.append(pixels(1110, 24, FACE, 4, [GHOST, "#1A2230", GHOST], cls="fade", start=1.2, stagger=.01))
    y = 98
    for i, (head, sub) in enumerate(c.WINS):
        p.append(f'<g class="rise" style="animation-delay:{.4 + i * .1:.2f}s">'
                 + t(814, y, f"{i + 1:02d}", 13, BLUE, weight=700) + t(846, y, head, 16, TEXT, cls="s", weight=600)
                 + t(846, y + 21, sub, 12.5, MUTED) + "</g>")
        y += 56
    return svg(W, H, "".join(p), "Model card for Bennish Christopher, with recent wins.", css)


# ------------------------------------------------------------------ training log

def month_index(d, start):
    return (d.year - start.year) * 12 + d.month - start.month


def training_log(st):
    W, H = 1200, 590
    css = ("@keyframes draw{from{stroke-dashoffset:var(--len)}to{stroke-dashoffset:0}}\n"
           ".draw{stroke-dasharray:var(--len);stroke-dashoffset:var(--len);animation:draw 3.2s cubic-bezier(.4,0,.2,1) .6s forwards}\n"
           ".bar{transform-box:fill-box;transform-origin:bottom;opacity:0;animation:grow .5s ease-out forwards}\n"
           "@keyframes grow{from{opacity:0;transform:scaleY(0)}to{opacity:1;transform:scaleY(1)}}\n"
           "@keyframes ping{0%{r:4;opacity:.9}100%{r:14;opacity:0}}\n.ping{animation:ping 1.6s ease-out 3.8s infinite}\n")
    start = st["created"].replace(day=1)
    months = month_index(st["now"], start) + 1
    own, fork = [0] * months, [0] * months
    for r in st["repos"]:
        m = month_index(dt.datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")), start)
        if 0 <= m < months:
            (fork if r["fork"] else own)[m] += 1
    x0, x1, y0, y1 = 80, 1150, 120, 390
    bw = (x1 - x0) / months
    peak = max(a + b for a, b in zip(own, fork)) or 1

    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    p.append(f'<rect x="40" y="10" width="{W - 80}" height="{H - 20}" fill="{PANEL}" stroke="{LINE}"/>')
    p.append(t(64, 46, "training_log.csv", 14, MUTED))
    p.append(t(64 + 17 * 14 * CW, 46, f"· {months} months · {st['public']} repos", 14, DIM))
    lx = W - 64
    for label, color, kind in [("forked team repos", DEEP, "sq"), ("repos created / month", BLUE, "sq"), ("loss = what i didn't know yet", ICE, "ln")]:
        p.append(t(lx, 46, label, 13, MUTED, anchor="end"))
        lx -= len(label) * 13 * CW + 10
        p.append(f'<rect x="{lx - 12:.1f}" y="36" width="12" height="12" fill="{color}"/>' if kind == "sq"
                 else f'<line x1="{lx - 22:.1f}" y1="42" x2="{lx:.1f}" y2="42" stroke="{color}" stroke-width="2.5"/>')
        lx -= 40
    p.append(f'<line x1="40" y1="62" x2="{W - 40}" y2="62" stroke="{LINE}"/>')

    for gy in range(4):
        yy = y0 + gy * (y1 - y0) / 4
        p.append(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" stroke="{GRID}"/>')
    p.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{LINE}"/>')

    # epochs
    starts = [month_index(dt.datetime.strptime(e[2], "%Y-%m").replace(tzinfo=dt.timezone.utc), start) for e in c.EPOCHS]
    for (num, *_), m in zip(c.EPOCHS, starts):
        ex = x0 + max(m, 0) * bw
        p.append(f'<line x1="{ex:.1f}" y1="{y0 - 22}" x2="{ex:.1f}" y2="{y1}" stroke="{LINE}" stroke-dasharray="3 4"/>')
        p.append(t(ex + 6, y0 - 8, f"e{num}", 12, BLUE2, weight=700))

    # bars: real repo creation per month
    for m in range(months):
        hx = x0 + m * bw + bw * .18
        ho = own[m] / peak * (y1 - y0 - 40)
        hf = fork[m] / peak * (y1 - y0 - 40)
        if own[m]:
            p.append(f'<rect class="bar" style="animation-delay:{.2 + m * .03:.2f}s" x="{hx:.1f}" y="{y1 - ho:.1f}" width="{bw * .64:.1f}" height="{ho:.1f}" fill="{BLUE}"/>')
        if fork[m]:
            p.append(f'<rect class="bar" style="animation-delay:{.2 + m * .03:.2f}s" x="{hx:.1f}" y="{y1 - ho - hf:.1f}" width="{bw * .64:.1f}" height="{hf:.1f}" fill="{DEEP}"/>')
        if own[m] + fork[m] >= peak * .5:
            p.append(t(hx + bw * .32, y1 - ho - hf - 8, str(own[m] + fork[m]), 12, ICE, anchor="middle", weight=700))

    # loss: falls over time, kicks up at each new epoch, then settles again
    pts = []
    for m in range(months * 4 + 1):
        u = m / 4
        base = .12 + .82 * math.exp(-2.6 * u / months)
        kick = sum(.16 * math.exp(-(u - s) * 1.1) for s in starts if 0 < s <= u)
        noise = .018 * math.sin(u * 3.1) + .012 * math.sin(u * 7.7)
        val = min(base + kick * (1 - u / months * .6) + noise, .98)
        pts.append((x0 + u * bw, y0 + (1 - val) * (y1 - y0)))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    length = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    p.append(f'<path class="draw" style="--len:{length:.0f}" d="{d}" fill="none" stroke="{ICE}" stroke-width="2.5" stroke-linejoin="round"/>')
    ex, ey = pts[-1]
    p.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{ICE}" class="fade" style="animation-delay:3.7s"/>'
             f'<circle class="ping" cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="none" stroke="{ICE}" stroke-width="2"/>')
    cx_, cy_ = pts[-14]
    p.append(f'<g class="fade" style="animation-delay:4.2s" transform="translate({cx_ - 6:.1f},{cy_ - 13:.1f}) scale(.55)">'
             f'<path d="M2 22 Q2 10 8 8 L6 1 L11 6 L15 6 L20 1 L18 8 Q24 10 24 22 Z M24 20 Q31 19 29 10" fill="{GHOST}" stroke="{GHOST}" stroke-width="1.5"/></g>')

    # x labels
    for m in range(0, months):
        d_ = (start.month - 1 + m)
        yr, mo = start.year + d_ // 12, d_ % 12 + 1
        if mo in (1, 7) or m == 0:
            p.append(t(x0 + m * bw, y1 + 22, f"{yr}.{mo:02d}", 12, DIM))
    p.append(t(x1, y1 + 22, "now", 12, BLUE2, anchor="end", weight=700))

    # epoch notes
    colw = (W - 128) / len(c.EPOCHS)
    for i, (num, name, since, lines) in enumerate(c.EPOCHS):
        ex = 64 + i * colw
        p.append(f'<g class="rise" style="animation-delay:{1.0 + i * .15:.2f}s">'
                 + t(ex, 458, f"epoch_{num} · {since.replace('-', '.')}", 13.5, BLUE2)
                 + ts(ex, 484, [(name, TEXT), ("/", BLUE)], 19, cls="s")
                 + "".join(t(ex, 510 + j * 22, ln, 13.5, MUTED) for j, ln in enumerate(lines)) + "</g>")
    return svg(W, H, "".join(p), "Training log: repos created per month since the account began, grouped into five epochs.", css)


# ------------------------------------------------------------------ flagship cards

def card(f, i):
    W, H = 600, 340
    css = "@keyframes ecg{from{stroke-dashoffset:420}to{stroke-dashoffset:0}}\n.ecg{stroke-dasharray:420;animation:ecg 2.4s linear infinite}\n"
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" fill="{PANEL}" stroke="{LINE}"/>', grid(W, H, 30, "#11161D")]
    p.append(typed(24, 37, f["slug"], 15, MUTED, start=.1 + i * .1, cps=28, linger=True))
    tag_w = len(f["tag"]) * 12 * CW + 20
    p.append(f'<rect x="{W - 24 - tag_w:.1f}" y="20" width="{tag_w:.1f}" height="24" fill="none" stroke="{DEEP}"/>')
    p.append(t(W - 24 - tag_w / 2, 36.5, f["tag"], 12, ICE, anchor="middle"))
    p.append(f'<line x1="0" y1="56" x2="{W}" y2="56" stroke="{LINE}"/>')
    p.append(f'<g class="rise" style="animation-delay:.2s">{t(24, 100, f["title"], 30, TEXT, cls="s", weight=700)}'
             f'{t(W - 24, 98, "↗", 24, BLUE, anchor="end", weight=700)}</g>')
    for j, ln in enumerate(wrap(f["desc"], 58)[:3]):
        p.append(t(24, 134 + j * 23, ln, 17, MUTED, cls="s"))
    tw = (W - 48 - 2 * 12) / 3
    for j, (val, label) in enumerate(f["metrics"]):
        mx = 24 + j * (tw + 12)
        p.append(f'<g class="rise" style="animation-delay:{.4 + j * .12:.2f}s"><rect x="{mx:.1f}" y="206" width="{tw:.1f}" height="76" fill="{BG}" stroke="{LINE}"/>'
                 f'<rect x="{mx:.1f}" y="206" width="3" height="76" fill="{BLUE}"/>'
                 + t(mx + 14, 241, val, 27, BLUE2, cls="s", weight=700) + t(mx + 14, 268, label, 13, MUTED) + "</g>")
    p.append(t(24, 318, f["stack"], 14, DIM))
    if f.get("deco") == "ecg":
        beat = "M0 12 L40 12 L46 4 L52 20 L58 12 L96 12 L100 6 L104 12 L108 6 L112 12 L150 12 L156 2 L162 22 L168 12 L210 12"
        p.append(f'<path class="ecg" transform="translate(300,24) scale(.72)" d="{beat}" fill="none" stroke="{BLUE}" stroke-width="2"/>')
    elif f.get("deco") == "paw":
        p.append(pixels(W - 50, H - 46, PAW, 6, [GHOST, "#1A2230"], cls="fade", start=1.0, stagger=.02))
    else:
        p.append(pixels(W - 40, H - 34, ["101", "011", "110"], 7, [DEEP, BLUE, ICE], cls="fade", start=1.0))
    return svg(W, H, "".join(p), f'{f["title"]}: {f["desc"]}', css)


# ------------------------------------------------------------------ model zoo

def zoo_tile(num, repo, sym, algo, data, fam):
    W, H = 170, 216
    name, color = c.FAMILIES[fam]
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" fill="{PANEL}" stroke="{LINE}"/>',
         f'<rect x="0" y="0" width="{W}" height="4" fill="{color}"/>']
    p.append(t(14, 30, f"{num:02d}", 14, color, weight=700))
    p.append(t(W - 14, 30, fam, 12, DIM, anchor="end"))
    p.append(f'<g class="rise" style="animation-delay:{num * .03:.2f}s">{t(14, 90, sym, 50, TEXT, cls="s", weight=700)}</g>')
    algo_lines = wrap(algo, 15)[:2]
    for j, ln in enumerate(algo_lines):
        p.append(t(14, 120 + j * 18, ln, 15, color, weight=700))
    for j, ln in enumerate(wrap(data, 17)[:2]):
        p.append(t(14, 120 + len(algo_lines) * 18 + 4 + j * 16, ln, 13.5, MUTED))
    p.append(f'<line x1="14" y1="{H - 30}" x2="{W - 14}" y2="{H - 30}" stroke="{LINE}"/>')
    p.append(t(14, H - 11, "streamlit app", 12.5, DIM))
    p.append(t(W - 14, H - 12, "↗", 13, BLUE, anchor="end", weight=700))
    return svg(W, H, "".join(p), f"{num}. {algo} on {data} ({repo})")


def zoo_legend():
    W, H = 1200, 70
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    p.append(t(40, 28, f"{len(c.ZOO)} elements · each one trained, evaluated and shipped as a Streamlit app · numbered in the order they were built", 14, MUTED))
    x = 40
    for fam, (name, color) in c.FAMILIES.items():
        count = sum(z[4] == fam for z in c.ZOO)
        p.append(f'<rect x="{x}" y="44" width="14" height="14" fill="{color}"/>')
        label = f"{fam} {name} ({count})"
        p.append(t(x + 22, 56, label, 13, TEXT))
        x += 22 + len(label) * 13 * CW + 30
    return svg(W, H, "".join(p), "Legend for the model zoo families.")


# ------------------------------------------------------------------ toolchain

def toolchain(st):
    W, H = 1200, 330
    skip = {"Jupyter Notebook", "Procfile", "Dockerfile", "Makefile", "Shell", "Mako"}
    langs = sorted(((k, v) for k, v in st["langs"].items() if k not in skip), key=lambda kv: -kv[1])
    total = sum(v for _, v in langs) or 1
    top = [kv for kv in langs[:7] if kv[1] / total >= .005]
    other = total - sum(v for _, v in top)
    if other / total >= .005:
        top.append(("other", other))
    tones = [BLUE, BLUE2, CYAN, ICE, "#8B7CFF", "#1E4FC4", "#A9B4C4", DIM]
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    p.append(f'<rect x="40" y="10" width="560" height="{H - 20}" fill="{PANEL}" stroke="{LINE}"/>')
    p.append(t(64, 46, "languages/", 14, MUTED))
    p.append(t(576, 46, "by bytes, own repos", 12, DIM, anchor="end"))
    p.append(f'<line x1="40" y1="62" x2="600" y2="62" stroke="{LINE}"/>')
    x, bw = 64, 512
    for i, (name, v) in enumerate(top):
        w = bw * v / total
        p.append(f'<rect class="fade" style="animation-delay:{.2 + i * .1:.1f}s" x="{x:.1f}" y="84" width="{max(w - 2, 1):.1f}" height="18" fill="{tones[i]}"/>')
        x += w
    for i, (name, v) in enumerate(top):
        col, row = i % 2, i // 2
        lx, ly = 64 + col * 260, 138 + row * 40
        p.append(f'<rect x="{lx}" y="{ly - 11}" width="12" height="12" fill="{tones[i]}"/>')
        p.append(t(lx + 22, ly, name, 15, TEXT))
        p.append(t(lx + 236, ly, f"{v / total * 100:.1f}%", 15, BLUE2, anchor="end", weight=700))

    p.append(f'<rect x="630" y="10" width="530" height="{H - 20}" fill="{PANEL}" stroke="{LINE}"/>')
    p.append(t(654, 46, "beni.lock", 14, MUTED))
    p.append(t(1136, 46, "resolved", 12, DIM, anchor="end"))
    p.append(f'<line x1="630" y1="62" x2="1160" y2="62" stroke="{LINE}"/>')
    y = 96
    for i, (k, v) in enumerate(c.LOCKFILE):
        p.append(f'<g class="rise" style="animation-delay:{.2 + i * .08:.2f}s">' + t(654, y, f"[{k}]", 14, BLUE2, weight=700)
                 + t(760, y, v, 13.5, TEXT) + "</g>")
        y += 34
    p.append(t(654, y + 2, "# 9 lives · 0 merge conflicts", 12, GHOST))
    return svg(W, H, "".join(p), "Languages by bytes across own repos, and the tools used.")


# ------------------------------------------------------------------ footer

def footer():
    W, H = 1200, 220
    css = ("@keyframes odo{from{transform:translateY(0)}to{transform:translateY(-480px)}}\n"
           "@keyframes odo6{from{transform:translateY(0)}to{transform:translateY(-288px)}}\n"
           ".o1{animation:odo 10s steps(10) infinite}.o10{animation:odo6 60s steps(6) infinite}\n")
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>', grid(W, H)]
    p.append(f'<line x1="0" y1="1" x2="{W}" y2="1" stroke="{LINE}"/>')
    p.append(t(40, 52, "status/", 15, DIM))
    p.append(typed(40, 92, c.STATUS, 30, TEXT, start=.3, cps=30, weight=700, linger=True))
    p.append(t(40, 132, f"{c.EMAIL}  ·  {c.LINKEDIN}", 16, MUTED))

    # an odometer that never stops counting
    ox, oy = 870, 70
    p.append(t(ox, 52, "compiling-next-project/", 15, DIM))
    p.append(t(ox, oy + 36, "00:", 40, TEXT, weight=700))
    p.append(f'<clipPath id="odo"><rect x="{ox + 72}" y="{oy}" width="48" height="48"/></clipPath>')
    for cls, dx, n in [("o10", 72, 6), ("o1", 96, 10)]:
        col = "".join(t(ox + dx, oy + 36 + j * 48, str(j % n), 40, BLUE2, weight=700) for j in range(n + 1))
        p.append(f'<g clip-path="url(#odo)"><g class="{cls}">{col}</g></g>')

    # thirty-two bits along the bottom
    bits = "".join(f"{ord(ch):08b}" for ch in "meow")
    for i, b in enumerate(bits):
        p.append(f'<rect x="{40 + i * 14}" y="{H - 44}" width="10" height="10" fill="{BLUE if b == "1" else GHOST}"/>')
    p.append(t(W - 40, H - 34, f"© {dt.date.today().year} {c.NAME} · drawn by scripts/build.py", 12, DIM, anchor="end"))
    return svg(W, H, "".join(p), "Status: open to ML and AI engineering roles. Contact details below.", css)


# ------------------------------------------------------------------ readme

CAT = r"""<!--
      /\_/\
     ( o.o )   you found the source. there are more of us in here.
      > ^ <
-->"""


def readme(st):
    gh = f"https://github.com/{c.USER}"
    img = lambda f, alt, w="100%": f'<img src="assets/{f}" alt="{escape(alt)}" width="{w}">'
    out = [CAT, "", '<p align="center">', img("hero.svg", "BENI-18: Bennish Christopher, ML and AI engineer"), "</p>", ""]
    out += ['<p align="center">', img("h-whoami.svg", "01 whoami"), img("whoami.svg", "Model card and recent wins"), "</p>", ""]
    out += [f'<p align="center"><a href="mailto:{c.EMAIL}"><b>email</b></a> &nbsp;/&nbsp; '
            f'<a href="https://{c.LINKEDIN}"><b>linkedin</b></a> &nbsp;/&nbsp; <a href="#flagship"><b>jump to projects</b></a></p>', ""]

    out += ['<p align="center">', img("h-training-log.svg", "02 training log"),
            img("training-log.svg", "Repos created per month, grouped into five epochs"), "</p>", ""]
    out += ["<sub>How this account learned, read like a training run. The bars are real: every repo, by the month it was created. "
            "Each new epoch kicks the loss back up, because something new is being learned.</sub>", ""]

    out += ['<a id="flagship"></a>', '<p align="center">', img("h-flagship.svg", "03 flagship"), "</p>", ""]
    for a, b in zip(c.FLAGSHIP[::2], c.FLAGSHIP[1::2]):
        out.append('<p align="center">' + " ".join(
            f'<a href="{gh}/{f["repo"]}">{img("card-" + f["slug"].split(".")[0] + ".svg", f["title"] + ": " + f["desc"], "49%")}</a>'
            for f in (a, b)) + "</p>")
    out.append("")

    out += ['<p align="center">', img("h-model-zoo.svg", "04 model zoo"), img("zoo-legend.svg", "Model zoo legend"), "</p>", ""]
    tiles = [f'<a href="{gh}/{repo}">{img(f"zoo-{i + 1:02d}.svg", f"{algo} on {data}", "13%")}</a>'
             for i, (repo, sym, algo, data, fam) in enumerate(c.ZOO)]
    for k in range(0, len(tiles), 7):
        out.append('<p align="center">' + " ".join(tiles[k:k + 7]) + "</p>")
    out += ["", f"<sub>The study notes behind these live in <a href=\"{gh}/Data-Scientist\">Data-Scientist</a>.</sub>", ""]

    out += ['<p align="center">', img("h-side-quests.svg", "05 side quests"), "</p>", "",
            "| repo | what it does | built with |", "|:--|:--|:--|"]
    out += [f"| [`{r}`]({gh}/{r}) | {what} | {how} |" for r, what, how in c.SIDE_QUESTS]
    out += ["", '<p align="center">', img("h-squads.svg", "06 squad builds"), "</p>", "",
            "| team repo | where | what we built |", "|:--|:--|:--|"]
    out += [f"| [`{r}`]({gh}/{r}) | {ev} | {what} |" for r, ev, what in c.SQUADS]
    out += ["", '<p align="center">', img("h-toolchain.svg", "07 toolchain"),
            img("toolchain.svg", "Languages by bytes and tools used"), "</p>", ""]

    out += ["<details>", "<summary><sub>forked to study &amp; practice repos</sub></summary>", "",
            "Forked to learn from: " + " · ".join(f"[`{r}`]({gh}/{r})" for r in c.STUDY_FORKS), "",
            "Early practice: " + " · ".join(f"[`{r}`]({gh}/{r})" for r in c.PRACTICE), "", "</details>", ""]
    out += ['<p align="center">', img("footer.svg", "Open to ML and AI engineering roles"), "</p>", "",
            "<!-- =^..^=  every image here is generated by scripts/build.py from live repo data -->", ""]
    return "\n".join(out)


# ------------------------------------------------------------------ main

def main():
    st = stats()
    ASSETS.mkdir(exist_ok=True)
    files = {
        "hero.svg": hero(st),
        "h-whoami.svg": header("01", "whoami/", "// the person behind the commits", "dev.whoami()"),
        "whoami.svg": whoami(),
        "h-training-log.svg": header("02", "training-log/", "// this account, read as a training run", "dev.fit()", f"{len(c.EPOCHS)} epochs"),
        "training-log.svg": training_log(st),
        "h-flagship.svg": header("03", "flagship/", "// the builds i'd demo first", "dev.ship()", f"{len(c.FLAGSHIP)} projects"),
        "h-model-zoo.svg": header("04", "model-zoo/", "// one repo per algorithm, all deployed", "dev.train()", f"{len(c.ZOO)} models"),
        "zoo-legend.svg": zoo_legend(),
        "h-side-quests.svg": header("05", "side-quests/", "// smaller builds, real users", "dev.explore()", f"{len(c.SIDE_QUESTS)} repos"),
        "h-squads.svg": header("06", "squad-builds/", "// hackathons and client work, built as a team", "dev.collab()", f"{len(c.SQUADS)} teams"),
        "h-toolchain.svg": header("07", "toolchain/", "// what the code is made of", "dev.stack()"),
        "toolchain.svg": toolchain(st),
        "footer.svg": footer(),
    }
    for i, f in enumerate(c.FLAGSHIP):
        files[f"card-{f['slug'].split('.')[0]}.svg"] = card(f, i)
    for i, z in enumerate(c.ZOO):
        files[f"zoo-{i + 1:02d}.svg"] = zoo_tile(i + 1, *z)
    for name, body in files.items():
        (ASSETS / name).write_text(body, encoding="utf-8")
    (ROOT / "README.md").write_text(readme(st), encoding="utf-8")
    print(f"wrote {len(files)} svgs + README.md · {st['public']} repos · {len(st['langs'])} languages")


if __name__ == "__main__":
    main()
