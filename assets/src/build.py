#!/usr/bin/env python3
"""Builds every animated SVG in ../ for the profile README.

Run:  python3 assets/src/build.py

All text is drawn as pixel art from the public-domain X11 "6x13B" bitmap
font (font-6x13B.json), so it looks identical on every device - SVGs shown
through <img> can't load web fonts.
"""
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
FONT = json.loads((HERE / "font-6x13B.json").read_text())

# Palette built around #ffb8bf.
PINK = "#ffb8bf"
PINK_LIGHT = "#ffe4e7"
PINK_SOFT = "#ffd1d6"
PINK_DEEP = "#ff8fa3"
ROSE = "#e05a7a"
SOUL = "#ff5c7a"
PLUM = "#5a2a3a"
CREAM = "#fff7f8"
NIGHT = "#0d0a0b"

ADV = 7  # glyph advance in font pixels (6px glyph + 1px gap)
GLYPH_H = 12


def f(n):
    """Compact number formatting for SVG attributes."""
    return f"{n:.2f}".rstrip("0").rstrip(".")


def bitmap_path(rows, x, y, scale):
    """Turn a list of '#'/'.' strings into one path of horizontal runs."""
    d = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            if row[c] != "#":
                c += 1
                continue
            start = c
            while c < len(row) and row[c] == "#":
                c += 1
            w = (c - start) * scale
            d.append(f"M{f(x + start * scale)} {f(y + r * scale)}h{f(w)}v{f(scale)}h-{f(w)}z")
    return "".join(d)


def text_path(s, x, y, scale):
    return "".join(bitmap_path(FONT.get(ch, FONT["?"]), x + i * ADV * scale, y, scale) for i, ch in enumerate(s))


def text_width(s, scale):
    return (len(s) * ADV - 1) * scale


HEART = [
    ".###...###.",
    "#####.#####",
    "###########",
    "###########",
    ".#########.",
    "..#######..",
    "...#####...",
    "....###....",
    ".....#.....",
]
HEART_SHINE = ["", ".#", "#"]  # two white pixels in the top-left lobe
SMALL_HEART = [
    ".##.##.",
    "#######",
    "#######",
    ".#####.",
    "..###..",
    "...#...",
]


def heart(x, y, scale, fill, shine=True, cls="", extra=""):
    attrs = f' class="{cls}"' if cls else ""
    out = f'<g{attrs}{extra}><path fill="{fill}" d="{bitmap_path(HEART, x, y, scale)}"/>'
    if shine:
        out += f'<path fill="#fff" opacity=".85" d="{bitmap_path(HEART_SHINE, x + scale, y + scale, scale)}"/>'
    return out + "</g>"


def sparkle(cx, cy, r):
    """Four-point star."""
    k = r * 0.28
    return (
        f"M{f(cx)} {f(cy - r)}Q{f(cx + k)} {f(cy - k)} {f(cx + r)} {f(cy)}"
        f"Q{f(cx + k)} {f(cy + k)} {f(cx)} {f(cy + r)}Q{f(cx - k)} {f(cy + k)} {f(cx - r)} {f(cy)}"
        f"Q{f(cx - k)} {f(cy - k)} {f(cx)} {f(cy - r)}z"
    )


def discrete_animate(attr, events, total, initial=0):
    """SMIL <animate> stepping `attr` through (time, value) events over a loop of `total` seconds."""
    events = sorted(events)
    if not events or events[0][0] > 0:
        events = [(0, initial)] + events
    keyed = {}
    for t, v in events:
        keyed[round(t / total, 4)] = v  # later events at the same instant win
    times = sorted(keyed)
    return (
        f'<animate attributeName="{attr}" dur="{f(total)}s" repeatCount="indefinite" calcMode="discrete" '
        f'keyTimes="{";".join(f(t) for t in times)}" values="{";".join(f(keyed[t]) for t in times)}"/>'
    )


def typing_times(s, start, step=0.045):
    """Times at which each character appears; pauses after punctuation like Undertale."""
    times, t = [], start
    for ch in s:
        times.append(t)
        t += step
        if ch in ",.!?":
            t += step * 5
    return times, t


REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def svg(w, h, body, style="", title=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{title}">'
        f"<title>{title}</title><style>{style}{REDUCED_MOTION}</style>{body}</svg>\n"
    )


def write(name, content):
    (OUT / name).write_text(content)
    print(f"  {name:<22} {len(content.encode()) / 1024:6.1f} KB")


def build_header():
    W, H = 1000, 220
    rnd = random.Random(1225)
    css = """
.blob{animation:drift 16s ease-in-out infinite alternate}
@keyframes drift{to{transform:translate(var(--bx),var(--by))}}
.rise{animation:rise var(--d) linear infinite;animation-delay:var(--dl);opacity:0}
@keyframes rise{0%{transform:translate(0,0) rotate(0);opacity:0}10%{opacity:var(--o)}
80%{opacity:var(--o)}100%{transform:translate(var(--dx),-400px) rotate(var(--r));opacity:0}}
.tw{transform-box:fill-box;transform-origin:center;animation:tw var(--d) ease-in-out infinite;animation-delay:var(--dl)}
@keyframes tw{0%,100%{transform:scale(.2) rotate(0);opacity:0}50%{transform:scale(1) rotate(90deg);opacity:1}}
.wave{animation:wave 2.4s ease-in-out infinite}
@keyframes wave{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-10px)}}
.beat{transform-box:fill-box;transform-origin:center;animation:beat 1.2s ease-in-out infinite}
@keyframes beat{0%,40%,100%{transform:scale(1)}12%{transform:scale(1.14)}26%{transform:scale(1.04)}}
.dash{animation:dash 30s linear infinite}
@keyframes dash{to{stroke-dashoffset:-400}}
"""
    b = [
        "<defs>"
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PINK_LIGHT}"/>'
        f'<stop offset=".55" stop-color="{PINK}"/><stop offset="1" stop-color="{PINK_DEEP}"/></linearGradient>'
        '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>'
        '<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">'
        '<rect x="11" y="11" width="2" height="2" fill="#fff" opacity=".35"/></pattern>'
        f'<clipPath id="card"><rect width="{W}" height="{H}" rx="28"/></clipPath>'
        "</defs>",
        '<g clip-path="url(#card)">',
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
    ]
    for cx, cy, r, col, bx, by in [
        (160, 60, 150, "#fff", 80, 40),
        (860, 260, 170, CREAM, -90, -30),
        (620, 40, 110, PINK_SOFT, -60, 50),
        (300, 300, 120, ROSE, 70, -40),
    ]:
        op = ".35" if col == ROSE else ".7"
        b.append(
            f'<circle class="blob" style="--bx:{bx}px;--by:{by}px" cx="{cx}" cy="{cy}" r="{r}" '
            f'fill="{col}" opacity="{op}" filter="url(#blur)"/>'
        )
    b.append(f'<rect width="{W}" height="{H}" fill="url(#dots)"/>')

    for _ in range(18):
        x = rnd.uniform(20, W - 40)
        s = rnd.choice([2, 3, 3, 4, 5])
        col = rnd.choice(["#fff", "#fff", CREAM, ROSE, PINK_DEEP])
        dur = rnd.uniform(9, 16)
        style = (
            f"--d:{f(dur)}s;--dl:-{f(rnd.uniform(0, dur))}s;--dx:{rnd.randint(-60, 60)}px;"
            f"--r:{rnd.randint(-40, 40)}deg;--o:{f(rnd.uniform(.45, .9))}"
        )
        b.append(f'<g class="rise" style="{style}"><path fill="{col}" d="{bitmap_path(SMALL_HEART, x, H + 10, s)}"/></g>')

    for x, y, r in [(80, 70, 14), (930, 60, 18), (870, 140, 9), (130, 230, 10), (700, 270, 12),
                    (230, 120, 7), (780, 90, 8), (40, 160, 8), (960, 250, 10), (520, 40, 9)]:
        style = f"--d:{f(rnd.uniform(2.2, 4))}s;--dl:-{f(rnd.uniform(0, 4))}s"
        b.append(f'<path class="tw" style="{style}" fill="#fff" d="{sparkle(x, y, r)}"/>')

    b.append(
        f'<rect class="dash" x="14" y="14" width="{W - 28}" height="{H - 28}" rx="18" fill="none" '
        'stroke="#fff" stroke-width="3" stroke-dasharray="14 10" stroke-linecap="round" opacity=".75"/>'
    )

    title, scale = "frisky", 10
    tw = text_width(title, scale)
    hs = 9
    heart_w = len(HEART[0]) * hs
    gap = 26
    x0 = (W - (tw + gap + heart_w)) / 2
    ty = 52
    for i, ch in enumerate(title):
        cx = x0 + i * ADV * scale
        shadow = bitmap_path(FONT[ch], cx + 6, ty + 6, scale)
        main = bitmap_path(FONT[ch], cx, ty, scale)
        b.append(
            f'<g class="wave" style="animation-delay:{f(i * 0.12)}s">'
            f'<path fill="{ROSE}" d="{shadow}"/><path fill="#fff" d="{main}"/></g>'
        )
    hx = x0 + tw + gap
    hy = ty + 2 * scale
    b.append(
        f'<g class="beat"><path fill="{PLUM}" d="{bitmap_path(HEART, hx + 6, hy + 6, hs)}"/>'
        + heart(hx, hy, hs, SOUL)
        + "</g>"
    )

    b.append("</g>")
    write("header.svg", svg(W, H, "".join(b), css, "frisky"))


