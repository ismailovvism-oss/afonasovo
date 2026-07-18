import _patch, ezdxf
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
doc=ezdxf.readfile("Генплан_Афанасово_МСК16.dxf"); msp=doc.modelspace()
fig=plt.figure(figsize=(18,11)); ax=fig.add_axes([0,0,1,1])
Frontend(RenderContext(doc),MatplotlibBackend(ax)).draw_layout(msp,finalize=True)
ax.axis('off'); fig.savefig("dxf_roundtrip.png",dpi=80,facecolor='white'); print("ok")
