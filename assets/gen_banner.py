"""Generate animated light/dark header SVGs for the GitHub profile README."""
import base64, math, random, sys
from pathlib import Path

out_dir = Path(sys.argv[1])
avatar_b64 = base64.b64encode(Path(sys.argv[2]).read_bytes()).decode()

W, H = 1200, 340
THEMES = {
    "light": dict(bg="#faf7f0", primary="#232b40", ink="#4a5d8c", accent="#c8901f",
                  secondary="#626a7c", ring_bg="#fffdf8", chip="#4a5d8c1f", border="#e9e2d3"),
    "dark": dict(bg="#141926", primary="#ede7d9", ink="#93a7d6", accent="#e6b24a",
                 secondary="#9ba3b5", ring_bg="#1c2231", chip="#93a7d626", border="#283044"),
}
PHRASES = ["Autonomous Driving", "World Models", "Vision-Language-Action", "AI Agents"]
MONO = "'SF Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

# ---------- network ----------
rng = random.Random(7)
nodes = []
while len(nodes) < 30:
    x, y = rng.uniform(885, 1172), rng.uniform(30, 310)
    if all(math.hypot(x - a, y - b) > 42 for a, b in nodes):
        nodes.append((x, y))
for _ in range(10):  # faint scattered nodes elsewhere
    nodes.append((rng.uniform(330, 820), rng.uniform(16, 52)))
edges = [(i, j) for i in range(len(nodes)) for j in range(i + 1, len(nodes))
         if math.hypot(nodes[i][0] - nodes[j][0], nodes[i][1] - nodes[j][1]) < 105]
adj = {i: [] for i in range(len(nodes))}
for i, j in edges:
    adj[i].append(j); adj[j].append(i)

def walk(start, steps):
    path, cur = [start], start
    for _ in range(steps):
        nxt = [n for n in adj[cur] if n not in path]
        if not nxt:
            break
        cur = rng.choice(nxt); path.append(cur)
    return path

pulse_paths = []
starts = [i for i in range(30) if len(adj[i]) >= 2]
rng.shuffle(starts)
for s in starts:
    p = walk(s, 5)
    if len(p) >= 4:
        pulse_paths.append(p)
    if len(pulse_paths) == 6:
        break

# ---------- typewriter timeline ----------
CW = 15.6           # monospace advance at 26px
TX, TY = 486, 240   # phrase origin
TYPE, ERASE, HOLD, GAP = 0.085, 0.03, 1.8, 0.35
events = []  # (time, phrase, chars); loop starts with phrase 0 fully typed
t = HOLD
order = list(range(1, len(PHRASES))) + [0]
prev = 0
for pi in order:
    for c in range(len(PHRASES[prev]) - 1, -1, -1):
        t += ERASE; events.append((t, prev, c))
    t += GAP
    for c in range(1, len(PHRASES[pi]) + 1):
        t += TYPE; events.append((t, pi, c))
    if pi != 0:
        t += HOLD
    prev = pi
CYCLE = t

def discrete_anim(attr, series):
    """series: list of (time, value) starting at t=0."""
    kt = ";".join(f"{tt / CYCLE:.5f}" for tt, _ in series)
    vals = ";".join(str(v) for _, v in series)
    return (f'<animate attributeName="{attr}" dur="{CYCLE:.3f}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{kt}" values="{vals}"/>')

def phrase_width_series(pi):
    s = [(0.0, round(len(PHRASES[0]) * CW, 1) if pi == 0 else 0)]
    for tt, p, c in events:
        if p == pi:
            s.append((tt, round(c * CW, 1)))
    return s

caret_series = [(0.0, round(TX + len(PHRASES[0]) * CW + 2, 1))]
for tt, p, c in events:
    caret_series.append((tt, round(TX + c * CW + 2, 1)))


