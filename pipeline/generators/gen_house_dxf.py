import ezdxf
from ezdxf.enums import TextEntityAlignment
W=10.0; WALL=0.4
ground=[(0.4,0.4,2.0,1.7,"Тамбур"),(0.4,2.1,2.0,3.0,"Холл"),(0.4,5.1,2.0,4.5,"Постирочная"),
 (2.4,0.4,3.6,9.2,"Кухня-гостиная"),(6.0,0.4,3.6,5.3,"Гараж"),(6.0,5.7,3.6,1.9,"Котельная"),(6.0,7.6,3.6,2.0,"Санузел")]
mansard=[(0.4,0.4,2.0,1.7,"Холл"),(0.4,2.1,2.0,3.0,"Лестница"),(0.4,5.1,2.7,4.5,"Ванная"),
 (2.4,0.4,3.6,4.6,"Спальня 1"),(6.0,0.4,3.6,4.6,"Спальня 2"),(3.1,5.1,2.9,4.5,"Спальня 3"),(6.0,5.1,3.6,4.5,"Гардероб/кабинет")]
doc=ezdxf.new("R2010",setup=True); doc.header['$INSUNITS']=6; msp=doc.modelspace()
for n,c in {"Стены":7,"Перегородки":8,"Помещения":3,"Подписи":2}.items(): doc.layers.add(n,color=c)
def rect(x,y,w,h,layer): msp.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)],dxfattribs={"layer":layer,"closed":True})
def floor(ox,rooms,title):
    rect(ox+0,0,W,W,"Стены"); rect(ox+WALL,WALL,W-2*WALL,W-2*WALL,"Стены")
    for x,y,w,h,name in rooms:
        rect(ox+x,y,w,h,"Перегородки")
        msp.add_text(f"{name} {w*h:.1f}м2",dxfattribs={"layer":"Помещения","height":0.3}).set_placement((ox+x+w/2,y+h/2),align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text(title,dxfattribs={"layer":"Подписи","height":0.5}).set_placement((ox+W/2,-1.2),align=TextEntityAlignment.MIDDLE_CENTER)
floor(0,ground,"План 1-го этажа"); floor(14,mansard,"План мансардного этажа")
doc.saveas("Дом_1кв_планы.dxf")
import ezdxf as e2; d2=e2.readfile("Дом_1кв_планы.dxf")
print("saved Дом_1кв_планы.dxf, entities:",len(list(d2.modelspace())))
