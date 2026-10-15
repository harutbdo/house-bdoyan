"""Small vector-map toolkit (no GIS deps): LAEA projection, Natural Earth drawing, labels."""
import json, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Ellipse, FancyBboxPatch
from matplotlib import patheffects as pe
from matplotlib.font_manager import FontProperties
from scipy.interpolate import splprep, splev

matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["axes.linewidth"] = 0

F = "/home/claude/bdo/fonts/"
FP = {
    "serif": FontProperties(fname=F + "SS4-Regular.ttf"),
    "serif_b": FontProperties(fname=F + "SS4-SemiBold.ttf"),
    "serif_i": FontProperties(fname=F + "SS4-Italic.ttf"),
    "sans": FontProperties(fname=F + "Inter-Regular.ttf"),
    "sans_b": FontProperties(fname=F + "Inter-SemiBold.ttf"),
    "disp": FontProperties(fname=F + "Corm-SemiBold.ttf"),
    "disp_b": FontProperties(fname=F + "Corm-Bold.ttf"),
    "disp_i": FontProperties(fname=F + "Corm-Italic.ttf"),
    "arm": FontProperties(fname=F + "NSArm-Regular.ttf"),
    "arm_b": FontProperties(fname=F + "NSArm-SemiBold.ttf"),
}

C = dict(
    sea="#D3DFE0", land="#F4EEE2", ott="#EEDCCB", rus="#E4E6D4", per="#EDE5D3",
    border="#A99E90", water="#B9CDD3", waterline="#8FAEB8", river="#A3BFC8",
    route="#8E2C2C", gold="#A9813F", ink="#2A2420", muted="#6E645A", paper="#FBF8F2",
)

D = "/home/claude/bdo/data/"
_cache = {}


def load(name):
    if name not in _cache:
        _cache[name] = json.load(open(D + name + ".geojson"))
    return _cache[name]


class LAEA:
    def __init__(self, lat0, lon0, R=6371.0):
        self.p0, self.l0, self.R = math.radians(lat0), math.radians(lon0), R

    def __call__(self, lon, lat):
        lon = np.radians(np.asarray(lon, float)); lat = np.radians(np.asarray(lat, float))
        dl = lon - self.l0
        k = np.sqrt(2 / (1 + math.sin(self.p0) * np.sin(lat) + math.cos(self.p0) * np.cos(lat) * np.cos(dl)))
        x = self.R * k * np.cos(lat) * np.sin(dl)
        y = self.R * k * (math.cos(self.p0) * np.sin(lat) - math.sin(self.p0) * np.cos(lat) * np.cos(dl))
        return x, y


class Equirect:
    def __init__(self, lat_ts=45):
        self.c = math.cos(math.radians(lat_ts))

    def __call__(self, lon, lat):
        return np.asarray(lon, float) * self.c * 111.32, np.asarray(lat, float) * 111.32


