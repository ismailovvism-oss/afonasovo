import json, math, numpy as np, pickle
from shapely.geometry import Polygon, box, LineString, MultiLineString, Point
from shapely.ops import unary_union, linemerge
from shapely.affinity import rotate

d=json.load(open("boundary.json")); site=Polygon(d["pts"])
if not site.is_valid: site=site.buffer(0)
cx,cy=site.centroid.x, site.centroid.y
P=np.array(d["pts"])-[cx,cy]
_,_,vt=np.linalg.svd(P-P.mean(0),full_matrices=False)
ang=math.degrees(math.atan2(vt[0][1],vt[0][0]))
R=rotate(site,-ang,origin=(cx,cy)); minx,miny,maxx,maxy=R.bounds
DEPTH=45.0; ROAD_HW=7.0; SETBACK=4.0; BLOCK=2*DEPTH+2*ROAD_HW
inset=R.buffer(-SETBACK)
back=lambda g: rotate(g,ang,origin=(cx,cy))

# road centerlines (rotated frame)
centers=[]
road_ys=list(np.arange(miny+ROAD_HW+DEPTH, maxy, BLOCK))
for ry in road_ys:
    ln=LineString([(minx,ry),(maxx,ry)]).intersection(inset)
    if not ln.is_empty: centers.append(ln)
for rx in np.arange(minx+70,maxx,150):
    ln=LineString([(rx,miny),(rx,maxy)]).intersection(inset)
    if not ln.is_empty: centers.append(ln)
def flat(geom):
    out=[]
    for g in ([geom] if geom.geom_type=='LineString' else list(geom.geoms) if hasattr(geom,'geoms') else []):
        if g.geom_type=='LineString' and g.length>5: out.append(g)
    return out
segs=[]
for c in centers: segs+=flat(c)
net_base=unary_union(segs)

# 4 networks = lateral offsets of the centerline network
def offset_net(off):
    res=[]
    for g in segs:
        try:
            o=g.parallel_offset(off,'left',join_style=2)
            for gg in ([o] if o.geom_type=='LineString' else list(getattr(o,'geoms',[]))):
                if gg.length>3: res.append(gg)
        except Exception: pass
    return unary_union(res)
NETS={
 "Водоснабжение":      (-2.0,'#1f77ff','-'),
 "Водоотведение":      (-0.7,'#8a5a2b','--'),
 "Электроснабжение":   ( 0.7,'#d62728','-'),
 "Газоснабжение":      ( 2.0,'#e8b800','-.'),
}
netgeom={name:offset_net(off) for name,(off,col,ls) in NETS.items()}

# nodes: КТП, ГРПШ, скважина — place at rotated-frame fractions
L=maxx-minx; yspan=maxy-miny
def node(fx,fy): 
    return Point(minx+fx*L, miny+fy*yspan)
nodes=[("КТП 2×630 кВА","КТП",node(0.40,0.50),'#d62728'),
       ("ГРПШ","ГРПШ",node(0.66,0.52),'#e8b800'),
       ("Водозаборная скважина","СКВ",node(0.30,0.62),'#1f77ff')]

pickle.dump({"segs":[back(g) for g in segs],
             "nets":{n:back(g) for n,g in netgeom.items()},
             "NETS":NETS,
             "nodes":[(nm,k,back(p),c) for nm,k,p,c in nodes]},
            open("utils.pkl","wb"))
print("road centerline segments:",len(segs))
for n,g in netgeom.items(): print(f"  {n:18} длина ~{g.length:8.0f} м")
