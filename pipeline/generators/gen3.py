import json, math, numpy as np, pickle
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from shapely.affinity import rotate

d=json.load(open("boundary.json")); site=Polygon(d["pts"])
if not site.is_valid: site=site.buffer(0)
cx,cy=site.centroid.x, site.centroid.y
P=np.array(d["pts"])-[cx,cy]
_,_,vt=np.linalg.svd(P-P.mean(0),full_matrices=False)
ang=math.degrees(math.atan2(vt[0][1],vt[0][0]))
R=rotate(site,-ang,origin=(cx,cy)); minx,miny,maxx,maxy=R.bounds
L=maxx-minx
FRONT=20.0; DEPTH=45.0; ROAD_HW=7.0; CONNECT_W=12.0; SETBACK=4.0; MIN_PARCEL=250.0
inset=R.buffer(-SETBACK); BLOCK=2*DEPTH+2*ROAD_HW
# social zones in rotated frame (fraction of L along x). (fx0,fx1, y_center_frac, w,h, name, key)
def zrect(fx,fy,w,h):
    x=minx+fx*L; yspan=maxy-miny; y=miny+fy*yspan
    return box(x-w/2,y-h/2,x+w/2,y+h/2)
socials=[
    ("Школа – детский сад","school", zrect(0.50,0.62,70,45),'#ff45ff'),
    ("Мечеть","mosque",             zrect(0.72,0.70,26,26),'#8a2be2'),
    ("Здание бытового обслуж. с магазином","shop", zrect(0.60,0.33,34,22),'#00c0c0'),
    ("Спортивная площадка","sport",  zrect(0.45,0.30,40,28),'#c0e0ff'),
    ("Детская площадка","kids",      zrect(0.55,0.70,26,20),'#c0e0ff'),
]
social_zone=unary_union([s[2] for s in socials]).buffer(6)

# roads
road_cells=[]
road_ys=list(np.arange(miny+ROAD_HW+DEPTH, maxy, BLOCK))
for ry in road_ys: road_cells.append(box(minx-5,ry-ROAD_HW,maxx+5,ry+ROAD_HW))
for rx in np.arange(minx+70,maxx,150): road_cells.append(box(rx-CONNECT_W/2,miny-5,rx+CONNECT_W/2,maxy+5))
roads=unary_union(road_cells).intersection(inset).difference(social_zone)
buildable=inset.difference(roads.buffer(0.01)).difference(social_zone)

# parcels
parcels=[]
for ry in road_ys:
    for side in (+1,-1):
        y0,y1=sorted([ry+side*ROAD_HW, ry+side*(ROAD_HW+DEPTH)])
        x=minx
        while x<maxx:
            cell=box(x,y0,x+FRONT,y1).intersection(buildable)
            if cell.geom_type=='MultiPolygon': cell=max(cell.geoms,key=lambda g:g.area)
            if cell.geom_type=='Polygon' and cell.area>=MIN_PARCEL:
                parcels.append((cell,ry,side)); 
            x+=FRONT
# classify by rx fraction: east end (high x) -> taunhouses; a mid band -> 2-family
items=[]
HOUSE={'1F':(10,10),'2F':(10,18),'TH':(10,28)}
COLOR={'1F':'#e000e0','2F':'#1e6ec8','TH':'#e8896a'}
for cell,ry,side in parcels:
    rx=(cell.centroid.x-minx)/L
    if rx>0.80: t='TH'
    elif 0.63<rx<0.72: t='2F'
    else: t='1F'
    # place house centered, oriented long side along parcel's longer extent
    b=cell.bounds; pw=b[2]-b[0]; pd=b[3]-b[1]; hw,hl=HOUSE[t]
    if pw>=pd:  w,l=max(hw,hl),min(hw,hl)   # long along x
    else:       w,l=min(hw,hl),max(hw,hl)
    ccx,ccy=cell.centroid.x,cell.centroid.y
    house=box(ccx-w/2,ccy-l/2,ccx+w/2,ccy+l/2)
    if not cell.buffer(-1).contains(house):
        house=house.intersection(cell.buffer(-1))
    items.append((cell,house,t))
from collections import Counter
cnt=Counter(t for _,_,t in items)
print("parcels total:",len(items),"types:",dict(cnt))

back=lambda g: rotate(g,ang,origin=(cx,cy))
out={"ang":ang,"cx":cx,"cy":cy,"L":L,"site":site,"roads":back(roads),
     "inset":back(inset),"parcels":[(back(c),back(h),t) for c,h,t in items],
     "socials":[(name,key,back(rect),col) for name,key,rect,col in socials],
     "COLOR":COLOR,"HOUSE":HOUSE,"counts":dict(cnt)}
pickle.dump(out,open("plan.pkl","wb"))

# render
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(20,12))
def pp(g,**kw):
    if g.is_empty: return
    for gg in ([g] if g.geom_type=='Polygon' else list(g.geoms)):
        xs,ys=gg.exterior.xy; ax.fill(xs,ys,**kw)
pp(back(roads),fc='#c8c8c8',ec='none',zorder=1)
for c,h,t in items:
    pp(back(c),fc='#e8f6d8',ec='#3a7d1e',lw=0.4,zorder=2)
    pp(back(h),fc=COLOR[t],ec='#333333',lw=0.3,zorder=3)
for name,key,rect,col in socials:
    pp(back(rect),fc=col,ec='#222',lw=0.8,zorder=3)
    c=back(rect).centroid; ax.annotate(name.split(' с ')[0],(c.x,c.y),ha='center',va='center',fontsize=7,zorder=5)
pp(site,fc='none',ec='red',lw=1.8,zorder=6)
ax.set_aspect('equal'); ax.axis('off')
ax.set_title("Генплан v3: %d участков (%s)"%(len(items),cnt),fontsize=12)
fig.savefig("gen_v3.png",dpi=85,bbox_inches='tight',facecolor='white'); print("saved gen_v3.png")
