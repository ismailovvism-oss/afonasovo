import pickle
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.font_manager import FontProperties
FP=FontProperties(family='DejaVu Sans')
p=pickle.load(open("plan.pkl","rb")); u=pickle.load(open("utils.pkl","rb"))
site=p["site"]; roads=p["roads"]; parcels=p["parcels"]; socials=p["socials"]
fig=plt.figure(figsize=(16.5,11.7),dpi=100); fig.patch.set_facecolor('white')
fig.add_artist(Rectangle((0.012,0.012),0.976,0.976,fill=False,ec='black',lw=1.5,transform=fig.transFigure))
axp=fig.add_axes([0.03,0.06,0.63,0.88]); axp.set_aspect('equal'); axp.axis('off')
def pp(ax,g,**kw):
    if g.is_empty: return
    for gg in ([g] if g.geom_type=='Polygon' else list(g.geoms)):
        xs,ys=gg.exterior.xy; ax.fill(xs,ys,**kw)
def pl(ax,g,**kw):
    if g.is_empty: return
    for gg in ([g] if g.geom_type=='LineString' else list(getattr(g,'geoms',[]))):
        xs,ys=gg.xy; ax.plot(xs,ys,**kw)
# faint base
pp(axp,roads,fc='#eeeeee',ec='none',zorder=1)
for c,h,t in parcels: pp(axp,c,fc='#f4faee',ec='#cfe0bf',lw=0.3,zorder=2)
for nm,k,rect,col in socials: pp(axp,rect,fc='#eaeaea',ec='#bbb',lw=0.5,zorder=2)
# networks
for name,(off,col,ls) in u["NETS"].items():
    pl(axp,u["nets"][name],color=col,lw=1.1,ls=ls,zorder=4)
# nodes
for nm,k,pt,col in u["nodes"]:
    axp.plot(pt.x,pt.y,marker='s',ms=9,mfc=col,mec='k',mew=0.6,zorder=6)
    axp.annotate(k,(pt.x,pt.y),textcoords='offset points',xytext=(7,4),fontsize=7,fontproperties=FP,weight='bold')
pp(axp,site,fc='none',ec='red',lw=1.6,zorder=7)
axp.set_title("Сводный план инженерных сетей.  М 1:2000",fontsize=11,fontproperties=FP)
# right column
def txt(x,y,s,**kw): fig.text(x,y,s,fontproperties=FP,**kw)
txt(0.67,0.955,"Пилотный проект коттеджного посёлка",fontsize=13,weight='bold')
txt(0.67,0.935,"Сводный план инженерных сетей · СК МСК-16",fontsize=9)
txt(0.67,0.895,"Условные обозначения",fontsize=10,weight='bold')
handles=[]; labels=[]
for name,(off,col,ls) in u["NETS"].items():
    handles.append(Line2D([0],[0],color=col,lw=2,ls=ls)); labels.append(name)
axl=fig.add_axes([0.665,0.66,0.32,0.22]); axl.axis('off')
axl.legend(handles,labels,loc='upper left',frameon=False,fontsize=8,prop=FP,handlelength=3)
# node legend
ny=0.66; txt(0.67,ny,"Сооружения:",fontsize=9,weight='bold')
axn=fig.add_axes([0.665,0.50,0.32,0.15]); axn.axis('off'); axn.set_xlim(0,1); axn.set_ylim(0,3)
for i,(nm,k,pt,col) in enumerate(u["nodes"]):
    yy=2-i+0.2
    axn.plot(0.05,yy+0.3,marker='s',ms=10,mfc=col,mec='k')
    axn.text(0.12,yy+0.3,f"{k} — {nm}",va='center',fontsize=7.5,fontproperties=FP)
txt(0.67,0.47,"Сети размещены вдоль проездов в габаритах красных линий;\nраскладка по разрезам — см. лист «Планы дорог. Разрезы».",fontsize=7.5,color='#444')
# stamp
axs=fig.add_axes([0.67,0.05,0.31,0.14]); axs.axis('off'); axs.add_patch(Rectangle((0,0),1,1,fill=False,ec='k',lw=1))
axs.text(0.03,0.78,"Пилотный проект коттеджного посёлка",fontsize=7.5,fontproperties=FP)
axs.text(0.03,0.60,"в н.п. Б. Афанасово Нижнекамского района",fontsize=7.5,fontproperties=FP)
axs.text(0.03,0.36,"Сводный план инженерных сетей",fontsize=8,weight='bold',fontproperties=FP)
axs.text(0.03,0.06,"Стадия: ПП   Лист 4   Формат A3",fontsize=6.5,fontproperties=FP)
fig.savefig("Сети_лист.pdf",facecolor='white'); fig.savefig("Сети_лист.png",dpi=110,facecolor='white')
print("saved Сети_лист.pdf/.png")
