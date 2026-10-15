"""Translate the text of matplotlib figures by exact string match.
BDO_LANG=hy|ru selects i18n/fig_<lang>.json; BDO_DUMP=1 records every string."""
import os, json, re
import matplotlib.text
from matplotlib.font_manager import FontProperties
LANG = os.environ.get('BDO_LANG', 'en')
ROOT = '/home/claude/bdo/'
D = {}
if LANG != 'en' and os.path.exists(ROOT + f'i18n/fig_{LANG}.json'):
    D = json.load(open(ROOT + f'i18n/fig_{LANG}.json'))
ARM = re.compile('[԰-֏]')
F = ROOT + 'fonts/'
ARMF = {'serif': FontProperties(fname=F + 'NotoSerifArmenian.ttf'), 'sans': FontProperties(fname=F + 'NotoSansArmenian.ttf')}

def suffix():
    return '' if LANG == 'en' else '_' + LANG

def localize(fig, name=''):
    seen = []
    for t in fig.findobj(matplotlib.text.Text):
        s = t.get_text()
        if not s or not re.search('[A-Za-z]', s): continue
        seen.append(s)
        if s in D:
            new_t = D[s]
            t.set_text(new_t)
            lo, ln = max(len(x) for x in s.split('\n')), max(len(x) for x in new_t.split('\n'))
            if s.upper() == s and ln > lo * 1.12:
                t._bdo_shrink = max(0.72, lo * 1.12 / ln)
        if LANG == "hy" and ARM.search(t.get_text()):
            fp = t.get_fontproperties()
            fam = (fp.get_file() or '') if hasattr(fp, 'get_file') else ''
            sans = 'Inter' in str(fam) or 'Inter' in str(fp.get_family())
            w = fp.get_weight()
            new = (ARMF['sans'] if sans else ARMF['serif']).copy()
            new.set_size(fp.get_size())
            try: new.set_weight(w)
            except Exception: pass
            t.set_fontproperties(new)
        if LANG == 'ru' and re.search('[\u0400-\u04FF]', t.get_text()) and 'Armenian' in str(t.get_fontproperties().get_name()):
            new = FontProperties(fname=F + 'Inter.ttf'); new.set_size(t.get_fontproperties().get_size()); t.set_fontproperties(new)
        if getattr(t, '_bdo_shrink', None):
            t.set_fontsize(t.get_fontsize() * t._bdo_shrink); t._bdo_shrink = None
    if os.environ.get('BDO_DUMP'):
        p = ROOT + 'i18n/fig_strings.json'
        allv = json.load(open(p)) if os.path.exists(p) else {}
        allv[name] = sorted(set(seen))
        json.dump(allv, open(p, 'w'), ensure_ascii=False, indent=1)
