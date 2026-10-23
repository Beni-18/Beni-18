"""Render the profile: SVGs into assets/{dark,light}/ and the README. Standard library only.

    python3 scripts/build.py

Live numbers (repo counts, languages, monthly activity) come from the GitHub API, using
$GITHUB_TOKEN or `gh auth token` when available. Words and facts live in content.py.
"""

import datetime as dt
import json
import os
import subprocess
import textwrap
import urllib.request
from html import escape
from pathlib import Path

import content as c

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Palette: GitHub's own canvas and type colours (Primer primitives 11.10), plus two accents from
# GitHub's display palette, plum and green. Of all non-blue display pairs they score best on hue
# separation (159 degrees), colour-blind separation and contrast (>= 5.6:1 on the panel in both
# modes); the green also matches the contribution graph below the README. Plum marks structure,
# green marks numbers, everything else is neutral. README.md serves each mode its own set.
THEMES = {
    "dark": dict(BG="#0d1117", PANEL="#151b23", LINE="#3d444d", TEXT="#f0f6fc", MUTED="#9198a1", DIM="#656c76",
                 GHOST="#1b222b", GHOST2="#19202a", PLUM="#d07ef7", GREEN="#41b445",
                 BAR="#26a641", BAR2="#0e4429", RAMP=["#d07ef7", "#41b445", "#9198a1", "#656c76", "#3d444d", "#2a313c"]),
    "light": dict(BG="#ffffff", PANEL="#f6f8fa", LINE="#d1d9e0", TEXT="#1f2328", MUTED="#59636e", DIM="#818b98",
                  GHOST="#eef1f4", GHOST2="#f1f3f6", PLUM="#961edc", GREEN="#2b6e3f",
                  BAR="#40c463", BAR2="#9be9a8", RAMP=["#961edc", "#2b6e3f", "#59636e", "#818b98", "#b7bdc5", "#d1d9e0"]),
}
globals().update(THEMES["dark"])

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"  # GitHub's stack
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
W = 1200      # full-width image
IN = 3        # every box is inset 3px, so boxes in neighbouring images sit 6px apart and edges line up
PAD = 24      # inner padding of every box
R = 6         # GitHub's corner radius


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


# ------------------------------------------------------------------ primitives

def svg(w, h, body, desc):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">\n'
            f"<desc>{escape(desc)}</desc>\n<style>\n"
            f"text{{font-family:{SANS}}} .m{{font-family:{MONO}}}\n"
            "@keyframes in{from{opacity:0}to{opacity:1}}\n"
            ".in{opacity:0;animation:in .6s ease-out forwards}\n"
            f"</style>\n{body}\n</svg>\n")


def t(x, y, s, size=14, fill=None, mono=False, anchor="start", weight=400):
    cls = ' class="m"' if mono else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill or TEXT}" text-anchor="{anchor}" '
            f'font-weight="{weight}"{cls} xml:space="preserve">{escape(s)}</text>')


def fade(delay, inner):
    return f'<g class="in" style="animation-delay:{delay:.2f}s">{inner}</g>'


def box(w, h, x=IN, y=IN):
    return f'<rect x="{x + .5}" y="{y + .5}" width="{w - 2 * IN - 1}" height="{h - 2 * IN - 1}" rx="{R}" fill="{PANEL}" stroke="{LINE}"/>'


def hline(x1, x2, y):
    return f'<line x1="{x1}" y1="{y + .5}" x2="{x2}" y2="{y + .5}" stroke="{LINE}"/>'


def cells(x, y, rows, cell, fill, delay=0.0):
    out, k = [], 0
    for r, row in enumerate(rows):
        for col, on in enumerate(row):
            if on == "1":
                out.append(f'<rect class="in" style="animation-delay:{delay + k * .008:.3f}s" x="{x + col * cell}" '
                           f'y="{y + r * cell}" width="{cell - 2}" height="{cell - 2}" fill="{fill}"/>')
                k += 1
    return "".join(out)


