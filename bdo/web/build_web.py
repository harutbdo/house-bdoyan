"""Build the shareable web edition: web/out/index.html + img/ + files/.
Usage: python3 web/build_web.py
"""
import re, os, sys, json, html as H, shutil
sys.path.insert(0, '/home/claude/bdo')
import build as B
from PIL import Image

ROOT = '/home/claude/bdo/'
OUT = ROOT + 'web/out/'
os.makedirs(OUT + 'img', exist_ok=True); os.makedirs(OUT + 'files', exist_ok=True)

LANG_ORDER = [l for l in ('en', 'hy', 'ru') if l in B.LANGS and (l == 'en' or os.path.exists(ROOT + f'parts_{l}/b_ch1.html'))]
UI = {l: json.load(open(ROOT + f'web/ui_{l}.json')) for l in LANG_ORDER}
for l in LANG_ORDER:
    if l != 'en':
        UI[l] = {**UI['en'], **UI[l]}
CFG = B.CONFIG


# ------------------------------------------------------------------ assets
def prep_images():
    for src, dst, w in [('photos/patara.jpg', 'patara.jpg', 2000), ('photos/panorama.jpg', 'panorama.jpg', 2000), ('photos/erzurum.jpg', 'erzurum.jpg', 1400)]:
        im = Image.open(ROOT + src).convert('RGB')
        if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save(OUT + 'img/' + dst, quality=82, optimize=True, progressive=True)
    for l in LANG_ORDER:
        sfx = '' if l == 'en' else '_' + l
        for m in ['map1_exodus', 'map2_dispersal', 'map3_heartland']:
            p = ROOT + f'build/{m}{sfx}.png'
            if not os.path.exists(p): p = ROOT + f'build/{m}.png'
            im = Image.open(p).convert('RGB')
            if im.width > 1700: im = im.resize((1700, round(im.height * 1700 / im.width)), Image.LANCZOS)
            im.save(OUT + f'img/{m}_{l}.jpg', quality=86, optimize=True)
        for c in ['chart_population', 'chart_countries']:
            p = ROOT + f'build/{c}{sfx}.svg'
            if not os.path.exists(p): p = ROOT + f'build/{c}.svg'
            s = open(p).read()
            s = re.sub(r'<\?xml[^>]*\?>\s*', '', s); s = re.sub(r'<!DOCTYPE[^>]*>\s*', '', s, flags=re.S)
            open(OUT + f'img/{c}_{l}.svg', 'w').write(s)
    for f, dst in [('build/book_en.pdf', 'book_en.pdf'), ('build/handbook.pdf', 'handbook_en.pdf'),
                   ('build/book_hy.pdf', 'book_hy.pdf'), ('build/book_ru.pdf', 'book_ru.pdf'),
                   ('build/handbook_hy.pdf', 'handbook_hy.pdf'), ('build/handbook_ru.pdf', 'handbook_ru.pdf')]:
        if os.path.exists(ROOT + f): shutil.copy(ROOT + f, OUT + 'files/' + dst)


# ------------------------------------------------------------------ content
def prefix_ids(s, l):
    s = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{l}-{m.group(1)}"', s)
    s = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{l}-{m.group(1)}"', s)
    s = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{l}-{m.group(1)})', s)
    return s


def web_notes(sec, l):
    sid = re.search(r'id="(ch\d)"', sec).group(1)
    items = []
    def rep(m):
        items.append(m.group(1).strip()); k = len(items)
        return f'<sup class="nr"><a href="#n-{sid}-{k}" id="r-{sid}-{k}">{k}</a></sup>'
    sec = re.sub(r'<n>(.*?)</n>', rep, sec, flags=re.S)
    if items:
        lis = ''.join(f'<li id="n-{sid}-{i+1}">{t} <a class="back" href="#r-{sid}-{i+1}" aria-label="back">↩</a></li>' for i, t in enumerate(items))
        notes = f'<details class="wnotes"><summary>{UI[l]["notes"]} ({len(items)})</summary><ol>{lis}</ol></details>'
        sec = sec[:sec.rindex('</section>')] + notes + '</section>'
    return sec


DIMS = {}
def dims(path):
    if path not in DIMS:
        p = OUT + path
        if path.endswith('.svg'):
            m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', open(p).read(2000))
            DIMS[path] = (round(float(m.group(1))), round(float(m.group(2)))) if m else None
        else:
            DIMS[path] = Image.open(p).size
    return DIMS[path]


def add_dims(s):
    def rep(m):
        tag = m.group(0)
        if ' width=' in tag: return tag
        src = re.search(r'src="([^"]+)"', tag).group(1)
        d = dims(src) if os.path.exists(OUT + src) else None
        return tag[:-1] + (f' width="{d[0]}" height="{d[1]}">' if d else '>')
    return re.sub(r'<img [^>]*src="img/[^"]+"[^>]*>', rep, s)


