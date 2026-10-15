import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mapkit import FP, C
matplotlib.rcParams["svg.fonttype"]="path"
d=[(1853,78),(1854,82),(1857,81),(1860,104),(1861,122),(1862,134),(1863,140),(1864,144),(1866,147),(1867,155),(1868,165),(1869,163),(1870,174),(1871,179),(1872,183),(1873,186),(1874,200),(1875,207),(1876,221),(1877,260),(1878,267),(1880,294),(1881,309),(1882,326),(1883,321),(1885,339),(1887,368),(1889,392),(1890,406),(1891,422),(1892,430),(1893,428),(1894,435),(1897,463),(1898,470),(1899,476),(1900,485),(1901,508),(1902,523),(1905,565),(1908,589),(1910,501),(1912,557),(1914,691),(1916,669),(1918,505),(1921,353),(1926,593)]
late=[(1926,593),(1987,801),(2014,554)]
fig=plt.figure(figsize=(6.9,2.45)); ax=fig.add_axes([0.07,0.15,0.9,0.71])
fig.patch.set_alpha(0); ax.set_facecolor("none")
for s in ["top","right","left"]: ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#B9AE9F"); ax.spines["bottom"].set_linewidth(0.8)
ax.grid(axis="y", color="#E3DACB", lw=0.6); ax.set_axisbelow(True)
x,y=zip(*d)
ax.fill_between(x,y,color=C["route"],alpha=0.07,lw=0)
ax.plot(x,y,color=C["route"],lw=2,solid_capstyle="round",solid_joinstyle="round",zorder=3)
lx,ly=zip(*late)
ax.plot(lx,ly,color=C["route"],lw=1.6,ls=(0,(2.5,2)),zorder=3)
for (a,b) in [(1853,78),(1914,691),(1921,353),(1926,593),(1987,801),(2014,554)]:
    ax.scatter([a],[b],s=26,c=C["route"],edgecolors="#FBF8F2",linewidths=1.2,zorder=4)
lab={1853:("78 people · 1853",7,-9,"left"),1914:("691 · 1914 peak",-4,10,"center"),1921:("353 · 1921",8,-4,"left"),1926:("593 · 1926",4,10,"center"),1987:("801 · 1987",0,10,"center"),2014:("554 · 2014 census",2,-13,"right")}
for a,b in [(1853,78),(1914,691),(1921,353),(1926,593),(1987,801),(2014,554)]:
    t,dx,dy,ha=lab[a]
    ax.annotate(t,(a,b),xytext=(dx,dy),textcoords="offset points",ha=ha,va="center",fontproperties=FP["sans"],fontsize=6.6,color=C["ink"])
ax.text(1923.4,300,"after war, refugees\nand famine, 1918–21",fontproperties=FP["serif_i"],fontsize=6.4,color=C["muted"],ha="left",va="top")
ax.text(1957,600,"no yearly figures\n1927–1986",fontproperties=FP["serif_i"],fontsize=6.4,color=C["muted"],ha="center",va="center")
ax.set_xlim(1848,2020); ax.set_ylim(0,900)
ax.set_yticks([0,200,400,600,800]); ax.set_xticks([1860,1880,1900,1920,1940,1960,1980,2000,2020])
for lbl in ax.get_xticklabels()+ax.get_yticklabels():
    lbl.set_fontproperties(FP["sans"]); lbl.set_fontsize(6.4); lbl.set_color(C["muted"])
ax.tick_params(length=0,pad=4)
ax.text(0.0,1.1,"PEOPLE LIVING IN POKR KHANCHALI, 1853–2014",transform=ax.transAxes,fontproperties=FP["sans_b"],fontsize=6.6,color=C["route"],ha="left")
import sys; sys.path.insert(0,"/home/claude/bdo/gen"); from i18n_fig import localize, suffix
localize(fig,"chart_population"); fig.savefig("build/chart_population"+suffix()+".svg",transparent=True); fig.savefig("build/chart_population"+suffix()+".png",dpi=200,facecolor="#FBF8F2")