def _rings(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return [c]
    if t == "MultiPolygon":
        return c
    return []


def _lines(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "LineString":
        return [c]
    if t == "MultiLineString":
        return c
    return []


def poly_path(proj, poly):
    verts, codes = [], []
    for ring in poly:
        a = np.asarray(ring)
        x, y = proj(a[:, 0], a[:, 1])
        pts = np.column_stack([x, y])
        verts.extend(pts.tolist()); codes.extend([Path.MOVETO] + [Path.LINETO] * (len(pts) - 2) + [Path.CLOSEPOLY])
    return Path(verts, codes)


def draw_countries(ax, proj, bbox_ll, colors=None, default=None, lw=0.45, src="ne_10m_admin_0_countries", ec=None, z=1):
    colors = colors or {}
    lo0, la0, lo1, la1 = bbox_ll
    for f in load(src)["features"]:
        name = f["properties"]["ADMIN"]
        for poly in _rings(f["geometry"]):
            a = np.asarray(poly[0])
            if a[:, 0].max() < lo0 or a[:, 0].min() > lo1 or a[:, 1].max() < la0 or a[:, 1].min() > la1:
                continue
            p = poly_path(proj, poly)
            ax.add_patch(PathPatch(p, fc=colors.get(name, default or C["land"]), ec=ec or C["border"], lw=lw, zorder=z, joinstyle="round"))


def draw_lakes(ax, proj, bbox_ll, z=2):
    lo0, la0, lo1, la1 = bbox_ll
    for f in load("ne_10m_lakes")["features"]:
        for poly in _rings(f["geometry"]):
            a = np.asarray(poly[0])
            if a[:, 0].max() < lo0 or a[:, 0].min() > lo1 or a[:, 1].max() < la0 or a[:, 1].min() > la1:
                continue
            ax.add_patch(PathPatch(poly_path(proj, poly), fc=C["water"], ec=C["waterline"], lw=0.4, zorder=z))


def draw_rivers(ax, proj, bbox_ll, names=None, lw=0.6, z=2):
    lo0, la0, lo1, la1 = bbox_ll
    for f in load("ne_10m_rivers_lake_centerlines")["features"]:
        nm = f["properties"].get("name") or ""
        if names is not None and nm not in names:
            continue
        for line in _lines(f["geometry"]):
            a = np.asarray(line)
            if a[:, 0].max() < lo0 or a[:, 0].min() > lo1 or a[:, 1].max() < la0 or a[:, 1].min() > la1:
                continue
            x, y = proj(a[:, 0], a[:, 1])
            ax.plot(x, y, color=C["river"], lw=lw, zorder=z, solid_capstyle="round")


def boundary(ax, proj, pairs, **kw):
    for f in load("ne_10m_admin_0_boundary_lines_land")["features"]:
        p = f["properties"]
        if frozenset((p["ADM0_LEFT"], p["ADM0_RIGHT"])) in pairs:
            for line in _lines(f["geometry"]):
                a = np.asarray(line); x, y = proj(a[:, 0], a[:, 1])
                ax.plot(x, y, **kw)


def admin1_lines(ax, proj, bbox_ll, countries, **kw):
    lo0, la0, lo1, la1 = bbox_ll
    for f in load("ne_10m_admin_1_states_provinces_lines")["features"]:
        if f["properties"].get("ADM0_NAME") not in countries:
            continue
        for line in _lines(f["geometry"]):
            a = np.asarray(line)
            if a[:, 0].max() < lo0 or a[:, 0].min() > lo1 or a[:, 1].max() < la0 or a[:, 1].min() > la1:
                continue
            x, y = proj(a[:, 0], a[:, 1]); ax.plot(x, y, **kw)


def lake_blob(ax, proj, lon, lat, w_km, h_km, angle=0, z=3):
    x, y = proj(lon, lat)
    ax.add_patch(Ellipse((x, y), w_km, h_km, angle=angle, fc=C["water"], ec=C["waterline"], lw=0.4, zorder=z))


def halo(w=2.4, c=None):
    return [pe.withStroke(linewidth=w, foreground=c or C["land"])]


def label(ax, proj, lon, lat, text, font="serif", size=7, color=None, dx=0, dy=0, ha="left", va="center", h=2.2, hc=None, z=20, **kw):
    x, y = proj(lon, lat)
    return ax.text(x + dx, y + dy, text, fontproperties=FP[font], fontsize=size, color=color or C["ink"], ha=ha, va=va,
                   zorder=z, path_effects=halo(h, hc) if h else None, **kw)


def dot(ax, proj, lon, lat, s=9, fc=None, ec=None, lw=0.6, marker="o", z=15):
    x, y = proj(lon, lat)
    ax.scatter([x], [y], s=s, c=fc or C["ink"], edgecolors=ec or C["paper"], linewidths=lw, marker=marker, zorder=z)


def smooth(proj, pts, n=200, k=3):
    a = np.asarray(pts)
    x, y = proj(a[:, 0], a[:, 1])
    tck, _ = splprep([x, y], s=0, k=min(k, len(a) - 1))
    u = np.linspace(0, 1, n)
    return splev(u, tck)


def arc(proj, p0, p1, bend=0.18, n=80):
    x0, y0 = proj(*p0); x1, y1 = proj(*p1)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    cx, cy = mx - dy * bend, my + dx * bend
    t = np.linspace(0, 1, n)
    x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1
    y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1
    return x, y


def arrowhead(ax, x, y, color, size=6, z=12, lw=0):
    ax.annotate("", xy=(x[-1], y[-1]), xytext=(x[-4], y[-4]),
                arrowprops=dict(arrowstyle=f"-|>,head_length={size/10},head_width={size/20}", color=color, lw=lw or 0.8, shrinkA=0, shrinkB=0), zorder=z)


def haversine(p, q):
    lo1, la1, lo2, la2 = map(math.radians, (*p, *q))
    a = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(a))


def setup(figsize, proj, bbox_ll, pad=0):
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])
    lo0, la0, lo1, la1 = bbox_ll
    gl = np.linspace(lo0, lo1, 60); gt = np.linspace(la0, la1, 60)
    xs, ys = [], []
    for lo, la in [(gl, np.full(60, la0)), (gl, np.full(60, la1)), (np.full(60, lo0), gt), (np.full(60, lo1), gt)]:
        x, y = proj(lo, la); xs += list(x); ys += list(y)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    W, H = figsize
    # fit aspect: expand the shorter side
    if (x1 - x0) / (y1 - y0) > W / H:
        c = (y0 + y1) / 2; h = (x1 - x0) * H / W; y0, y1 = c - h / 2, c + h / 2
    else:
        c = (x0 + x1) / 2; w = (y1 - y0) * W / H; x0, x1 = c - w / 2, c + w / 2
    ax.set_xlim(x0 + pad, x1 - pad); ax.set_ylim(y0 + pad, y1 - pad)
    ax.set_facecolor(C["sea"]); ax.set_xticks([]); ax.set_yticks([])
    fig.patch.set_alpha(0)
    return fig, ax