def fix_media(s, l):
    s = re.sub(r'src="build/(map\d_\w+?)\.svg"', lambda m: f'src="img/{m.group(1)}_{l}.jpg" loading="lazy"', s)
    s = re.sub(r'src="build/(chart_\w+?)\.svg"', lambda m: f'src="img/{m.group(1)}_{l}.svg" loading="lazy"', s)
    s = re.sub(r'src="photos/(\w+)\.jpg"', lambda m: f'src="img/{m.group(1)}.jpg" loading="lazy"', s)
    s = s.replace('style="width:94%;margin:0 auto" ', '')
    s = add_dims(s)
    # wrap wide tables for phones
    s = re.sub(r'(<table class="(?:who|pairs|lib|spell|timet)[^"]*">.*?</table>)', r'<div class="tscroll">\1</div>', s, flags=re.S)
    return s


def section(s, sid):
    m = re.search(r'<section class="chapter" id="' + sid + r'".*?</section>', s, re.S)
    return m.group(0) if m else ''


def lang_content(l):
    L = B.LANGS[l]; pp, sv = L['parts'], L['svg']
    u = UI[l]
    svgs = {'SVG_GERD': 'svg_gerd_L.svg', 'SVG_PROFILE': 'svg_profile_L.svg', 'SVG_VILLAGE': 'svg_village_L.svg', 'SVG_FAMCHART': 'svg_famchart.svg'}
    def fill_svg(s):
        for k, f in svgs.items():
            s = s.replace('{{' + k + '}}', sv(f))
        return s
    chapters = []
    for i in range(1, 8):
        chapters.append(pp(f'b_ch{i}.html'))
    chapters.append(pp('b_after.html'))
    story = []
    for c in chapters:
        c = fill_svg(c)
        c = web_notes(c, l)
        story.append(c)
    keyf = pp('b_keyfind.html').replace('class="frontpg"', 'class="wkeyfind"')
    back = pp('b_back.html')
    sources = section(back, 'sources')
    gloss = pp('b_gloss.html')
    guide = pp('h_ch1.html'); online = pp('h_ch2.html'); offline = pp('h_ch3.html')
    def refify(s):
        s = re.sub(r'<div class="big">[IVX]+</div>', '', s)
        s = re.sub(r'<div class="no">[^<]*? [IVX]+ <span>', f'<div class="no">{u["ref_word"]} <span>', s)
        for a, b2 in u['ref_xrefs']:
            s = s.replace(a, b2)
        return s
    guide, online, offline = refify(guide), refify(online), refify(offline)
    hero = u['hero']
    hero_html = f'''<header class="hero"><img src="img/patara.jpg" alt="{hero['cred']}" class="hbg"><div class="hshade"></div>
      <div class="hin"><div class="kicker">{hero['kicker']}</div><h1>{hero['title']}</h1><div class="st">{hero['sub']}</div>
      <div class="harm" lang="hy">{hero['arm']}</div><div class="places">{hero['places']}</div><div class="hline">{hero['line']}</div>
      <a class="btn hero-cta" href="#contribute">{hero['cta']}</a></div><div class="hcred">{hero['cred']}</div></header>'''
    making = pp('w_making.html').replace('{{COMPILER}}', CFG.get('COMPILER') or u['compiler_placeholder'])
    toc = ''.join(f'<a href="#ch{i}"><span class="n">{n}</span><span class="t">{t}</span></a>'
                  for i, (n, t) in enumerate(u['toc'], start=1))
    ref_nav = ''.join(f'<a href="#{k}">{v}</a>' for k, v in u['ref_nav'])
    body = f'''
<div class="L" data-l="{l}" lang="{l}">
  {hero_html}
  <section class="wsec intro" id="story">
    <p class="intro-note">{u["intro"]}</p>
    <div class="wtoc"><div class="kick">{u["contents"]}</div>{toc}</div>
  </section>
  {keyf}
  <div class="story">{''.join(story)}</div>
  <section class="wsec refpart" id="reference">
    <div class="kick">{u["ref_kick"]}</div><h2 class="wh2">{u["ref_h"]}</h2>
    <p class="lead">{u["ref_intro"]}</p>
    <nav class="refnav">{ref_nav}</nav>
    <div id="sources-wrap">{sources}</div>
    <div id="online-wrap">{online}</div>
    <div id="offline-wrap">{offline}</div>
    <div id="guide-wrap">{guide}</div>
    <div id="gloss-wrap">{gloss}</div>
    <div class="wsheets"><h3>{u["sheets_h"]}</h3><p>{u["sheets_p"]}</p></div>
  </section>
  {making}
  {contribute(l)}
  {downloads(l)}
  <footer class="wfoot">{u["footer"]}</footer>
</div>'''
    body = fix_media(body, l)
    body = body.replace('{{WEBLINK}}', u['this_page'])
    body = B.linkify(B.config_fill(body))
    body += f'<footer class="wfoot" data-l="{l}">{u["footer"]}</footer>' if False else ''
    body = prefix_ids(body, l)
    return body


