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
import subprocess
import textwrap
import urllib.request
from html import escape
from pathlib import Path

import content as c

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# matte black, blue, and amber for numbers and highlights
BG, PANEL, LINE, GRID = "#0A0C0F", "#0F1217", "#1C222B", "#12171E"
TEXT, MUTED, DIM, GHOST = "#E8EDF4", "#8B95A4", "#4A5361", "#222A35"
BLUE, BLUE2, ICE, DEEP = "#2F6BFF", "#5C8DFF", "#A8C6FF", "#14306E"
AMBER, SAND = "#FFB224", "#FFD98A"
MONO = "ui-monospace,'SF Mono',Menlo,'DejaVu Sans Mono','Courier New',monospace"
SANS = "'Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif"
CW = 0.6   # monospace advance, in font-size units
M = 40     # outer margin on every full-width image
W = 1200   # full-width image width

_ids = itertools.count()


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


def t(x, y, s, size=14, fill=TEXT, cls="", anchor="start", weight=400):
    c_ = f' class="{cls}"' if cls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}"{c_} xml:space="preserve">{escape(s)}</text>')


def ts(x, y, parts, size, cls="", weight=700, anchor="start"):
    """One text run with coloured pieces, so a suffix like '/' sits exactly after the word."""
    spans = "".join(f'<tspan fill="{fill}">{escape(s)}</tspan>' for s, fill in parts)
    c_ = f' class="{cls}"' if cls else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"{c_} xml:space="preserve">{spans}</text>'


def rise(delay, inner):
    return f'<g class="rise" style="animation-delay:{delay:.2f}s">{inner}</g>'


def typed(x, y, s, size, fill, start=0.0, cps=24, cursor=True, weight=400, linger=False):
    """Typewriter text with a block cursor."""
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


def panel(x, y, w, h, title, note=""):
    """The one panel style used everywhere: hairline box, mono title bar."""
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PANEL}" stroke="{LINE}"/>'
           + t(x + 24, y + 36, title, 14, MUTED)
           + f'<line x1="{x}" y1="{y + 52}" x2="{x + w}" y2="{y + 52}" stroke="{LINE}"/>')
    if note:
        out += t(x + w - 24, y + 36, note, 13, DIM, anchor="end")
    return out


def grid(w, h, step=40):
    return "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="{GRID}"/>' for x in range(step, w, step))


def pixels(x, y, rows, cell, colors, cls="", start=0.0, stagger=0.04):
    """Pixel cluster from strings of '1'/'0'. Colours cycle so the shape reads as noise."""
    out, k = [], 0
    for r, row in enumerate(rows):
        for col, on in enumerate(row):
            if on == "1":
                fill = colors[(r * 7 + col * 3) % len(colors)]
                out.append(f'<rect x="{x + col * cell}" y="{y + r * cell}" width="{cell - 1}" height="{cell - 1}" '
                           f'fill="{fill}" class="{cls}" style="animation-delay:{start + k * stagger:.2f}s"/>')
                k += 1
    return "".join(out)


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


