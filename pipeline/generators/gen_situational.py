import _patch, ezdxf, ezdxf.recover, json, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle
from matplotlib.font_manager import FontProperties
from shapely.geometry import Polygon, LineString, box
FP=FontProperties(family='DejaVu Sans')
doc,aud=ezdxf.recover.readfile("topo.dxf"); msp=doc.modelspace()
site=Polygon(json.load(open("boundary.json"))["pts"])
b=site.bounds; pad=260
env=box(b[0]-pad,b[1]-pad,b[2]+pad,b[3]+pad)
fig=plt.figure(figsize=(15,10)); ax=fig.add_axes([0.02,0.02,0.96,0.94]); ax.set_aspect('equal'); ax.axis('off')
def pts_of(e):
    if e.dxftype()=='LWPOLYLINE': return [(p[0],p[1]) for p in e.get_points()]
    if e.dxftype()=='POLYLINE': return [(v.dxf.location[0],v.dxf.location[1]) for v in e.vertices]
    if e.dxftype()=='LINE': return [(e.dxf.start[0],e.dxf.start[1]),(e.dxf.end[0],e.dxf.end[1])]
    return []
# context lines (faint)
for e in msp.query('LWPOLYLINE POLYLINE LINE'):
    p=pts_of(e)
    if len(p)<2: continue
    ls=LineString(p)
    if not ls.intersects(env): continue
    if ls.length>1200: continue      # skip huge contour spaghetti
    xs=[q[0] for q in p]; ys=[q[1] for q in p]
    ax.plot(xs,ys,'-',color='#bcbcbc',lw=0.4,zorder=1)
# our site
xs=[p[0] for p in site.exterior.coords]; ys=[p[1] for p in site.exterior.coords]
ax.add_patch(MPoly(list(zip(xs,ys)),closed=True,fc='#c33628',ec='#c33628',lw=2.2,alpha=0.20,zorder=3))
ax.plot(xs,ys,'-',color='#c33628',lw=2.2,zorder=4)
ax.set_xlim(b[0]-pad,b[2]+pad); ax.set_ylim(b[1]-pad,b[3]+pad)
# label our site
cxy=site.centroid
ax.annotate("ПРОЕКТИРУЕМАЯ\nТЕРРИТОРИЯ\n17,69 га",(cxy.x,cxy.y),ha='center',va='center',
            fontsize=12,weight='bold',color='#7a1d14',fontproperties=FP,zorder=5)
# context labels (approx positions relative to bounds)
def lab(fx,fy,t,c='#333'):
    x=b[0]+fx*(b[2]-b[0]); y=b[1]+fy*(b[3]-b[1])
    ax.text(x,y,t,fontsize=9,color=c,ha='center',fontproperties=FP,zorder=5,
            bbox=dict(boxstyle='round,pad=0.25',fc='white',ec='#ccc',alpha=0.8))
lab(0.15,1.06,"с. Большое Афанасово")
lab(-0.02,0.02,"Покровская\nцерковь")
lab(0.45,-0.06,"ручей")
lab(1.06,0.55,"к г. Нижнекамск →",'#7a1d14')
# north arrow
nx,ny=b[2]+pad*0.55,b[3]+pad*0.35
ax.annotate("С",(nx,ny+70),ha='center',fontsize=13,weight='bold',fontproperties=FP)
ax.annotate("",(nx,ny+60),(nx,ny-10),arrowprops=dict(arrowstyle='-|>',lw=1.6,color='k'))
# scale bar 200 m
sx,sy=b[0]-pad*0.6,b[1]-pad*0.6
ax.plot([sx,sx+200],[sy,sy],'k-',lw=2); ax.plot([sx,sx],[sy-8,sy+8],'k-'); ax.plot([sx+200,sx+200],[sy-8,sy+8],'k-')
ax.text(sx+100,sy+16,"200 м",ha='center',fontsize=8,fontproperties=FP)
fig.text(0.03,0.965,"Ситуационный план",fontsize=15,weight='bold',fontproperties=FP)
fig.text(0.03,0.94,"Пилотный проект коттеджного посёлка · н.п. Б. Афанасово · СК МСК-16 · Лист 2",fontsize=8,fontproperties=FP)
fig.savefig("Ситуационный.pdf",facecolor='white'); fig.savefig("Ситуационный.png",dpi=105,facecolor='white',bbox_inches='tight')
print("saved Ситуационный.png/.pdf")
