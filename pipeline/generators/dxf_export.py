import pickle, ezdxf
from ezdxf.enums import TextEntityAlignment
p=pickle.load(open("plan.pkl","rb"))
tep=pickle.load(open("tep.pkl","rb"))
doc=ezdxf.new("R2010",setup=True); doc.header['$INSUNITS']=6  # meters
msp=doc.modelspace()
# layers: name, aci color
L={"Граница_участка":1,"Дороги_проезды":8,"Участки":94,"Дом_1кв":6,
   "Дом_2кв":5,"Таунхаус":30,"Соцобъект":211,"Подписи":7,"ТЭП":7}
for name,col in L.items(): doc.layers.add(name,color=col)
def poly(g,layer,closed=True):
    if g.is_empty: return
    for gg in ([g] if g.geom_type=='Polygon' else list(g.geoms)):
        pts=[(x,y) for x,y in gg.exterior.coords]
        msp.add_lwpolyline(pts,dxfattribs={"layer":layer,"closed":closed})
        for ring in gg.interiors:
            msp.add_lwpolyline([(x,y) for x,y in ring.coords],dxfattribs={"layer":layer,"closed":True})
poly(p["site"],"Граница_участка")
poly(p["roads"],"Дороги_проезды")
LAY={'1F':"Дом_1кв",'2F':"Дом_2кв",'TH':"Таунхаус"}
for c,h,t in p["parcels"]:
    poly(c,"Участки"); poly(h,LAY[t])
for name,key,rect,col in p["socials"]:
    poly(rect,"Соцобъект")
    cc=rect.centroid
    msp.add_text(name,dxfattribs={"layer":"Подписи","height":3}).set_placement((cc.x,cc.y),align=TextEntityAlignment.MIDDLE_CENTER)
# TEP table as text block near site, to the NE
b=p["site"].bounds; tx=b[2]+20; ty=b[3]
lines=["ТЕХНИКО-ЭКОНОМИЧЕСКИЕ ПОКАЗАТЕЛИ",""]
for a,name,s,pc in tep["rows"]:
    lines.append(f"{a:4} {name:52} {s:11.1f} м2  {pc:6.2f}%")
mt=msp.add_mtext("\\P".join(lines),dxfattribs={"layer":"ТЭП","char_height":4,"style":"OpenSans"})
mt.set_location((tx,ty))
msp.add_text("Пилотный проект коттеджного посёлка. н.п. Б.Афанасово. СПОЗУ. СК МСК-16.",
             dxfattribs={"layer":"Подписи","height":6}).set_placement((b[0],b[1]-20))
doc.saveas("Генплан_Афанасово_МСК16.dxf")
print("saved Генплан_Афанасово_МСК16.dxf  layers:",len(L),"parcels:",len(p["parcels"]))
# verify by reading back
import ezdxf as e2
d2=e2.readfile("Генплан_Афанасово_МСК16.dxf")
from collections import Counter
c=Counter(en.dxf.layer for en in d2.modelspace())
print("read back OK, entities per layer:",dict(c))
