import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D
from mapkit import *

OUT = "/home/claude/bdo/build/"
import os; os.makedirs(OUT, exist_ok=True)

P = dict(
    erzurum=(41.267, 39.905), pasinler=(41.68, 39.98), horasan=(42.17, 40.04), sarikamis=(42.59, 40.33),
    kars=(43.095, 40.60), ardahan=(42.70, 41.11), akhalkalaki=(43.486, 41.405), ninotsminda=(43.591, 41.264),
    pokr=(43.548, 41.232), mets=(43.5925, 41.2467), akhaltsikhe=(42.98, 41.64), tsalka=(44.09, 41.59), gyumri=(43.85, 40.79),
    tbilisi=(44.79, 41.715), yerevan=(44.51, 40.18), batumi=(41.64, 41.64), trabzon=(39.72, 41.00), bayburt=(40.23, 40.26),
    ararat=(44.30, 39.70), van=(43.38, 38.50), oltu=(41.99, 40.54), abovyan=(44.63, 40.27), vagharshapat=(44.29, 40.16),
    vanadzor=(44.49, 40.81), krasnodar=(38.975, 45.035), sochi=(39.72, 43.585), armavir_ru=(41.12, 44.99),
    rostov=(39.72, 47.22), stavropol=(41.97, 45.04), moscow=(37.62, 55.75), spb=(30.31, 59.94), pyatigorsk=(43.06, 44.04),
    volgograd=(44.51, 48.71), sukhumi=(41.0, 43.0)
)


def save(fig, name):
    fig.savefig(OUT + name + ".svg", transparent=True)
    fig.savefig(OUT + name + ".png", dpi=170, transparent=False, facecolor=C["paper"])
    plt.close(fig)


