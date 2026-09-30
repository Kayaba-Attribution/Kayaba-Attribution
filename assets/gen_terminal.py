import sys, pyfiglet
from xml.sax.saxutils import escape
STATIC = '--static' in sys.argv
out = sys.argv[1]

banner = [l for l in pyfiglet.figlet_format('KAYABA', font='ansi_shadow').splitlines() if l.strip()]
# (kind, text, type_seconds, pause_after)
script = [
    ('cmd', 'signals run --env prod --date 2026-09-29', 1.6, 0.4),
    ('out', '  22,654 companies searched · 1,304,965 results', 0, 0.25),
    ('out', '  → prefilter    952,178', 0, 0.15),
    ('out', '  → classified    20,017', 0, 0.15),
    ('out', '  → validated     16,579', 0, 0.15),
    ('ok',  '  ✓ emitted       14,255 signals', 0, 0.9),
    ('cmd', 'jev ask "does acme.io belong to Acme Corp?"', 1.7, 0.5),
    ('warn','  → insufficient_evidence   refusing, not guessing', 0, 0.9),
    ('cmd', 'whoami', 0.5, 0.3),
    ('out', '  idea → enterprise product. owns it end to end.', 0, 3.5),
]
CW, FS, LH = 8.43, 14, 21
X0, BANNER_Y = 24, 62
TERM_Y = BANNER_Y + len(banner) * 16 + 30
W = 820
H = TERM_Y + (len(script) + 1) * LH + 16
PROMPT = 'juan@prod:~$ '

# timeline
t = 0.6; events = []
for kind, text, typ, pause in script:
    start = t; t += typ if kind == 'cmd' else 0.05
    events.append((kind, text, start, t)); t += pause
T = t + 0.6  # loop length

def kt(x): return f'{min(max(x / T, 0), 1):.4f}'

colors = {'cmd': '#e6edf3', 'out': '#8b949e', 'ok': '#3fb950', 'warn': '#d29922'}
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal: signals pipeline funnel and a Jev decision">',
'<defs>',
'<linearGradient id="g" x1="0" x2="1" spreadMethod="reflect"><stop offset="0" stop-color="#3fb950"/><stop offset="0.5" stop-color="#58a6ff"/><stop offset="1" stop-color="#bc8cff"/>'
 + ('' if STATIC else '<animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0;-1 0" dur="8s" repeatCount="indefinite"/>') + '</linearGradient>',
'</defs>',
'<style>text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;font-size:14px;white-space:pre}.b{font-size:14px;fill:url(#g)}</style>',
f'<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>',
'<circle cx="22" cy="20" r="6" fill="#ff5f56"/><circle cx="42" cy="20" r="6" fill="#ffbd2e"/><circle cx="62" cy="20" r="6" fill="#27c93f"/>',
f'<text x="{W/2}" y="25" text-anchor="middle" fill="#6e7681" style="font-size:12px">kayaba-attribution — zsh</text>',
]
for i, line in enumerate(banner):
    y = BANNER_Y + i * 16
    svg.append(f'<text class="b" x="{X0}" y="{y}" textLength="{len(line)*CW:.1f}" lengthAdjust="spacingAndGlyphs">{escape(line)}</text>')

for i, (kind, text, start, end) in enumerate(events):
    y = TERM_Y + i * LH
    full = (PROMPT + text) if kind == 'cmd' else text
    w = len(full) * CW + 12
    cid = f'c{i}'
    if kind == 'cmd':
        pw = len(PROMPT) * CW
        vals = f'0;0;{pw:.1f};{w:.1f};{w:.1f}'
    else:
        vals = f'0;0;{w:.1f};{w:.1f}'
    keys = f'0;{kt(start)};{kt(start + 0.01)};{kt(end)};1' if kind == 'cmd' else f'0;{kt(start)};{kt(end)};1'
    anim = '' if STATIC else f'<animate attributeName="width" dur="{T:.2f}s" repeatCount="indefinite" values="{vals}" keyTimes="{keys}" calcMode="linear"/>'
    init = w if STATIC else 0
    svg.append(f'<clipPath id="{cid}"><rect x="{X0-2}" y="{y-16}" height="{LH}" width="{init}">{anim}</rect></clipPath>')
    g = [f'<g clip-path="url(#{cid})">']
    if kind == 'cmd':
        g.append(f'<text x="{X0}" y="{y}"><tspan fill="#3fb950">juan@prod</tspan><tspan fill="#6e7681">:</tspan><tspan fill="#58a6ff">~</tspan><tspan fill="#6e7681">$ </tspan><tspan fill="{colors[kind]}">{escape(text)}</tspan></text>')
    else:
        g.append(f'<text x="{X0}" y="{y}" fill="{colors[kind]}">{escape(text)}</text>')
    g.append('</g>')
    svg += g

# blinking cursor on the last prompt line
cy = TERM_Y + len(events) * LH
end_t = events[-1][3] + 0.3
show = '' if STATIC else f'<animate attributeName="opacity" dur="{T:.2f}s" repeatCount="indefinite" values="0;1;1" keyTimes="0;{kt(end_t)};1" calcMode="discrete"/>'
svg.append(f'<g opacity="{1 if STATIC else 0}">{show}')
svg.append(f'<text x="{X0}" y="{cy}"><tspan fill="#3fb950">juan@prod</tspan><tspan fill="#6e7681">:</tspan><tspan fill="#58a6ff">~</tspan><tspan fill="#6e7681">$ </tspan></text>')
blink = '' if STATIC else '<animate attributeName="opacity" values="1;0;1" dur="1s" calcMode="discrete" repeatCount="indefinite"/>'
svg.append(f'<rect x="{X0 + len(PROMPT)*CW:.1f}" y="{cy-13}" width="8" height="16" fill="#e6edf3">{blink}</rect>')
svg.append('</g>')
svg.append('</svg>')
open(out, 'w').write('\n'.join(svg))
print(out, f'loop={T:.1f}s', f'{W}x{H}')
