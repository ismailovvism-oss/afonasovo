import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc, PathPatch
from matplotlib.path import Path
from matplotlib.font_manager import FontProperties
import numpy as np
FP=FontProperties(family='DejaVu Sans')
W=10.0; WALL=0.4

def draw_floor(ax,title,rooms,windows,doors,stairs=None):
    ax.set_title(title,fontsize=11,fontproperties=FP)
    # exterior wall: outer 10x10 minus inner
    outer=Rectangle((0,0),W,W,fc='none',ec='k',lw=1.6)
    inner=Rectangle((WALL,WALL),W-2*WALL,W-2*WALL,fc='none',ec='k',lw=0.8)
    # wall hatch between outer and inner
    wall=Path.make_compound_path(
        Path([(0,0),(W,0),(W,W),(0,W),(0,0)],closed=True),
        Path([(WALL,WALL),(WALL,W-WALL),(W-WALL,W-WALL),(W-WALL,WALL),(WALL,WALL)],closed=True))
    ax.add_patch(PathPatch(wall,fc='#b0b0b0',ec='k',lw=0.8,hatch='////'))
    # rooms
    for x,y,w,h,name in rooms:
        ax.add_patch(Rectangle((x,y),w,h,fc='none',ec='k',lw=0.7))
        area=w*h
        ax.text(x+w/2,y+h/2,f"{name}\n{area:.1f} м²",ha='center',va='center',
                fontsize=6.2,fontproperties=FP)
    # windows: (side,pos,length) side in NESW
    for side,pos,ln in windows:
        if side=='S': ax.add_patch(Rectangle((pos,0.05),ln,WALL-0.1,fc='white',ec='k',lw=0.6)); ax.plot([pos,pos+ln],[WALL/2,WALL/2],'k-',lw=0.5)
        if side=='N': ax.add_patch(Rectangle((pos,W-WALL+0.05),ln,WALL-0.1,fc='white',ec='k',lw=0.6)); ax.plot([pos,pos+ln],[W-WALL/2,W-WALL/2],'k-',lw=0.5)
        if side=='W': ax.add_patch(Rectangle((0.05,pos),WALL-0.1,ln,fc='white',ec='k',lw=0.6)); ax.plot([WALL/2,WALL/2],[pos,pos+ln],'k-',lw=0.5)
        if side=='E': ax.add_patch(Rectangle((W-WALL+0.05,pos),WALL-0.1,ln,fc='white',ec='k',lw=0.6)); ax.plot([W-WALL/2,W-WALL/2],[pos,pos+ln],'k-',lw=0.5)
    # doors: (x,y,size,angle_start) quarter-circle swing
    for x,y,s,a0 in doors:
        ax.add_patch(Arc((x,y),2*s,2*s,angle=0,theta1=a0,theta2=a0+90,lw=0.7))
        import math
        ax.plot([x,x+s*math.cos(math.radians(a0))],[y,y+s*math.sin(math.radians(a0))],'k-',lw=0.7)
    # stairs
    if stairs:
        sx,sy,sw,sh,n=stairs
        for i in range(n+1):
            ax.plot([sx,sx+sw],[sy+i*sh/n,sy+i*sh/n],'k-',lw=0.5)
        ax.annotate("",(sx+sw/2,sy+sh),(sx+sw/2,sy),arrowprops=dict(arrowstyle='->',lw=0.8))
        ax.text(sx+sw/2,sy-0.25,"вверх",ha='center',fontsize=5,fontproperties=FP)
    # dimension chains
    ax.annotate("",(0,-0.8),(W,-0.8),arrowprops=dict(arrowstyle='<->',lw=0.7))
    ax.text(W/2,-1.15,f"{W*1000:.0f}",ha='center',fontsize=7,fontproperties=FP)
    ax.annotate("",(-0.8,0),(-0.8,W),arrowprops=dict(arrowstyle='<->',lw=0.7))
    ax.text(-1.15,W/2,f"{W*1000:.0f}",va='center',rotation=90,fontsize=7,fontproperties=FP)
    ax.set_xlim(-1.8,W+0.6); ax.set_ylim(-1.8,W+0.6); ax.set_aspect('equal'); ax.axis('off')

ground=[
 (0.4,0.4,2.0,1.7,"Тамбур"),
 (0.4,2.1,2.0,3.0,"Холл"),
 (0.4,5.1,2.0,4.5,"Постирочная"),
 (2.4,0.4,3.6,9.2,"Кухня-гостиная"),
 (6.0,0.4,3.6,5.3,"Гараж"),
 (6.0,5.7,3.6,1.9,"Котельная"),
 (6.0,7.6,3.6,2.0,"Санузел"),
]
mansard=[
 (0.4,0.4,2.0,1.7,"Холл"),
 (0.4,2.1,2.0,3.0,"Лестница"),
 (0.4,5.1,2.7,4.5,"Ванная"),
 (2.4,0.4,3.6,4.6,"Спальня 1"),
 (6.0,0.4,3.6,4.6,"Спальня 2"),
 (3.1,5.1,2.9,4.5,"Спальня 3"),
 (6.0,5.1,3.6,4.5,"Гардероб / кабинет"),
]
fig=plt.figure(figsize=(16.5,11.7),dpi=100); fig.patch.set_facecolor('white')
fig.add_artist(Rectangle((0.012,0.012),0.976,0.976,fill=False,ec='black',lw=1.5,transform=fig.transFigure))
axA=fig.add_axes([0.05,0.12,0.40,0.74]); axB=fig.add_axes([0.50,0.12,0.40,0.74])
draw_floor(axA,"План 1-го этажа",ground,
           [('S',3.0,2.0),('S',6.6,2.2),('W',6.0,2.0),('E',1.5,1.6),('N',6.6,2.0)],
           [(2.4,0.6,0.9,0),(2.4,3.0,0.9,0)],
           stairs=(0.5,2.2,1.8,2.6,9))
draw_floor(axB,"План мансардного этажа",mansard,
           [('S',3.0,2.0),('S',6.6,2.2),('W',6.5,2.0),('E',1.5,1.8),('N',3.0,2.0),('N',6.6,2.0)],
           [(2.4,3.0,0.9,0),(6.0,3.0,0.9,90)])
fig.text(0.05,0.945,"Одноквартирный двухэтажный жилой дом. Планы 1-го и мансардного этажа.",
         fontsize=13,weight='bold',fontproperties=FP)
fig.text(0.05,0.918,"Габариты 10×10 м · Наружные стены — газобетон 400 мм · Стадия ПП · Лист 8 · A3",
         fontsize=8,fontproperties=FP)
# small spec
fig.text(0.05,0.06,"Наружные стены — газобетон 400 мм · Перегородки — 120 мм · Кровля — битумная черепица · "
         "Фундамент — ленточный сборный ж/б · Отделка фасада — облицовочный кирпич",
         fontsize=7.5,fontproperties=FP,color='#333')
fig.savefig("Дом_планы.pdf",facecolor='white'); fig.savefig("Дом_планы.png",dpi=110,facecolor='white')
print("saved Дом_планы.pdf/.png")
