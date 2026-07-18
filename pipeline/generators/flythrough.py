import pickle, numpy as np, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import LightSource
r=pickle.load(open("village_render.pkl","rb"))
faces=r["faces"]; cols=r["cols"]; gx=r["gx"]; gy=r["gy"]; Zg=r["Zg"]
GX,GY=np.meshgrid(gx,gy)
ls=LightSource(azdeg=315,altdeg=42)
# precompute face bbox for culling
fb=[(min(p[0] for p in f),max(p[0] for p in f),min(p[1] for p in f),max(p[1] for p in f)) for f in faces]
zmin=np.nanmin(Zg)
N=90
xc0,xc1=170,820
def yc_of(x): return 150+(x-170)/(820-170)*(360-150)
WX,WY=190,150
for k in range(N):
    t=k/(N-1)
    xc=xc0+(xc1-xc0)*t; yc=yc_of(xc)
    x0,x1=xc-WX,xc+WX; y0,y1=yc-WY,yc+WY
    ix=(gx>=x0)&(gx<=x1); iy=(gy>=y0)&(gy<=y1)
    if ix.sum()<2 or iy.sum()<2: continue
    sub=np.ix_(iy,ix)
    fig=plt.figure(figsize=(12.8,7.2)); ax=fig.add_subplot(111,projection='3d')
    Zs=Zg[sub]
    rgb=ls.shade(np.nan_to_num(Zs,nan=zmin),cmap=plt.cm.summer,vert_exag=2.5,blend_mode='soft')
    ax.plot_surface(GX[sub],GY[sub],Zs,facecolors=rgb,linewidth=0,antialiased=False,shade=False)
    sel=[i for i,(a,b,c,d) in enumerate(fb) if a>x0-10 and b<x1+10 and c>y0-10 and d<y1+10]
    if sel:
        ax.add_collection3d(Poly3DCollection([faces[i] for i in sel],
            facecolors=[cols[i] for i in sel],edgecolors='#33333340',linewidths=0.2))
    azim=-78+18*np.sin(t*np.pi*2)         # gentle pan
    elev=20+6*np.sin(t*np.pi)             # rise then fall
    ax.view_init(elev=elev,azim=azim)
    ax.set_box_aspect((x1-x0,y1-y0,(np.nanmax(Zs)-np.nanmin(Zs)+25)*3.2))
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_zlim(np.nanmin(Zs),np.nanmin(Zs)+45)
    ax.set_axis_off()
    fig.subplots_adjust(0,0,1,1)
    fig.savefig(f"frames/f{k:03d}.png",dpi=72,facecolor='#eef4f7'); plt.close(fig)
    if k%15==0: print("frame",k)
print("frames done")