def wrap(text, width):
    """Undertale wrapping: '* ' bullet, continuation lines indented two spaces."""
    words, lines, cur = text[2:].split(" "), [], "* "
    for w in words:
        cand = cur + ("" if cur.strip() in ("*", "") else " ") + w
        if len(cand) > width and cur.strip() not in ("*", ""):
            lines.append(cur)
            cur = "  " + w
        else:
            cur = cand
    lines.append(cur)
    return lines


def build_dialogue():
    W = 1000
    scale, pad, line_h = 3, 40, 50
    cols = (W - 2 * pad) // (ADV * scale)
    pages = [
        ["* Hi! I'm Frsxk... but you can call me frisky<3"],
        ["* I make web apps, Discord bots & games.",
         "* Mostly TypeScript, plus Python, Dart & Rust."],
        ["* I'm in love with Frisk.", "* Currently learning how to be Frisk's."],
        ["* Looking to collaborate on Frisk's heart.", "* (It's a long-term project.)"],
        ["* Pronouns: she/them... but any pronouns are okay!", "* Discord: @frxskie - send a friend request!"],
        ["* Really nice to meet you!", "* (Reading this profile fills you with DETERMINATION.)"],
    ]
    css = """
.blink{animation:blink 1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.bob{animation:bob 1.6s ease-in-out infinite}
@keyframes bob{50%{transform:translateY(-4px)}}
"""
    wrapped = [[ln for para in page for ln in wrap(para, cols)] for page in pages]
    H = 2 * pad + (max(map(len, wrapped)) - 1) * line_h + GLYPH_H * scale + 10
    body, t = [], 0.5
    schedule = []
    for lines in wrapped:
        line_events = []
        for li, ln in enumerate(lines):
            times, t = typing_times(ln, t, 0.04)
            line_events.append((ln, times))
            t += 0.25
        hold_end = t + 2.8
        schedule.append((line_events, hold_end))
        t = hold_end + 0.35
    total = t

    body.append(
        f'<rect width="{W}" height="{H}" rx="10" fill="#000"/>'
        f'<rect x="10" y="10" width="{W - 20}" height="{H - 20}" fill="none" stroke="#fff" stroke-width="6"/>'
    )
    cw = ADV * scale
    for pi, (line_events, hold_end) in enumerate(schedule):
        for li, (ln, times) in enumerate(line_events):
            x, y = pad, pad + li * line_h
            ev = [(tt, (i + 1) * cw) for i, tt in enumerate(times)] + [(hold_end, 0)]
            cid = f"d{pi}_{li}"
            body.append(
                f'<clipPath id="{cid}"><rect x="{x}" y="{y - 4}" height="{GLYPH_H * scale + 8}" width="0">'
                f"{discrete_animate('width', ev, total)}</rect></clipPath>"
                f'<path clip-path="url(#{cid})" fill="#fff" d="{text_path(ln, x, y, scale)}"/>'
            )
    body.append(
        f'<g class="bob">{heart(W - 66, H - 56, 3, PINK)}</g>'
    )
    write("dialogue.svg", svg(W, H, "".join(body), css, "Undertale-style dialogue box introducing frisky"))


