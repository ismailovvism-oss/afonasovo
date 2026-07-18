import pickle, ezdxf
from ezdxf.enums import TextEntityAlignment
u=pickle.load(open("utils.pkl","rb"))
doc=ezdxf.readfile("Генплан_Афанасово_МСК16.dxf"); msp=doc.modelspace()
LAYC={"Сеть_Водоснабжение":5,"Сеть_Водоотведение":34,"Сеть_Электроснабжение":1,
      "Сеть_Газоснабжение":2,"Инж_сооружения":6}
for n,c in LAYC.items():
    if n not in doc.layers: doc.layers.add(n,color=c)
LMAP={"Водоснабжение":"Сеть_Водоснабжение","Водоотведение":"Сеть_Водоотведение",
      "Электроснабжение":"Сеть_Электроснабжение","Газоснабжение":"Сеть_Газоснабжение"}
def addline(g,layer):
    if g.is_empty: return
    for gg in ([g] if g.geom_type=='LineString' else list(getattr(g,'geoms',[]))):
        msp.add_lwpolyline([(x,y) for x,y in gg.coords],dxfattribs={"layer":layer})
for name,g in u["nets"].items(): addline(g,LMAP[name])
for nm,k,pt,col in u["nodes"]:
    msp.add_circle((pt.x,pt.y),3,dxfattribs={"layer":"Инж_сооружения"})
    msp.add_text(k,dxfattribs={"layer":"Инж_сооружения","height":3}).set_placement((pt.x+4,pt.y),align=TextEntityAlignment.LEFT)
doc.saveas("Генплан_Афанасово_МСК16.dxf")
from collections import Counter
import ezdxf as e2; d2=e2.readfile("Генплан_Афанасово_МСК16.dxf")
print("layers now:",len(d2.layers),"; net entities:",sum(1 for e in d2.modelspace() if e.dxf.layer.startswith('Сеть_')))
