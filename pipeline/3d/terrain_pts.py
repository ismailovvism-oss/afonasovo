import _patch, ezdxf, ezdxf.recover, json
from shapely.geometry import Polygon, Point
doc,aud=ezdxf.recover.readfile("topo.dxf"); msp=doc.modelspace()
site=Polygon(json.load(open("boundary.json"))["pts"]); env=site.buffer(80)
pts=[]
for e in msp.query('TEXT'):
    if e.dxf.layer!="ВЫСОТА": continue
    try: z=float(e.dxf.text.replace(',','.'))
    except: continue
    p=e.dxf.insert; 
    if 60<z<130 and env.contains(Point(p[0],p[1])):   # sane elevations, near site
        pts.append((p[0],p[1],z))
print("terrain points near site:",len(pts))
zs=[p[2] for p in pts]
print("z range: %.2f .. %.2f  span %.2f m"%(min(zs),max(zs),max(zs)-min(zs)))
json.dump(pts,open("terrain_pts.json","w"))
