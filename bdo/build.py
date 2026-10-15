"""Builds the two PDFs: the story book and the research handbook.
Usage: python3 build.py book|handbook
"""
import re, sys, html as H
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

ROOT = '/home/claude/bdo/'
P = lambda f: open(ROOT + 'parts/' + f).read()

FILLERS = [
    ('“They acquired not only single houses, but whole quarters.”', 'Vard Bdoyan, on the settlers of 1830'),
    ('His father’s household numbered thirty-three people, and five cradles were rocking in the house at once.', 'A man of Dinarigom, remembering · 1959'),
    ('The man christened Petros lived on as Bdo.', 'Chapter I'),
    ('When the elders of Pokr Khanchali speak the village tongue, they are still using the words of the Karin plain.', 'Chapter III'),
    ('Յոթ պորտ — seven generations of ancestors, as every Armenian was expected to know them.', 'An old saying'),
    ('Every Bdoyan is a descendant of Bdo (Bedros).', 'The family story'),
]
ROSETTE = '<svg width="40" height="40" viewBox="-50 -50 100 100" aria-hidden="true"><g fill="none" stroke="#A9813F" stroke-width="2.6"><circle r="44" opacity=".5"/><g id="fp{i}"><path d="M0 0 C 10 -14, 10 -30, 0 -40 C -10 -30, -10 -14, 0 0 Z"/></g>' + ''.join(f'<use href="#fp{{i}}" transform="rotate({a})"/>' for a in range(45, 360, 45)) + '<circle r="5" fill="#A9813F"/></g></svg>'


def filler(i, lst=None):
    lst = lst or FILLERS
    q, s = lst[i % len(lst)]
    return f'<section class="filler">{ROSETTE.replace("{i}", str(i))}<div class="q">{q}</div><div class="s">{s}</div></section>\n'


def svg(name):
    return open(ROOT + 'parts/' + name).read()


def process_notes(doc):
    """Number <n>..</n> per chapter; return doc and notes html."""
    notes_html = []
    def do_section(m):
        sec = m.group(0)
        sid = re.search(r'id="(ch\d)"', sec).group(1)
        run = re.search(r'data-run="([^"]+)"', sec).group(1)
        items = []
        def rep(mm):
            items.append(mm.group(1).strip())
            k = len(items)
            return f'<sup class="nr" id="r-{sid}-{k}"><a href="#n-{sid}-{k}">{k}</a></sup>'
        sec2 = re.sub(r'<n>(.*?)</n>', rep, sec, flags=re.S)
        if items:
            lis = ''.join(f'<li id="n-{sid}-{i+1}">{t}</li>' for i, t in enumerate(items))
            notes_html.append(f'<h4>{run.replace(" · ", " · ")}</h4><ol>{lis}</ol>')
        return sec2
    doc = re.sub(r'<section class="chapter" id="ch\d".*?</section>', do_section, doc, flags=re.S)
    return doc, '\n'.join(notes_html)


def runhead_css(doc, lefttitle):
    css = [f'@page :left {{ @top-left {{ content: "{lefttitle}"; }} }}']
    for sid, run in re.findall(r'<section class="chapter" id="([\w-]+)" data-run="([^"]+)"', doc):
        css.append(f'#{sid} {{ page: p_{sid}; }}')
        css.append(f'@page p_{sid}:right {{ @top-right {{ content: "{run}"; }} }}')
        css.append(f'@page p_{sid}:left {{ @top-left {{ content: "{lefttitle}"; }} }}')
    for n in ['cover', 'front', 'blankp']:
        for side in ['left', 'right']:
            css.append(f'@page {n}:{side} {{ @top-left {{ content: none; }} @top-right {{ content: none; }} @bottom-left {{ content: none; }} @bottom-right {{ content: none; }} }}')
    for side in ['left', 'right']:
        css.append(f'@page plain:{side} {{ @top-left {{ content: none; }} @top-right {{ content: none; }} }}')
    return '\n'.join(css)