# ------------------------------------------------------------------ contribute + downloads
HOUSES = ['h28', 'h29', 'h30', 'h31', 'h32', 'abul', 'akh', 'other']


def contribute(l):
    u = UI[l]
    t = u['c']
    types = ''.join(f'<button type="button" class="ctype" data-t="{k}" aria-pressed="{str(k=="branch").lower()}"><b>{v[0]}</b><span>{v[1]}</span></button>' for k, v in t['types'].items())
    houses = ''.join(f'<option value="{k}">{t["houses"][k]}</option>' for k in HOUSES)
    helps = ''.join(f'<label class="chk"><input type="checkbox" name="help" value="{k}"> {v}</label>' for k, v in t['helps'].items())
    def fld(name, label, kind='input', hint='', req=False, rows=3, type_='text'):
        r = ' required' if req else ''
        lab = f'<label for="{name}">{label}{" *" if req else ""}</label>'
        h = f'<small>{hint}</small>' if hint else ''
        if kind == 'textarea':
            ctl = f'<textarea id="{name}" name="{name}" rows="{rows}"{r}></textarea>'
        elif kind == 'select':
            ctl = f'<select id="{name}" name="{name}">{houses}</select>'
        else:
            ctl = f'<input id="{name}" name="{name}" type="{type_}"{r}>'
        return f'<div class="f">{lab}{ctl}{h}</div>'
    return f'''
<section class="wsec contrib" id="contribute">
  <div class="kick">{t["kick"]}</div><h2 class="wh2">{t["h"]}</h2>
  <p class="lead">{t["lead"]}</p>
  <div class="ctypes" role="group" aria-label="{t["kind"]}">{types}</div>
  <form class="cform" data-lang="{l}" novalidate>
    <fieldset data-for="branch">
      <legend>{t["types"]["branch"][0]}</legend>
      {fld("house", t["f_house"], "select")}
      {fld("ancestor", t["f_ancestor"], hint=t["h_ancestor"])}
      {fld("village", t["f_village"])}
      {fld("today", t["f_today"], "textarea", t["h_today"], rows=4)}
    </fieldset>
    <fieldset data-for="story" hidden>
      <legend>{t["types"]["story"][0]}</legend>
      {fld("title", t["f_title"])}
      {fld("teller", t["f_teller"])}
    </fieldset>
    <fieldset data-for="document" hidden>
      <legend>{t["types"]["document"][0]}</legend>
      {fld("what", t["f_what"], hint=t["h_what"])}
      {fld("original", t["f_original"])}
      <p class="note">{t["n_attach"]}</p>
    </fieldset>
    <fieldset data-for="correction" hidden>
      <legend>{t["types"]["correction"][0]}</legend>
      {fld("where", t["f_where"], hint=t["h_where"])}
      {fld("source", t["f_source"])}
    </fieldset>
    <fieldset data-for="help" hidden>
      <legend>{t["types"]["help"][0]}</legend>
      <div class="chks">{helps}</div>
    </fieldset>
    <fieldset class="always">
      {fld("text", t["f_text"], "textarea", t["h_text"], rows=6)}
      <div class="row2">{fld("name", t["f_name"], req=True)}{fld("relation", t["f_relation"], hint=t["h_relation"])}</div>
      <div class="row2">{fld("contact", t["f_contact"], hint=t["h_contact"])}
        <div class="f"><label for="credit">{t["f_credit"]}</label><select id="credit" name="credit"><option value="name">{t["cr_name"]}</option><option value="initials">{t["cr_init"]}</option><option value="anon">{t["cr_anon"]}</option></select></div></div>
      <label class="chk"><input type="checkbox" name="consent" id="consent"> {t["consent"]} *</label>
      <label class="chk"><input type="checkbox" name="living" id="living"> {t["living"]}</label>
      <p class="err" role="alert" hidden></p>
      <button type="submit" class="btn primary">{t["prepare"]}</button>
    </fieldset>
  </form>
  <div class="cout" hidden>
    <h3>{t["out_h"]}</h3>
    <p>{t["out_p"]}</p>
    <div class="sendto"><span>{t["send_to"]}</span> <code class="addr">{CFG["EMAIL"]}</code> <button type="button" class="btn sm copyaddr">{t["copy_addr"]}</button></div>
    <textarea class="msg" rows="12" readonly></textarea>
    <div class="acts">
      <button type="button" class="btn primary copymsg">{t["copy_msg"]}</button>
      <a class="btn mail" href="#" target="_blank" rel="noopener">{t["open_mail"]}</a>
      <a class="btn wa" href="#" target="_blank" rel="noopener">WhatsApp</a>
      <a class="btn tg" href="#" target="_blank" rel="noopener">Telegram</a>
      <button type="button" class="btn savedb" hidden>{t["save_db"]}</button>
    </div>
    <p class="status" role="status"></p>
    <p class="note">{t["out_note"]}</p>
    <button type="button" class="btn ghost edit">{t["edit"]}</button>
  </div>
  <div class="wall">
    <h3>{t["wall_h"]}</h3>
    <div class="wall-list"><p class="empty">{t["wall_empty"]}</p></div>
  </div>
  <div class="owner" hidden>
    <h3>{t["owner_h"]}</h3>
    <p class="note">{t["owner_p"]}</p>
    <label for="import">{t["import_l"]}</label>
    <textarea id="import" class="importbox" rows="4"></textarea>
    <button type="button" class="btn sm doimport">{t["import_b"]}</button>
    <p class="istatus" role="status"></p>
    <div class="inbox-list"><p class="empty">{t["inbox_empty"]}</p></div>
  </div>
</section>'''


