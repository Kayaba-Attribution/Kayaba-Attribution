"""Replace the radar chart in the 3D contribution SVGs with real stats.

The radar only sees public activity, so private-repo reviews and PRs show as zero.
scripts/publish_stats.py runs on my Mac with access to those repos and commits
assets/devstats.json; this step draws its counts in the radar's place. Without the
file we only remove the radar.
"""
import glob, json, re
from pathlib import Path
import xml.etree.ElementTree as ET

SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)
STATS = Path('assets/devstats.json')
TRANSLATE = re.compile(r'^translate\(([\d.]+), ([\d.]+)\)$')


def stats():
    if not STATS.exists():
        return None
    q = json.loads(STATS.read_text())['search']
    return [('last 12 months', q['year']['merged'], q['year']['reviewed']),
            ('last 90 days', q['quarter']['merged'], q['quarter']['reviewed'])]


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
    rows = stats()
    print('stats:', rows or f'no {STATS}, removing radar only')
    for f in sorted(glob.glob('profile-3d-contrib/*.svg')):
        print(f, 'patched' if patch(f, rows) else 'no radar found')