def width(s, size, mono=False):
    """Rough rendered width, used only to keep text inside its box."""
    return len(s) * size * (.6 if mono else .54)


# ------------------------------------------------------------------ hero

GLYPHS = {
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "-": ["0000", "0000", "1001", "1111", "0000", "0000", "0000"],  # a hyphen, or two ears
    "1": ["00100", "01100", "10100", "00100", "00100", "00100", "11111"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
}
SITTING = ["010001000", "011011000", "011111000", "010101000", "011111001",
           "001110001", "011111010", "011111100", "011111000"]
PAW = ["01010", "10101", "00000", "01110", "11111", "01110"]


def hero(st):
    H = 250
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    p.append(fade(.05, t(IN, 82, c.NAME, 46, weight=600)))
    p.append(fade(.15, t(IN, 120, "ML and AI Engineer · B.E. Computer Science (AI & ML) · Coimbatore, India", 19, MUTED)))
    p.append(fade(.2, t(IN, 152, c.SUMMARY, 16, MUTED)))
    age = st["now"] - st["created"]
    yrs, mos = age.days // 365, (age.days % 365) // 30
    facts = [(str(st["public"]), "public repositories"), (str(len(c.ZOO)), "deployed ML models"),
             (f"{yrs}y {mos}m", "on GitHub")]
    x = IN
    for i, (val, label) in enumerate(facts):
        p.append(fade(.3 + i * .08, t(x, 212, val, 24, GREEN, weight=600) + t(x + width(val, 24) + 10, 212, label, 15, MUTED)))
        x += width(val, 24) + 10 + width(label, 15) + 48

    # signature mark: B-18 in pixels
    cell, gap = 12, 1
    word = "B-18"
    total = (sum(len(GLYPHS[ch][0]) for ch in word) + gap * (len(word) - 1)) * cell
    mx, my, col = W - IN - total, 64, 0
    for ch in word:
        p.append(cells(mx + col * cell, my, GLYPHS[ch], cell, DIM if ch == "-" else PLUM, delay=.35 + col * .02))
        col += len(GLYPHS[ch][0]) + gap
    p.append(cells(W - IN - 27, H - 36, SITTING, 3, GHOST, delay=1.0))
    p.append(hline(IN, W - IN, H - 2))
    return svg(W, H, "".join(p), f"{c.NAME}, ML and AI engineer. =^..^=")


# ------------------------------------------------------------------ section header

def header(idx, title, note=""):
    H = 66
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    p.append(t(IN, 38, idx, 13, PLUM, mono=True, weight=600))
    p.append(t(IN + 34, 40, title, 22, weight=600))
    if note:
        p.append(t(W - IN, 38, note, 13, MUTED, mono=True, anchor="end"))
    p.append(hline(IN, W - IN, H - 10))
    return svg(W, H, "".join(p), f"{idx} {title}")


# ------------------------------------------------------------------ about

def about():
    rows, half = c.MODEL_CARD, (len(c.MODEL_CARD) + 1) // 2
    H = 2 * IN + PAD + half * 36 + 76
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>', box(W, H)]
    colw = (W - 2 * IN) / 2
    for i, (k, v) in enumerate(rows):
        x, y = IN + PAD + (i // half) * colw, IN + PAD + 22 + (i % half) * 36
        assert 130 + width(v, 15) < colw - PAD, f"about value too long: {k}"
        p.append(fade(.05 + i * .04, t(x, y, k, 14, MUTED) + t(x + 130, y, v, 15)))
    sy = IN + PAD + half * 36 + 8
    p.append(hline(IN + 1, W - IN - 1, sy))
    p.append(fade(.3, f'<circle cx="{IN + PAD + 5}" cy="{sy + 34}" r="5" fill="{GREEN}"/>'
                      + t(IN + PAD + 20, sy + 39, c.STATUS, 15, weight=600)
                      + t(W - IN - PAD, sy + 39, f"{c.EMAIL}  ·  {c.LINKEDIN}", 13, MUTED, mono=True, anchor="end")))
    return svg(W, H, "".join(p), "About Bennish Christopher.")


# ------------------------------------------------------------------ cards

def card(f, i):
    CWD, H = 600, 280
    p = [f'<rect width="{CWD}" height="{H}" fill="{BG}"/>', box(CWD, H)]
    x0, x1 = IN + PAD, CWD - IN - PAD
    p.append(fade(.05, t(x0, 52, f["title"], 22, weight=600) + t(x1, 50, f["tag"], 12, MUTED, mono=True, anchor="end")))
    lines = textwrap.wrap(f["desc"], 62)
    assert len(lines) <= 2, f"card text too long: {f['title']}"
    for j, ln in enumerate(lines):
        p.append(t(x0, 86 + j * 22, ln, 15, MUTED))
    colw = (x1 - x0) / 3
    for j, (val, label) in enumerate(f["metrics"]):
        mx = x0 + j * colw + (16 if j else 0)
        assert width(label, 13) < colw - 24, f"metric label too long: {label}"
        if j:
            p.append(f'<line x1="{x0 + j * colw:.1f}" y1="146" x2="{x0 + j * colw:.1f}" y2="200" stroke="{LINE}"/>')
        p.append(fade(.15 + j * .06, t(mx, 172, val, 26, GREEN, weight=600) + t(mx, 194, label, 13, MUTED)))
    p.append(hline(x0, x1, 222))
    p.append(t(x0, 250, f["stack"], 12.5, DIM, mono=True))
    p.append(t(x1, 250, "↗", 15, PLUM, anchor="end", weight=600))
    if f.get("deco") == "paw":
        p.append(cells(x1 - 44, 238, PAW, 3, GHOST2, delay=.8))
    return svg(CWD, H, "".join(p), f'{f["title"]}: {f["desc"]}')


def row_card(repo, title, tag, line, stack, i):
    RW, H = 600, 108
    p = [f'<rect width="{RW}" height="{H}" fill="{BG}"/>', box(RW, H)]
    x0, x1 = IN + PAD, RW - IN - PAD
    assert width(line, 14) < x1 - x0, f"row text too long: {title}"
    p.append(fade(.05, t(x0, 40, title, 17, weight=600) + t(x1, 39, tag, 12, MUTED, mono=True, anchor="end")))
    p.append(t(x0, 66, line, 14, MUTED))
    p.append(t(x0, 90, stack, 12, DIM, mono=True))
    p.append(t(x1, 90, "↗", 14, PLUM, anchor="end", weight=600))
    return svg(RW, H, "".join(p), f"{title}: {line}")


# ------------------------------------------------------------------ model zoo

def zoo_tile(num, repo, sym, algo, data, fam):
    TW, H = 172, 176
    p = [f'<rect width="{TW}" height="{H}" fill="{BG}"/>', box(TW, H)]
    x0, x1 = IN + 14, TW - IN - 14
    p.append(t(x0, 30, f"{num:02d}", 11, DIM, mono=True))
    p.append(t(x1, 30, c.FAMILIES[fam][0], 11, MUTED, mono=True, anchor="end"))
    p.append(fade(num * .02, t(x0, 76, sym, 34, PLUM, weight=600)))
    algo_lines = textwrap.wrap(algo, 18)[:2]
    for j, ln in enumerate(algo_lines):
        p.append(t(x0, 106 + j * 17, ln, 13.5, weight=600))
    for j, ln in enumerate(textwrap.wrap(data, 20)[:2]):
        p.append(t(x0, 106 + len(algo_lines) * 17 + 4 + j * 16, ln, 12.5, MUTED))
    return svg(TW, H, "".join(p), f"{num}. {algo} on {data} ({repo})")


# ------------------------------------------------------------------ timeline (real data only)

def month_index(d, start):
    return (d.year - start.year) * 12 + d.month - start.month


def timeline(st):
    H = 380
    start = st["created"].replace(day=1)
    months = month_index(st["now"], start) + 1
    own, fork = [0] * months, [0] * months
    for r in st["repos"]:
        m = month_index(dt.datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")), start)
        if 0 <= m < months:
            (fork if r["fork"] else own)[m] += 1
    x0, x1, y0, y1 = IN + PAD, W - IN - PAD, 84, 240
    bw = (x1 - x0) / months
    peak = max(a + b for a, b in zip(own, fork)) or 1

    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>', box(W, H)]
    p.append(t(x0, IN + 42, "Repositories created per month", 15, weight=600))
    lx = x1
    for label, color in [("forked team repos", BAR2), ("own repos", BAR)]:
        p.append(t(lx, IN + 41, label, 12.5, MUTED, anchor="end"))
        lx -= width(label, 12.5) + 10
        p.append(f'<rect x="{lx - 11:.1f}" y="{IN + 31}" width="11" height="11" rx="2" fill="{color}"/>')
        lx -= 30

    starts = [month_index(dt.datetime.strptime(e[2], "%Y-%m").replace(tzinfo=dt.timezone.utc), start) for e in c.EPOCHS]
    for m in starts[1:]:
        ex = x0 + m * bw
        p.append(f'<line x1="{ex:.1f}" y1="{y0 - 8}" x2="{ex:.1f}" y2="{y1}" stroke="{LINE}" stroke-dasharray="2 4"/>')
    p.append(hline(x0, x1, y1))
    for m in range(months):
        hx, bwid = x0 + m * bw + bw * .2, bw * .6
        ho = own[m] / peak * (y1 - y0)
        hf = fork[m] / peak * (y1 - y0)
        if own[m]:
            p.append(f'<rect class="in" style="animation-delay:{.1 + m * .02:.2f}s" x="{hx:.1f}" y="{y1 - ho:.1f}" width="{bwid:.1f}" height="{ho:.1f}" rx="2" fill="{BAR}"/>')
        if fork[m]:
            p.append(f'<rect class="in" style="animation-delay:{.1 + m * .02:.2f}s" x="{hx:.1f}" y="{y1 - ho - hf:.1f}" width="{bwid:.1f}" height="{hf:.1f}" rx="2" fill="{BAR2}"/>')
        if own[m] + fork[m] == peak:
            p.append(t(hx + bwid / 2, y1 - ho - hf - 8, str(peak), 12, MUTED, anchor="middle", mono=True))
            p.append(cells(hx + bwid / 2 - 13, y1 - ho - hf - 47, SITTING, 3, GHOST, delay=.9))
    for m in range(months):
        k = start.month - 1 + m
        yr, mo = start.year + k // 12, k % 12 + 1
        if mo == 1 or m == 0:
            p.append(t(x0 + m * bw, y1 + 20, f"{yr}", 12, DIM, mono=True))
    p.append(t(x1, y1 + 20, "now", 12, DIM, mono=True, anchor="end"))

    p.append(hline(IN + 1, W - IN - 1, 286))
    colw = (x1 - x0) / len(c.EPOCHS)
    for i, (num, name, since, lines) in enumerate(c.EPOCHS):
        ex = x0 + i * colw
        p.append(fade(.2 + i * .06, t(ex, 316, since.replace("-", "."), 12, PLUM, mono=True)
                      + t(ex, 340, name, 15, weight=600) + t(ex, 362, lines[0], 13, MUTED)))
    return svg(W, H, "".join(p), "Repositories created per month since the account began.")


# ------------------------------------------------------------------ stack

def stack(st):
    H = 320
    half = W / 2
    skip = {"Jupyter Notebook", "Procfile", "Dockerfile", "Makefile", "Shell", "Mako"}
    langs = sorted(((k, v) for k, v in st["langs"].items() if k not in skip), key=lambda kv: -kv[1])
    total = sum(v for _, v in langs) or 1
    top = [kv for kv in langs[:5] if kv[1] / total >= .005]
    other = total - sum(v for _, v in top)
    if other / total >= .005:
        top.append(("Other", other))

    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>', box(half, H), box(half, H, x=half + IN)]
    x0 = IN + PAD
    p.append(t(x0, IN + 42, "Languages", 15, weight=600))
    p.append(t(half - IN - PAD, IN + 42, "own repos, by size", 12.5, MUTED, anchor="end"))
    bx, bwid = x0, half - 2 * IN - 2 * PAD
    p.append(f'<clipPath id="bar"><rect x="{bx}" y="76" width="{bwid}" height="8" rx="4"/></clipPath><g clip-path="url(#bar)">')
    for i, (name, v) in enumerate(top):
        w = bwid * v / total
        p.append(f'<rect x="{bx:.1f}" y="76" width="{w:.1f}" height="8" fill="{RAMP[i]}"/>')
        bx += w
    p.append("</g>")
    for i, (name, v) in enumerate(top):
        y = 124 + i * 30
        p.append(f'<circle cx="{x0 + 5}" cy="{y - 5}" r="5" fill="{RAMP[i]}"/>')
        p.append(t(x0 + 20, y, name, 14))
        p.append(t(half - IN - PAD, y, f"{v / total * 100:.1f}%", 13, MUTED, mono=True, anchor="end"))

    rx0 = half + IN + PAD
    p.append(t(rx0, IN + 42, "Toolkit", 15, weight=600))
    for i, (k, v) in enumerate(c.LOCKFILE):
        y = 92 + i * 36
        assert 110 + width(v, 14) < half - 2 * PAD, f"toolkit line too long: {k}"
        p.append(t(rx0, y, k, 14, MUTED) + t(rx0 + 110, y, v, 14))
    return svg(W, H, "".join(p), "Languages by size across own repos, and the toolkit.")


# ------------------------------------------------------------------ footer

def footer():
    H = 120
    p = [f'<rect width="{W}" height="{H}" fill="{BG}"/>', hline(IN, W - IN, 2)]
    p.append(f'<circle cx="{IN + 6}" cy="{50}" r="6" fill="{GREEN}"/>')
    p.append(t(IN + 22, 57, c.STATUS, 19, weight=600))
    p.append(t(W - IN, 46, c.EMAIL, 14, MUTED, anchor="end"))
    p.append(t(W - IN, 68, c.LINKEDIN, 14, MUTED, anchor="end"))
    bits = "".join(f"{ord(ch):08b}" for ch in "meow")
    for i, b in enumerate(bits):
        p.append(f'<rect x="{IN + i * 7}" y="{H - 24}" width="5" height="5" fill="{GHOST if b == "1" else GHOST2}"/>')
    p.append(t(W - IN, H - 18, f"© {dt.date.today().year} {c.NAME}", 12, DIM, anchor="end"))
    return svg(W, H, "".join(p), "Open to ML and AI engineering roles.")


# ------------------------------------------------------------------ readme

CAT = r"""<!--
      /\_/\
     ( o.o )   you found the source. there are more of us in here.
      > ^ <
-->"""


def pic(f, alt, w="100%"):
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/{f}">'
            f'<source media="(prefers-color-scheme: light)" srcset="assets/light/{f}">'
            f'<img src="assets/dark/{f}" alt="{escape(alt)}" width="{w}"></picture>')


def readme():
    gh = f"https://github.com/{c.USER}"
    link = lambda repo, f, alt, w: f'<a href="{gh}/{repo}">{pic(f, alt, w)}</a>'
    block = lambda *parts: '<p align="center">' + "".join(parts) + "</p>"   # no spaces: boxes sit 6px apart
    flagship = [link(f["repo"], f"card-{i + 1}.svg", f'{f["title"]}: {f["desc"]}', "50%") for i, f in enumerate(c.FLAGSHIP)]
    tiles = [link(z[0], f"zoo-{i + 1:02d}.svg", f"{z[2]} on {z[3]}", "14.28%") for i, z in enumerate(c.ZOO)]
    more = [link(m[0], f"more-{i + 1:02d}.svg", f"{m[1]}: {m[3]}", "50%") for i, m in enumerate(c.MORE)]
    team = [link(m[0], f"team-{i + 1:02d}.svg", f"{m[1]}: {m[3]}", "50%") for i, m in enumerate(c.SQUADS)]
    out = [CAT, "",
           block(pic("hero.svg", f"{c.NAME}, ML and AI engineer")), "",
           block(pic("h-about.svg", "About"), pic("about.svg", "About")), "",
           '<a id="projects"></a>', block(pic("h-projects.svg", "Featured projects")), block(*flagship), "",
           '<a id="models"></a>', block(pic("h-models.svg", "Model zoo")), block(*tiles), "",
           block(pic("h-more.svg", "More builds")), block(*more), "",
           block(pic("h-team.svg", "Team builds")), block(*team), "",
           block(pic("h-timeline.svg", "Timeline"), pic("timeline.svg", "Repositories created per month")), "",
           block(pic("h-stack.svg", "Stack"), pic("stack.svg", "Languages and toolkit")), "",
           block(pic("footer.svg", c.STATUS)), "",
           f'<p align="center"><sub><a href="mailto:{c.EMAIL}">Email</a> · <a href="https://{c.LINKEDIN}">LinkedIn</a> · '
           f'<a href="#projects">Projects</a> · <a href="#models">Model zoo</a></sub></p>', "",
           "<!-- =^..^=  every image here is generated by scripts/build.py from live repo data -->", ""]
    return "\n".join(out)


# ------------------------------------------------------------------ main

def render(st):
    files = {
        "hero.svg": hero(st),
        "h-about.svg": header("01", "About"),
        "about.svg": about(),
        "h-projects.svg": header("02", "Featured projects", f"{len(c.FLAGSHIP)} projects"),
        "h-models.svg": header("03", "Model zoo", f"{len(c.ZOO)} models, each deployed as a Streamlit app"),
        "h-more.svg": header("04", "More builds", "agents, analytics and full-stack apps"),
        "h-team.svg": header("05", "Team builds", "hackathons and client work"),
        "h-timeline.svg": header("06", "Timeline", "live from the GitHub API"),
        "timeline.svg": timeline(st),
        "h-stack.svg": header("07", "Stack"),
        "stack.svg": stack(st),
        "footer.svg": footer(),
    }
    for i, f in enumerate(c.FLAGSHIP):
        files[f"card-{i + 1}.svg"] = card(f, i)
    for i, z in enumerate(c.ZOO):
        files[f"zoo-{i + 1:02d}.svg"] = zoo_tile(i + 1, *z)
    for i, o in enumerate(c.MORE):
        files[f"more-{i + 1:02d}.svg"] = row_card(*o, i)
    for i, o in enumerate(c.SQUADS):
        files[f"team-{i + 1:02d}.svg"] = row_card(*o, i)
    return files


def main():
    st = stats()
    for old in ASSETS.rglob("*.svg"):
        old.unlink()
    for mode in THEMES:
        globals().update(THEMES[mode])
        out = ASSETS / mode
        out.mkdir(parents=True, exist_ok=True)
        files = render(st)
        for name, body in files.items():
            (out / name).write_text(body, encoding="utf-8")
    (ROOT / "README.md").write_text(readme(), encoding="utf-8")
    print(f"wrote {len(files)} svgs x {len(THEMES)} modes + README.md · {st['public']} repos · {len(st['langs'])} languages")


if __name__ == "__main__":
    main()