# ---------------------------------------------------------------- MAP 1: the exodus
def map1():
    bb = (39.4, 38.75, 46.4, 42.25)
    proj = LAEA(40.6, 42.9)
    fig, ax = setup((6.9, 5.15), proj, bb)
    colors = {"Turkey": C["ott"], "Georgia": C["rus"], "Armenia": C["rus"], "Azerbaijan": C["rus"], "Russia": C["rus"], "Iran": C["per"]}
    draw_countries(ax, proj, (30, 30, 55, 50), colors, lw=0.0)
    # modern borders, very faint
    boundary(ax, proj, {frozenset(p) for p in [("Georgia", "Armenia"), ("Armenia", "Azerbaijan"), ("Georgia", "Azerbaijan"), ("Georgia", "Russia"), ("Azerbaijan", "Russia"), ("Turkey", "Iran"), ("Armenia", "Iran"), ("Azerbaijan", "Iran"), ("Azerbaijan", "Turkey")]},
             color=C["border"], lw=0.45, dashes=(3, 1.5), zorder=5)
    # approximate Russo-Ottoman frontier 1829-1878 ~ modern Turkey/Georgia + Turkey/Armenia line
    boundary(ax, proj, {frozenset(("Georgia", "Turkey")), frozenset(("Armenia", "Turkey"))}, color=C["ink"], lw=1.25, zorder=6, solid_capstyle="round")
    boundary(ax, proj, {frozenset(("Georgia", "Turkey")), frozenset(("Armenia", "Turkey"))}, color=C["ink"], lw=4.5, alpha=0.08, zorder=5)
    draw_rivers(ax, proj, bb, names={"Aras", "Kura", "Firat", "Murat", "Kelkit"}, lw=0.55)
    draw_lakes(ax, proj, bb)
    lake_blob(ax, proj, 43.23, 41.06, 15, 9, angle=-20)  # Cildir
    lake_blob(ax, proj, 43.81, 41.45, 8, 5, angle=10)    # Paravani
    lake_blob(ax, proj, 43.555, 41.255, 4.2, 2.6, angle=20)  # Khanchali (slightly exaggerated)
    graticule(ax, proj, [40, 42, 44, 46], [39, 40, 41, 42], bb)

    # Karin plain
    x, y = proj(*P["erzurum"])
    ax.add_patch(Ellipse((x + 6, y + 2), 78, 32, angle=8, fc=C["route"], alpha=0.07, ec="none", zorder=7))
    ax.add_patch(Ellipse((x + 6, y + 2), 78, 32, angle=8, fill=False, ec=C["route"], lw=0.7, ls=(0, (3, 2)), zorder=8))

    # other migrant destinations (thin gold)
    for dest in ["akhaltsikhe", "tsalka", "gyumri", "akhalkalaki"]:
        src = P["kars"] if dest in ("tsalka", "gyumri") else P["ardahan"]
        xs, ys = arc(proj, src, P[dest], bend=-0.12 if dest in ("gyumri",) else 0.12)
        xs, ys = trim(xs, ys, end_gap=5)
        ax.plot(xs, ys, color=C["gold"], lw=0.9, dashes=(4, 2), zorder=10, solid_capstyle="round")
        arrowhead(ax, xs, ys, C["gold"], size=5)
    xs, ys = arc(proj, P["oltu"], P["ardahan"], bend=0.1)
    ax.plot(xs, ys, color=C["gold"], lw=0.9, dashes=(4, 2), zorder=10)
    xs, ys = arc(proj, P["erzurum"], P["oltu"], bend=0.1)
    ax.plot(xs, ys, color=C["gold"], lw=0.9, dashes=(4, 2), zorder=10)

    # main route
    route = [P["erzurum"], P["pasinler"], P["horasan"], P["sarikamis"], P["kars"], (43.33, 40.98), P["pokr"]]
    rx, ry = smooth(proj, route, n=300)
    ax.plot(rx, ry, color=C["paper"], lw=4.2, zorder=11, solid_capstyle="round")
    ax.plot(rx, ry, color=C["route"], lw=2.1, zorder=12, solid_capstyle="round")
    arrowhead(ax, np.array(rx[:-6]), np.array(ry[:-6]), C["route"], size=9, z=13, lw=1.6)
    km = sum(haversine(route[i], route[i + 1]) for i in range(len(route) - 1))

    # places
    towns = [("kars", "Kars", 4, -3, "left"), ("ardahan", "Ardahan", -4, 2, "right"), ("akhaltsikhe", "Akhaltsikhe", 0, 7, "center"),
             ("tsalka", "Tsalka", 4, 2, "left"), ("gyumri", "Gyumri", 5, -2, "left"),
             ("tbilisi", "Tiflis (Tbilisi)", 5, 0, "left"), ("yerevan", "Erivan (Yerevan)", 5, -3, "left"), ("batumi", "Batumi", 4, -5, "left"),
             ("trabzon", "Trabzon", 0, 7, "center"), ("bayburt", "Bayburt", 0, -7, "center"), ("sarikamis", "Sarıkamış", -5, 5, "right"),
             ("horasan", "Horasan", 2, -8, "center"), ("pasinler", "Hasankale", 2, -8, "center"), ("oltu", "Oltu", 4, 3, "left")]
    for k, name, dx, dy, ha in towns:
        dot(ax, proj, *P[k], s=8)
        label(ax, proj, *P[k], name, size=6.6, dx=dx, dy=dy, ha=ha)
    dot(ax, proj, *P["akhalkalaki"], s=10)
    label(ax, proj, *P["akhalkalaki"], "Akhalkalaki", size=6.8, dx=-5, dy=4, ha="right")
    # Ararat
    x, y = proj(*P["ararat"])
    ax.scatter([x], [y], marker="^", s=26, c=C["muted"], edgecolors=C["paper"], linewidths=0.5, zorder=15)
    label(ax, proj, *P["ararat"], "Mt Ararat", font="serif_i", size=6, dx=5, dy=-4, color=C["muted"])

    # Karin
    dot(ax, proj, *P["erzurum"], s=30, fc=C["route"])
    label(ax, proj, *P["erzurum"], "KARIN", font="disp_b", size=11, dx=-2, dy=-11, ha="center", color=C["route"])
    label(ax, proj, *P["erzurum"], "(Erzurum)", font="serif_i", size=6.4, dx=-2, dy=-20, ha="center", color=C["route"])
    label(ax, proj, *P["erzurum"], "Karin plain · c. 1,900 m\nDinarigom, home of Bdo\n(family tradition)", font="serif_i", size=6, dx=-2, dy=-52, ha="center", color=C["ink"], va="center", linespacing=1.15)
    # Pokr Khanchali
    x, y = proj(*P["pokr"])
    ax.scatter([x], [y], marker="*", s=170, c=C["route"], edgecolors=C["paper"], linewidths=0.9, zorder=16)
    ax.text(x + 9, y - 3, "POKR KHANCHALI", fontproperties=FP["disp_b"], fontsize=10.5, color=C["route"], ha="left", va="center", zorder=20, path_effects=halo(2.6))
    ax.text(x + 9, y - 12.5, "Փոքր Խանչալի · Javakheti plateau · c. 1,950 m", fontproperties=FP["arm"], fontsize=5.6, color=C["ink"], ha="left", va="center", zorder=20, path_effects=halo(2))
    ax.text(x + 9, y - 21, "settled 1829–1830", fontproperties=FP["serif_i"], fontsize=6.2, color=C["ink"], ha="left", va="center", zorder=20, path_effects=halo(2))
    label(ax, proj, 43.23, 41.06, "L. Çıldır", font="serif_i", size=5.4, dx=0, dy=-8, ha="center", color="#4F6E78")
    label(ax, proj, 45.04, 40.40, "Lake Sevan", font="serif_i", size=6, ha="center", color="#4F6E78", hc=C["water"])
    label(ax, proj, 42.9, 38.82, "Lake Van", font="serif_i", size=6, ha="center", color="#4F6E78", hc=C["water"])

    # empires
    for (lo, la, t, s) in [(40.25, 39.25, "OTTOMAN  EMPIRE", 9), (45.35, 41.98, "RUSSIAN  EMPIRE", 9), (45.75, 39.2, "PERSIA", 7.5)]:
        x, y = proj(lo, la)
        ax.text(x, y, t, fontproperties=FP["disp"], fontsize=s, color=C["muted"], ha="center", va="center", zorder=9, alpha=0.9)
    x, y = proj(40.35, 41.42)
    ax.text(x, y, "Black Sea", fontproperties=FP["disp_i"], fontsize=10, color="#4F6E78", ha="center", va="center", zorder=9)

    # frontier label
    x, y = proj(42.25, 41.38)
    ax.text(x, y, "Russo-Ottoman frontier after 1829", fontproperties=FP["sans_b"], fontsize=5, color=C["ink"], rotation=-8, ha="center", va="center", zorder=21, path_effects=halo(1.8))

    # route label
    x, y = proj(43.02, 40.30)
    ax.text(x, y, f"probable route ≈ {round(km, -1):.0f} km", fontproperties=FP["serif_i"], fontsize=6.3, color=C["route"], rotation=37, ha="center", va="center", zorder=21, path_effects=halo(2))

    # legend
    lx, ly = 0.018, 0.755
    lg = ax.inset_axes([lx, ly, 0.28, 0.215]); lg.set_xlim(0, 1); lg.set_ylim(0, 1); lg.axis("off")
    lg.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.03", fc=C["paper"], ec=C["ink"], lw=0.5, alpha=0.95, transform=lg.transAxes))
    rows = [("route", "Bdoyan ancestors’ probable route"), ("gold", "Other Karin migrants, 1829–30"), ("front", "Russo-Ottoman frontier, 1829–78"), ("modern", "Modern borders")]
    for i, (k, t) in enumerate(rows):
        yy = 0.80 - i * 0.205
        if k == "route": lg.plot([0.06, 0.2], [yy, yy], color=C["route"], lw=2)
        if k == "gold": lg.plot([0.06, 0.2], [yy, yy], color=C["gold"], lw=1, dashes=(3, 1.5))
        if k == "front": lg.plot([0.06, 0.2], [yy, yy], color=C["ink"], lw=1.2)
        if k == "modern": lg.plot([0.06, 0.2], [yy, yy], color=C["border"], lw=0.6, dashes=(3, 1.5))
        lg.text(0.25, yy, t, fontproperties=FP["sans"], fontsize=5.4, va="center", color=C["ink"])

    scalebar(ax, 100, xfrac=0.03, yfrac=0.05)
    north(ax, xfrac=0.962, yfrac=0.86)
    frame(ax)
    save(fig, "map1_exodus")
    return km


