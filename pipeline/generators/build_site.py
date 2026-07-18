import base64, os, re
R="/home/qaadiy/projects/architect/результат_v2"
def datauri(path, mime):
    b=base64.b64encode(open(path,"rb").read()).decode()
    return f"data:{mime};base64,{b}"
IMG={k:datauri(f"web/{k}.jpg","image/jpeg") for k in
     ["genplan","seti","dorogi","domplan","topo","village","kvartal","dom3d",
      "orig","fasady","situ","cover"]}
VID=datauri("village_flythrough.mp4","video/mp4")
DL={
 "DL_DXF_GEN":  datauri(f"{R}/Генплан_Афанасово_МСК16.dxf","application/dxf"),
 "DL_DXF_HOUSE":datauri(f"{R}/Дом_1кв_планы.dxf","application/dxf"),
 "DL_PDF_GEN":  datauri(f"{R}/Лист 3 - СПОЗУ (генплан).pdf","application/pdf"),
 "DL_PDF_SETI": datauri(f"{R}/Лист 4 - Сводный план инженерных сетей.pdf","application/pdf"),
 "DL_PDF_DOR":  datauri(f"{R}/Лист 6 - Планы дорог. Разрезы.pdf","application/pdf"),
 "DL_PDF_DOM":  datauri(f"{R}/Лист 8 - Одноквартирный дом. Планы этажей.pdf","application/pdf"),
}
TPL=open("template.html","r",encoding="utf-8").read()
for k,v in IMG.items(): TPL=TPL.replace("@@%s@@"%k.upper(), v)
for k,v in DL.items():  TPL=TPL.replace("@@%s@@"%k, v)
TPL=TPL.replace("@@VIDEO@@", VID)
open("artifact.html","w",encoding="utf-8").write(TPL)
print("artifact.html:", os.path.getsize("artifact.html")//1024, "KB")
left=set(re.findall(r'@@[A-Z_]+@@', TPL))
print("leftover tokens:", left or "none")
