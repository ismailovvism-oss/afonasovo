import json, math, numpy as np
from shapely.geometry import Polygon, box, LineString, Point
from shapely.ops import unary_union
from shapely.affinity import rotate, translate

# ---------- load site ----------
d=json.load(open("boundary.json")); pts=d["pts"]
site=Polygon(pts)
if not site.is_valid: site=site.buffer(0)
cx,cy=site.centroid.x, site.centroid.y

# ---------- principal axis via PCA ----------
P=np.array(pts)-[cx,cy]
u,s,vt=np.linalg.svd(P-P.mean(0),full_matrices=False)
ang=math.degrees(math.atan2(vt[0][1],vt[0][0]))   # main axis angle
print("principal axis angle deg:",round(ang,2))

# work in rotated frame: rotate site by -ang about centroid so long axis = X
R=rotate(site,-ang,origin=(cx,cy))
minx,miny,maxx,maxy=R.bounds
print("rotated bounds LxH: %.0f x %.0f m"%(maxx-minx,maxy-miny))

# ---------- parameters ----------
FRONT=20.0      # parcel frontage along road (m) => 10 sotok if depth 50
ROAD_HW=7.5     # half corridor width of main road
SETBACK=3.0     # inset from site edge (red line)
MIN_PARCEL=300.0

inset=R.buffer(-SETBACK)

# ---------- bending spine: centroid-y per column ----------
cols=[]
x=minx
while x<maxx:
    strip=inset.intersection(box(x,miny-10,x+FRONT,maxy+10))
    if not strip.is_empty and strip.area>50:
        b=strip.bounds
        yc=strip.centroid.y
        cols.append((x,b[1],b[3],yc,strip))
    x+=FRONT
print("columns:",len(cols))

# smooth spine yc
ycs=np.array([c[3] for c in cols])
if len(ycs)>=5:
    k=np.ones(5)/5; ycs=np.convolve(ycs,k,mode='same')
    # fix ends
    ycs[:2]=[c[3] for c in cols][:2]; ycs[-2:]=[c[3] for c in cols][-2:]

road_cells=[]; parcels=[]
for (x,y0,y1,_,strip),yc in zip(cols,ycs):
    road=strip.intersection(box(x,yc-ROAD_HW,x+FRONT,yc+ROAD_HW))
    if not road.is_empty: road_cells.append(road)
    # upper & lower parcels (depth<=50)
    up=strip.intersection(box(x,yc+ROAD_HW,x+FRONT,min(y1,yc+ROAD_HW+50)))
    lo=strip.intersection(box(x,max(y0,yc-ROAD_HW-50),x+FRONT,yc-ROAD_HW))
    for pc in (up,lo):
        if pc.geom_type=='Polygon' and pc.area>=MIN_PARCEL:
            parcels.append(pc)
road=unary_union(road_cells)
print("parcels:",len(parcels),"road area m2:",int(road.area))

# rotate everything back to MSK-16
def back(g): return rotate(g,ang,origin=(cx,cy))
site_w=site; road_w=back(road); parcels_w=[back(p) for p in parcels]

# save geometry for next stages
import pickle
pickle.dump({"ang":ang,"cx":cx,"cy":cy,"site":site,"road":road_w,
             "parcels":parcels_w,"inset":back(inset)}, open("geom.pkl","wb"))

# quick render
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(18,11))
def plot_poly(g,**kw):
    if g.is_empty: return
    gs=[g] if g.geom_type=='Polygon' else list(g.geoms)
    for gg in gs:
        xs,ys=gg.exterior.xy; ax.fill(xs,ys,**kw)
plot_poly(site_w,fc='none',ec='red',lw=1.5)
plot_poly(road_w,fc='#c8c8c8',ec='none')
for p in parcels_w: plot_poly(p,fc='#d8f0c0',ec='#3a7d1e',lw=0.4)
ax.set_aspect('equal'); ax.axis('off')
ax.set_title("Genplan v1: %d parcels"%len(parcels_w))
fig.savefig("gen_v1.png",dpi=80,bbox_inches='tight',facecolor='white')
print("saved gen_v1.png")