# ---------------------------------------------------------------- MAP 2: dispersal
TIER = {
    "home": dict(s=150, marker="*", fc=C["route"]),
    "major": dict(s=70, marker="o", fc=C["route"]),
    "likely": dict(s=30, marker="o", fc=C["gold"]),
}


def tier_dot(ax, proj, p, tier):
    t = TIER[tier]; x, y = proj(*p)
    if tier != "home":
        ax.scatter([x], [y], s=t["s"] * 3.2, c=t["fc"], alpha=0.15, edgecolors="none", zorder=14)
    ax.scatter([x], [y], s=t["s"], c=t["fc"], marker=t["marker"], edgecolors=C["paper"], linewidths=0.8, zorder=16)


def map2():
    bb = (33.5, 39.3, 49.0, 56.6)
    proj = LAEA(47.5, 41.0)
    fig, ax = setup((6.9, 8.5), proj, bb)
    colors = {"Russia": "#EFEBDD", "Georgia": "#F6E7D3", "Armenia": "#F6E7D3"}
    draw_countries(ax, proj, (20, 30, 65, 65), colors, lw=0.4, src="ne_10m_admin_0_countries")
    draw_rivers(ax, proj, bb, names={"Volga", "Don", "Kuban", "Kura", "Aras", "Donets"}, lw=0.5)
    draw_lakes(ax, proj, bb)
    graticule(ax, proj, [32, 36, 40, 44, 48], [40, 44, 48, 52, 56], bb)

    src = P["pokr"]
    flows = [("yerevan", -0.25, 1.4), ("tbilisi", 0.3, 1.0), ("krasnodar", 0.12, 1.4), ("sochi", 0.15, 1.0), ("armavir_ru", -0.1, 1.0),
             ("rostov", 0.08, 1.0), ("stavropol", -0.12, 1.0), ("moscow", 0.1, 1.8), ("pyatigorsk", -0.15, 0.8)]
    for k, b, w in flows:
        xs, ys = arc(proj, src, P[k], bend=b)
        xs, ys = trim(xs, ys, end_gap=22 if k not in ("gyumri", "tbilisi", "yerevan") else 16, start_gap=10)
        ax.plot(xs, ys, color=C["route"], lw=w, alpha=0.55, zorder=11, solid_capstyle="round")
        arrowhead(ax, xs, ys, C["route"], size=5 + w * 1.5, z=12)
    # off-map St Petersburg
    xs, ys = arc(proj, P["moscow"], P["spb"], bend=0.05)
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim(); m = (ys < y1 - 20)
    ax.plot(xs[m], ys[m], color=C["gold"], lw=1, dashes=(3, 2), zorder=11)
    arrowhead(ax, xs[m], ys[m], C["gold"], size=6)
    ax.text(xs[m][-1] - 12, ys[m][-1] - 6, "to St Petersburg", fontproperties=FP["serif_i"], fontsize=6.2, ha="right", va="center", color=C["ink"], zorder=21, path_effects=halo(2))

    for k in ["yerevan", "moscow", "krasnodar"]:
        tier_dot(ax, proj, P[k], "major")
    for k in ["tbilisi", "sochi", "armavir_ru", "rostov", "stavropol", "pyatigorsk"]:
        tier_dot(ax, proj, P[k], "likely")
    tier_dot(ax, proj, src, "home")

    lab = [("moscow", "Moscow", 9, 0, "left", 8, "serif_b"), ("krasnodar", "Krasnodar", -9, 0, "right", 7.2, "serif_b"), ("yerevan", "Yerevan", 9, -4, "left", 7.2, "serif_b"),
           ("tbilisi", "Tbilisi", 9, 3, "left", 6.4, "serif"), ("sochi", "Sochi", -9, 0, "right", 6.4, "serif"),
           ("armavir_ru", "Armavir", -9, 6, "right", 6.4, "serif"), ("rostov", "Rostov-on-Don", 7, 0, "left", 6.4, "serif"), ("stavropol", "Stavropol", 7, 0, "left", 6.4, "serif"),
           ("pyatigorsk", "Pyatigorsk", 7, -3, "left", 6.4, "serif")]
    for k, t, dx, dy, ha, s, f in lab:
        label(ax, proj, *P[k], t, font=f, size=s, dx=dx, dy=dy, ha=ha)
    x, y = proj(*src)
    ax.text(x - 22, y - 8, "Pokr Khanchali", fontproperties=FP["disp_b"], fontsize=9.5, color=C["route"], ha="right", va="center", zorder=22, path_effects=halo(2.6))
    ax.text(x - 22, y - 50, "ancestral village", fontproperties=FP["serif_i"], fontsize=6, color=C["ink"], ha="right", va="center", zorder=22, path_effects=halo(2))

    for lo, la, t, s in [(36.5, 51.6, "RUSSIA", 13), (44.6, 42.15, "GEORGIA", 6.5), (34.0, 39.6, "TURKEY", 9), (33.6, 47.9, "UKRAINE", 8), (48.0, 40.75, "AZERBAIJAN", 6.0)]:
        x, y = proj(lo, la)
        ax.text(x, y, t, fontproperties=FP["disp"], fontsize=s, color=C["muted"], ha="center", va="center", zorder=9)
    for lo, la, t in [(35.0, 42.9, "Black Sea"), (49.6, 42.2, "Caspian\nSea"), (36.3, 46.1, "Sea of\nAzov")]:
        x, y = proj(lo, la)
        ax.text(x, y, t, fontproperties=FP["disp_i"], fontsize=9 if "Azov" not in t else 6.5, color="#4F6E78", ha="center", va="center", zorder=9, linespacing=0.9)

    lg = ax.inset_axes([0.62, 0.57, 0.36, 0.17]); lg.set_xlim(0, 1); lg.set_ylim(0, 1); lg.axis("off")
    lg.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.03", fc=C["paper"], ec=C["ink"], lw=0.5, alpha=0.96, transform=lg.transAxes))
    lg.text(0.06, 0.84, "LIKELY BDOYAN FAMILY CENTRES", fontproperties=FP["sans_b"], fontsize=5.4, color=C["ink"], va="center")
    lg.scatter([0.11], [0.62], s=80, marker="*", c=C["route"], edgecolors=C["paper"], linewidths=0.6)
    lg.text(0.2, 0.62, "Ancestral village (documented)", fontproperties=FP["sans"], fontsize=5.4, va="center")
    lg.scatter([0.11], [0.43], s=44, c=C["route"], edgecolors=C["paper"], linewidths=0.6)
    lg.text(0.2, 0.43, "Main centres of Javakhk migration", fontproperties=FP["sans"], fontsize=5.4, va="center")
    lg.scatter([0.11], [0.24], s=20, c=C["gold"], edgecolors=C["paper"], linewidths=0.6)
    lg.text(0.2, 0.24, "Other likely centres", fontproperties=FP["sans"], fontsize=5.4, va="center")
    lg.text(0.06, 0.07, "Indicative — based on Javakhk migration patterns", fontproperties=FP["serif_i"], fontsize=4.9, color=C["muted"], va="center")

    scalebar(ax, 400, xfrac=0.045, yfrac=0.905)
    north(ax, xfrac=0.955, yfrac=0.9)
    frame(ax)
    save(fig, "map2_dispersal")