def build_hud():
    W, H = 1000, 64
    s = 3
    y = (H - GLYPH_H * s) / 2 + 2
    max_hp, min_hp, bar_width = 20, 14, 174
    timeline = [(0, max_hp), (40, max_hp)]
    for step in range(1, max_hp - min_hp + 1):
        timeline.append((40 + 8 * step / (max_hp - min_hp), max_hp - step))
    timeline.append((52, min_hp))
    for step in range(1, max_hp - min_hp + 1):
        timeline.append((52 + 18 * step / (max_hp - min_hp), min_hp + step))
    timeline.append((100, max_hp))
    css = ".hp{animation:hp 7s steps(1,end) infinite}\n@keyframes hp{"
    css += "".join(f"{f(t)}%{{width:{f(bar_width * hp / max_hp)}px}}" for t, hp in timeline)
    css += "}\n"
    for value in range(min_hp, max_hp + 1):
        css += f".hp-{value}{{opacity:{int(value == max_hp)};animation:hp-{value} 7s steps(1,end) infinite}}\n"
        css += f"@keyframes hp-{value}{{"
        css += "".join(f"{f(t)}%{{opacity:{int(hp == value)}}}" for t, hp in timeline)
        css += "}\n"
    css += """
.heal{animation:heal 7s steps(1) infinite;opacity:0}
@keyframes heal{55%{opacity:1}75%{opacity:0}}
"""
    b = [f'<rect width="{W}" height="{H}" rx="10" fill="#000"/>']
    b.append(f'<path fill="#fff" d="{text_path("frisky", 30, y, s)}"/>')
    b.append(f'<path fill="#fff" d="{text_path("LV 1", 230, y, s)}"/>')
    b.append(f'<path fill="#fff" d="{text_path("HP", 420, y, s)}"/>')
    bar_x, bar_y = 480, y + 2
    b.append(f'<rect x="{bar_x}" y="{f(bar_y)}" width="{bar_width}" height="30" fill="{ROSE}"/>')
    b.append(f'<rect class="hp" x="{bar_x}" y="{f(bar_y)}" width="{bar_width}" height="30" fill="{PINK}"/>')
    for value in range(min_hp, max_hp + 1):
        b.append(f'<path class="hp-{value}" fill="#fff" d="{text_path(f"{value} / {max_hp}", 690, y, s)}"/>')
    b.append(f'<g class="heal"><path fill="{PINK}" d="{text_path("+love", 870, y, s)}"/></g>')
    write("hud.svg", svg(W, H, "".join(b), css, "frisky  LV 1  HP drops from 20/20 to 14/20, then +love heals to full"))


ICONS = {
    "FIGHT": [
        "........##",
        ".......###",
        "......###.",
        ".....###..",
        "#...###...",
        ".#.###....",
        "..###.....",
        "..##......",
        ".#..#.....",
        "#.........",
    ],
    "ACT": [
        ".########.",
        "##########",
        "##.##.##.#",
        "##########",
        ".########.",
        "..##......",
        "..#.......",
        ".#........",
    ],
    "ITEM": [
        "...####...",
        "..#....#..",
        ".########.",
        "##########",
        "###.##.###",
        "##########",
        "##########",
        ".########.",
    ],
    "MERCY": [
        "##......##",
        ".##....##.",
        "..##..##..",
        "...####...",
        "...####...",
        "..##..##..",
        ".##....##.",
        "##......##",
    ],
}


