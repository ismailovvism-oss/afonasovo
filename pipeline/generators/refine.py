import ezdxf, statistics as st
doc=ezdxf.readfile("topo.dxf"); msp=doc.modelspace()
# elevations from layer ВЫСОТА (heights) and POINTS z
heights=[]
for e in msp.query('TEXT'):
    if e.dxf.layer in ("ВЫСОТА",):
        try: heights.append(float(e.dxf.text.replace(',','.')))
        except: pass
pts=[]
for e in msp.query('POINT'):
    p=e.dxf.location; pts.append((p[0],p[1],p[2]))
xs=sorted(p[0] for p in pts); ys=sorted(p[1] for p in pts)
def pct(a,q): return a[int(q*(len(a)-1))]
print("Съёмочных точек (POINT):", len(pts))
print(f"Реальный охват участка (2.5–97.5 перцентиль, отсев выбросов):")
print(f"  X: {pct(xs,.025):.1f} .. {pct(xs,.975):.1f}  → ~{pct(xs,.975)-pct(xs,.025):.0f} м")
print(f"  Y: {pct(ys,.025):.1f} .. {pct(ys,.975):.1f}  → ~{pct(ys,.975)-pct(ys,.025):.0f} м")
if heights:
    print(f"\nОтметки рельефа (слой ВЫСОТА, {len(heights)} шт):")
    print(f"  мин {min(heights):.2f}  макс {max(heights):.2f}  перепад {max(heights)-min(heights):.2f} м  медиана {st.median(heights):.2f}")
# cadastral-ish closed polylines on boundary layers
import collections
poly=collections.Counter()
for e in msp.query('LWPOLYLINE'):
    poly[e.dxf.layer]+=1
print("\nПолилинии по слоям (границы/контуры):")
for l,c in poly.most_common(10): print(f"  {c:4}  {l}")
