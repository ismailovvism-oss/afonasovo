import pickle, numpy as np
from shapely.affinity import rotate
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow
from matplotlib.font_manager import FontProperties
p=pickle.load(open("plan.pkl","rb"))
site=p["site"]; roads=p["roads"]; parcels=p["parcels"]; socials=p["socials"]; COLOR=p["COLOR"]
# ---- TEP ----
def area(g): return 0 if g.is_empty else g.area
S_site=area(site); S_roads=area(roads)
S={'1F':0,'2F':0,'TH':0}
for c,h,t in parcels: S[t]+=area(c)
S_res=sum(S.values())
S_soc=sum(area(r) for _,_,r,_ in socials)
S_green=max(S_site-S_roads-S_res-S_soc,0)
n=p["counts"]
def ha(x): return x/10000
rows=[
 ("1","Общая площадь территории",S_site,100),
 ("2","Участки жилой застройки, всего",S_res,S_res/S_site*100),
 ("2.1","  — одноквартирные 2-эт. дома (10×10), %d уч."%n['1F'],S['1F'],S['1F']/S_site*100),
 ("2.2","  — двухквартирные 2-эт. дома (10×18), %d уч."%n['2F'],S['2F'],S['2F']/S_site*100),
 ("2.3","  — таунхаусы 4-кв. 2-эт. (10×28), %d уч."%n['TH'],S['TH'],S['TH']/S_site*100),
 ("3","Участки соц. инфраструктуры",S_soc,S_soc/S_site*100),
 ("4","Улицы, проезды, площадки",S_roads,S_roads/S_site*100),
 ("5","Озеленение, тер. общего польз.",S_green,S_green/S_site*100),
]
print("=== ТЭП ===")
for a,b,s,pc in rows: print(f"{a:4} {b[:52]:52} {s:11.1f} {pc:6.2f}%")

# ---- sheet A3 landscape ----
FP=FontProperties(family='DejaVu Sans')
fig=plt.figure(figsize=(16.5,11.7),dpi=100)  # ~A3
fig.patch.set_facecolor('white')
# border frame
fig.add_artist(Rectangle((0.012,0.012),0.976,0.976,fill=False,ec='black',lw=1.5,transform=fig.transFigure))
# --- plan axis (left ~66%) ---
axp=fig.add_axes([0.03,0.06,0.63,0.88]); axp.set_aspect('equal'); axp.axis('off')
def pp(ax,g,**kw):
    if g.is_empty: return
    for gg in ([g] if g.geom_type=='Polygon' else list(g.geoms)):
        xs,ys=gg.exterior.xy; ax.fill(xs,ys,**kw)
pp(axp,roads,fc='#c8c8c8',ec='none',zorder=1)
for c,h,t in parcels:
    pp(axp,c,fc='#e8f6d8',ec='#3a7d1e',lw=0.4,zorder=2)
    pp(axp,h,fc=COLOR[t],ec='#333',lw=0.3,zorder=3)
for name,key,rect,col in socials:
    pp(axp,rect,fc=col,ec='#222',lw=0.8,zorder=3)
    cc=rect.centroid; axp.annotate(name.split(' с ')[0],(cc.x,cc.y),ha='center',va='center',fontsize=6,zorder=5)
pp(axp,site,fc='none',ec='red',lw=1.8,zorder=6)
axp.set_title("Схема планировочной организации земельного участка.  М 1:2000",fontsize=11,fontproperties=FP)
# north arrow
b=site.bounds; axp.annotate("С",xy=(b[0]+ (b[2]-b[0])*0.02,b[3]-(b[3]-b[1])*0.02),fontsize=13,fontproperties=FP,weight='bold')
# --- right column ---
def txt(x,y,s,**kw): fig.text(x,y,s,fontproperties=FP,**kw)
txt(0.67,0.955,"Пилотный проект коттеджного посёлка",fontsize=13,weight='bold')
txt(0.67,0.935,"н.п. Большое Афанасово, Нижнекамский р-н, РТ",fontsize=9)
txt(0.67,0.915,"Улучшенный вариант генплана · СК МСК-16",fontsize=8,style='italic',color='#666')
# ТЭП table
ty=0.885; txt(0.67,ty+0.012,"Технико-экономические показатели",fontsize=10,weight='bold')
axt=fig.add_axes([0.665,0.60,0.325,0.28]); axt.axis('off')
tbl=[["№","Наименование","м²","%"]]+[[a,b,f"{s:,.0f}".replace(",", " "),f"{pc:.2f}"] for a,b,s,pc in rows]
T=axt.table(cellText=tbl,cellLoc='left',colWidths=[0.06,0.60,0.20,0.14],loc='upper left')
T.auto_set_font_size(False); T.set_fontsize(5.6); T.scale(1,1.25)
for (r,c),cell in T.get_celld().items():
    cell.set_linewidth(0.4)
    if r==0: cell.set_facecolor('#dddddd'); cell.set_text_props(weight='bold')
    for t in [cell.get_text()]: t.set_fontproperties(FP)
# legend
ly=0.565; txt(0.67,ly,"Условные обозначения",fontsize=10,weight='bold')
leg=[('#e000e0','Одноквартирный 2-эт. жилой дом (10×10)'),
     ('#1e6ec8','Двухквартирный 2-эт. жилой дом (10×18)'),
     ('#e8896a','Таунхаус 4-кв. 2-эт. (10×28)'),
     ('#ff45ff','Школа – детский сад'),('#8a2be2','Мечеть'),
     ('#00c0c0','Здание бытового обслуживания с магазином'),
     ('#c0e0ff','Спортивная / детская площадка'),
     ('#e8f6d8','Приусадебный участок'),('#c8c8c8','Улицы, проезды, площадки')]
axl=fig.add_axes([0.67,0.35,0.31,0.205]); axl.axis('off'); axl.set_xlim(0,1); axl.set_ylim(0,len(leg))
for i,(col,lab) in enumerate(leg):
    yy=len(leg)-1-i+0.15
    axl.add_patch(Rectangle((0.02,yy),0.09,0.7,fc=col,ec='#333',lw=0.4))
    axl.text(0.15,yy+0.35,lab,va='center',fontsize=6.6,fontproperties=FP)
# stamp
axs=fig.add_axes([0.67,0.05,0.31,0.14]); axs.axis('off'); axs.add_patch(Rectangle((0,0),1,1,fill=False,ec='k',lw=1))
axs.text(0.03,0.80,"Пилотный проект коттеджного посёлка",fontsize=7.5,fontproperties=FP)
axs.text(0.03,0.62,"в н.п. Б. Афанасово Нижнекамского района",fontsize=7.5,fontproperties=FP)
axs.text(0.03,0.40,"Схема планировочной организации",fontsize=7.5,weight='bold',fontproperties=FP)
axs.text(0.03,0.24,"земельного участка",fontsize=7.5,weight='bold',fontproperties=FP)
axs.text(0.03,0.05,"Стадия: ПП   Лист 3   Формат A3",fontsize=6.5,fontproperties=FP)
axs.text(0.62,0.05,"Сгенерировано автоматически",fontsize=6,style='italic',color='#888',fontproperties=FP)
fig.savefig("СПОЗУ_лист.pdf",facecolor='white'); fig.savefig("СПОЗУ_лист.png",dpi=110,facecolor='white')
pickle.dump({"rows":rows,"counts":n,"S_site":S_site},open("tep.pkl","wb"))
print("saved СПОЗУ_лист.pdf / .png")