def graticule(ax, proj, lons, lats, bbox_ll, color="#9C9384", alpha=0.35, labels=True, size=5.2):
    lo0, la0, lo1, la1 = bbox_ll
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    for lo in lons:
        la = np.linspace(la0 - 5, la1 + 5, 200); x, y = proj(np.full_like(la, lo), la)
        ax.plot(x, y, color=color, lw=0.3, alpha=alpha, zorder=4, dashes=(2, 2))
        if labels:
            m = (y > y0) & (y < y1)
            if m.any():
                i = np.argmin(y[m]); xx = x[m][i]
                if x0 < xx < x1:
                    ax.text(xx, y0 + (y1 - y0) * 0.012, f"{lo}°E", fontproperties=FP["sans"], fontsize=size, color=C["muted"], ha="center", va="bottom", zorder=30, path_effects=halo(1.6, C["sea"]))
    for la in lats:
        lo = np.linspace(lo0 - 8, lo1 + 8, 200); x, y = proj(lo, np.full_like(lo, la))
        ax.plot(x, y, color=color, lw=0.3, alpha=alpha, zorder=4, dashes=(2, 2))
        if labels:
            m = (x > x0) & (x < x1)
            if m.any():
                i = np.argmin(x[m]); yy = y[m][i]
                if y0 < yy < y1:
                    ax.text(x0 + (x1 - x0) * 0.008, yy, f"{la}°N", fontproperties=FP["sans"], fontsize=size, color=C["muted"], ha="left", va="bottom", zorder=30, path_effects=halo(1.6, C["sea"]))


def scalebar(ax, km, xfrac=0.04, yfrac=0.05, segs=4, size=5.5):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    x = x0 + (x1 - x0) * xfrac; y = y0 + (y1 - y0) * yfrac
    step = km / segs; h = (y1 - y0) * 0.008
    for i in range(segs):
        ax.add_patch(plt.Rectangle((x + i * step, y), step, h, fc=C["ink"] if i % 2 == 0 else C["paper"], ec=C["ink"], lw=0.4, zorder=40))
    for i in (0, segs):
        ax.text(x + i * step, y + h * 2.2, f"{int(i*step)}" + (" km" if i == segs else ""), fontproperties=FP["sans"], fontsize=size, color=C["ink"], ha="center", va="bottom", zorder=40, path_effects=halo(1.6, C["paper"]))


def north(ax, xfrac=0.955, yfrac=0.88, size=7):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    x = x0 + (x1 - x0) * xfrac; y = y0 + (y1 - y0) * yfrac; h = (y1 - y0) * 0.06; w = h * 0.32
    ax.add_patch(plt.Polygon([(x, y + h / 2), (x - w, y - h / 2), (x, y - h / 4)], fc=C["ink"], ec=C["ink"], lw=0.4, zorder=40))
    ax.add_patch(plt.Polygon([(x, y + h / 2), (x + w, y - h / 2), (x, y - h / 4)], fc=C["paper"], ec=C["ink"], lw=0.4, zorder=40))
    ax.text(x, y + h / 2 + h * 0.12, "N", fontproperties=FP["disp_b"], fontsize=size + 2, ha="center", va="bottom", color=C["ink"], zorder=40)


def frame(ax, color=None):
    color = color or C["ink"]
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False, ec=color, lw=1.4, zorder=100, clip_on=False))
    ax.add_patch(plt.Rectangle((0.006, 0.008), 0.988, 0.984, transform=ax.transAxes, fill=False, ec=color, lw=0.35, zorder=100, clip_on=False))


def trim(xs, ys, end_gap=0.0, start_gap=0.0):
    xs = np.asarray(xs); ys = np.asarray(ys)
    seg = np.hypot(np.diff(xs), np.diff(ys)); cum = np.concatenate([[0], np.cumsum(seg)])
    m = (cum >= start_gap) & (cum <= cum[-1] - end_gap)
    return xs[m], ys[m]
