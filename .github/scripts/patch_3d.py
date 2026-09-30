"""Replace the radar chart in the 3D contribution SVGs with real stats.

The radar only sees public activity, so private-repo reviews and PRs show as zero.
With STATS_TOKEN (a token that can read the private repos) we draw merged PRs and
reviews from GitHub search instead. Without it we only remove the radar.
"""
import glob, json, os, re, urllib.request
from datetime import date, timedelta
import xml.etree.ElementTree as ET

SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)
USER = os.environ.get('GITHUB_REPOSITORY_OWNER', 'Kayaba-Attribution')
TRANSLATE = re.compile(r'^translate\(([\d.]+), ([\d.]+)\)$')


def stats(token):
    to = date.today()
    win = f'{to - timedelta(days=365)}..{to}'
    q = '''query($merged:String!,$reviewed:String!){
      merged:search(query:$merged,type:ISSUE,first:1){issueCount}
      reviewed:search(query:$reviewed,type:ISSUE,first:1){issueCount}}'''
    body = json.dumps({'query': q, 'variables': {
        'merged': f'is:pr is:merged author:{USER} merged:{win}',
        'reviewed': f'is:pr reviewed-by:{USER} -author:{USER} created:{win}'}}).encode()
    req = urllib.request.Request('https://api.github.com/graphql', body,
                                 {'Authorization': f'bearer {token}', 'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(req))['data']
    return [(d['merged']['issueCount'], 'PRs merged'), (d['reviewed']['issueCount'], 'PRs reviewed')]


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
        g = ET.SubElement(parent, f'{{{SVG}}}g', transform=f'translate({x} {y - 60})')
        ET.SubElement(g, f'{{{SVG}}}text', {'text-anchor': 'middle', 'fill': fg,
                      'style': 'font-size: 18px; opacity: 0.7;'}).text = 'last 12 months, private repos included'
        for i, (n, label) in enumerate(rows):
            ty = str(62 + i * 62)
            ET.SubElement(g, f'{{{SVG}}}text', {'x': '-10', 'y': ty, 'text-anchor': 'end', 'fill': strong,
                          'style': 'font-size: 44px; font-weight: bold;'}).text = f'{n:,}'
            ET.SubElement(g, f'{{{SVG}}}text', {'x': '4', 'y': ty, 'text-anchor': 'start', 'fill': fg,
                          'style': 'font-size: 24px;'}).text = label
    tree.write(path, encoding='utf-8')
    return True


if __name__ == '__main__':
    token = os.environ.get('STATS_TOKEN')
    rows = stats(token) if token else None
    print('stats:', rows or 'no STATS_TOKEN, removing radar only')
    for f in sorted(glob.glob('profile-3d-contrib/*.svg')):
        print(f, 'patched' if patch(f, rows) else 'no radar found')