def downloads(l):
    u = UI[l]
    items = []
    for f, key in [('book_en.pdf', 'dl_book_en'), ('handbook_en.pdf', 'dl_hb_en'), ('book_hy.pdf', 'dl_book_hy'), ('handbook_hy.pdf', 'dl_hb_hy'), ('book_ru.pdf', 'dl_book_ru'), ('handbook_ru.pdf', 'dl_hb_ru')]:
        p = OUT + 'files/' + f
        if os.path.exists(p):
            mb = os.path.getsize(p) / 1e6
            items.append(f'<div class="dl"><div><b>{u[key][0]}</b><span>{u[key][1]} · PDF · {mb:.1f} MB</span></div><button type="button" class="btn sm dlbtn" data-f="{f}">{u["dl_btn"]}</button></div>')
    return f'''
<section class="wsec downloads" id="download">
  <div class="kick">{u["dl_kick"]}</div><h2 class="wh2">{u["dl_h"]}</h2>
  <p>{u["dl_p"]}</p>
  <div class="dls">{''.join(items)}</div>
  <p class="dlnote note" hidden>{u["dl_none"]}</p>
</section>'''


# ------------------------------------------------------------------ page
def css():
    s = open(ROOT + 'style.css').read()
    s = re.sub(r'@font-face\s*\{[^}]*\}', '', s)
    # drop @page blocks (with nested margin boxes)
    out = []; i = 0
    while True:
        j = s.find('@page', i)
        if j < 0: out.append(s[i:]); break
        out.append(s[i:j]); depth = 0; k = s.index('{', j)
        while True:
            if s[k] == '{': depth += 1
            elif s[k] == '}':
                depth -= 1
                if depth == 0: break
            k += 1
        i = k + 1
    s = ''.join(out)
    s = s.replace('/*RUNHEADS*/', '')
    return s + open(ROOT + 'web/web.css').read()


def page():
    langs = LANG_ORDER
    content = '\n'.join(lang_content(l) for l in langs)
    i18n_js = {l: {k: UI[l][k] for k in ('js',)} for l in langs}
    hero = {l: UI[l]['hero'] for l in langs}
    nav = {l: UI[l]['nav'] for l in langs}
    langbtn = ''.join(f'<button type="button" class="lb" data-set="{l}" lang="{l}">{UI[l]["lang_label"]}</button>' for l in langs)
    tpl = open(ROOT + 'web/template.html').read()
    tpl = (tpl.replace('{{CSS}}', css()).replace('{{CONTENT}}', content).replace('{{LANGBTN}}', langbtn)
              .replace('{{I18N}}', json.dumps({l: UI[l]['js'] for l in langs}, ensure_ascii=False))
              .replace('{{HERO}}', json.dumps(hero, ensure_ascii=False)).replace('{{NAV}}', json.dumps(nav, ensure_ascii=False))
              .replace('{{LANGS}}', json.dumps(langs)).replace('{{EMAIL}}', CFG['EMAIL'])
              .replace('{{JS}}', open(ROOT + 'web/app.js').read()))
    open(OUT + 'index.html', 'w').write(tpl)
    print('index.html', round(len(tpl) / 1e6, 2), 'MB; languages', langs)


if __name__ == '__main__':
    prep_images()
    page()