def build_buttons():
    W, H = 240, 72
    s = 3
    names = list(ICONS)
    for k, name in enumerate(names):
        a, z = k * 25, (k + 1) * 25
        # Each button owns a quarter of the loop, moving the soul cursor across all four images.
        sel_frames = "0%{opacity:0}" if a > 0 else ""
        sel_frames += f"{a}%{{opacity:1}}{z}%{{opacity:0}}100%{{opacity:0}}"
        css = f"""
.sel{{animation:sel 6s steps(1,end) infinite;opacity:0}}
@keyframes sel{{{sel_frames}}}
.beat{{transform-box:fill-box;transform-origin:center;animation:beat 1.2s ease-in-out infinite}}
@keyframes beat{{0%,40%,100%{{transform:scale(1)}}12%{{transform:scale(1.18)}}26%{{transform:scale(1.05)}}}}
"""
        icon = ICONS[name]
        iw, ih = len(icon[0]) * s, len(icon) * s
        ix, iy = 22, (H - ih) / 2
        tw = text_width(name, s)
        tx = ix + iw + (W - (ix + iw) - tw) / 2 - 6
        ty = (H - GLYPH_H * s) / 2 + 3

        def layer(color, sel):
            out = (
                f'<rect x="3" y="3" width="{W - 6}" height="{H - 6}" rx="4" fill="#000" stroke="{color}" stroke-width="5"/>'
                f'<path fill="{color}" d="{text_path(name, tx, ty, s)}"/>'
            )
            if sel:
                hx, hy = ix - 1, (H - 9 * s) / 2
                out += f'<g class="beat">{heart(hx, hy, s, SOUL)}</g>'
            else:
                out += f'<path fill="{color}" d="{bitmap_path(icon, ix, iy, s)}"/>'
            return out

        body = layer(PINK_DEEP, False) + f'<g class="sel">{layer(PINK_LIGHT, True)}</g>'
        write(f"btn-{name.lower()}.svg", svg(W, H, body, css, name))


def build_titles():
    W, H = 1000, 84
    s = 3
    css = """
.bob{animation:bob 1.8s ease-in-out infinite}
@keyframes bob{50%{transform:translateY(-5px)}}
.tw{transform-box:fill-box;transform-origin:center;animation:tw 2.6s ease-in-out infinite}
@keyframes tw{0%,100%{transform:scale(.3);opacity:.2}50%{transform:scale(1) rotate(90deg);opacity:1}}
.flow{animation:flow 1.2s linear infinite}
@keyframes flow{to{stroke-dashoffset:-16}}
"""
    for slug, label in [
        ("about", "* about me"),
        ("inventory", "* my inventory"),
        ("check", "* check"),
        ("snake", "* the snek ate my commits"),
    ]:
        tw = text_width(label, s)
        hs = 2
        heart_w = len(HEART[0]) * hs
        pill_w = tw + 2 * (28 + heart_w + 16)
        px = (W - pill_w) / 2
        py, ph = 14, 56
        cy = py + ph / 2
        b = [
            f'<path class="flow" d="M10 {cy}H{f(px - 14)}M{f(px + pill_w + 14)} {cy}H{W - 10}" stroke="{PINK}" '
            'stroke-width="4" stroke-dasharray="2 14" stroke-linecap="round"/>',
            f'<rect x="{f(px)}" y="{py + 5}" width="{f(pill_w)}" height="{ph}" rx="{ph / 2}" fill="{ROSE}"/>',
            f'<rect x="{f(px)}" y="{py}" width="{f(pill_w)}" height="{ph}" rx="{ph / 2}" fill="{PINK}"/>',
            f'<path fill="{PLUM}" d="{text_path(label, (W - tw) / 2, cy - GLYPH_H * s / 2 + 2, s)}"/>',
        ]
        for i, hx in enumerate([px + 28, px + pill_w - 28 - heart_w]):
            b.append(
                f'<g class="bob" style="animation-delay:{i * 0.9}s">'
                f"{heart(hx, cy - 9 * hs / 2, hs, SOUL)}</g>"
            )
        for i, (x, y, r) in enumerate([(px - 4, py + 2, 9), (px + pill_w + 2, py + ph - 2, 8)]):
            b.append(f'<path class="tw" style="animation-delay:{i * 1.3}s" fill="{PINK_DEEP}" d="{sparkle(x, y, r)}"/>')
        write(f"title-{slug}.svg", svg(W, H, "".join(b), css, label[2:]))


