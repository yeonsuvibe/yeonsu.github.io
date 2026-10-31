#!/usr/bin/env python3
"""Build the four per-set entry points (index.html) and the sets hub page."""
import os

P = '/Users/eungsikahn/Dev/yeonsu_profile'
S = os.path.join(P, 'sets')

META = [
    ('01-warm-paper',   'Warm Paper',   '#f4f1ea', '#16150f', 'Default / warm paper baseline'),
    ('02-black-box',    'Black Box',    '#0d0c0a', '#f3efe7', 'Dark gallery / cob-lit concrete'),
    ('03-white-cube',   'White Cube',   '#f0efe9', '#16150f', 'Daylit white cube / skylight panels'),
    ('04-warm-pavilion','Warm Pavilion','#dccfb9', '#2a2016', 'Limewash pavilion / 2026 warm trend'),
]

ENTRY = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' fill='%23{bgc}%'/%3E%3Crect x='3' y='3' width='10' height='10' fill='none' stroke='%23{inkc}%'/%3E%3C/svg%3E"/>
<title>Yeonsu Ahn &mdash; {name}</title>
<style>
  html,body{{margin:0;padding:0;height:100%;background:{bg};overflow:hidden}}
  .stage{{position:fixed;inset:0;width:100%;height:100%;border:0;display:block}}
  .nojs{{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;
    font:300 .68rem/1.9 'Jost',sans-serif;letter-spacing:.28em;text-transform:uppercase;color:{ink};text-align:center}}
</style>
</head>
<body>
<iframe class="stage" src="gallery.html" title="Yeonsu Ahn &mdash; {name}" allow="fullscreen"></iframe>
<noscript><div class="nojs">Yeonsu Ahn &mdash; the gallery needs JavaScript.<br>Open <a href="gallery.html" style="color:inherit">gallery.html</a> directly.</div></noscript>
</body>
</html>
"""


def build_entries():
    for d, name, bg, ink, _desc in META:
        html = ENTRY.format(name=name, bg=bg, ink=ink,
                            bgc=bg.lstrip('#'), inkc=ink.lstrip('#'))
        path = os.path.join(S, d, 'index.html')
        with open(path, 'w') as fh:
            fh.write(html)
        print(f'  {d}/index.html  {len(html)}B')


if __name__ == '__main__':
    build_entries()
