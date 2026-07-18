import _patch, ezdxf, ezdxf.recover
doc,aud=ezdxf.recover.readfile("topo.dxf"); msp=doc.modelspace()
cands=[]
for e in msp.query('LWPOLYLINE POLYLINE'):
    try:
        pts=[(p[0],p[1]) for p in (e.get_points() if e.dxftype()=='LWPOLYLINE' else [(v.dxf.location[0],v.dxf.location[1]) for v in e.vertices])]
    except Exception:
        continue
    if len(pts)<3: continue
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    w=max(xs)-min(xs); h=max(ys)-min(ys)
    # shoelace area
    a=0.0
    for i in range(len(pts)):
        x1,y1=pts[i]; x2,y2=pts[(i+1)%len(pts)]; a+=x1*y2-x2*y1
    area=abs(a)/2
    cands.append((area,w,h,len(pts),e.dxf.layer,e.dxf.color,e.dxftype(),e.dxf.handle,pts))
cands.sort(reverse=True)
print("Крупнейшие замкнутые контуры (площадь м², ширина, высота, вершин, слой, цвет):")
for area,w,h,n,lay,col,typ,hnd,pts in cands[:12]:
    print(f"  S={area:12.1f}  {w:6.0f}x{h:6.0f}  верш={n:4}  слой={lay[:18]:18} цвет={col} {typ} h={hnd}")
# save the top candidate's points
import json
top=cands[0]
json.dump({"area":top[0],"layer":top[4],"pts":top[8]}, open("boundary.json","w"))
print("\nСохранил крупнейший контур в boundary.json: S=%.0f м2 = %.2f га"%(top[0],top[0]/10000))
