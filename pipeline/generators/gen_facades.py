import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MPoly
from matplotlib.font_manager import FontProperties
import numpy as np
FP=FontProperties(family='DejaVu Sans')
W=10.0; H1=3.2; H2=6.4; RIDGE=9.2
WALLC='#efe7d6'; ROOFC='#8a3826'; WIN='#c8d4e2'; DOORC='#6a4526'; GARC='#8a5a34'
def ground(ax,x0,x1):
    ax.plot([x0-0.5,x1+0.5],[0,0],'k-',lw=1.3)
    for x in np.arange(x0-0.3,x1+0.6,0.5): ax.plot([x,x-0.28],[0,-0.32],'k-',lw=0.5)
def window(ax,x,z,w,h):
    ax.add_patch(Rectangle((x,z),w,h,fc=WIN,ec='k',lw=0.8))
    ax.plot([x+w/2,x+w/2],[z,z+h],'k-',lw=0.6); ax.plot([x,x+w],[z+h/2,z+h/2],'k-',lw=0.6)
def level(ax,x,z,txt):
    ax.add_patch(MPoly([(x,z),(x-0.18,z+0.22),(x+0.18,z+0.22)],closed=True,fc='k'))
    ax.plot([x-0.7,x],[z,z],'k-',lw=0.6)
    ax.text(x-0.8,z,txt,ha='right',va='center',fontsize=6.5,fontproperties=FP)

def facade_gable(ax,title):
    ax.set_title(title,fontsize=10,fontproperties=FP)
    ax.add_patch(Rectangle((0,0),W,H2,fc=WALLC,ec='k',lw=1.2))
    ax.add_patch(MPoly([(0,H2),(W,H2),(W/2,RIDGE)],closed=True,fc=ROOFC,ec='k',lw=1.2))
    # entrance + porch
    ax.add_patch(Rectangle((3.1,0),1.0,2.15,fc=DOORC,ec='k',lw=0.8))
    ax.add_patch(MPoly([(2.6,2.5),(4.6,2.5),(4.3,3.0),(2.9,3.0)],closed=True,fc='#cfc4ad',ec='k',lw=0.6)) # козырёк
    for st in range(3): ax.plot([2.9+st*0.06,4.3-st*0.06],[-0.05-st*0.08]*2,'k-',lw=0.7)
    # garage (integrated right)
    ax.add_patch(Rectangle((6.3,0),3.0,2.4,fc=GARC,ec='k',lw=0.9))
    for gx in np.arange(6.5,9.3,0.35): ax.plot([gx,gx],[0.1,2.3],'k-',lw=0.4)
    # windows: ground + mansard
    window(ax,1.0,1.1,1.3,1.5); window(ax,4.7,1.1,1.3,1.5)
    window(ax,1.2,4.2,1.3,1.4); window(ax,4.2,4.2,1.6,1.4); window(ax,6.6,4.2,1.3,1.4)
    window(ax,4.3,7.0,1.4,1.2)  # мансардное в фронтоне
    ground(ax,0,W)
    for z,t in [(0,'0.000'),(H1,'+3.200'),(H2,'+6.400'),(RIDGE,'+9.200')]: level(ax,0,z,t)
    ax.set_xlim(-2.2,W+0.6); ax.set_ylim(-1.2,RIDGE+0.6); ax.set_aspect('equal'); ax.axis('off')

def facade_side(ax,title):
    ax.set_title(title,fontsize=10,fontproperties=FP)
    ax.add_patch(Rectangle((0,0),W,H2,fc=WALLC,ec='k',lw=1.2))
    # eave-side roof: trapezoid profile
    ax.add_patch(MPoly([(0,H2),(W,H2),(W-1.2,RIDGE),(1.2,RIDGE)],closed=True,fc=ROOFC,ec='k',lw=1.2))
    for x in (1.5,4.0,6.5): window(ax,x,1.1,1.3,1.5)
    for x in (1.7,4.2,6.7): window(ax,x,4.2,1.3,1.4)
    ground(ax,0,W)
    for z,t in [(0,'0.000'),(H2,'+6.400'),(RIDGE,'+9.200')]: level(ax,0,z,t)
    ax.set_xlim(-2.2,W+0.6); ax.set_ylim(-1.2,RIDGE+0.6); ax.set_aspect('equal'); ax.axis('off')

