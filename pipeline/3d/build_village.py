import pickle, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import LightSource
d=np.load("dem.npz"); gx=d["gx"]; gy=d["gy"]; GZ=d["GZ"]; mask=d["mask"]; ox=float(d["ox"]); oy=float(d["oy"])
Zg=np.where(mask&np.isfinite(GZ),GZ,np.nan)
def zof(x,y):  # bilinear sample local coords
    fx=np.clip((x-gx[0])/(gx[1]-gx[0]),0,len(gx)-1.001); fy=np.clip((y-gy[0])/(gy[1]-gy[0]),0,len(gy)-1.001)
    i,j=int(fx),int(fy); tx,ty=fx-i,fy-j
    def g(a,b):
        v=GZ[b,a]; return v if np.isfinite(v) else np.nanmedian(GZ[np.isfinite(GZ)])
    return (g(i,j)*(1-tx)*(1-ty)+g(i+1,j)*tx*(1-ty)+g(i,j+1)*(1-tx)*ty+g(i+1,j+1)*tx*ty)
plan=pickle.load(open("plan.pkl","rb"))
COLOR={'1F':'#c98b6a','2F':'#c98b6a','TH':'#b56a4a'}
ROOF={'1F':'#8a3b2a','2F':'#8a3b2a','TH':'#6a2b1a'}
HT={'1F':(6,3),'2F':(6,3),'TH':(6,3)}
def local(poly): return [(x-ox,y-oy) for x,y in poly.exterior.coords[:-1]]
def building(fp,hw,rise,wallc,roofc):
    ring=local(fp); n=len(ring)
    zb=zof(*np.mean(ring,axis=0))
    verts=[]; faces=[]; cols=[]
    base=[(x,y,zb) for x,y in ring]; top=[(x,y,zb+hw) for x,y in ring]
    apex=(np.mean([p[0] for p in ring]),np.mean([p[1] for p in ring]),zb+hw+rise)
    verts=base+top+[apex]; A=apex
    for i in range(n):
        a,b=i,(i+1)%n
        faces.append([base[a],base[b],top[b],top[a]]); cols.append(wallc)   # wall
        faces.append([top[a],top[b],A]); cols.append(roofc)                 # roof
    return faces,cols
allfaces=[]; allcols=[]; obj_v=[]; obj_f=[]; obj_g=[]
def add_obj(faces,gname):
    obj_g.append((gname,len(obj_f)))
    for fc in faces:
        base=len(obj_v)
        for v in fc: obj_v.append(v)
        obj_f.append(tuple(range(base+1,base+1+len(fc))))
for c,h,t in plan["parcels"]:
    hw,rise=HT[t]; fa,co=building(h,hw,rise,COLOR[t],ROOF[t])
    allfaces+=fa; allcols+=co; add_obj(fa,"house_"+t)
SOC={'school':(7,2,'#d9d0c0','#7a5a3a'),'mosque':(9,6,'#e8e0d0','#3a7a5a'),
     'shop':(5,1.5,'#cfe0d0','#5a7a5a'),'sport':(0.3,0.1,'#9fd08f','#9fd08f'),'kids':(0.3,0.1,'#9fd08f','#9fd08f')}
for name,key,rect,col in plan["socials"]:
    hw,rise,wc,rc=SOC.get(key,(6,2,'#ddd','#888'))
    fa,co=building(rect,hw,rise,wc,rc); allfaces+=fa; allcols+=co; add_obj(fa,"soc_"+key)

# ---- render ----
fig=plt.figure(figsize=(19,11)); ax=fig.add_subplot(111,projection='3d')
GX,GY=np.meshgrid(gx,gy)
ls=LightSource(azdeg=315,altdeg=45)
rgb=ls.shade(np.nan_to_num(Zg,nan=np.nanmin(Zg)),cmap=plt.cm.terrain,vert_exag=2,blend_mode='soft')
ax.plot_surface(GX,GY,Zg,facecolors=rgb,rstride=1,cstride=1,linewidth=0,antialiased=False,shade=False,zorder=1)
pc=Poly3DCollection(allfaces,facecolors=allcols,edgecolors='#20202030',linewidths=0.2)
ax.add_collection3d(pc)
ax.set_box_aspect((gx.max(),gy.max(),(np.nanmax(Zg)-np.nanmin(Zg))*3))
ax.view_init(elev=38,azim=-60); ax.set_axis_off()
ax.set_xlim(0,gx.max()); ax.set_ylim(0,gy.max()); ax.set_zlim(np.nanmin(Zg),np.nanmin(Zg)+70)
fig.savefig("village3d.png",dpi=95,bbox_inches='tight',facecolor='white')
print("saved village3d.png; buildings:",len(plan["parcels"])+len(plan["socials"]))

# ---- export combined OBJ (village) ----
with open("village.obj","w") as f:
    f.write("# village massing, local origin ox=%.2f oy=%.2f\n"%(ox,oy))
    f.write("mtllib village.mtl\n")
    # terrain
    import numpy as _np
    f.write("o terrain\n")
    # reuse terrain.obj verts/faces
    tv=[];tf=[]
    for line in open("terrain.obj"):
        if line.startswith("v "): f.write(line)
        elif line.startswith("f "): tf.append(line)
    nvert_terrain=sum(1 for l in open("terrain.obj") if l.startswith("v "))
    f.write("usemtl terrain\n"); 
    for l in tf: f.write(l)
    # buildings (offset indices by terrain verts)
    off=nvert_terrain
    f.write("o buildings\n")
    for v in obj_v: f.write("v %.3f %.3f %.3f\n"%(v[0],v[1],v[2]))
    last=None
    for gname,fi in obj_g:
        pass
    f.write("usemtl building\n")
    for fc in obj_f:
        f.write("f "+" ".join(str(i+off) for i in fc)+"\n")
open("village.mtl","w").write(
"newmtl terrain\nKd 0.45 0.55 0.35\n\nnewmtl building\nKd 0.78 0.55 0.42\n")
print("saved village.obj + village.mtl  (terrain verts %d + building verts %d)"%(nvert_terrain,len(obj_v)))
pickle.dump({"faces":allfaces,"cols":allcols,"gx":gx,"gy":gy,"Zg":Zg},open("village_render.pkl","wb"))
