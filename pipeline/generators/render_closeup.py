import pickle, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import LightSource
r=pickle.load(open("village_render.pkl","rb"))
faces=r["faces"]; cols=r["cols"]; gx=r["gx"]; gy=r["gy"]; Zg=r["Zg"]
GX,GY=np.meshgrid(gx,gy)
# crop window (local coords) over a dense residential stretch
x0,x1,y0,y1=280,620,180,430
def inwin(fc):
    xs=[p[0] for p in fc]; ys=[p[1] for p in fc]
    return (min(xs)>x0-5 and max(xs)<x1+5 and min(ys)>y0-5 and max(ys)<y1+5)
fsel=[f for f in faces if inwin(f)]; csel=[c for f,c in zip(faces,cols) if inwin(f)]
# terrain subgrid
ix=(gx>=x0)&(gx<=x1); iy=(gy>=y0)&(gy<=y1)
sub=np.ix_(iy,ix)
fig=plt.figure(figsize=(19,10)); ax=fig.add_subplot(111,projection='3d')
ls=LightSource(azdeg=315,altdeg=42)
Zs=Zg[sub]; 
rgb=ls.shade(np.nan_to_num(Zs,nan=np.nanmin(Zg)),cmap=plt.cm.summer,vert_exag=2,blend_mode='soft')
ax.plot_surface(GX[sub],GY[sub],Zs,facecolors=rgb,linewidth=0,antialiased=False,shade=False)
ax.add_collection3d(Poly3DCollection(fsel,facecolors=csel,edgecolors='#33333360',linewidths=0.25))
ax.set_box_aspect((x1-x0,y1-y0,(np.nanmax(Zs)-np.nanmin(Zs)+25)*3.0))
ax.view_init(elev=22,azim=-72); ax.set_axis_off()
ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_zlim(np.nanmin(Zs),np.nanmin(Zs)+45)
fig.savefig("village_closeup.png",dpi=100,bbox_inches='tight',facecolor='white')
print("closeup faces:",len(fsel))