def build(theme):
    c = THEMES[theme]
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
             f'viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
             f'aria-label="Qingyuan Liu — Autonomous Driving, World Models, VLA, AI Agents">')
    o.append(f'''<style>
  .node {{ animation: tw 4s ease-in-out infinite; }}
  @keyframes tw {{ 0%,100% {{ opacity: .35; }} 50% {{ opacity: 1; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .caret {{ animation: blink 1s steps(1) infinite; }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>''')
    o.append(f'''<defs>
  <radialGradient id="g1" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(120 -20) scale(520 300)">
    <stop offset="0" stop-color="{c['ink']}" stop-opacity=".16"/><stop offset="1" stop-color="{c['ink']}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="g2" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(1150 40) scale(420 280)">
    <stop offset="0" stop-color="{c['accent']}" stop-opacity=".16"/><stop offset="1" stop-color="{c['accent']}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="name" gradientUnits="userSpaceOnUse" x1="350" y1="0" x2="1150" y2="0" spreadMethod="reflect">
    <stop offset="0" stop-color="{c['primary']}"/><stop offset=".45" stop-color="{c['primary']}"/>
    <stop offset=".75" stop-color="{c['ink']}"/><stop offset="1" stop-color="{c['accent']}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;-420 0;0 0" dur="10s" repeatCount="indefinite"/>
  </linearGradient>
  <clipPath id="av"><circle cx="200" cy="170" r="100"/></clipPath>''')
    for pi in range(len(PHRASES)):
        o.append(f'  <clipPath id="cp{pi}"><rect x="{TX}" y="{TY - 30}" height="42" width="{phrase_width_series(pi)[0][1]}">'
                 f'{discrete_anim("width", phrase_width_series(pi))}</rect></clipPath>')
    o.append('</defs>')

    o.append(f'<rect width="{W}" height="{H}" rx="22" fill="{c["bg"]}"/>')
    o.append(f'<rect width="{W}" height="{H}" rx="22" fill="url(#g1)"/><rect width="{W}" height="{H}" rx="22" fill="url(#g2)"/>')
    o.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{c["border"]}"/>')

    # network
    o.append(f'<g stroke="{c["ink"]}" stroke-width="1" fill="none">')
    for k, (i, j) in enumerate(edges):
        (x1, y1), (x2, y2) = nodes[i], nodes[j]
        d = math.hypot(x1 - x2, y1 - y2)
        op = (1 - d / 105) * (0.45 if i < 30 and j < 30 else 0.2)
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke-opacity="{op:.2f}" style="animation-delay:{(k % 17) * 0.08:.2f}s"/>')
    o.append('</g>')
    for k, (x, y) in enumerate(nodes):
        hot = k % 8 == 0 and k < 30
        r = 3.2 if hot else (2.2 if k < 30 else 1.6)
        fill = c["accent"] if hot else c["ink"]
        o.append(f'<circle class="node" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" '
                 f'style="animation-delay:{(k * 0.37) % 4:.2f}s"/>')
    for k, p in enumerate(pulse_paths):
        d = "M" + " L".join(f"{nodes[n][0]:.1f} {nodes[n][1]:.1f}" for n in p)
        dur = 2.2 + 0.6 * len(p)
        o.append(f'<circle r="3.4" fill="{c["accent"]}" opacity="0">'
                 f'<animateMotion dur="{dur:.1f}s" begin="{k * 0.9:.1f}s" repeatCount="indefinite" path="{d}" keyPoints="0;1;1" keyTimes="0;.7;1" calcMode="linear"/>'
                 f'<animate attributeName="opacity" dur="{dur:.1f}s" begin="{k * 0.9:.1f}s" repeatCount="indefinite" values="0;.9;.9;0;0" keyTimes="0;.08;.62;.7;1"/></circle>')

    # avatar
    o.append('<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -8;0 0" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')
    o.append(f'<circle cx="200" cy="170" r="114" fill="none" stroke="{c["accent"]}" stroke-width="2" stroke-dasharray="7 9" opacity=".7">'
             '<animateTransform attributeName="transform" type="rotate" from="0 200 170" to="360 200 170" dur="30s" repeatCount="indefinite"/></circle>')
    o.append(f'<circle cx="200" cy="170" r="104" fill="{c["ring_bg"]}"/>')
    o.append(f'<image href="data:image/jpeg;base64,{avatar_b64}" x="100" y="70" width="200" height="200" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>')
    o.append('</g>')

    # text
    o.append(f'<g class="fade" style="animation-delay:.1s"><text x="352" y="106" font-family="{SANS}" font-size="22" letter-spacing="1.5" fill="{c["secondary"]}">Hi, I\'m</text></g>')
    o.append(f'<g class="fade" style="animation-delay:.25s"><text x="348" y="176" font-family="{SANS}" font-size="66" font-weight="700" fill="url(#name)">Qingyuan Liu</text></g>')
    o.append(f'<g class="fade" style="animation-delay:.45s">')
    o.append(f'<rect x="352" y="{TY - 24}" width="118" height="32" rx="8" fill="{c["chip"]}"/>')
    o.append(f'<text x="411" y="{TY - 2}" text-anchor="middle" font-family="{MONO}" font-size="16" fill="{c["secondary"]}">Exploring</text>')
    for pi, ph in enumerate(PHRASES):
        o.append(f'<text x="{TX}" y="{TY}" font-family="{MONO}" font-size="26" font-weight="600" fill="{c["ink"]}" '
                 f'textLength="{len(ph) * CW:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#cp{pi})">{ph}</text>')
    o.append(f'<rect class="caret" y="{TY - 24}" width="3" height="30" rx="1.5" fill="{c["accent"]}" x="{caret_series[0][1]}">'
             f'{discrete_anim("x", caret_series)}</rect>')
    o.append('</g>')
    o.append(f'<g class="fade" style="animation-delay:.65s"><text x="352" y="296" font-family="{SANS}" font-size="18" fill="{c["secondary"]}">'
             f'Master\'s @ USTC<tspan fill="{c["accent"]}">  ·  </tspan>Bachelor\'s @ SYSU<tspan fill="{c["accent"]}">  ·  </tspan>'
             f'<tspan fill="{c["ink"]}">tsing-yuan.github.io</tspan></text></g>')
    o.append('</svg>')
    return "\n".join(o)


for name in THEMES:
    (out_dir / f"header-{name}.svg").write_text(build(name), encoding="utf-8")
print("cycle", round(CYCLE, 2), "edges", len(edges), "pulses", len(pulse_paths))
