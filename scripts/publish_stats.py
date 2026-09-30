"""Publish my own rolling work stats to this profile repo. Runs daily on my Mac.

1. Runs devstats (a local tool that reads the org's repos with my gh login) and
   keeps only my row. Nobody else's numbers leave the machine.
2. Adds 12-month and 90-day merged/reviewed PR counts from GitHub search.
3. Writes assets/devstats.json + assets/devstats.svg, commits and pushes if changed.

The nightly Action reads assets/devstats.json for the 3D chart panel, so no token
with private-repo access has to live in GitHub.
"""
import json, os, re, subprocess, sys
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parent.parent
DEVSTATS = os.environ.get('DEVSTATS', str(Path.home() / 'bin/dev_stats.py'))
NAME = os.environ.get('DEVSTATS_NAME', 'Juan David Gomez')
LOGIN = os.environ.get('GH_LOGIN', 'Kayaba-Attribution')
DAYS = int(os.environ.get('DEVSTATS_DAYS', '90'))
ANSI = re.compile(r'\x1b\[[0-9;]*m')
COLS = ['add', 'del', 'src', 'migr', 'test', 'fix', 'doc', 'hunks', 'prs', 'reviews', 'help', 'prod', 'impact']


def my_row():
    run = subprocess.run([sys.executable, DEVSTATS, '--days', str(DAYS)],
                         capture_output=True, text=True, check=True)
    # devstats logs a failed gh call as a warning and carries on with partial counts;
    # a partial day must not overwrite a complete one
    if 'warning' in run.stderr.lower() or 'failed' in run.stderr.lower():
        raise SystemExit('devstats reported warnings, not publishing:\n' + run.stderr[-2000:])
    out = ANSI.sub('', run.stdout)
    repos = re.search(r'(\d+) active \S+ repos', run.stderr + out)
    for line in out.splitlines():
        m = re.match(rf'^\s*\d+\s+{re.escape(NAME)}\s+(.*)$', line)
        if not m:
            continue
        cells = m.group(1).split()
        if len(cells) != len(COLS):
            continue
        row = dict(zip(COLS, cells))
        num = lambda v: int(v.replace(',', '')) if v not in ('-', '') else 0
        # help/prod/impact are scaled against teammates, so they stay local
        keep = {k: num(row[k]) for k in COLS[:10]}
        keep['repos'] = int(repos.group(1)) if repos else None
        return keep
    raise SystemExit(f'no devstats row for {NAME!r}; not publishing')


def search_counts():
    to = date.today()
    res = {}
    for key, days in (('year', 365), ('quarter', 90)):
        win = f'{to - timedelta(days=days)}..{to}'
        for kind, q in (('merged', f'is:pr is:merged author:{LOGIN} merged:{win}'),
                        ('reviewed', f'is:pr is:merged reviewed-by:{LOGIN} -author:{LOGIN} merged:{win}')):
            n = subprocess.run(['gh', 'api', 'search/issues', '-X', 'GET', '-f', f'q={q}', '-f', 'per_page=1',
                                '--jq', '.total_count'], capture_output=True, text=True, check=True).stdout
            res.setdefault(key, {})[kind] = int(n)
    return res