def render(doc, out):
    tmp = ROOT + '_tmp.html'
    open(tmp, 'w').write(doc)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        pg.goto('file://' + tmp); pg.wait_for_load_state('networkidle'); pg.evaluate('document.fonts.ready')
        ov = pg.evaluate("""()=>{const W=document.documentElement.clientWidth;const o=[];document.querySelectorAll('body *').forEach(e=>{if(e.closest('svg'))return;const r=e.getBoundingClientRect();if(r.right>W+2)o.push(e.tagName+'.'+e.className+'@'+(e.closest('section')?.id||''));});return o.slice(0,8)}""")
        if ov: print('WARNING overflow:', ov)
        pg.pdf(path=out, prefer_css_page_size=True, print_background=True, outline=True, tagged=True, display_header_footer=False)
        b.close()
    r = PdfReader(out)
    texts = [(pp.extract_text() or '') for pp in r.pages]
    return texts


def norm(t):
    t = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', t)
    t = t.replace('­', '')
    return re.sub(r'\s+', ' ', t)


def find_starts(texts, marks):
    res = {}
    for k, m in marks.items():
        for i, t in enumerate(texts):
            if i >= 2 and m in norm(t):
                res[k] = i + 1; break
    return res


def wrap(body, title, lefttitle, lang='en'):
    head = f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{title}</title>