def wave_path(width, amp, period, y, height):
    pts = [f"M0 {height}"]
    for x in range(0, width + 1, 10):
        pts.append(f"L{x} {f(y + amp * math.sin(2 * math.pi * x / period))}")
    pts.append(f"L{width} {height}Z")
    return "".join(pts)


def build_footer():
    W, H = 1000, 230
    css = """
.w1{animation:slide 9s linear infinite}
.w2{animation:slide 14s linear infinite reverse}
.w3{animation:slide 20s linear infinite}
@keyframes slide{from{transform:translateX(0)}to{transform:translateX(-500px)}}
.star{transform-box:fill-box;transform-origin:center;animation:star 2s ease-in-out infinite}
@keyframes star{0%,100%{transform:scale(.85) rotate(0)}50%{transform:scale(1.1) rotate(8deg)}}
.glow{transform-box:fill-box;transform-origin:center;animation:glow 2s ease-in-out infinite}
@keyframes glow{0%,100%{opacity:.35;transform:scale(.8)}50%{opacity:.8;transform:scale(1.2)}}
.rise{animation:rise 5s ease-in infinite;opacity:0}
@keyframes rise{0%{transform:translateY(0);opacity:0}20%{opacity:1}100%{transform:translateY(-120px);opacity:0}}
"""
    b = []
    # Undertale save-point star.
    star = [
        "....##....",
        "....##....",
        "...####...",
        "##########",
        ".########.",
        "..######..",
        "..######..",
        ".###..###.",
        ".##....##.",
    ]
    s = 4
    sx, sy = (W - 10 * s) / 2, 18
    b.append('<defs><radialGradient id="halo"><stop offset="0" stop-color="#fff" stop-opacity=".9"/>'
             f'<stop offset=".4" stop-color="{PINK}" stop-opacity=".6"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/>'
             '</radialGradient></defs>')
    b.append(f'<circle class="glow" cx="{W / 2}" cy="{sy + 18}" r="40" fill="url(#halo)"/>')
    b.append(f'<g class="star"><path fill="{PINK_DEEP}" d="{bitmap_path(star, sx, sy, s)}"/>'
             f'<path fill="#fff" opacity=".8" d="{bitmap_path(["", "", "", "....#"], sx, sy, s)}"/></g>')
    msg = "* thanks for stopping by! stay determined <3"
    ts = 3
    b.append(f'<path fill="{ROSE}" d="{text_path(msg, (W - text_width(msg, ts)) / 2, 76, ts)}"/>')
    for i, x in enumerate([120, 260, 410, 590, 740, 880]):
        b.append(
            f'<g class="rise" style="animation-delay:{i * 0.8}s">'
            f'<path fill="{PINK if i % 2 else PINK_DEEP}" d="{bitmap_path(SMALL_HEART, x, 200, 3)}"/></g>'
        )
    for cls, amp, period, y, col, op in [
        ("w3", 10, 500, 150, PINK_LIGHT, ".9"),
        ("w2", 12, 250, 165, PINK, ".85"),
        ("w1", 9, 500, 185, PINK_DEEP, ".9"),
    ]:
        b.append(f'<path class="{cls}" fill="{col}" opacity="{op}" d="{wave_path(W + 500, amp, period, y, H)}"/>')
    write("footer.svg", svg(W, H, "".join(b), css, "thanks for stopping by! stay determined"))


if __name__ == "__main__":
    print("building svgs ->", OUT)
    build_header()
    build_dialogue()
    build_hud()
    build_buttons()
    build_titles()
    build_footer()
