import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys; sys.path.insert(0,'/home/claude/bdo')
from mapkit import FP, C
matplotlib.rcParams["svg.fonttype"]="path"
data=[("Georgia",559),("Armenia",499),("Russia",374),("Elsewhere",5)]
fig=plt.figure(figsize=(5.85,2.05)); ax=fig.add_axes([0.16,0.08,0.74,0.72])
fig.patch.set_alpha(0); ax.set_facecolor("none")
ys=list(range(len(data)))[::-1]
for y,(n,v) in zip(ys,data):
    ax.barh(y,v,height=0.56,color=C["route"] if n!="Elsewhere" else C["gold"],edgecolor="none")
    ax.text(v+8,y,f"{v:,}",fontproperties=FP["sans_b"],fontsize=8.6,color=C["ink"],va="center",ha="left")
    ax.text(-10,y,n,fontproperties=FP["serif_b"],fontsize=9,color=C["ink"],va="center",ha="right")
ax.text(5+60,ys[-1],"USA 2 · Belgium 1 · Bulgaria 1 · Abkhazia 1",fontproperties=FP["serif_i"],fontsize=7.6,color=C["muted"],va="center",ha="left")
for s in ["top","right","left","bottom"]: ax.spines[s].set_visible(False)
ax.set_xticks([]); ax.set_yticks([]); ax.set_xlim(0,640); ax.set_ylim(-0.6,len(data)-0.4)
fig.text(0.02,0.93,"BDOYANS BY COUNTRY TODAY · ESTIMATE, ABOUT 1,440 PEOPLE",fontproperties=FP["sans_b"],fontsize=7.6,color=C["route"],ha="left")
import sys; sys.path.insert(0,"/home/claude/bdo/gen"); from i18n_fig import localize, suffix
localize(fig,"chart_countries"); fig.savefig("build/chart_countries"+suffix()+".svg",transparent=True); fig.savefig("build/chart_countries"+suffix()+".png",dpi=200,facecolor="#FBF8F2")
