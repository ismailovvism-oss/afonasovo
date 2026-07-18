import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
W=10.0; H1=3.2; H2=6.4; RIDGE=9.2   # storey heights, ridge
faces=[]; cols=[]
WALL='#e8dcc5'; ROOF='#7a3826'; WIN='#3b4a63'; DOOR='#5a3b22'; GAR='#8a5a34'; BASE='#cfc2ad'
def quad(p,c): faces.append(p); cols.append(c)
# box walls 0..W x 0..W, up to H2
c=[(0,0),(W,0),(W,W),(0,W)]
for i in range(4):
    a,b=c[i],c[(i+1)%4]
    quad([(a[0],a[1],0),(b[0],b[1],0),(b[0],b[1],H2),(a[0],a[1],H2)],WALL)
# gable roof: ridge along x at y=W/2
ridge=[(0,W/2,RIDGE),(W,W/2,RIDGE)]
quad([(0,0,H2),(W,0,H2),ridge[1],ridge[0]],ROOF)     # front slope
quad([(0,W,H2),(W,W,H2),ridge[1],ridge[0]],ROOF)     # back slope
quad([(0,0,H2),(0,W,H2),ridge[0]],WALL)              # gable triangle L
quad([(W,0,H2),(W,W,H2),ridge[1]],WALL)              # gable triangle R
# windows on front (y=0): grid
def win(x0,z0,w,h,face='S'):
    if face=='S': quad([(x0,0.02,z0),(x0+w,0.02,z0),(x0+w,0.02,z0+h),(x0,0.02,z0+h)],WIN)
    if face=='E': quad([(W-0.02,x0,z0),(W-0.02,x0+w,z0),(W-0.02,x0+w,z0+h),(W-0.02,x0,z0+h)],WIN)
for zx in (1.0,7.6):
    win(zx,1.0,1.5,1.5); win(zx,4.2,1.5,1.5)
win(3.2,4.2,1.6,1.5); win(3.2,1.2,1.4,2.0)   # ground center + upper
# door
quad([(2.9,0.02,0),(3.9,0.02,0),(3.9,0.02,2.1),(2.9,0.02,2.1)],DOOR)
# integrated garage door on front-right
quad([(6.3,0.02,0),(9.3,0.02,0),(9.3,0.02,2.4),(6.3,0.02,2.4)],GAR)
# side windows east
win(2.0,2.0,1.4,1.5,'E'); win(6.0,4.5,1.4,1.5,'E')
# ground plane
G=16
gp=[(-3,-3,0),(W+3,-3,0),(W+3,W+3,0),(-3,W+3,0)]; quad(gp,'#9fc27a')

fig=plt.figure(figsize=(14,10)); ax=fig.add_subplot(111,projection='3d')
ax.add_collection3d(Poly3DCollection(faces,facecolors=cols,edgecolors='#2a2a2a',linewidths=0.4))
ax.set_box_aspect((1,1,0.75))
ax.set_xlim(-3,W+3); ax.set_ylim(-3,W+3); ax.set_zlim(0,RIDGE+1)
ax.view_init(elev=20,azim=-52); ax.set_axis_off()
ax.set_title("Одноквартирный 2-эт. жилой дом 10×10 — 3D вид (собственная модель)",fontsize=13)
fig.savefig("house3d.png",dpi=100,bbox_inches='tight',facecolor='white')
# export OBJ
with open("house3d.obj","w") as f:
    f.write("# one-family house 10x10\n"); vi=1
    for fc in faces:
        for v in fc: f.write("v %.3f %.3f %.3f\n"%v)
        f.write("f "+" ".join(str(vi+k) for k in range(len(fc)))+"\n"); vi+=len(fc)
print("saved house3d.png + house3d.obj  faces:",len(faces))
