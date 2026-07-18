import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MPoly
from matplotlib.font_manager import FontProperties
import numpy as np
FP=FontProperties(family='DejaVu Sans')

def dim(ax,x0,x1,y,txt,tick=0.25):
    ax.annotate("",(x1,y),(x0,y),arrowprops=dict(arrowstyle='<->',lw=0.8))
    for x in (x0,x1): ax.plot([x,x],[y-tick,y+tick],'k-',lw=0.8)
    ax.text((x0+x1)/2,y+0.12,txt,ha='center',va='bottom',fontsize=6.5,fontproperties=FP)

def section(ax,title,total,carriage,util_left,util_right,lamp=True):
    ax.set_title(title,fontsize=10,fontproperties=FP)
    W=total; c=carriage; cx0=(W-c)/2; cx1=(W+c)/2
    verge=cx0
    # ground line (slight camber)
    gx=np.linspace(0,W,200); gy=np.zeros_like(gx)
    # road crown
    ax.fill_between([cx0,cx1],[0.15,0.15],[0.0,0.0],color='#cfcfcf',ec='k',lw=0.8,zorder=2)  # carriageway
    ax.plot([cx0,(cx0+cx1)/2,cx1],[0.10,0.18,0.10],'k-',lw=0.7,zorder=3)
    # verges / green
    for a,b in [(0,cx0),(cx1,W)]:
        ax.fill_between([a,b],[0.05,0.05],[0,0],color='#8ec87a',ec='k',lw=0.5,zorder=1)
    ax.plot([0,W],[0,0],'k-',lw=0.9)
    # ground hatch below
    for xx in np.arange(0.3,W,0.6):
        ax.plot([xx,xx-0.25],[-0.05,-0.35],'k-',lw=0.4,zorder=0)
    ax.plot([0,W],[-0.05,-0.05],'k-',lw=0.5)
    # buried utilities: (pos, depth, color, label)
    def put(x,depth,color,label):
        ax.plot(x,-depth,'o',ms=6,mfc=color,mec='k',mew=0.5,zorder=5)
        ax.text(x,-depth-0.18,label,ha='center',va='top',fontsize=5.3,rotation=90,fontproperties=FP)
    lx=verge/2; rx=W-verge/2
    for i,(col,lab) in enumerate(util_left):
        put(lx-0.5+i*0.5,0.8+0.25*i,col,lab)
    for i,(col,lab) in enumerate(util_right):
        put(rx-0.5+i*0.5,0.8+0.25*i,col,lab)
    if lamp:
        for x in (cx0-0.4,cx1+0.4):
            ax.plot([x,x],[0.05,1.4],'k-',lw=1); ax.plot(x,1.4,'o',ms=5,mfc='#ffd24d',mec='k')
    # dims
    dim(ax,0,W,-1.9,f"{W:.2f}")
    dim(ax,cx0,cx1,1.7,f"{c:.2f}")
    ax.text(cx0-0.1,1.0,"Ось дороги" if False else "",fontsize=5)
    ax.set_xlim(-1.5,W+1.5); ax.set_ylim(-3.0,2.6); ax.set_aspect('equal'); ax.axis('off')

def road_plan(ax,title,total,carriage):
    ax.set_title(title,fontsize=10,fontproperties=FP)
    W=total; c=carriage; cx0=(W-c)/2; cx1=(W+c)/2; Ln=16
    ax.add_patch(Rectangle((0,0),Ln,W,fc='#f2f2f2',ec='none'))
    ax.add_patch(Rectangle((0,cx0),Ln,c,fc='#d8d8d8',ec='k',lw=0.8))          # carriageway
    ax.plot([0,Ln],[W/2,W/2],'k-.',lw=0.7)                                     # axis
    for y,col,ls in [(cx0-1.2,'#1f77ff','-'),(cx0-0.6,'#8a5a2b','--'),(cx1+0.6,'#d62728','-'),(cx1+1.2,'#e8b800','-.')]:
        ax.plot([0,Ln],[y,y],color=col,ls=ls,lw=1)
    ax.text(-0.3,W/2,"Ось дороги",rotation=90,va='center',ha='right',fontsize=6,fontproperties=FP)
    dim(ax,0,Ln,-1.2,"тип. фрагмент")
    ax.annotate("",(Ln+0.6,cx0),(Ln+0.6,cx1),arrowprops=dict(arrowstyle='<->',lw=0.8))
    ax.text(Ln+0.9,W/2,f"{c:.2f}",rotation=90,va='center',fontsize=6.5,fontproperties=FP)
    ax.annotate("",(Ln+1.6,0),(Ln+1.6,W),arrowprops=dict(arrowstyle='<->',lw=0.8))
    ax.text(Ln+1.9,W/2,f"{W:.2f}",rotation=90,va='center',fontsize=6.5,fontproperties=FP)
    ax.set_xlim(-2,Ln+3); ax.set_ylim(-2,W+1); ax.set_aspect('equal'); ax.axis('off')

fig=plt.figure(figsize=(16.5,11.7),dpi=100); fig.patch.set_facecolor('white')
fig.add_artist(Rectangle((0.012,0.012),0.976,0.976,fill=False,ec='black',lw=1.5,transform=fig.transFigure))
UL=[('#1f77ff','Водопровод'),('#8a5a2b','Ливневая канализация')]
UR=[('#d62728','Кабель эл. снабжения'),('#e8b800','Газопровод низк. давл.')]
ax1=fig.add_axes([0.05,0.54,0.42,0.33]); road_plan(ax1,"План дороги 1 (главный проезд)",19.0,7.0)
ax2=fig.add_axes([0.53,0.54,0.42,0.33]); road_plan(ax2,"План дороги 2 (второстепенный)",12.0,6.0)
ax3=fig.add_axes([0.05,0.10,0.42,0.40]); section(ax3,"Разрез 1–1 (главный проезд)",19.0,7.0,UL,UR)
ax4=fig.add_axes([0.53,0.10,0.42,0.40]); section(ax4,"Разрез 2–2 (второстепенный)",12.0,6.0,UL,UR)
fig.text(0.05,0.955,"Планы дорог 1, 2.   Разрезы 1–1, 2–2.",fontsize=13,weight='bold',fontproperties=FP)
fig.text(0.05,0.912,"Пилотный проект коттеджного посёлка · н.п. Б. Афанасово · Стадия ПП · Лист 6 · A3",fontsize=8,fontproperties=FP)
fig.savefig("Дороги_разрезы.pdf",facecolor='white'); fig.savefig("Дороги_разрезы.png",dpi=110,facecolor='white')
print("saved Дороги_разрезы.pdf/.png")
