import json, math, numpy as np, pickle
from shapely.geometry import Polygon, box, MultiPolygon
from shapely.ops import unary_union
from shapely.affinity import rotate

d=json.load(open("boundary.json")); site=Polygon(d["pts"])
if not site.is_valid: site=site.buffer(0)
cx,cy=site.centroid.x, site.centroid.y
P=np.array(d["pts"])-[cx,cy]
_,_,vt=np.linalg.svd(P-P.mean(0),full_matrices=False)
ang=math.degrees(math.atan2(vt[0][1],vt[0][0]))
R=rotate(site,-ang,origin=(cx,cy))
minx,miny,maxx,maxy=R.bounds

# ---- parameters ----
FRONT=20.0; DEPTH=45.0; ROAD_HW=7.0; CONNECT_W=12.0
SETBACK=4.0; MIN_PARCEL=250.0
inset=R.buffer(-SETBACK)
BLOCK=2*DEPTH+2*ROAD_HW           # pitch between road centerlines
# main roads (horizontal in rotated frame)
road_cells=[]
road_ys=list(np.arange(miny+ROAD_HW+DEPTH, maxy, BLOCK))
for ry in road_ys:
    road_cells.append(box(minx-5,ry-ROAD_HW,maxx+5,ry+ROAD_HW))
# cross connectors every ~140 m
cross_xs=list(np.arange(minx+70, maxx, 150))
for rx in cross_xs:
    road_cells.append(box(rx-CONNECT_W/2,miny-5,rx+CONNECT_W/2,maxy+5))
roads=unary_union(road_cells).intersection(inset)

# ---- parcels: fill bands between roads ----
buildable=inset.difference(roads.buffer(0.01))
parcels=[]
for ry in road_ys:
    for side in (+1,-1):
        y_near=ry+side*ROAD_HW
        y_far=ry+side*(ROAD_HW+DEPTH)
        lo,hi=sorted([y_near,y_far])
        x=minx
        while x<maxx:
            cell=box(x,lo,x+FRONT,hi).intersection(buildable)
            if cell.geom_type=='MultiPolygon':
                cell=max(cell.geoms,key=lambda g:g.area)
            if cell.geom_type=='Polygon' and cell.area>=MIN_PARCEL:
                parcels.append(cell)
            x+=FRONT
print("roads area m2:",int(roads.area),"parcels:",len(parcels))

back=lambda g: rotate(g,ang,origin=(cx,cy))
pickle.dump({"ang":ang,"cx":cx,"cy":cy,"site":site,
            "roads":back(roads),"parcels":[back(p) for p in parcels],
            "inset":back(inset)}, open("geom.pkl","wb"))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(18,11))
def pp(g,**kw):
    if g.is_empty: return
    for gg in ([g] if g.geom_type=='Polygon' else list(g.geoms)):
        xs,ys=gg.exterior.xy; ax.fill(xs,ys,**kw)
pp(back(roads),fc='#cccccc',ec='none')
for p in parcels: pp(back(p),fc='#d8f0c0',ec='#3a7d1e',lw=0.4)
pp(site,fc='none',ec='red',lw=1.5)
ax.set_aspect('equal'); ax.axis('off'); ax.set_title("Genplan v2 grid-fill: %d parcels"%len(parcels))
fig.savefig("gen_v2.png",dpi=80,bbox_inches='tight',facecolor='white'); print("saved gen_v2.png")