# ---------------------------------------------------------------- MAP 3: heartland
def map3():
    bb = (42.75, 39.85, 45.35, 41.95)
    proj = LAEA(40.9, 44.05)
    fig, ax = setup((6.9, 5.6), proj, bb)
    colors = {"Georgia": "#F6EFE2", "Armenia": "#F3E7D4", "Turkey": "#ECE6DA", "Azerbaijan": "#ECE6DA", "Iran": "#ECE6DA"}
    draw_countries(ax, proj, (35, 35, 55, 48), colors, lw=0.0)
    admin1_lines(ax, proj, bb, {"Georgia", "Armenia"}, color="#BDB3A4", lw=0.35, dashes=(1.5, 1.5), zorder=5)
    boundary(ax, proj, {frozenset(p) for p in [("Georgia", "Armenia"), ("Georgia", "Turkey"), ("Armenia", "Turkey"), ("Georgia", "Azerbaijan"), ("Armenia", "Azerbaijan"), ("Armenia", "Iran"), ("Azerbaijan", "Turkey"), ("Azerbaijan", "Iran")]},
             color="#8C8174", lw=0.9, zorder=6)
    draw_rivers(ax, proj, bb, names={"Aras", "Kura"}, lw=0.7)
    draw_lakes(ax, proj, bb)
    for lo, la, w, h, a in [(43.23, 41.06, 15, 9, -20), (43.81, 41.45, 8, 5, 10), (43.555, 41.255, 4.4, 2.8, 20), (43.63, 41.65, 4.5, 3.5, 0), (43.73, 41.30, 2.2, 1.6, 0), (43.66, 41.38, 2, 1.4, 0)]:
        lake_blob(ax, proj, lo, la, w, h, angle=a)
    graticule(ax, proj, [43, 44, 45], [40, 41], bb)

    # Javakhk halo
    x, y = proj(43.55, 41.33)
    ax.add_patch(Ellipse((x, y), 62, 50, angle=-15, fc=C["route"], alpha=0.06, ec=C["route"], lw=0.6, ls=(0, (3, 2)), zorder=7))
    ax.text(x - 4, y + 32, "J A V A K H K", fontproperties=FP["disp_b"], fontsize=9, color=C["route"], ha="center", va="center", zorder=20, path_effects=halo(2.4, "#F6EFE2"))

    pts = dict(P)
    pts.update(dict(spitak=(44.27, 40.83), ashtarak=(44.36, 40.30), artik=(43.97, 40.62), bavra=(43.71, 41.03), gandza=(43.40, 41.20)))
    for k in ["yerevan"]: tier_dot(ax, proj, pts[k], "major")
    for k in ["gyumri", "tbilisi", "akhalkalaki", "ninotsminda", "abovyan", "vagharshapat", "tsalka"]: tier_dot(ax, proj, pts[k], "likely")
    for k in ["akhaltsikhe", "vanadzor", "ashtarak", "artik", "spitak", "bavra"]:
        dot(ax, proj, *pts[k], s=7)
    tier_dot(ax, proj, pts["pokr"], "home")

    L = [("yerevan", "YEREVAN", 9, 0, "left", 8, "serif_b"), ("gyumri", "Gyumri", -8, 3, "right", 7, "serif_b"), ("tbilisi", "Tbilisi", -8, 0, "right", 7, "serif_b"),
         ("akhalkalaki", "Akhalkalaki", -7, 4, "right", 6.6, "serif_b"), ("ninotsminda", "Ninotsminda", 7, 3, "left", 6.6, "serif_b"), ("abovyan", "Abovyan", 7, 2, "left", 6.2, "serif"),
         ("vagharshapat", "Vagharshapat\n(Etchmiadzin)", -7, -2, "right", 6.0, "serif"), ("tsalka", "Tsalka", 7, 0, "left", 6.4, "serif"),
         ("akhaltsikhe", "Akhaltsikhe", 5, 4, "left", 6, "serif"), ("vanadzor", "Vanadzor", 5, 0, "left", 6, "serif"),
         ("ashtarak", "Ashtarak", -5, 3, "right", 5.6, "serif"), ("artik", "Artik", 5, 0, "left", 5.6, "serif"), ("spitak", "Spitak", 5, 0, "left", 5.6, "serif"),
         ("bavra", "Bavra", 5, 0, "left", 5.6, "serif"), ("kars", "Kars", 5, 0, "left", 6, "serif")]
    dot(ax, proj, *pts["kars"], s=7)
    for k, t, dx, dy, ha, s, f in L:
        label(ax, proj, *pts[k], t, font=f, size=s, dx=dx, dy=dy, ha=ha, hc="#F6EFE2")
    x, y = proj(*pts["pokr"])
    ax.text(x - 9, y - 4, "POKR KHANCHALI", fontproperties=FP["disp_b"], fontsize=9.5, color=C["route"], ha="right", va="center", zorder=22, path_effects=halo(2.6, "#F6EFE2"))
    ax.text(x - 9, y - 12, "St Hakob church · since 1829–30", fontproperties=FP["serif_i"], fontsize=5.6, color=C["ink"], ha="right", va="center", zorder=22, path_effects=halo(2, "#F6EFE2"))
    label(ax, proj, 43.81, 41.45, "L. Paravani", font="serif_i", size=5.4, dx=6, dy=0, color="#4F6E78", hc="#F6EFE2")
    label(ax, proj, 43.555, 41.255, "L. Khanchali", font="serif_i", size=5.2, dx=5, dy=-4, color="#4F6E78", hc="#F6EFE2")
    label(ax, proj, 43.23, 41.06, "L. Çıldır", font="serif_i", size=5.4, dx=0, dy=-8, ha="center", color="#4F6E78", hc="#ECE6DA")
    label(ax, proj, 45.10, 40.45, "Lake\nSevan", font="serif_i", size=6.2, ha="center", color="#4F6E78", hc=C["water"])
    for lo, la, t, s in [(44.75, 41.92, "GEORGIA", 9), (44.95, 40.05, "ARMENIA", 9), (43.05, 40.2, "TURKEY", 8.5), (43.9, 40.38, "SHIRAK", 6), (44.15, 41.30, "KVEMO KARTLI", 5.5)]:
        x, y = proj(lo, la)
        ax.text(x, y, t, fontproperties=FP["disp"], fontsize=s, color=C["muted"], ha="center", va="center", zorder=9, linespacing=0.9)
    # Ararat
    x, y = proj(*P["ararat"])

    lg = ax.inset_axes([0.715, 0.445, 0.27, 0.15]); lg.set_xlim(0, 1); lg.set_ylim(0, 1); lg.axis("off")
    lg.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.03", fc=C["paper"], ec=C["ink"], lw=0.5, alpha=0.96, transform=lg.transAxes))
    lg.scatter([0.1], [0.78], s=80, marker="*", c=C["route"], edgecolors=C["paper"], linewidths=0.6); lg.text(0.19, 0.78, "Ancestral village", fontproperties=FP["sans"], fontsize=5.4, va="center")
    lg.scatter([0.1], [0.56], s=44, c=C["route"], edgecolors=C["paper"], linewidths=0.6); lg.text(0.19, 0.56, "Main centre", fontproperties=FP["sans"], fontsize=5.4, va="center")
    lg.scatter([0.1], [0.34], s=20, c=C["gold"], edgecolors=C["paper"], linewidths=0.6); lg.text(0.19, 0.34, "Likely centre", fontproperties=FP["sans"], fontsize=5.4, va="center")
    lg.text(0.06, 0.12, "Indicative, not a census", fontproperties=FP["serif_i"], fontsize=5, color=C["muted"], va="center")
    scalebar(ax, 40, xfrac=0.03, yfrac=0.05)
    north(ax, xfrac=0.955, yfrac=0.88)
    frame(ax)
    save(fig, "map3_heartland")


