import ezdxf
from collections import Counter, defaultdict
doc = ezdxf.readfile("topo.dxf")
msp = doc.modelspace()
print("DXF version:", doc.dxfversion, "->", doc.acad_release)
# layers
layers = list(doc.layers)
print(f"\nСлоёв: {len(layers)}")
# entity counts overall and per layer
etype = Counter()
per_layer = Counter()
per_layer_types = defaultdict(Counter)
xs=[]; ys=[]
texts=[]
for e in msp:
    t=e.dxftype(); etype[t]+=1
    lay=e.dxf.layer; per_layer[lay]+=1; per_layer_types[lay][t]+=1
    if t in ("TEXT","MTEXT"):
        try:
            s=e.plain_text() if t=="MTEXT" else e.dxf.text
            if s and s.strip(): texts.append(s.strip())
        except: pass
    # collect coords for extents
    try:
        if hasattr(e,"dxf") and e.dxftype() in ("LINE",):
            for p in (e.dxf.start,e.dxf.end): xs.append(p[0]); ys.append(p[1])
        elif t in ("LWPOLYLINE",):
            for p in e.get_points(): xs.append(p[0]); ys.append(p[1])
        elif t in ("POINT","TEXT","MTEXT","INSERT","CIRCLE"):
            p=e.dxf.insert if t in ("TEXT","MTEXT","INSERT") else (e.dxf.location if t=="POINT" else e.dxf.center)
            xs.append(p[0]); ys.append(p[1])
    except: pass
print("\n=== Типы объектов (всего) ===")
for t,c in etype.most_common(): print(f"  {t:16} {c}")
print(f"\n=== Топ-25 слоёв по числу объектов ===")
for lay,c in per_layer.most_common(25):
    tt=", ".join(f"{k}:{v}" for k,v in per_layer_types[lay].most_common(3))
    print(f"  {c:6}  {lay[:45]:45}  [{tt}]")
if xs:
    print(f"\n=== Габариты (координаты МСК-16) ===")
    print(f"  X: {min(xs):.2f} .. {max(xs):.2f}  (ширина {max(xs)-min(xs):.1f} м)")
    print(f"  Y: {min(ys):.2f} .. {max(ys):.2f}  (высота {max(ys)-min(ys):.1f} м)")
print(f"\n=== Текстовых надписей: {len(texts)} (пример) ===")
for s in texts[:30]: print("   ", s[:70])