def card(s):
    d = s['devstats']
    lines = d['add'] + d['del']
    per_day = lambda v: v / DAYS
    W, H = 820, 330
    mono = 'font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace'
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Rolling {DAYS}-day work stats: {d["add"]:,} lines added, {d["prs"]} PRs merged, {d["reviews"]} PRs reviewed">',
         f'<style>text{{{mono};white-space:pre}}.k{{fill:#8b949e;font-size:14px}}.n{{font-size:30px;font-weight:700}}'
         '</style>',
         f'<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>',
         f'<text x="24" y="34" style="font-size:14px"><tspan fill="#3fb950">juan@prod</tspan><tspan fill="#6e7681">:</tspan>'
         f'<tspan fill="#58a6ff">~</tspan><tspan fill="#6e7681">$ </tspan><tspan fill="#e6edf3">devstats --me --days {DAYS}</tspan></text>',
         f'<text x="{W-24}" y="34" text-anchor="end" class="k" style="font-size:12px">{d["repos"] or ""} repos · updated {s["updated"]}</text>']
    cells = [
        (f'+{d["add"]:,}', 'lines added', '#3fb950'),
        (f'−{d["del"]:,}', 'lines deleted', '#f85149'),
        (f'{d["hunks"]:,}', 'change hunks', '#d2a8ff'),
        (f'{d["prs"]:,}', 'PRs merged', '#58a6ff'),
        (f'{d["reviews"]:,}', 'PRs reviewed for teammates', '#d29922'),
        (f'{per_day(lines):,.0f}', 'lines changed / day', '#e6edf3'),
    ]
    for i, (n, k, c) in enumerate(cells):
        x, y = 24 + (i % 3) * 262, 88 + (i // 3) * 70
        # SMIL fade that starts at 0s: where animation is off, the base opacity (1) shows
        start, dur = 0.15 * i, 0.15 * i + 0.6
        fade = (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{start / dur:.3f};1" '
                f'dur="{dur:.2f}s" fill="freeze"/>')
        o.append(f'<g>{fade}<text x="{x}" y="{y}" class="n" fill="{c}">{escape(n)}</text>'
                 f'<text x="{x}" y="{y + 22}" class="k">{escape(k)}</text></g>')
    # where the lines went: the five shares sum to 100
    mix = [('source', d['src'], '#58a6ff'), ('migrations', d['migr'], '#d2a8ff'), ('tests', d['test'], '#3fb950'),
           ('fixtures', d['fix'], '#d29922'), ('docs', d['doc'], '#8b949e')]
    total = sum(p for _, p, _ in mix) or 1
    bx, by, bw, bh = 24, 250, W - 48, 16
    o.append(f'<text x="{bx}" y="{by - 12}" class="k">where the lines went</text>')
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="4" fill="#161b22"/>')
    x = bx
    for i, (label, p, c) in enumerate(mix):
        w = bw * p / total
        if w <= 0:
            continue
        o.append(f'<rect x="{x:.1f}" y="{by}" width="{w:.1f}" height="{bh}" fill="{c}">'
                 f'<animate attributeName="width" values="0;0;{w:.1f}" keyTimes="0;{(0.9 + 0.2 * i) / (1.7 + 0.2 * i):.3f};1" '
                 f'dur="{1.7 + 0.2 * i:.1f}s" fill="freeze"/></rect>')
        x += w
    lx = bx
    for label, p, c in mix:
        t = f'{label} {p}%'
        o.append(f'<rect x="{lx}" y="{by + 30}" width="10" height="10" rx="2" fill="{c}"/>'
                 f'<text x="{lx + 16}" y="{by + 40}" class="k" style="font-size:13px">{t}</text>')
        lx += 16 + len(t) * 8 + 26
    o.append('</svg>')
    return '\n'.join(o)


def main():
    stats = {'updated': date.today().isoformat(), 'days': DAYS, 'devstats': my_row(), 'search': search_counts()}
    (REPO / 'assets').mkdir(exist_ok=True)
    (REPO / 'assets/devstats.json').write_text(json.dumps(stats, indent=2) + '\n')
    (REPO / 'assets/devstats.svg').write_text(card(stats))
    print(json.dumps(stats))
    if '--no-push' in sys.argv:
        return
    git = lambda *a: subprocess.run(['git', '-C', str(REPO), *a], check=True, capture_output=True, text=True)
    git('add', 'assets/devstats.json', 'assets/devstats.svg')
    if subprocess.run(['git', '-C', str(REPO), 'diff', '--cached', '--quiet']).returncode == 0:
        print('no change')
        return
    git('commit', '-m', f'stats: {stats["updated"]}')
    git('pull', '--rebase', '--autostash', '-q')  # the nightly Action commits here too
    git('push', '-q')
    print('pushed')


if __name__ == '__main__':
    main()