# ---------------------------------------------------------------- MAP 4: the wider world
def map4():
    bb = (-128, 22, 62, 66)
    proj = Equirect(45)
    fig, ax = setup((6.9, 2.55), proj, bb)
    draw_countries(ax, proj, (-180, -60, 180, 85), {}, default="#EFE8DA", lw=0.25, src="ne_50m_admin_0_countries", ec="#C7BDAE")
    src = (43.55, 41.23)
    dest = [((-118.25, 34.15), "Los Angeles · Glendale", 0.18, 1.3, 7, 2, "left"), ((2.35, 48.86), "France", 0.25, 0.9, 0, -9, "center"),
            ((9.0, 51.0), "Germany", 0.25, 0.9, 6, 6, "left"), ((4.35, 50.85), "Belgium", 0.3, 0.7, -7, 7, "right"), ((37.62, 55.75), "Moscow", 0.25, 1.1, 0, 8, "center")]
    for p, t, b, w, dx, dy, ha in dest:
        xs, ys = arc(proj, src, p, bend=b)
        ax.plot(xs, ys, color=C["route"], lw=w, alpha=0.6, zorder=11)
        arrowhead(ax, xs, ys, C["route"], size=5, z=12)
        tier_dot(ax, proj, p, "likely")
        x, y = proj(*p)
        ax.text(x + dx * 25, y + dy * 25, t, fontproperties=FP["serif"], fontsize=6.4, ha=ha, va="center", color=C["ink"], zorder=21, path_effects=halo(2, "#EFE8DA"))
    tier_dot(ax, proj, src, "home")
    x, y = proj(*src)
    ax.text(x + 160, y - 280, "Javakhk", fontproperties=FP["disp_b"], fontsize=8, color=C["route"], ha="left", zorder=21, path_effects=halo(2, "#EFE8DA"))
    for lo, la, t in [(-40, 38, "Atlantic Ocean")]:
        x, y = proj(lo, la); ax.text(x, y, t, fontproperties=FP["disp_i"], fontsize=9, color="#4F6E78", ha="center")
    frame(ax)
    save(fig, "map4_world")


