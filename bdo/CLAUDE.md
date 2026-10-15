# The House Bdoyan — project handover

A family history of the Bdoyan family (Dinarigom on the Karin plain → Pokr Khanchali / Abul in Javakhk),
built as print PDFs in English, Armenian and Russian plus a trilingual web edition with a contribution form.
Compiler: the user (Bdoyan family). Work began 15 October 2026 in a Claude cloud session.

## What exists
| Output | Built by | Source parts |
|---|---|---|
| `build/book_en.pdf` — *The House Bdoyan* (48 pp) | `python3 build.py book en` | `parts/b_*.html` |
| `build/book_hy.pdf` — *Բդոյանների տունը* | `python3 build.py book hy` | `parts_hy/b_*.html` (falls back to `parts/`) |
| `build/book_ru.pdf` — *Дом Бдоянов* | `python3 build.py book ru` | `parts_ru/b_*.html` |
| `build/handbook.pdf`, `handbook_hy.pdf`, `handbook_ru.pdf` — *Finding the Bdoyans* | `python3 build.py handbook en|hy|ru` | `parts*/h_*.html` |
| `web/out/` — web edition | `python3 web/build_web.py` | book + handbook parts, `parts*/w_making.html`, `web/ui_*.json`, `web/template.html`, `web/app.js`, `web/web.css` |

Published web page (claude.ai Artifact, owner's account): https://claude.ai/artifact/FcnSZy3zKiXexgTckt51aL
(capabilities: db with `inbox` admin-only, `wall` public read; user; downloads). Republish with the Artifact tool,
passing that URL as `url`, `root: web/out`, and the `img/*` and `files/*.pdf` supporting files.

## Rebuild from scratch
1. `pip install playwright pypdf matplotlib numpy pillow fonttools --break-system-packages` (Chromium via Playwright).
2. Figures: `python3 maps.py && python3 chart_pop.py && python3 gen/chart_countries.py` (English);
   repeat each with `BDO_LANG=hy` and `BDO_LANG=ru` for translated figures (`i18n/fig_*.json`).
   Family chart SVG: `python3 gen/famchart.py`. Diagram labels are translated at build time from `i18n/svg_*.json`.
3. PDFs: `python3 build.py book en|hy|ru` and `python3 build.py handbook en|hy|ru` (each ~45 s; multi-pass:
   inserts verso fillers so chapters open on right-hand pages, fills contents page numbers, builds the index).
4. Web: copy PDFs happen automatically in `web/build_web.py`; then republish.
`config.json` holds `WEBURL` (printed on covers); `CONFIG['EMAIL']` in build.py is the contribution address.

## Conventions (keep)
- Every fact carries an endnote `<n>…</n>` and, where certainty matters, a mark: `<span class="mk c">●</span>` confirmed,
  `mk p` ◐ probable, `mk t` ○ tradition/estimate. Living people only where a published source names them.
- Founder is written **Bdo (Bedros)** / **Բդո (Պետրոս)** / **Бдо (Бедрос)** until a register gives his baptismal name.
- Title: **The House Bdoyan** / **Բդոյանների տունը** / **Дом Бдоянов** (chosen by the user).
- Quotes from sources are short; Armenian passages are paraphrased in translation.

## Key sources (in `src/`)
- Vard Bdoyan, *Ethnography and Folk Art of the Armenians of Javakhk* (2014) — `src/arar_javaxq.pdf`, text `src/javaxq.txt`
  (legacy ArmSCII-8 text needs decoding; see notes in build history). Storytellers pp. 707–738, village plan 148–152, Papo's mill 730.
- Samvel Karapetian, *Javakhk* (2011) — `src/Javakhk_Karapetian.pdf`, `src/karap.txt`. Pokr Khanchali pp. 530–532.
- Full bibliography: `parts/b_back.html` (sources used) and `parts/h_ch2.html`, `parts/h_ch3.html` (to read next / offline).

## Open items
- Bdo's baptismal name: unconfirmed (probably Petros/Bedros). Two generations between Bdoyents Papo and the 1910s
  householders are unnamed. First record to check: Harutyun Bdoyan × Varvare marriage, 1887 — FamilySearch films
  1915055 / 1915180 (user must sign in; never enter credentials for them).
- Compiler's name for the credit line: not yet given (placeholder "the compiler"; set `COMPILER` in `config.json`).
- Armenian and Russian texts are machine-assisted translations — need a native reader's check.
- Contributions arrive by email with a `BDOYAN-CONTRIBUTION-1:` code; paste into the page's owner inbox to approve.
