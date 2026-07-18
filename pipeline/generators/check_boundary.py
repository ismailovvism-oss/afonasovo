import json, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
d=json.load(open("boundary.json")); pts=d["pts"]
xs=[p[0] for p in pts]+[pts[0][0]]; ys=[p[1] for p in pts]+[pts[0][1]]
fig,ax=plt.subplots(figsize=(14,9))
ax.plot(xs,ys,'-',color='red',lw=1.5)
ax.fill(xs,ys,color='red',alpha=0.08)
ax.plot(xs[0],ys[0],'go',ms=8,label='start'); ax.plot(xs[-2],ys[-2],'bs',ms=6,label='end')
ax.set_aspect('equal'); ax.legend(); ax.set_title(f"Boundary {d['area']/10000:.2f} ha, {len(pts)} verts")
fig.savefig("boundary_check.png",dpi=80,bbox_inches='tight')
# closure gap
import math
gap=math.hypot(pts[0][0]-pts[-1][0], pts[0][1]-pts[-1][1])
print(f"vertices={len(pts)} area={d['area']/10000:.2f}ha closure_gap={gap:.2f}m bbox={max(xs)-min(xs):.0f}x{max(ys)-min(ys):.0f}m")