def hero(st):
    H = 470
    css = (".cell{opacity:0;animation:fade .3s ease-out forwards}\n"
           "@keyframes scan{from{transform:translateX(-80px)}to{transform:translateX(1240px)}}\n"
           ".scan{animation:scan 6.5s linear 1.8s infinite}\n"
           "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(var(--d))}}\n"
           ".bob{animation:bob var(--t) ease-in-out infinite}\n")
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>', grid(W, H)]
    p.append(f'<line x1="0" y1="72" x2="{W}" y2="72" stroke="{LINE}"/><line x1="0" y1="{H - 76}" x2="{W}" y2="{H - 76}" stroke="{LINE}"/>')

    # top row: who, and since when
    p.append(typed(M, 46, "bennish-christopher/", 18, TEXT, start=.2, cursor=False, weight=600))
    p.append(typed(M + 21 * 18 * CW, 46, f"{c.ROLE} · {c.PLACE}", 18, MUTED, start=1.1, linger=True))
    p.append(ts(W - M, 46, [("since/ ", DIM), (st["created"].strftime("%Y.%m"), AMBER)], 18, anchor="end"))

    # split letterforms
    word, cell, step, gap = "BENI-18", 20, 24, 2
    widths = [len(GLYPHS[ch][0]) for ch in word]
    total = (sum(widths) + gap * (len(word) - 1)) * step - (step - cell)
    x0, y0 = (W - total) / 2, 136
    col, seps = 0, []
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
            # centred in the empty space between this glyph's last cell and the next glyph's first
            seps.append(x0 + col * step - (step - cell) + (gap * step + (step - cell)) / 2)
        col += gap
    for i, sx in enumerate(seps):
        top, bot = y0 - 30, y0 + 7 * step + 26
        p.append(f'<line x1="{sx:.1f}" y1="{top}" x2="{sx:.1f}" y2="{bot}" stroke="{BLUE}" stroke-width="2" opacity=".8"/>')
        d, tt = (-1) ** i * (14 + i * 4), 2.2 + i * .45
        dot = AMBER if i == 2 else ICE
        p.append(f'<rect class="bob" style="--d:{d}px;--t:{tt:.2f}s" x="{sx - 4:.1f}" y="{y0 + 64}" width="8" height="8" fill="{dot}"/>')

    p.append('<defs><linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="#2F6BFF" stop-opacity="0"/>'
             '<stop offset=".85" stop-color="#2F6BFF" stop-opacity=".26"/><stop offset="1" stop-color="#A8C6FF" stop-opacity=".9"/>'
             '</linearGradient></defs>')
    p.append(f'<g class="scan"><rect x="0" y="{y0 - 30}" width="80" height="{7 * step + 56}" fill="url(#beam)"/></g>')

    # bottom row: symbol trail left, live numbers right
    by = H - 50
    trail = "-/).+=^.^=*&;~>"
    tones = [BLUE, BLUE2, AMBER, ICE, DEEP, BLUE2, BLUE]
    for i, ch in enumerate(trail):
        bx = M + i * 28
        fill = tones[i % len(tones)]
        ink = ICE if fill == DEEP else BG
        p.append(rise(2.0 + i * .05, f'<rect x="{bx}" y="{by}" width="26" height="26" fill="{fill}"/>'
                      + t(bx + 13, by + 18.5, ch, 16, ink, anchor="middle", weight=700)))

    age = st["now"] - st["created"]
    yrs, rem = divmod(age.days, 365)
    mos, days = divmod(rem, 30)
    facts = [("repos/ ", str(st["public"])), ("models/ ", str(len(c.ZOO))), ("uptime/ ", f"{yrs:02d}y {mos:02d}m {days:02d}d")]
    x = W - M - 70
    for label, val in reversed(facts):
        p.append(rise(2.6, ts(x, by + 19, [(label, DIM), (val, AMBER)], 17, anchor="end")))
        x -= (len(label) + len(val)) * 17 * CW + 40
    p.append(pixels(W - M - 54, H - 62, SITTING, 6, [BLUE, DEEP, BLUE2, "#1E4FC4", ICE], cls="rise", start=2.8, stagger=.012))
    return svg(W, H, "".join(p), "BENI-18. Bennish Christopher, ML and AI engineer, Coimbatore. =^..^=", css)


# ------------------------------------------------------------------ section header

def header(idx, title, eyebrow, fn):
    H = 104
    css = ("@keyframes slide{from{transform:translateX(0)}to{transform:translateX(1020px)}}\n"
           ".sl{animation:slide 5s cubic-bezier(.6,0,.4,1) infinite alternate}\n")
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    p.append(t(M, 30, idx, 16, AMBER, weight=700))
    p.append(typed(M + 4 * 16 * CW, 30, eyebrow, 16, MUTED, start=.15, cps=30))
    p.append(rise(.1, ts(M - 2, 78, [(title.rstrip("/"), TEXT), ("/", BLUE)], 40, cls="s")))
    fw = len(fn) * 15 * CW + 28
    p.append(f'<rect x="{W - M - fw:.1f}" y="52" width="{fw:.1f}" height="30" fill="none" stroke="{LINE}"/>')
    p.append(t(W - M - fw / 2, 72, fn, 15, ICE, anchor="middle"))
    p.append(f'<line x1="{M}" y1="{H - 6}" x2="{W - M}" y2="{H - 6}" stroke="{LINE}"/>')
    p.append(f'<rect class="sl" x="{M}" y="{H - 7}" width="100" height="3" fill="{BLUE}"/>')
    return svg(W, H, "".join(p), f"{idx} {title}", css)


# ------------------------------------------------------------------ whoami

