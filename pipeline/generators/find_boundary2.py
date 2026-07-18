import _patch, ezdxf, ezdxf.recover, json
doc,aud=ezdxf.recover.readfile("topo.dxf"); msp=doc.modelspace()
def poly_pts(e):
    if e.dxftype()=='LWPOLYLINE': return [(p[0],p[1]) for p in e.get_points()]
    return [(v.dxf.location[0],v.dxf.location[1]) for v in e.vertices]
cands=[]
for e in msp.query('LWPOLYLINE POLYLINE'):
    try: pts=poly_pts(e)
    except Exception: continue
    if len(pts)<4: continue
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    a=0.0
    for i in range(len(pts)):
        x1,y1=pts[i]; x2,y2=pts[(i+1)%len(pts)]; a+=x1*y2-x2*y1
    area=abs(a)/2
    closed = getattr(e,'closed',False) or getattr(e.dxf,'flags',0)
    cands.append((area,max(xs)-min(xs),max(ys)-min(ys),len(pts),e.dxf.layer,e.dxf.color,e.dxf.handle,pts))
# filter area range 150k..270k
sub=[c for c in cands if 150000<c[0]<280000]
sub.sort(reverse=True)
print("Контуры площадью 15..28 га:")
seen=set()
for area,w,h,n,lay,col,hnd,pts in sub:
    key=(round(area),n)
    if key in seen: continue
    seen.add(key)
    print(f"  S={area/10000:6.2f} га  {w:5.0f}x{h:5.0f}м  верш={n:4}  слой={lay[:16]:16} цвет={col} h={hnd}")
# pick the one closest to 21.71 ha, prefer red (col 1) else any
target=217100
best=min(sub, key=lambda c: abs(c[0]-target)) if sub else None
if best:
    json.dump({"area":best[0],"layer":best[4],"pts":best[7]}, open("boundary.json","w"))
    print(f"\nВыбран контур: {best[0]/10000:.2f} га, слой '{best[4]}', вершин {best[3]} -> boundary.json")
