#!/usr/bin/env python3
"""Экспорт сцены для 3D-прогулки (three.js): рельеф(base64 float32)+дома+дороги.
Вход: plan.pkl, dem.npz, utils.pkl, boundary.json (в ../data/ или рядом).
Выход: scene.json — потребляется web/walk_tpl.html.
Запуск: ../venv/bin/python export_scene.py   (из папки с данными)"""
import pickle, json, numpy as np, base64, math
dem=np.load("dem.npz"); gx=dem["gx"]; gy=dem["gy"]; GZ=dem["GZ"]; mask=dem["mask"]
ox=float(dem["ox"]); oy=float(dem["oy"])
s=2
gx2=gx[::s]; gy2=gy[::s]; Z=GZ[::s,::s]; M=(mask[::s,::s]&np.isfinite(Z))
Zf=np.where(np.isfinite(Z),Z,-9999.0).astype(np.float32)
nx,ny=len(gx2),len(gy2); step=float(gx2[1]-gx2[0])
b64=lambda a: base64.b64encode(np.ascontiguousarray(a)).decode()
terrain={"nx":nx,"ny":ny,"step":step,"z":b64(Zf.ravel()),
         "mask":b64(M.astype(np.uint8).ravel()),
         "zmin":float(np.nanmin(Z[np.isfinite(Z)])),"zmax":float(np.nanmax(Z[np.isfinite(Z)]))}
plan=pickle.load(open("plan.pkl","rb")); TIDX={'1F':0,'2F':1,'TH':2}
def box_of(poly):
    p=list(poly.exterior.coords)[:-1]; (x0,y0),(x1,y1),(x2,y2)=p[0],p[1],p[2]
    l1=math.hypot(x1-x0,y1-y0); l2=math.hypot(x2-x1,y2-y1); ang=math.atan2(y1-y0,x1-x0)
    c=poly.centroid; return round(c.x-ox,2),round(c.y-oy,2),round(ang,4),round(l1,2),round(l2,2)
houses=[[*box_of(h),TIDX[t]] for cell,h,t in plan["parcels"]]
SOC={'school':(7,'#c86a86'),'mosque':(9,'#6a9a86'),'shop':(5,'#5a9a9a'),
     'sport':(0.3,'#9fc27a'),'kids':(0.3,'#9fc27a')}; SK=list(SOC.keys())
socials=[]
for name,key,rect,col in plan["socials"]:
    cx,cy,ang,l1,l2=box_of(rect); h,_=SOC.get(key,(6,'#ccc'))
    socials.append([cx,cy,ang,l1,l2,round(h,1),SK.index(key)])
u=pickle.load(open("utils.pkl","rb"))
roads=[[[round(x-ox,2),round(y-oy,2)] for x,y in g.coords] for g in u["segs"] if len(g.coords)>=2]
bnd=[[round(x-ox,2),round(y-oy,2)] for x,y in plan["site"].exterior.coords]
longest=max(u["segs"],key=lambda g:g.length); mp=longest.interpolate(0.5,normalized=True)
scene={"terrain":terrain,"houses":houses,"socials":socials,
       "soc_colors":[SOC[k][1] for k in SK],"roads":roads,"boundary":bnd,
       "spawn":[round(mp.x-ox,2),round(mp.y-oy,2)],"houseWall":6.0,"houseRoof":3.0}
json.dump(scene,open("scene.json","w"))
print("scene.json:",len(houses),"houses,",len(roads),"roads, grid",nx,"x",ny)
