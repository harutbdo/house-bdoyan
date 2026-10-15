import sys
from playwright.sync_api import sync_playwright
svgfile, out = sys.argv[1], sys.argv[2]
svg=open(svgfile).read()
html=f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="style.css"><style>body{{background:#FBF8F2;margin:0;padding:10mm}} .w{{width:170mm}} svg{{width:100%;display:block}}</style></head><body><div class="w">{svg}</div></body></html>'''
open('/home/claude/bdo/_prev.html','w').write(html)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(device_scale_factor=2); pg.set_viewport_size({'width':760,'height':900})
    pg.goto('file:///home/claude/bdo/_prev.html'); pg.wait_for_timeout(500)
    pg.locator('.w').screenshot(path=out); b.close()