# ---------------------------------------------------------------- COVER ART
def cover():
    bb = (39.0, 38.6, 46.6, 42.6)
    proj = LAEA(40.6, 42.9)
    fig, ax = setup((7.0, 5.6), proj, bb)
    ax.set_facecolor("none")
    draw_countries(ax, proj, (30, 30, 55, 50), {}, default="none", lw=0.5, ec="#C9A86A")
    for line in [("Georgia", "Turkey"), ("Armenia", "Turkey")]:
        pass
    route = [P["erzurum"], P["pasinler"], P["horasan"], P["sarikamis"], P["kars"], (43.33, 40.98), P["pokr"]]
    rx, ry = smooth(proj, route, n=300)
    for w, a in [(9, 0.06), (5, 0.12), (2.2, 1)]:
        ax.plot(rx, ry, color="#E8C887", lw=w, alpha=a, solid_capstyle="round", zorder=5)
    for k in ["erzurum", "pokr"]:
        x, y = proj(*P[k]); ax.scatter([x], [y], s=40, c="#E8C887", edgecolors="none", zorder=6)
        ax.scatter([x], [y], s=220, facecolors="none", edgecolors="#E8C887", linewidths=0.6, alpha=0.6, zorder=6)
    x, y = proj(*P["erzurum"]); ax.text(x, y - 18, "KARIN · 1829", fontproperties=FP["sans_b"], fontsize=6.5, color="#E8C887", ha="center", va="top")
    x, y = proj(*P["pokr"]); ax.text(x + 14, y, "KHANCHALI · 1830", fontproperties=FP["sans_b"], fontsize=6.5, color="#E8C887", ha="left", va="center")
    fig.patch.set_alpha(0)
    fig.savefig(OUT + "cover_art.svg", transparent=True)
    plt.close(fig)


if __name__ == "__main__":
    km = map1(); print("route km", km)
    map2(); map3(); map4(); cover()
    print("done")
