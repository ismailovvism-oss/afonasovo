import json, numpy as np, pickle
import matplotlib; matplotlib.use("Agg")
import matplotlib.tri as mtri
from matplotlib.path import Path
from shapely.geometry import Polygon
pts=np.array(json.load(open("terrain_pts.json")))
site=Polygon(json.load(open("boundary.json"))["pts"])
X,Y,Z=pts[:,0],pts[:,1],pts[:,2]
ox,oy=X.min(),Y.min()             # local origin for small coords
xl,yl=X-ox,Y-oy
tri=mtri.Triangulation(xl,yl)
interp=mtri.LinearTriInterpolator(tri,Z)
# regular DEM grid
step=3.0
gx=np.arange(0,xl.max()+step,step); gy=np.arange(0,yl.max()+step,step)
GX,GY=np.meshgrid(gx,gy)
GZ=interp(GX,GY)                    # masked array outside hull
# fill small gaps with nearest via triangulation already; outside hull -> nan
GZ=np.array(GZ.filled(np.nan))
# site mask (local coords)
ext=np.array(site.exterior.coords)-[ox,oy]
mask_in=Path(ext).contains_points(np.column_stack([GX.ravel(),GY.ravel()])).reshape(GX.shape)
np.savez("dem.npz",gx=gx,gy=gy,GZ=GZ,mask=mask_in,ox=ox,oy=oy)
valid=np.isfinite(GZ)&mask_in
print("DEM grid %dx%d, valid cells: %d, z %.1f..%.1f"%(GX.shape[1],GX.shape[0],valid.sum(),np.nanmin(GZ[valid]),np.nanmax(GZ[valid])))

# export terrain OBJ (triangulated grid, only cells inside site & finite)
def write_terrain_obj(fn,exagg=1.0):
    idx=np.full(GX.shape,-1,int); c=0; verts=[]
    for j in range(GX.shape[0]):
        for i in range(GX.shape[1]):
            if valid[j,i]:
                idx[j,i]=c; c+=1
                verts.append((gx[i],gy[j],GZ[j,i]*exagg))
    faces=[]
    for j in range(GX.shape[0]-1):
        for i in range(GX.shape[1]-1):
            a,b,cc,d=idx[j,i],idx[j,i+1],idx[j+1,i+1],idx[j+1,i]
            if min(a,b,cc,d)>=0:
                faces.append((a,b,cc)); faces.append((a,cc,d))
    with open(fn,"w") as f:
        f.write("# terrain MSK-16 local origin ox=%.2f oy=%.2f (meters)\n"%(ox,oy))
        for v in verts: f.write("v %.3f %.3f %.3f\n"%v)
        for fa in faces: f.write("f %d %d %d\n"%(fa[0]+1,fa[1]+1,fa[2]+1))
    return len(verts),len(faces)
nv,nf=write_terrain_obj("terrain.obj")
print("terrain.obj:",nv,"verts",nf,"faces")
