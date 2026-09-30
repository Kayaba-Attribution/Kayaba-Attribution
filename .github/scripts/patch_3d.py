"""Replace the radar chart in the 3D contribution SVGs with real stats.

The radar only sees public activity, so private-repo reviews and PRs show as zero.
With STATS_TOKEN (a token that can read the private repos) we draw merged PRs and
reviews of merged PRs from GitHub search, for 12 months and 90 days. Without it we only remove the radar.
"""
import glob, json, os, re, urllib.request
from datetime import date, timedelta
import xml.etree.ElementTree as ET

SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)
USER = os.environ.get('GITHUB_REPOSITORY_OWNER', 'Kayaba-Attribution')
TRANSLATE = re.compile(r'^translate\(([\d.]+), ([\d.]+)\)$')


def stats(token):
    """Merged PRs authored, and merged PRs reviewed for someone else, per window."""
    to = date.today()
    parts, variables = [], {}
    for key, days in (('y', 365), ('q', 90)):
        win = f'{to - timedelta(days=days)}..{to}'
        variables[f'{key}m'] = f'is:pr is:merged author:{USER} merged:{win}'
        variables[f'{key}r'] = f'is:pr is:merged reviewed-by:{USER} -author:{USER} merged:{win}'
        parts += [f'{key}m:search(query:${key}m,type:ISSUE,first:1){{issueCount}}',
                  f'{key}r:search(query:${key}r,type:ISSUE,first:1){{issueCount}}']
    q = 'query(' + ','.join(f'${k}:String!' for k in variables) + '){' + ' '.join(parts) + '}'
    req = urllib.request.Request('https://api.github.com/graphql',
                                 json.dumps({'query': q, 'variables': variables}).encode(),
                                 {'Authorization': f'bearer {token}', 'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(req))['data']
    return [('last 12 months', d['ym']['issueCount'], d['yr']['issueCount']),
            ('last 90 days', d['qm']['issueCount'], d['qr']['issueCount'])]


def patch(path, rows):
    tree = ET.parse(path)
    root = tree.getroot()
    # the radar is the translated group that holds the pentagon axes
    radar = next((g for g in root.iter(f'{{{SVG}}}g') if TRANSLATE.match(g.get('transform', ''))
                  and any(c.get('class') == 'axis' for c in g.iter(f'{{{SVG}}}g'))), None)
    if radar is None:
        return False
    x, y = (float(v) for v in TRANSLATE.match(radar.get('transform')).groups())
    parent = next(p for p in root.iter() if radar in list(p))
    parent.remove(radar)
    if rows:
        # reuse the file's own colors: the big contributions number and its label
        texts = list(root.iter(f'{{{SVG}}}text'))
        strong = next((t.get('fill') for t in texts if 'font-weight: bold' in (t.get('style') or '')), '#ffc837')
        fg = next((t.get('fill') for t in texts if (t.text or '').strip() == 'contributions'), '#eeeeff')
        g = ET.SubElement(parent, f'{{{SVG}}}g', transform=f'translate({x} {y - 90})')
        ET.SubElement(g, f'{{{SVG}}}text', {'text-anchor': 'middle', 'fill': fg,
                      'style': 'font-size: 16px; opacity: 0.7;'}).text = 'private repos included'
        for i, (window, merged, reviewed) in enumerate(rows):
            top = 44 + i * 130
            ET.SubElement(g, f'{{{SVG}}}text', {'y': str(top), 'text-anchor': 'middle', 'fill': fg,
                          'style': 'font-size: 20px; font-weight: bold;'}).text = window
            for j, (n, label) in enumerate(((merged, 'PRs merged'), (reviewed, 'PRs reviewed'))):
                ty = str(top + 44 + j * 44)
                ET.SubElement(g, f'{{{SVG}}}text', {'x': '-10', 'y': ty, 'text-anchor': 'end', 'fill': strong,
                              'style': 'font-size: 36px; font-weight: bold;'}).text = f'{n:,}'
                ET.SubElement(g, f'{{{SVG}}}text', {'x': '4', 'y': ty, 'text-anchor': 'start', 'fill': fg,
                              'style': 'font-size: 22px;'}).text = label
    tree.write(path, encoding='utf-8')
    return True


if __name__ == '__main__':
    token = os.environ.get('STATS_TOKEN')
    rows = stats(token) if token else None
    print('stats:', rows or 'no STATS_TOKEN, removing radar only')
    for f in sorted(glob.glob('profile-3d-contrib/*.svg')):
        print(f, 'patched' if patch(f, rows) else 'no radar found')
