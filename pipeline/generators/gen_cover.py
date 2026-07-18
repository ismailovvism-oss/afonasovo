import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MPoly
from matplotlib.font_manager import FontProperties
import numpy as np, json
from shapely.geometry import Polygon
FP=FontProperties(family='DejaVu Sans')
fig=plt.figure(figsize=(11.7,16.5),dpi=100); fig.patch.set_facecolor('#F2EFE8')  # A3 portrait, paper
fig.add_artist(Rectangle((0.04,0.03),0.92,0.94,fill=False,ec='#20292B',lw=2,transform=fig.transFigure))
fig.add_artist(Rectangle((0.055,0.045),0.89,0.91,fill=False,ec='#C33628',lw=0.8,transform=fig.transFigure))
# faint site silhouette
site=Polygon(json.load(open("boundary.json"))["pts"])
ax=fig.add_axes([0.12,0.30,0.76,0.34]); ax.set_aspect('equal'); ax.axis('off')
xs=[p[0] for p in site.exterior.coords]; ys=[p[1] for p in site.exterior.coords]
ax.add_patch(MPoly(list(zip(xs,ys)),closed=True,fc='#C33628',ec='#C33628',lw=1.5,alpha=0.10))
ax.plot(xs,ys,'-',color='#C33628',lw=1.5,alpha=0.5)
b=site.bounds; ax.set_xlim(b[0]-40,b[2]+40); ax.set_ylim(b[1]-40,b[3]+40)
def t(x,y,s,**kw): fig.text(x,y,s,fontproperties=FP,ha='center',**kw)
t(0.5,0.88,"ПИЛОТНЫЙ ПРОЕКТ",fontsize=13,color='#5B635F',**{'weight':'normal'})
t(0.5,0.83,"Коттеджный посёлок",fontsize=30,weight='bold',color='#20292B')
t(0.5,0.785,"в н.п. Большое Афанасово",fontsize=20,color='#20292B')
t(0.5,0.75,"Нижнекамский район · Республика Татарстан",fontsize=12,color='#5B635F')
fig.add_artist(plt.Line2D([0.35,0.65],[0.72,0.72],color='#C33628',lw=1.5,transform=fig.transFigure))
t(0.5,0.69,"Схема планировочной организации территории",fontsize=12,color='#5B635F',style='italic')
# stamp block bottom
axs=fig.add_axes([0.12,0.09,0.76,0.15]); axs.axis('off'); axs.set_xlim(0,1); axs.set_ylim(0,1)
axs.add_patch(Rectangle((0,0),1,1,fill=False,ec='#20292B',lw=1))
for x in (0.55,): axs.plot([x,x],[0,1],color='#20292B',lw=1)
rows=[("Стадия","Пилотный проект (ПП)"),("Система координат","МСК-16, высоты Балтийские"),
      ("Площадь территории","17,69 га"),("Жилых единиц","205")]
for i,(k,v) in enumerate(rows):
    yy=0.86-i*0.22
    axs.text(0.03,yy,k,fontsize=9,color='#5B635F',fontproperties=FP,va='center')
    axs.text(0.57,yy,v,fontsize=10,color='#20292B',weight='bold',fontproperties=FP,va='center')
t(0.5,0.055,"АО «Нижнекамский Татагропромпроект»  ·  улучшенный вариант",fontsize=9,color='#5B635F')
fig.savefig("Обложка.pdf",facecolor='#F2EFE8'); fig.savefig("Обложка.png",dpi=105,facecolor='#F2EFE8')
print("saved Обложка.png/.pdf")
