(function () {
  const root = document.documentElement;
  const NAVMAP = { story: 'story', family: 'ch6', reference: 'reference', making: 'making', contribute: 'contribute', download: 'download' };
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } }
  };
  function pickLang() {
    const saved = store.get('bdo-lang');
    if (saved && LANGS.includes(saved)) return saved;
    const nav = (navigator.language || 'en').slice(0, 2).toLowerCase();
    return LANGS.includes(nav) ? nav : 'en';
  }
  let lang = pickLang();
  const T = () => I18N[lang] || I18N.en;

  function setLang(l, remember) {
    lang = l;
    root.dataset.l = l;
    root.lang = l;
    document.querySelectorAll('.lb').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.set === l)));
    const n = NAV[l] || NAV.en;
    document.querySelectorAll('.mainnav [data-nav]').forEach(a => { if (n[a.dataset.nav]) a.textContent = n[a.dataset.nav]; });
    const bt = document.querySelector('.brand .bt'); if (bt) bt.textContent = n.brand;
    if (remember) store.set('bdo-lang', l);
  }
  document.querySelectorAll('.lb').forEach(b => b.addEventListener('click', () => {
    const y = window.scrollY; setLang(b.dataset.set, true); if (y < 200) window.scrollTo(0, 0);
  }));
  if (LANGS.length < 2) { const lg = document.querySelector('.langs'); if (lg) lg.hidden = true; }

  function go(target) {
    const el = document.getElementById(lang + '-' + (NAVMAP[target] || target));
    if (el) el.scrollIntoView({ block: 'start' });
  }
  document.querySelectorAll('[data-nav]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); go(a.dataset.nav); }));
  setLang(lang, false);
  const h = (location.hash || '').slice(1);
  if (h) setTimeout(() => go(h), 60);

  /* ---------------- helpers ---------------- */
  function b64(str) { const bytes = new TextEncoder().encode(str); let bin = ''; bytes.forEach(c => bin += String.fromCharCode(c)); return btoa(bin); }
  function unb64(s) { const bin = atob(s); const bytes = Uint8Array.from(bin, c => c.charCodeAt(0)); return new TextDecoder().decode(bytes); }
  async function copyText(text, statusEl, ta) {
    try { await navigator.clipboard.writeText(text); statusEl.textContent = T().copied; }
    catch (e) { if (ta) { ta.focus(); ta.select(); } statusEl.textContent = T().copy_fail; }
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
  function creditName(e, t) {
    if (e.credit === 'anon' || !e.name) return t.anon;
    if (e.credit === 'initials') return e.name.split(/\s+/).filter(Boolean).map(w => w[0].toUpperCase() + '.').join(' ');
    return e.name;
  }
  const FIELDS = ['house', 'ancestor', 'village', 'today', 'title', 'teller', 'what', 'original', 'where', 'source'];
  const TYPEFIELDS = { branch: ['house', 'ancestor', 'village', 'today'], story: ['title', 'teller'], document: ['what', 'original'], correction: ['where', 'source'], help: [] };

  /* ---------------- contribute forms ---------------- */
  const forms = [];
  document.querySelectorAll('.contrib').forEach(sec => {
    const form = sec.querySelector('.cform');
    const l = form.dataset.lang;
    const t = I18N[l] || I18N.en;
    let type = 'branch';
    const out = sec.querySelector('.cout');
    const msg = out.querySelector('.msg');
    const status = out.querySelector('.status');
    const err = form.querySelector('.err');
    let entry = null;
    function showType(k) {
      type = k;
      sec.querySelectorAll('.ctype').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.t === k)));
      form.querySelectorAll('fieldset[data-for]').forEach(fs => fs.hidden = fs.dataset.for !== k);
    }
    sec.querySelectorAll('.ctype').forEach(b => b.addEventListener('click', () => { showType(b.dataset.t); out.hidden = true; form.hidden = false; }));
    form.addEventListener('submit', ev => {
      ev.preventDefault();
      const v = n => (form.elements[n] && form.elements[n].value || '').trim();
      const helps = [...form.querySelectorAll('input[name=help]:checked')].map(i => i.value);
      const e = { v: 1, type, lang: l, name: v('name'), relation: v('relation'), contact: v('contact'), credit: v('credit') || 'name',
        consent: form.elements.consent.checked, living: form.elements.living.checked, text: v('text'), help: helps, at: new Date().toISOString() };
      TYPEFIELDS[type].forEach(f => e[f] = v(f));
      if (type === 'branch') { const sel = form.elements.house; e.house_label = sel.options[sel.selectedIndex].text; }
      if (!e.name) { err.textContent = t.err_name; err.hidden = false; form.elements.name.focus(); return; }
      if (!e.text && type !== 'branch' && type !== 'help') { err.textContent = t.err_text; err.hidden = false; form.elements.text.focus(); return; }
      if (!e.consent) { err.textContent = t.err_consent; err.hidden = false; return; }
      err.hidden = true;
      entry = e;
      const L = t.labels; const lines = [t.hello, ''];
      lines.push(`${L.type}: ${t.types[type]}`);
      lines.push(`${L.name}: ${e.name}`);
      if (e.relation) lines.push(`${L.relation}: ${e.relation}`);
      if (e.contact) lines.push(`${L.contact}: ${e.contact}`);
      lines.push(`${L.credit}: ${t.credit[e.credit]}`);
      TYPEFIELDS[type].forEach(f => { const val = f === 'house' ? e.house_label : e[f]; if (val) lines.push(`${L[f]}: ${val}`); });
      if (helps.length) lines.push(`${L.help}: ${helps.map(k => (form.querySelector(`input[value="${k}"]`).parentNode.textContent || k).trim()).join('; ')}`);
      if (e.text) { lines.push('', `${L.text}:`, e.text); }
      lines.push('', `${L.consent}: ${t.yes}`, `${L.living}: ${e.living ? t.yes : t.no}`);
      lines.push('', '—', t.code_note, 'BDOYAN-CONTRIBUTION-1:' + b64(JSON.stringify(e)));
      const body = lines.join('\n');
      const subject = t.subject.replace('{type}', t.types[type]).replace('{name}', e.name);
      msg.value = body;
      out.querySelector('.mail').href = `mailto:${EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      out.querySelector('.wa').href = `https://wa.me/?text=${encodeURIComponent(subject + '\n\n' + body)}`;
      out.querySelector('.tg').href = `https://t.me/share/url?url=${encodeURIComponent('The House Bdoyan')}&text=${encodeURIComponent(subject + '\n\n' + body)}`;
      status.textContent = '';
      form.hidden = true; out.hidden = false;
      out.scrollIntoView({ block: 'start' });
    });
    out.querySelector('.copymsg').addEventListener('click', () => copyText(msg.value, status, msg));
    out.querySelector('.copyaddr').addEventListener('click', () => copyText(EMAIL, status, null));
    out.querySelector('.edit').addEventListener('click', () => { out.hidden = true; form.hidden = false; form.scrollIntoView({ block: 'start' }); });
    forms.push({ sec, l, t, get entry() { return entry; }, status, out, wallEmpty: sec.querySelector('.wall-list').textContent.trim(), inboxEmpty: sec.querySelector('.inbox-list').textContent.trim() });
  });

  /* ---------------- shared archive (db) ---------------- */
  function publicView(e, t) {
    const parts = [];
    TYPEFIELDS[e.type || 'story'].forEach(f => { const val = f === 'house' ? e.house_label : e[f]; if (val) parts.push(`${t.labels[f]}: ${val}`); });
    return { type: e.type, credit: creditName(e, t), relation: e.relation || '', title: e.title || e.what || e.house_label || '',
      text: [parts.join('\n'), e.text || ''].filter(Boolean).join('\n\n'), lang: e.lang, at: e.at || new Date().toISOString() };
  }
  function renderWall(docs) {
    forms.forEach(({ sec, t, wallEmpty }) => {
      const box = sec.querySelector('.wall-list');
      if (!docs.length) { box.innerHTML = `<p class="empty">${esc(wallEmpty)}</p>`; return; }
      box.innerHTML = docs.map(d => { const x = d.data(); return `<article class="witem" data-id="${esc(d.id)}"><div class="wt">${esc((t.types || {})[x.type] || x.type)}</div>${x.title ? `<h4>${esc(x.title)}</h4>` : ''}<p>${esc(x.text)}</p><div class="wm">${esc(x.credit)}${x.relation ? ' · ' + esc(x.relation) : ''} · ${esc((x.at || '').slice(0, 10))}</div>${canEdit ? `<div class="wb"><button type="button" class="btn sm unpub">${esc(t.unpublish)}</button></div>` : ''}</article>`; }).join('');
      box.querySelectorAll('.unpub').forEach(b => b.addEventListener('click', async () => { try { await db.doc('wall/' + b.closest('.witem').dataset.id).delete(); } catch (e) { /* refused */ } }));
    });
  }
  function renderInbox(docs) {
    forms.forEach(({ sec, t, inboxEmpty }) => {
      const box = sec.querySelector('.inbox-list');
      const pending = docs.filter(d => (d.data().status || 'new') === 'new');
      if (!pending.length) { box.innerHTML = `<p class="empty">${esc(inboxEmpty)}</p>`; return; }
      box.innerHTML = pending.map(d => { const x = d.data(); const pv = publicView(x, t); return `<article class="witem" data-id="${esc(d.id)}"><div class="wt">${esc(t.types[x.type] || x.type)} · ${esc(x.lang || '')}</div><h4>${esc(x.name)}${x.relation ? ' · ' + esc(x.relation) : ''}</h4><p>${esc(pv.text)}</p><div class="wm">${x.contact ? esc(x.contact) + ' · ' : ''}${esc(t.labels.credit)}: ${esc(pv.credit)} · ${esc(t.labels.living)}: ${x.living ? t.yes : t.no}</div><div class="wb"><button type="button" class="btn sm primary appr">${esc(t.approve)}</button><button type="button" class="btn sm rem">${esc(t.remove)}</button></div></article>`; }).join('');
      box.querySelectorAll('.appr').forEach(b => b.addEventListener('click', async () => {
        const id = b.closest('.witem').dataset.id; const d = docs.find(z => z.id === id); if (!d) return;
        b.disabled = true;
        try { await db.doc('wall/' + id).set(publicView(d.data(), t)); await db.doc('inbox/' + id).update({ status: 'approved' }); } catch (e) { b.disabled = false; }
      }));
      box.querySelectorAll('.rem').forEach(b => b.addEventListener('click', async () => {
        const id = b.closest('.witem').dataset.id; b.disabled = true;
        try { await db.doc('inbox/' + id).delete(); } catch (e) { b.disabled = false; }
      }));
    });
  }
  let db = null, canEdit = false;
  (async () => {
    if (!window.claude || !window.claude.use) return;
    try {
      const [d, u] = await Promise.all([window.claude.use('db'), window.claude.use('user')]);
      db = d;
      canEdit = u ? !!(await u.canEdit()) : false;
    } catch (e) { db = null; }
    if (!db) return;
    db.collection('wall').orderBy('at', 'desc').limit(200).onSnapshot(s => renderWall(s.docs), () => {});
    if (!canEdit) return;
    forms.forEach(({ sec, t, status }) => {
      sec.querySelector('.owner').hidden = false;
      const save = sec.querySelector('.savedb'); save.hidden = false;
      save.addEventListener('click', async () => {
        const f = forms.find(x => x.sec === sec); if (!f.entry) return;
        save.disabled = true;
        try { await db.collection('inbox').add({ ...f.entry, status: 'new', via: 'page' }); status.textContent = t.saved; }
        catch (e) { status.textContent = t.save_fail; save.disabled = false; }
      });
      sec.querySelector('.doimport').addEventListener('click', async () => {
        const box = sec.querySelector('.importbox'); const st = sec.querySelector('.istatus');
        const m = (box.value || '').match(/BDOYAN-CONTRIBUTION-1:([A-Za-z0-9+/=\s]+)/);
        if (!m) { st.textContent = t.no_code; return; }
        try { const e = JSON.parse(unb64(m[1].replace(/\s+/g, ''))); await db.collection('inbox').add({ ...e, status: 'new', via: 'import' }); st.textContent = t.imported; box.value = ''; }
        catch (e) { st.textContent = t.no_code; }
      });
    });
    db.collection('inbox').orderBy('at', 'desc').limit(300).onSnapshot(s => renderInbox(s.docs), () => {});
  })();

  /* ---------------- downloads ---------------- */
  (async () => {
    let dl = null;
    try { dl = window.claude && window.claude.use ? await window.claude.use('downloads') : null; } catch (e) { dl = null; }
    document.querySelectorAll('.downloads').forEach(sec => {
      const btns = sec.querySelectorAll('.dlbtn');
      if (!dl) { btns.forEach(b => b.hidden = true); sec.querySelector('.dlnote').hidden = false; return; }
      btns.forEach(b => b.addEventListener('click', async () => {
        const t = T(); b.disabled = true;
        try {
          const r = await fetch('files/' + b.dataset.f); const blob = await r.blob();
          await dl.save({ filename: ({book_en:'The_House_Bdoyan.pdf',handbook_en:'Finding_the_Bdoyans_Handbook.pdf',book_hy:'Bdoyanneri_tune_Armenian.pdf',handbook_hy:'Bdoyanneri_oronume_Armenian_Handbook.pdf',book_ru:'Dom_Bdoyanov_Russian.pdf',handbook_ru:'V_poiskakh_Bdoyanov_Russian_Handbook.pdf'})[b.dataset.f.replace('.pdf','')] || b.dataset.f, data: blob });
        } catch (e) { if (!(e && e.code === 'declined')) sec.querySelector('.dlnote').hidden = false; }
        b.disabled = false;
      }));
    });
  })();
})();
