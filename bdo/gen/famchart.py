ACC="#8E2C2C"; GOLD="#A9813F"; INK="#2A2420"; MUT="#6F655B"; RULE="#DCD2C2"; TINT="#F4EDE1"; PAPER="#FBF8F2"
out=[]
def esc(s): return s.replace("&","&amp;")
def t(x,y,s,size=11,fam="Inter",fill=INK,anchor="middle",weight=400,style="normal",ls=0,halo=False):
    h=f' stroke="{PAPER}" stroke-width="4" paint-order="stroke" stroke-linejoin="round"' if halo else ''
    out.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}" letter-spacing="{ls}"{h}>{esc(s)}</text>')
def box(x,y,w,h,fill="#fff",stroke=RULE,sw=1.2,rx=6):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def line(d,dash=False,col=GOLD,w=1.5):
    da=' stroke-dasharray="4 3"' if dash else ''
    out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}"{da}/>')
def mark(cx,cy,k,r=4.2,col=ACC):
    if k=='c': out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}"/>')
    elif k=='t': out.append(f'<circle cx="{cx}" cy="{cy}" r="{r-0.6}" fill="none" stroke="{col}" stroke-width="1.3"/>')
    else:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r-0.6}" fill="none" stroke="{col}" stroke-width="1.3"/>')
        out.append(f'<path d="M{cx} {cy-r+0.6} A{r-0.6} {r-0.6} 0 0 0 {cx} {cy+r-0.6} Z" fill="{col}"/>')
def person(x,y,w,h,name,lines,mk='c',hl=False,root=False,nsize=15):
    if root: box(x,y,w,h,fill=ACC,stroke=ACC)
    else: box(x,y,w,h,fill=TINT if hl else "#fff",stroke=ACC if hl else RULE,sw=1.6 if hl else 1.2)
    cx=x+w/2
    t(cx,y+19,name,size=nsize,fam="Cormorant Garamond",fill="#F7E7C6" if root else INK,weight=700)
    # mark after name: estimate name width ~ 0.48*size per char
    mark(x+w-9,y+h-9,mk,r=3.8,col="#F7E7C6" if root else ACC)
    for i,l in enumerate(lines):
        t(cx,y+34+i*12.5,l,size=9.6,fill="#EBCB95" if root else MUT)
def note(x,y,s,anchor="start",mk=None):
    t(x,y,s,size=9.6,fill=MUT,style="italic",fam="Source Serif 4",anchor=anchor,halo=True)
W=680
t(0,14,"THE BDOYANS KNOWN SO FAR",size=10,fill=ACC,anchor="start",weight=650,ls=2)
t(0,40,"Every Bdoyan named in the sources, and how they connect",size=21,fam="Cormorant Garamond",anchor="start",weight=600)
out.append(f'<line x1="0" y1="52" x2="{W}" y2="52" stroke="{RULE}" stroke-width="1"/>')
t(0,74,"POKR KHANCHALI",size=9.5,fill=ACC,anchor="start",weight=650,ls=1.6)
t(492,74,"AKHALKALAKI",size=9.5,fill=ACC,anchor="start",weight=650,ls=1.6)
# connectors to right column first (so boxes sit on top)
line("M320 102 C 400 102, 430 100, 492 100",dash=True); note(406,94,"kin",anchor="middle")
line("M320 128 C 430 150, 430 280, 492 296",dash=True); note(436,214,"same root?",anchor="middle")
# Bdo and Papo
person(150,84,170,58,"Bdo (Bedros)",["c. 1740–1780 · Dinarigom, Karin","the founder"],mk='t',root=True)
line("M235 142 V176",dash=True); note(243,163,"son or grandson")
person(150,176,170,52,"Bdoyents Papo",["patriarch of the village’s Bdoyans","built the first mill, 1830s"],mk='c')
line("M235 228 V262",dash=True); note(243,249,"two generations not yet known")
hx=[0,91,176,279,394]; hw=[88,82,100,112,76]; cw=[x+w/2 for x,w in zip(hx,hw)]
line(f"M{cw[0]} 262 H{cw[-1]} "+" ".join(f"M{c} 262 V272" for c in cw))
names=[("Harutyun",["house 28","m. 1887 Varvare","b. 1870, Nardivan"],True),("Grigor",["house 29"],False),("Anton, Davit",["house 30"],False),("Mesrop",["house 31 · † 1918","m. Anush (1880–1953)","brother Khnko † 1919"],False),("Zakar",["house 32"],False)]
for (n,l,hl),x,w in zip(names,hx,hw):
    person(x,272,w,80,n,l,mk='c',hl=hl,nsize=14)
line("M44 352 V388"); line("M132 352 V388",dash=True); line("M335 352 V388")
note(235,371,"the five Bdoyan houses of the 1910s — probably Papo’s great-grandsons",anchor="middle")
person(0,388,88,64,"Vard",["1910–1986","ethnographer"],mk='c',hl=True)
note(2,466,"mother: Varvare (probable)",anchor="start")
person(91,388,82,64,"Khachatur",["b. 1888","son of Grigor"],mk='p',nsize=13)
person(279,388,112,64,"Grigor, Zavik",["sons of Mesrop","† 1941–1942"],mk='c',nsize=14)
box(0,472,470,28,fill="#fff",stroke=RULE)
t(228,490,"Also of Pokr Khanchali: Balasan Bdoyan (b. 1930) — place in the tree not yet known",size=9.8,fill=INK)
mark(458,486.5,'c')
# right column
person(492,84,188,44,"Tadevos",["shoemaker, Akhalkalaki"],mk='c')
line("M586 128 V146")
person(492,146,188,70,"Gevorg",["b. 1890 · storyteller","Vard’s “relative”","lived in Kharkiv, Yerevan, Chaltyr"],mk='c')
note(586,232,"also M. Bdoyan, photographer",anchor="middle")
t(492,262,"ABUL · FROM UMUDUM",size=9.5,fill=ACC,anchor="start",weight=650,ls=1.6)
person(492,272,188,46,"Hakob",["came to Abul in 1830"],mk='c')
line("M586 318 V338",dash=True); note(578,332,"a generation not known",anchor="end")
person(492,338,188,46,"Smbat",["1887–1963 · singer, church clerk"],mk='c')
person(492,394,188,58,"Ruben & Sirun",["both b. 1908 · singers","Ruben’s aunt: Horomsima"],mk='c')
note(586,468,"also Stepan, who kept the family’s songs",anchor="middle")
# legend
out.append(f'<line x1="0" y1="516" x2="{W}" y2="516" stroke="{RULE}" stroke-width="1"/>')
mark(5,532,'c'); t(14,536,"confirmed by records",size=9.8,anchor="start")
mark(132,532,'p'); t(141,536,"probable",size=9.8,anchor="start")
mark(203,532,'t'); t(212,536,"family tradition or estimate",size=9.8,anchor="start")
line("M392 532 H420"); t(425,536,"documented link",size=9.8,anchor="start")
line("M528 532 H556",dash=True); t(561,536,"not yet documented",size=9.8,anchor="start")
svg=f'<svg viewBox="0 0 {W} 546" xmlns="http://www.w3.org/2000/svg">'+"".join(out)+'</svg>'
open('/home/claude/bdo/parts/svg_famchart.svg','w').write(svg)
