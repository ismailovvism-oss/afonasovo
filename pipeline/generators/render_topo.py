import _patch
import ezdxf, ezdxf.recover
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
doc,aud=ezdxf.recover.readfile("topo.dxf"); msp=doc.modelspace()
xs=[];ys=[]
for e in msp.query('POINT'):
    p=e.dxf.location; xs.append(p[0]); ys.append(p[1])
xs.sort(); ys.sort()
def pct(a,q): return a[int(q*(len(a)-1))]
x0,x1=pct(xs,.01),pct(xs,.99); y0,y1=pct(ys,.01),pct(ys,.99)
mx=(x1-x0)*0.08; my=(y1-y0)*0.08
fig=plt.figure(figsize=(20,12)); ax=fig.add_axes([0,0,1,1]); ax.set_facecolor('white')
Frontend(RenderContext(doc),MatplotlibBackend(ax)).draw_layout(msp,finalize=False)
ax.set_xlim(x0-mx,x1+mx); ax.set_ylim(y0-my,y1+my); ax.set_aspect('equal'); ax.axis('off')
fig.savefig("topo_full.png",dpi=72,facecolor='white'); print("saved core bbox:", int(x0),int(y0),"-",int(x1),int(y1))