def whoami():
    rows = c.MODEL_CARD
    half = (len(rows) + 1) // 2
    H = 64 + 52 + half * 34 + 70
    css = "@keyframes ping{0%{r:5;opacity:.9}100%{r:16;opacity:0}}\n.ping{animation:ping 1.6s ease-out infinite}\n"
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>', panel(M, 10, W - 2 * M, H - 20, "model_card.yaml", "v2026.10")]
    colw = (W - 2 * M) / 2
    for i, (k, v) in enumerate(rows):
        cx, ry = M + 24 + (i // half) * colw, 104 + (i % half) * 34
        assert 118 + len(v) * 15 * CW < colw - 24, f"model card value too long: {k}"
        p.append(rise(.15 + i * .06, t(cx, ry, f"{k}:", 15, BLUE2) + t(cx + 118, ry, v, 15, TEXT)))
    sy = 104 + half * 34 + 18
    p.append(f'<line x1="{M}" y1="{sy - 30}" x2="{W - M}" y2="{sy - 30}" stroke="{LINE}"/>')
    p.append(rise(.7, t(M + 24, sy, "status:", 15, BLUE2)
                  + f'<circle cx="{M + 150}" cy="{sy - 5}" r="5" fill="{AMBER}"/>'
                  + f'<circle class="ping" cx="{M + 150}" cy="{sy - 5}" r="5" fill="none" stroke="{AMBER}" stroke-width="2"/>'
                  + t(M + 166, sy, c.STATUS, 15, TEXT, weight=700)))
    return svg(W, H, "".join(p), "Model card for Bennish Christopher.", css)


# ------------------------------------------------------------------ training log

def month_index(d, start):
    return (d.year - start.year) * 12 + d.month - start.month


def training_log(st):
    H = 580
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
    x0, x1, y0, y1 = M + 40, W - M - 24, 116, 380
    bw = (x1 - x0) / months
    peak = max(a + b for a, b in zip(own, fork)) or 1

    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>', panel(M, 10, W - 2 * M, H - 20, "training_log.csv")]
    lx = W - M - 24
    for label, color, kind in [("team forks", DEEP, "sq"), ("repos created", BLUE, "sq"), ("skill", AMBER, "ln")]:
        p.append(t(lx, 46, label, 13, MUTED, anchor="end"))
        lx -= len(label) * 13 * CW + 10
        p.append(f'<rect x="{lx - 12:.1f}" y="36" width="12" height="12" fill="{color}"/>' if kind == "sq"
                 else f'<line x1="{lx - 22:.1f}" y1="42" x2="{lx:.1f}" y2="42" stroke="{color}" stroke-width="2.5"/>')
        lx -= 44

    for gy in range(4):
        yy = y0 + gy * (y1 - y0) / 4
        p.append(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" stroke="{GRID}"/>')
    p.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{LINE}"/>')

    starts = [month_index(dt.datetime.strptime(e[2], "%Y-%m").replace(tzinfo=dt.timezone.utc), start) for e in c.EPOCHS]
    for (num, *_), m in zip(c.EPOCHS, starts):
        ex = x0 + max(m, 0) * bw
        p.append(f'<line x1="{ex:.1f}" y1="{y0 - 20}" x2="{ex:.1f}" y2="{y1}" stroke="{LINE}" stroke-dasharray="3 4"/>')
        p.append(t(ex + 6, y0 - 6, f"e{num}", 12, AMBER, weight=700))

    for m in range(months):
        hx = x0 + m * bw + bw * .18
        ho = own[m] / peak * (y1 - y0 - 40)
        hf = fork[m] / peak * (y1 - y0 - 40)
        if own[m]:
            p.append(f'<rect class="bar" style="animation-delay:{.2 + m * .03:.2f}s" x="{hx:.1f}" y="{y1 - ho:.1f}" width="{bw * .64:.1f}" height="{ho:.1f}" fill="{BLUE}"/>')
        if fork[m]:
            p.append(f'<rect class="bar" style="animation-delay:{.2 + m * .03:.2f}s" x="{hx:.1f}" y="{y1 - ho - hf:.1f}" width="{bw * .64:.1f}" height="{hf:.1f}" fill="{DEEP}"/>')
        if own[m] + fork[m] == peak:
            p.append(t(hx + bw * .32, y1 - ho - hf - 8, str(peak), 12, AMBER, anchor="middle", weight=700))

    # skill climbs over time, with a step up at every new kind of project
    pts = []
    for m in range(months * 4 + 1):
        u = m / 4
        base = .08 + .5 * (1 - math.exp(-2.2 * u / months))
        steps = sum(.075 * (1 - math.exp(-(u - s) * 1.4)) for s in starts if 0 < s <= u)
        wobble = .012 * math.sin(u * 3.1) + .008 * math.sin(u * 7.7)
        val = min(base + steps + wobble, .96)
        pts.append((x0 + u * bw, y0 + (1 - val) * (y1 - y0)))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    length = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    p.append(f'<path class="draw" style="--len:{length:.0f}" d="{d}" fill="none" stroke="{AMBER}" stroke-width="2.5" stroke-linejoin="round"/>')
    ex, ey = pts[-1]
    p.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{AMBER}" class="fade" style="animation-delay:3.7s"/>'
             f'<circle class="ping" cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="none" stroke="{AMBER}" stroke-width="2"/>')
    cx_, cy_ = pts[-16]
    p.append(f'<g class="fade" style="animation-delay:4.2s" transform="translate({cx_ - 6:.1f},{cy_ - 13:.1f}) scale(.55)">'
             f'<path d="M2 22 Q2 10 8 8 L6 1 L11 6 L15 6 L20 1 L18 8 Q24 10 24 22 Z M24 20 Q31 19 29 10" fill="{GHOST}" stroke="{GHOST}" stroke-width="1.5"/></g>')

    for m in range(months):
        k = start.month - 1 + m
        yr, mo = start.year + k // 12, k % 12 + 1
        if mo in (1, 7) or m == 0:
            p.append(t(x0 + m * bw, y1 + 22, f"{yr}.{mo:02d}", 12, DIM))
    p.append(t(x1, y1 + 22, "now", 12, AMBER, anchor="end", weight=700))

    p.append(f'<line x1="{M}" y1="418" x2="{W - M}" y2="418" stroke="{LINE}"/>')
    colw = (W - 2 * M - 48) / len(c.EPOCHS)
    for i, (num, name, since, lines) in enumerate(c.EPOCHS):
        ex = M + 24 + i * colw
        p.append(rise(1.0 + i * .12, t(ex, 452, f"epoch_{num} · {since.replace('-', '.')}", 13, AMBER)
                      + ts(ex, 480, [(name, TEXT), ("/", BLUE)], 19, cls="s")
                      + "".join(t(ex, 508 + j * 22, ln, 13.5, MUTED) for j, ln in enumerate(lines))))
    return svg(W, H, "".join(p), "Training log: repos created per month since the account began, in five epochs.", css)


# ------------------------------------------------------------------ cards

def card(f, i):
    CWD, H = 600, 330
    css = "@keyframes ecg{from{stroke-dashoffset:420}to{stroke-dashoffset:0}}\n.ecg{stroke-dasharray:420;animation:ecg 2.4s linear infinite}\n"
    p = [f'<rect width="{CWD}" height="{H}" fill="{BG}"/>',
         f'<rect x=".5" y=".5" width="{CWD - 1}" height="{H - 1}" fill="{PANEL}" stroke="{LINE}"/>']
    p.append(typed(24, 37, f["slug"], 15, MUTED, start=.1 + i * .1, cps=28, linger=True))
    tag_w = len(f["tag"]) * 12 * CW + 20
    p.append(f'<rect x="{CWD - 24 - tag_w:.1f}" y="20" width="{tag_w:.1f}" height="24" fill="none" stroke="{LINE}"/>')
    p.append(t(CWD - 24 - tag_w / 2, 36.5, f["tag"], 12, ICE, anchor="middle"))
    p.append(f'<line x1="0" y1="56" x2="{CWD}" y2="56" stroke="{LINE}"/>')
    p.append(rise(.2, t(24, 100, f["title"], 30, TEXT, cls="s", weight=700) + t(CWD - 24, 98, "↗", 24, BLUE, anchor="end", weight=700)))
    assert len(wrap(f["desc"], 58)) <= 2, f"card text too long: {f['title']}"
    for j, ln in enumerate(wrap(f["desc"], 58)):
        p.append(t(24, 134 + j * 23, ln, 17, MUTED, cls="s"))
    tw = (CWD - 48 - 24) / 3
    for j, (val, label) in enumerate(f["metrics"]):
        mx = 24 + j * (tw + 12)
        assert 16 + len(label) * 13 * CW <= tw - 10, f"metric label too long: {label}"
        p.append(rise(.4 + j * .12, f'<rect x="{mx:.1f}" y="192" width="{tw:.1f}" height="80" fill="{BG}" stroke="{LINE}"/>'
                      f'<rect x="{mx:.1f}" y="192" width="3" height="80" fill="{BLUE}"/>'
                      + t(mx + 16, 230, val, 28, AMBER, cls="s", weight=700) + t(mx + 16, 256, label, 13, MUTED)))
    p.append(f'<line x1="24" y1="292" x2="{CWD - 24}" y2="292" stroke="{LINE}"/>')
    p.append(t(24, 316, f["stack"], 14, DIM))
    if f.get("deco") == "ecg":
        beat = "M0 12 L40 12 L46 4 L52 20 L58 12 L96 12 L100 6 L104 12 L108 6 L112 12 L150 12 L156 2 L162 22 L168 12 L210 12"
        p.append(f'<path class="ecg" transform="translate(300,24) scale(.72)" d="{beat}" fill="none" stroke="{BLUE}" stroke-width="2"/>')
    elif f.get("deco") == "paw":
        p.append(pixels(CWD - 52, 302, PAW, 4, [GHOST, "#1A2230"], cls="fade", start=1.0, stagger=.02))
    return svg(CWD, H, "".join(p), f'{f["title"]}: {f["desc"]}', css)


def row_card(repo, title, tag, line, stack, i):
    RW, H = 600, 124
    p = [f'<rect width="{RW}" height="{H}" fill="{BG}"/>',
         f'<rect x=".5" y=".5" width="{RW - 1}" height="{H - 1}" fill="{PANEL}" stroke="{LINE}"/>',
         f'<rect x="0" y="0" width="3" height="{H}" fill="{BLUE}"/>']
    p.append(rise(.05 + i * .05, t(24, 42, title, 22, TEXT, cls="s", weight=700)
                  + t(RW - 24, 40, tag, 13, AMBER, anchor="end")))
    assert len(line) <= 62, f"row text too long: {title}"
    p.append(t(24, 72, line, 15, MUTED, cls="s"))
    p.append(ts(24, 102, [(stack, DIM), ("   ↗", BLUE)], 13, weight=400))
    return svg(RW, H, "".join(p), f"{title}: {line}")


# ------------------------------------------------------------------ model zoo

def zoo_tile(num, repo, sym, algo, data, fam):
    TW, H = 170, 190
    name, color = c.FAMILIES[fam]
    p = [f'<rect width="{TW}" height="{H}" fill="{BG}"/>',
         f'<rect x=".5" y=".5" width="{TW - 1}" height="{H - 1}" fill="{PANEL}" stroke="{LINE}"/>',
         f'<rect x="0" y="0" width="{TW}" height="4" fill="{color}"/>']
    p.append(t(14, 30, f"{num:02d}", 14, color, weight=700))
    p.append(t(TW - 14, 30, fam, 12, DIM, anchor="end"))
    p.append(rise(num * .03, t(14, 90, sym, 50, TEXT, cls="s", weight=700)))
    algo_lines = wrap(algo, 15)[:2]
    for j, ln in enumerate(algo_lines):
        p.append(t(14, 122 + j * 18, ln, 15, color, weight=700))
    for j, ln in enumerate(wrap(data, 17)[:2]):
        p.append(t(14, 122 + len(algo_lines) * 18 + 4 + j * 16, ln, 13.5, MUTED))
    return svg(TW, H, "".join(p), f"{num}. {algo} on {data} ({repo})")


def zoo_legend():
    H = 56
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    x = M
    for fam, (name, color) in c.FAMILIES.items():
        count = sum(z[4] == fam for z in c.ZOO)
        p.append(f'<rect x="{x}" y="20" width="14" height="14" fill="{color}"/>')
        p.append(ts(x + 22, 32, [(f"{name} ", TEXT), (str(count), AMBER)], 14, weight=400))
        x += 22 + (len(name) + len(str(count)) + 1) * 14 * CW + 34
    return svg(W, H, "".join(p), "Model zoo families.")


# ------------------------------------------------------------------ toolchain

def toolchain(st):
    H = 330
    skip = {"Jupyter Notebook", "Procfile", "Dockerfile", "Makefile", "Shell", "Mako"}
    langs = sorted(((k, v) for k, v in st["langs"].items() if k not in skip), key=lambda kv: -kv[1])
    total = sum(v for _, v in langs) or 1
    top = [kv for kv in langs[:7] if kv[1] / total >= .005]
    other = total - sum(v for _, v in top)
    if other / total >= .005:
        top.append(("other", other))
    tones = [BLUE, AMBER, BLUE2, SAND, ICE, DEEP, "#A9B4C4", DIM]
    lw = 540
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>', panel(M, 10, lw, H - 20, "languages/", "by bytes, own repos")]
    x, bw = M + 24, lw - 48
    for i, (name, v) in enumerate(top):
        w = bw * v / total
        p.append(f'<rect class="fade" style="animation-delay:{.2 + i * .1:.1f}s" x="{x:.1f}" y="86" width="{max(w - 2, 1):.1f}" height="16" fill="{tones[i]}"/>')
        x += w
    for i, (name, v) in enumerate(top):
        cx, ly = M + 24 + (i % 2) * 252, 144 + (i // 2) * 40
        p.append(f'<rect x="{cx}" y="{ly - 11}" width="12" height="12" fill="{tones[i]}"/>')
        p.append(t(cx + 22, ly, name, 15, TEXT))
        p.append(t(cx + 226, ly, f"{v / total * 100:.1f}%", 15, AMBER, anchor="end", weight=700))

    rx = M + lw + 40
    p.append(panel(rx, 10, W - M - rx, H - 20, "beni.lock", "resolved"))
    y = 98
    for i, (k, v) in enumerate(c.LOCKFILE):
        p.append(rise(.2 + i * .08, t(rx + 24, y, f"[{k}]", 14, BLUE2, weight=700) + t(rx + 140, y, v, 13.5, TEXT)))
        y += 34
    p.append(t(rx + 24, y + 2, "# 9 lives · 0 merge conflicts", 12, GHOST))
    return svg(W, H, "".join(p), "Languages by bytes across own repos, and the tools used.")


# ------------------------------------------------------------------ footer

def footer():
    H = 200
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>', grid(W, H)]
    p.append(f'<line x1="0" y1="1" x2="{W}" y2="1" stroke="{LINE}"/>')
    p.append(t(M, 50, "status/", 15, DIM))
    p.append(typed(M, 92, c.STATUS, 30, TEXT, start=.3, cps=30, weight=700, linger=True))
    p.append(t(W - M, 50, "reach/", 15, DIM, anchor="end"))
    p.append(t(W - M, 82, c.EMAIL, 16, TEXT, anchor="end"))
    p.append(t(W - M, 108, c.LINKEDIN, 16, MUTED, anchor="end"))
    bits = "".join(f"{ord(ch):08b}" for ch in "meow")
    for i, b in enumerate(bits):
        p.append(f'<rect x="{M + i * 14}" y="{H - 44}" width="10" height="10" fill="{BLUE if b == "1" else GHOST}"/>')
    p.append(t(W - M, H - 34, f"© {dt.date.today().year} {c.NAME}", 12, DIM, anchor="end"))
    return svg(W, H, "".join(p), "Status: open to ML and AI engineering roles.")


# ------------------------------------------------------------------ readme

CAT = r"""<!--
      /\_/\
     ( o.o )   you found the source. there are more of us in here.
      > ^ <
-->"""


def readme():
    gh = f"https://github.com/{c.USER}"
    img = lambda f, alt, w="100%": f'<img src="assets/{f}" alt="{escape(alt)}" width="{w}">'
    pair = lambda items: '<p align="center">' + " ".join(items) + "</p>"  # one paragraph: equal gaps both ways
    out = [CAT, "", '<p align="center">', img("hero.svg", "BENI-18: Bennish Christopher, ML and AI engineer"), "</p>", ""]
    out += [f'<p align="center"><sub><a href="mailto:{c.EMAIL}">email</a> &nbsp;·&nbsp; '
            f'<a href="https://{c.LINKEDIN}">linkedin</a> &nbsp;·&nbsp; <a href="#flagship">projects</a> &nbsp;·&nbsp; '
            f'<a href="#model-zoo">model zoo</a></sub></p>', ""]
    out += ['<p align="center">', img("h-whoami.svg", "01 whoami"), img("whoami.svg", "Model card"), "</p>", ""]
    out += ['<p align="center">', img("h-training-log.svg", "02 training log"),
            img("training-log.svg", "Repos created per month, in five epochs"), "</p>", ""]

    out += ['<a id="flagship"></a>', '<p align="center">', img("h-flagship.svg", "03 flagship"), "</p>"]
    out.append(pair([f'<a href="{gh}/{f["repo"]}">{img("card-" + f["slug"].split(".")[0] + ".svg", f["title"] + ": " + f["desc"], "49%")}</a>'
                     for f in c.FLAGSHIP]))
    out.append("")

    out += ['<a id="model-zoo"></a>', '<p align="center">', img("h-model-zoo.svg", "04 model zoo"), img("zoo-legend.svg", "Model zoo families"), "</p>"]
    tiles = [f'<a href="{gh}/{repo}">{img(f"zoo-{i + 1:02d}.svg", f"{algo} on {data}", "13%")}</a>'
             for i, (repo, sym, algo, data, fam) in enumerate(c.ZOO)]
    out.append('<p align="center">' + " ".join(tiles) + "</p>")
    out.append("")

    out += ['<p align="center">', img("h-more.svg", "05 more builds"), "</p>"]
    out.append(pair([f'<a href="{gh}/{m[0]}">{img(f"more-{i + 1:02d}.svg", m[1] + ": " + m[3], "49%")}</a>' for i, m in enumerate(c.MORE)]))
    out += ["", '<p align="center">', img("h-squads.svg", "06 team builds"), "</p>"]
    out.append(pair([f'<a href="{gh}/{s[0]}">{img(f"squad-{i + 1:02d}.svg", s[1] + ": " + s[3], "49%")}</a>' for i, s in enumerate(c.SQUADS)]))
    out += ["", '<p align="center">', img("h-toolchain.svg", "07 toolchain"),
            img("toolchain.svg", "Languages by bytes and tools used"), "</p>", ""]
    out += ['<p align="center">', img("footer.svg", "Open to ML and AI engineering roles"), "</p>", "",
            "<!-- =^..^=  every image here is generated by scripts/build.py from live repo data -->", ""]
    return "\n".join(out)


# ------------------------------------------------------------------ main

def main():
    st = stats()
    ASSETS.mkdir(exist_ok=True)
    for old in ASSETS.glob("*.svg"):
        old.unlink()
    files = {
        "hero.svg": hero(st),
        "h-whoami.svg": header("01", "whoami/", "// the person behind the commits", "dev.whoami()"),
        "whoami.svg": whoami(),
        "h-training-log.svg": header("02", "training-log/", "// this account, read as a training run", "dev.fit()"),
        "training-log.svg": training_log(st),
        "h-flagship.svg": header("03", "flagship/", "// the builds i'd demo first", "dev.ship()"),
        "h-model-zoo.svg": header("04", "model-zoo/", "// one repo per algorithm, all deployed", "dev.train()"),
        "zoo-legend.svg": zoo_legend(),
        "h-more.svg": header("05", "more-builds/", "// agents, analytics and full-stack apps", "dev.explore()"),
        "h-squads.svg": header("06", "team-builds/", "// hackathons and client work", "dev.collab()"),
        "h-toolchain.svg": header("07", "toolchain/", "// what the code is made of", "dev.stack()"),
        "toolchain.svg": toolchain(st),
        "footer.svg": footer(),
    }
    for i, f in enumerate(c.FLAGSHIP):
        files[f"card-{f['slug'].split('.')[0]}.svg"] = card(f, i)
    for i, z in enumerate(c.ZOO):
        files[f"zoo-{i + 1:02d}.svg"] = zoo_tile(i + 1, *z)
    for i, m in enumerate(c.MORE):
        files[f"more-{i + 1:02d}.svg"] = row_card(*m, i)
    for i, s in enumerate(c.SQUADS):
        files[f"squad-{i + 1:02d}.svg"] = row_card(*s, i)
    for name, body in files.items():
        (ASSETS / name).write_text(body, encoding="utf-8")
    (ROOT / "README.md").write_text(readme(), encoding="utf-8")
    print(f"wrote {len(files)} svgs + README.md · {st['public']} repos · {len(st['langs'])} languages")


if __name__ == "__main__":
    main()
