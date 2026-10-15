import re, sys, asyncio
from playwright.sync_api import sync_playwright
from pypdf import PdfReader
SRC='/home/claude/bdo/article.html'; TMP='/home/claude/bdo/_tmp.html'; OUT=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bdo/build/House_of_Bdo.pdf'
MARK={'ch1':'THE FOUNDER','ch2':'THE JOURNEY','ch3':'THE VILLAGE','ch4':'THE SCHOLAR','ch5':'THE BLOODLINE','ch6':'THE FAMILY TODAY','ch7':'THE GUIDE','library':'OPEN SOURCES','offline':'OFFLINE SOURCES','sheet':'WORKSHEET','sources':'REFERENCES'}
def build(html, out):
    open(TMP,'w').write(html)
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page()
        pg.goto('file://'+TMP); pg.wait_for_load_state('networkidle'); pg.evaluate('document.fonts.ready')
        pg.pdf(path=out, prefer_css_page_size=True, print_background=True, outline=True, tagged=True, display_header_footer=False)
        b.close()
def pages(out):
    r=PdfReader(out); res={}
    for i,pgx in enumerate(r.pages):
        t=re.sub(r'\s+',' ',pgx.extract_text() or '')
        for k,m in MARK.items():
            if k not in res and i>=2 and m.replace('’',"'") in t.replace('’',"'"): res[k]=i+1
    return res, len(r.pages)
html=open(SRC).read()
fill=lambda h,d: re.sub(r'\{\{(\w+)\}\}', lambda m: str(d.get(m.group(1),'·')), h)
build(fill(html,{}), OUT); res,n=pages(OUT); print('pass1',res,n)
build(fill(html,res), OUT); res2,n=pages(OUT); print('pass2',res2,n)