def section(ax,title):
    ax.set_title(title,fontsize=10,fontproperties=FP)
    # foundation
    ax.add_patch(Rectangle((0,-1.2),W,1.2,fc='#cfc4ad',ec='k',lw=1,hatch='xx'))
    # slabs
    for z in (0,H1,H2): ax.add_patch(Rectangle((0,z-0.15),W,0.15,fc='#b9b9b9',ec='k',lw=0.8))
    # walls
    for x in (0,W-0.3): ax.add_patch(Rectangle((x,0),0.3,H2,fc=WALLC,ec='k',lw=0.8))
    # roof triangle + mansard ceiling
    ax.add_patch(MPoly([(0,H2),(W,H2),(W/2,RIDGE)],closed=True,fc='none',ec='k',lw=1.2))
    ax.plot([0,W],[H2,H2],'k-',lw=0.6)
    ax.text(W/2,H1/2,'1 этаж\nh=3.0',ha='center',va='center',fontsize=6.5,fontproperties=FP)
    ax.text(W/2,H1+(H2-H1)/2,'Мансарда\nh=3.0',ha='center',va='center',fontsize=6.5,fontproperties=FP)
    ax.text(W/2,-0.6,'Ленточный фундамент',ha='center',va='center',fontsize=6,fontproperties=FP)
    for z,t in [(0,'0.000'),(H1,'+3.200'),(H2,'+6.400'),(RIDGE,'+9.200')]: level(ax,0,z,t)
    ax.set_xlim(-2.2,W+0.6); ax.set_ylim(-1.6,RIDGE+0.6); ax.set_aspect('equal'); ax.axis('off')

fig=plt.figure(figsize=(16.5,11.7),dpi=100); fig.patch.set_facecolor('white')
fig.add_artist(Rectangle((0.012,0.012),0.976,0.976,fill=False,ec='black',lw=1.5,transform=fig.transFigure))
a1=fig.add_axes([0.03,0.50,0.44,0.40]); facade_gable(a1,"Фасад 1–7 (главный)")
a2=fig.add_axes([0.52,0.50,0.44,0.40]); facade_side(a2,"Фасад А–Г (боковой)")
a3=fig.add_axes([0.03,0.07,0.44,0.38]); section(a3,"Разрез 1–1")
fig.text(0.52,0.42,"Материалы",fontsize=10,weight='bold',fontproperties=FP)
spec=["Наружные стены — газобетон 400 мм","Отделка фасада — облицовочный кирпич",
      "Кровля — битумная черепица по деревянной стропильной системе",
      "Перекрытия — сборные ж/б плиты","Фундамент — ленточный сборный ж/б",
      "Окна — ПВХ, двухкамерный стеклопакет","Высота этажа — 3.0 м (в чистоте)"]
for i,s in enumerate(spec): fig.text(0.52,0.38-i*0.03,"•  "+s,fontsize=8.5,fontproperties=FP)
fig.text(0.03,0.945,"Одноквартирный двухэтажный жилой дом. Фасады. Разрез.",fontsize=13,weight='bold',fontproperties=FP)
fig.text(0.03,0.918,"Габариты 10×10 м · Стадия ПП · Лист 9 · A3",fontsize=8,fontproperties=FP)
fig.savefig("Дом_фасады.pdf",facecolor='white'); fig.savefig("Дом_фасады.png",dpi=110,facecolor='white')
print("saved Дом_фасады.png/.pdf")