<link rel="stylesheet" href="style.css"><style>{{RUNCSS}}</style></head><body>
'''
    return head + body + '\n</body></html>'



import os

import html as _html
def localize_svg(s, lang):
    import json as _json
    pth = ROOT + f'i18n/svg_{lang}.json'
    D = _json.load(open(pth)) if os.path.exists(pth) else {}
    arm = lang == 'hy'
    from PIL import ImageFont
    FF = ROOT + 'fonts/'
    fonts = {'Cormorant': FF + 'CormorantGaramond.ttf', 'Source': FF + 'SourceSerif4.ttf', 'Inter': FF + 'Inter.ttf',
             'ArmSerif': FF + 'NotoSerifArmenian.ttf', 'ArmSans': FF + 'NotoSansArmenian.ttf'}
    rootfam = re.search(r'<svg[^>]*font-family="([^"]+)"', s)
    rootfam = rootfam.group(1) if rootfam else 'Inter'
    _cache = {}
    def width(t, fam, target):
        key = 'Cormorant' if 'Cormorant' in fam else 'Source' if 'Source' in fam else 'Inter'
        if target and re.search('[\u0530-\u058F]', t):
            key = 'ArmSans' if key == 'Inter' else 'ArmSerif'
        if key not in _cache: _cache[key] = ImageFont.truetype(fonts[key], 100)
        return _cache[key].getlength(t)
    rootsize = '12'
    stack = [(rootfam, rootsize)]
    out = []
    pos = 0
    for m in re.finditer(r'<g\b[^>]*?(/?)>|</g>|<text([^>]*)>(.*?)</text>', s, flags=re.S):
        out.append(s[pos:m.start()]); pos = m.end()
        tok = m.group(0)
        if tok.startswith('<g'):
            fam = re.search(r'font-family="([^"]+)"', tok); size = re.search(r'font-size="([\d.]+)"', tok)
            if not tok.endswith('/>'):
                stack.append((fam.group(1) if fam else stack[-1][0], size.group(1) if size else stack[-1][1]))
            out.append(tok); continue
        if tok == '</g>':
            if len(stack) > 1: stack.pop()
            out.append(tok); continue
        attrs, inner = m.group(2), m.group(3)
        fam = re.search(r'font-family="([^"]+)"', attrs); fam = fam.group(1) if fam else stack[-1][0]
        size = re.search(r'font-size="([\d.]+)"', attrs); size = float(size.group(1)) if size else float(stack[-1][1])
        ratio = [1.0]
        def node(mm):
            raw = mm.group(1)
            key = _html.unescape(raw).strip()
            if key in D:
                tr = D[key]
                ratio.append(width(tr, fam, True) / max(1.0, width(key, fam, False)))
                lead = raw[:len(raw) - len(raw.lstrip())]; trail = raw[len(raw.rstrip()):]
                return '>' + lead + _html.escape(tr, quote=False) + trail + '<'
            return mm.group(0)
        inner2 = re.sub(r'>([^<]+)<', node, '>' + inner + '<')[1:-1]
        r = max(ratio)
        if r > 1.04:
            k = max(0.6, 1.04 / r)
            if 'font-size=' in attrs:
                attrs = re.sub(r'font-size="([\d.]+)"', lambda q: f'font-size="{float(q.group(1)) * k:.2f}"', attrs)
            else:
                attrs += f' font-size="{size * k:.2f}"'
            inner2 = re.sub(r'font-size="([\d.]+)"', lambda q: f'font-size="{float(q.group(1)) * k:.2f}"', inner2)
        out.append(f'<text{attrs}>{inner2}</text>')
    out.append(s[pos:])
    s = ''.join(out)
    if arm:
        s = s.replace('font-family="Inter"', 'font-family="Noto Sans Armenian, Inter, sans-serif"')
        s = re.sub(r'font-family="(Cormorant Garamond|Source Serif 4)"', r'font-family="Noto Serif Armenian, \1, serif"', s)
        s = s.replace("font-family=\"Inter, sans-serif\"", 'font-family="Noto Sans Armenian, Inter, sans-serif"')
    return s

def _parts_for(lang):
    d = ROOT + ('parts/' if lang == 'en' else f'parts_{lang}/')
    def pp(f):
        p = d + f
        return open(p if os.path.exists(p) else ROOT + 'parts/' + f).read()
    def sv(f):
        p = d + f
        if os.path.exists(p): return open(p).read()
        s = open(ROOT + 'parts/' + f).read()
        return localize_svg(s, lang) if lang != 'en' else s
    def has(f): return os.path.exists(d + f) or os.path.exists(ROOT + 'parts/' + f)
    return pp, sv, has

LANGS = {}
def register(lang, **kw):
    pp, sv, has = _parts_for(lang)
    LANGS[lang] = dict(parts=pp, svg=sv, has=has, **kw)

# ---------------------------------------------------------------- BOOK
BOOK_MARKS = {'keyfind': 'KEY FINDINGS', 'ch1': 'THE FOUNDER', 'ch2': 'THE JOURNEY', 'ch3': 'THE VILLAGE', 'ch4': 'THE SCHOLAR',
              'ch5': 'THE BLOODLINE', 'ch6': 'Chapter VI THE FAMILY', 'ch7': 'THE FAMILY TODAY', 'ch8': 'HOW IT WAS POSSIBLE', 'gloss': 'WORDS TO KNOW',
              'notes': 'NOTES TO THE CHAPTERS', 'sources': 'SOURCES USED', 'index': 'INDEX OF NAMES AND PLACES'}
CHAPTERS = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'gloss', 'notes', 'sources', 'index']

INDEX_TERMS = {
 'People': [
  ('Acharyan, Hrachia', ['Acharyan']), ('Anush (Bdoyan), daughter of Matevos', ['Anush']), ('Avagyan, Horomsima', ['Horomsima']),
  ('Bagratuni, Archbishop Karapet', ['Bagratuni']), ('Balasan Bdoyan', ['Balasan']), ('Bdo (Bedros), founder', ['Bdo (Bedros)', 'Bdo ', 'Bdo’s', 'Bdo,', 'Bdo.']),
  ('Bdoyents Papo', ['Papo']), ('Chavush, Gevorg', ['Gevorg Chavush']), ('Davtyan, Simon', ['Simon Davtyan', 'Simon']),
  ('Gevorg Bdoyan, of Akhalkalaki', ['Gevorg Bdoyan', 'Gevorg of Akhalkalaki', 'Gevorg']), ('Gharibyan, Rafayel', ['Gharibyan']),
  ('Grigor Bdoyan, house 29', ['Grigor Bdoyan', 'Grigor,', 'Grigor ']), ('Hakob Bdoyan, of Abul', ['Hakob Bdoyan', 'Hakob of Umudum', 'Hakob']),
  ('Harutyun Bdoyan', ['Harutyun']), ('Karapetian, Samvel', ['Karapetian']), ('Khachatur Bdoyan', ['Khachatur']), ('Khnko Bdoyan', ['Khnko']),
  ('Khoperyants, Karapet', ['Khoperyants']), ('Melkonyan, Ashot', ['Melkonyan']), ('Mesrop Bdoyan', ['Mesrop']), ('Movsisyan, Fr Vardan', ['Vardan Movsisyan', 'Father Vardan']),
  ('Nahapetyan, Rafik', ['Nahapetyan']), ('Paskevich, Ivan', ['Paskevich']), ('Ruben Bdoyan', ['Ruben']), ('Sirun Bdoyan', ['Sirun']),
  ('Smbat Bdoyan', ['Smbat']), ('Stepan Bdoyan', ['Stepan']), ('Tadevos Bdoyan', ['Tadevos']), ('Vard Harutyuni Bdoyan', ['Vard']),
  ('Varvare Bdoyan', ['Varvare']), ('Zakar Bdoyan', ['Zakar']), ('Zavik Bdoyan', ['Zavik'])],
 'Places': [
  ('Abul', ['Abul']), ('Akhalkalaki', ['Akhalkalaki']), ('Akhaltsikhe', ['Akhaltsikhe']), ('Altai', ['Altai']), ('Chaltyr', ['Chaltyr']),
  ('Dilif', ['Dilif']), ('Dinarigom', ['Dinarigom', 'Dinargom']), ('Erzurum, see Karin', ['Erzurum']), ('Gyumri (Leninakan)', ['Gyumri', 'Leninakan']),
  ('Jigrashen', ['Jigrashen']), ('Javakhk', ['Javakhk']), ('Karin', ['Karin']), ('Kars', ['Kars']), ('Katnatu', ['Katnatu']), ('Kharkiv', ['Kharkiv']),
  ('Khanchali, Lake', ['Lake Khanchali']), ('Majadia', ['Majadia']), ('Mets Khanchali', ['Mets Khanchali']), ('Nardivan', ['Nardivan']),
  ('Ninotsminda (Bogdanovka)', ['Ninotsminda', 'Bogdanovka']), ('Pokr Khanchali', ['Pokr Khanchali']), ('Tbilisi (Tiflis)', ['Tbilisi', 'Tiflis']),
  ('Umudum', ['Umudum']), ('Yerevan', ['Yerevan'])],
 'Subjects': [
  ('church of St Hakob', ['St Hakob', 'Surb Hakob']), ('DNA', ['DNA']), ('exodus of 1829–1830', ['exodus']), ('gerdastan', ['gerdastan']),
  ('kin quarters', ['kin quarter']), ('Karin dialect', ['Karin dialect', 'Karno']), ('mill of Bdoyents Papo', ['mill']), ('name Bdo, origin of', ['pet form', 'Petros']),
  ('parish registers', ['register']), ('tohmanun (clan name)', ['tohmanun', 'tohm']), ('population of Pokr Khanchali', ['78 people', '691', '353 people', '554']), ('Treaty of Adrianople', ['Adrianople'])],
}


def build_index(texts, first, last, terms=None, prefix=False):
    terms = terms or INDEX_TERMS
    pages = {i + 1: norm(texts[i]) for i in range(first - 1, last)}
    out = []
    for grp, tl in terms.items():
        out.append(f'<h4>{grp}</h4>')
        for disp, pats in sorted(tl, key=lambda x: x[0].lower()):
            pg = []
            for n, t in pages.items():
                for pat in pats:
                    rx = r'(?<![\w])' + re.escape(pat if prefix else pat.strip()) + (r'(?![\w])' if pat[-1].isalnum() and not prefix else '')
                    if re.search(rx, t):
                        pg.append(n); break
            if pg:
                out.append(f'<p><b>{H.escape(disp)}</b> <span class="pg">{", ".join(map(str, compact(pg)))}</span></p>')
    return '\n'.join(out)


def compact(pg):
    pg = sorted(set(pg)); res = []; i = 0
    while i < len(pg):
        j = i
        while j + 1 < len(pg) and pg[j + 1] == pg[j] + 1: j += 1
        res.append(f'{pg[i]}–{pg[j]}' if j > i else str(pg[i])); i = j + 1
    return res


register('en', title='The House Bdoyan — A History of the Bdoyan Family', lefttitle='The House Bdoyan',
         marks=BOOK_MARKS, chapters=CHAPTERS, fillers=FILLERS, index_terms=INDEX_TERMS)
for _l in ('hy', 'ru'):
    try:
        _m = __import__('lang_' + _l)
        register(_l, **_m.SPEC)
    except ImportError:
        pass

CONFIG = {'EMAIL': 'harut.bdo116@gmail.com', 'WEBURL': '', 'BYLINE': 'Compiled for the Bdoyan family'}
try:
    import json as _j
    CONFIG.update(_j.load(open(ROOT + 'config.json')))
except Exception:
    pass

TLD = r'(?:am|org|ge|ru|com|net|de|uk|es|edu|info|io)'
URL_RX = re.compile(r'(?<![\w@/.-])((?:[a-z0-9-]+\.)+' + TLD + r'(?:/[\w./%#?=&~-]*)?)(?![\w@])')


def linkify(doc):
    """Turn plain web addresses in text into links (skips tags, links, svg, style, head)."""
    out = []; skip = 0
    for tok in re.split(r'(<[^>]+>)', doc):
        if tok.startswith('<'):
            low = tok.lower()
            if re.match(r'<(a|svg|style|title|script)[\s>]', low): skip += 1
            elif re.match(r'</(a|svg|style|title|script)>', low): skip = max(0, skip - 1)
            out.append(tok); continue
        if skip or not tok.strip():
            out.append(tok); continue
        def rep(m):
            u = m.group(1); tail = ''
            while u and u[-1] in '.,;:)': tail = u[-1] + tail; u = u[:-1]
            return f'<a class="lk" href="https://{u}">{u}</a>{tail}'
        out.append(URL_RX.sub(rep, tok))
    return ''.join(out)


def config_fill(doc):
    url = CONFIG.get('WEBURL') or ''
    weblink = (f'<a href="{url}">{url.replace("https://", "")}</a>' if url else 'the link is on the back cover of the next printing')
    return (doc.replace('{{WEBLINK}}', weblink).replace('{{EMAIL}}', CONFIG['EMAIL'])
               .replace('{{BYLINE}}', CONFIG['BYLINE']).replace('{{WEBURL}}', f'<a href="{url}" style="color:inherit">{url.replace("https://", "")}</a>' if url else ''))


def assemble(spec, doc, out):
    """Generic multi-pass build: fillers before right-hand chapters, TOC page numbers, index."""
    marks, chapters = spec['marks'], spec['chapters']
    fill = lambda d, vals: re.sub(r'\{\{(\w+)\}\}', lambda m: str(vals.get(m.group(1), '·')), d)
    texts = render(fill(doc.replace('{{INDEX}}', '<p>index</p>'), {}), out)
    st = find_starts(texts, marks); print('pass1', st, len(texts))
    off = 0; k = spec.get('filler_start', 0)
    for sid in chapters:
        if sid not in st: continue
        if (st[sid] + off) % 2 == 0:
            doc = doc.replace(f'<section class="chapter" id="{sid}"', filler(k, spec.get('fillers')) + f'<section class="chapter" id="{sid}"', 1)
            off += 1; k += 1
    for it in range(3):
        texts = render(fill(doc.replace('{{INDEX}}', '<p>index</p>'), st), out)
        st = find_starts(texts, marks)
        if spec.get('index'):
            idx = spec['index'](texts, st)
            texts = render(fill(doc.replace('{{INDEX}}', idx), st), out)
            st2 = find_starts(texts, marks)
            if st2 != st: st = st2; continue
            doc_final = doc.replace('{{INDEX}}', idx)
        else:
            doc_final = doc
        break
    if len(texts) % 2 == 1:
        doc_final = doc_final.replace('<section class="bcover">', filler(k, spec.get('fillers')) + '<section class="bcover">'); k += 1
    final = fill(doc_final, st)
    texts = render(final, out)
    st3 = find_starts(texts, marks); print('final', st3, len(texts))
    print('chapters on left pages:', [s for s in chapters if s in st3 and st3[s] % 2 == 0])
    open(out.replace('.pdf', '.html'), 'w').write(final)
    return st3, len(texts)


def book(lang='en'):
    L = LANGS[lang]
    pp = L['parts']
    parts = [pp('b_front.html'), pp('b_toc.html'), pp('b_keyfind.html')]
    chs = [pp(f'b_ch{i}.html') for i in range(1, 8)]
    chs[0] = chs[0].replace('{{SVG_GERD}}', L['svg']('svg_gerd_L.svg'))
    chs[1] = chs[1].replace('{{SVG_PROFILE}}', L['svg']('svg_profile_L.svg'))
    chs[2] = chs[2].replace('{{SVG_VILLAGE}}', L['svg']('svg_village_L.svg'))
    chs[5] = chs[5].replace('{{SVG_FAMCHART}}', L['svg']('svg_famchart.svg'))
    extra = [pp('b_after.html')] if L['has']('b_after.html') else []
    back = [pp('b_gloss.html'), pp('b_back.html')]
    tail = pp('b_backcover.html')
    body = '\n'.join(parts) + '\n'.join(chs + extra + back) + '\n' + tail
    doc = wrap(body, L['title'], L['lefttitle'], lang)
    if L.get('css'): doc = doc.replace('</head>', '<style>' + L['css'] + '</style></head>', 1)
    for nm in ['map1_exodus', 'map2_dispersal', 'map3_heartland', 'chart_population', 'chart_countries', 'cover_art']:
        if lang != 'en' and os.path.exists(ROOT + f'build/{nm}_{lang}.svg'):
            doc = doc.replace(f'build/{nm}.svg', f'build/{nm}_{lang}.svg')
    doc, notes = process_notes(doc)
    doc = doc.replace('{{NOTES}}', notes)
    doc = doc.replace('{RUNCSS}', runhead_css(doc, L['lefttitle']))
    if L.get('byline'): doc = doc.replace('{{BYLINE}}', L['byline'])
    doc = linkify(config_fill(doc))
    spec = {'marks': L['marks'], 'chapters': L['chapters'], 'fillers': L['fillers'],
            'index': lambda texts, st: build_index(texts, st['ch1'], st['gloss'] - 1, L['index_terms'], L.get('prefix_terms', False))}
    return assemble(spec, doc, ROOT + f'build/book_{lang}.pdf')


HB_MARKS = {'h1': 'THE GUIDE', 'h2': 'OPEN SOURCES', 'h3': 'OFFLINE SOURCES', 'h4': 'WORKSHEETS Worksheets', 'h5': 'Last page SHARE WHAT YOU FIND'}
HB_TITLES = {'en': ('Finding the Bdoyans — A Research Handbook', 'Finding the Bdoyans')}


def handbook(lang='en'):
    L = LANGS[lang]; pp = L['parts']
    parts = [pp('h_front.html'), pp('h_ch1.html'), pp('h_ch2.html'), pp('h_ch3.html'), pp('h_ch4.html'), pp('h_back.html'), pp('h_backcover.html')]
    title, left = L.get('hb_titles', HB_TITLES['en'])
    doc = wrap('\n'.join(parts), title, left, lang)
    if L.get('css'): doc = doc.replace('</head>', '<style>' + L['css'] + '</style></head>', 1)
    if lang != 'en' and os.path.exists(ROOT + f'build/cover_art_{lang}.svg'):
        doc = doc.replace('build/cover_art.svg', f'build/cover_art_{lang}.svg')
    doc = doc.replace('{RUNCSS}', runhead_css(doc, left))
    if L.get('byline'): doc = doc.replace('{{BYLINE}}', L['byline'])
    doc = linkify(config_fill(doc))
    spec = {'marks': L.get('hb_marks', HB_MARKS), 'chapters': ['h1', 'h2', 'h3', 'h4', 'h5'], 'fillers': L.get('fillers'), 'filler_start': 0}
    return assemble(spec, doc, ROOT + ('build/handbook.pdf' if lang == 'en' else f'build/handbook_{lang}.pdf'))


if __name__ == '__main__':
    if sys.argv[1] == 'handbook': handbook(sys.argv[2] if len(sys.argv) > 2 else 'en')
    else: book(sys.argv[2] if len(sys.argv) > 2 else 'en')
