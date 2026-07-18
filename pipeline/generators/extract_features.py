import _patch, ezdxf, ezdxf.recover, json, math
from shapely.geometry import LineString, Polygon
doc,aud=ezdxf.recover.readfile("topo.dxf"); msp=doc.modelspace()
site=Polygon(json.load(open("boundary.json"))["pts"])
env=site.buffer(60)
def pl_pts(e):
    if e.dxftype()=='LWPOLYLINE': return [(p[0],p[1]) for p in e.get_points()]
    if e.dxftype()=='POLYLINE': return [(v.dxf.location[0],v.dxf.location[1]) for v in e.vertices]
    if e.dxftype()=='LINE': return [(e.dxf.start[0],e.dxf.start[1]),(e.dxf.end[0],e.dxf.end[1])]
    return []
# gather long polylines intersecting site env, by layer, to spot stream (long, sinuous) and ЛЭП (straight)
segs=[]
for e in msp.query('LWPOLYLINE POLYLINE LINE'):
    pts=pl_pts(e)
    if len(pts)<2: continue
    ls=LineString(pts)
    if ls.length<80: continue
    if not ls.intersects(env): continue
    segs.append((round(ls.length,1),len(pts),e.dxf.layer,e.dxf.color,e.dxftype(),pts))
segs.sort(reverse=True)
print("Длинные линии в районе участка (длина, точек, слой, цвет, тип):")
for L,n,lay,col,typ,_ in segs[:20]:
    print(f"  {L:8.0f}м  n={n:4} слой={lay[:16]:16} цвет={col} {typ}")
# save all candidates
json.dump([{"len":L,"n":n,"layer":lay,"color":col,"type":typ,"pts":pts} for L,n,lay,col,typ,pts in segs[:40]],
          open("longlines.json","w"))
print("saved longlines.json (top40)")
