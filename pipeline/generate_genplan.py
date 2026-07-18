#!/usr/bin/env python3
"""
Генератор концепт-генплана коттеджного посёлка из топосъёмки DWG/DXF.

Вход:  топосъёмка .dwg (или .dxf) с замкнутым контуром проектной границы.
Выход: редактируемый DXF (МСК-16) + лист СПОЗУ (PDF/PNG) + ТЭП.

Запуск:
    python generate_genplan.py <топосъёмка.dwg> --out <папка> \
        [--boundary-layer -_линия] [--boundary-color 1] \
        [--front 20] [--depth 45] [--road 7]

Зависимости: ezdxf, shapely, numpy, matplotlib  (+ dwg2dxf из LibreDWG для .dwg)
См. README.md и setup.sh.
"""
import argparse, json, math, os, subprocess, sys, pickle
import numpy as np

# --- глушим строгую проверку linetype у DXF от сторонних CAD (только чтение) ---
def _patch_ezdxf():
    import ezdxf.entities.dxfgfx as dg
    from ezdxf.lldxf import const
    orig = dg.DXFGraphic.post_new_hook
    def safe(self):
        try: orig(self)
        except const.DXFInvalidLineType:
            try: self.dxf.linetype = "BYLAYER"
            except Exception: pass
    dg.DXFGraphic.post_new_hook = safe

def dwg_to_dxf(path, out_dxf):
    """Конвертирует .dwg -> .dxf через dwg2dxf (LibreDWG). .dxf возвращает как есть."""
    if path.lower().endswith(".dxf"):
        return path
    exe = "dwg2dxf"
    for cand in (exe, os.path.expanduser("~/.local/bin/dwg2dxf")):
        try:
            subprocess.run([cand, "-o", out_dxf, path], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return out_dxf
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    sys.exit("dwg2dxf не найден. Установите LibreDWG (см. setup.sh) или подайте .dxf.")

def extract_boundary(dxf_path, layer=None, color=None, target_ha=None):
    """Ищет замкнутый контур проектной границы. Приоритет: слой/цвет, иначе крупнейший
    контур в разумном диапазоне площадей (по умолчанию 5..40 га)."""
    import ezdxf.recover
    from shapely.geometry import Polygon
    doc, _ = ezdxf.recover.readfile(dxf_path)
    msp = doc.modelspace()
    cands = []
    for e in msp.query("LWPOLYLINE POLYLINE"):
        try:
            if e.dxftype() == "LWPOLYLINE":
                pts = [(p[0], p[1]) for p in e.get_points()]
            else:
                pts = [(v.dxf.location[0], v.dxf.location[1]) for v in e.vertices]
        except Exception:
            continue
        if len(pts) < 4:
            continue
        a = 0.0
        for i in range(len(pts)):
            x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % len(pts)]
            a += x1 * y2 - x2 * y1
        area = abs(a) / 2
        cands.append((area, e.dxf.layer, e.dxf.color, pts))
    if not cands:
        sys.exit("В файле не найдено замкнутых полилиний.")
    pool = cands
    if layer is not None:
        pool = [c for c in pool if c[1] == layer] or pool
    if color is not None:
        pool = [c for c in pool if c[2] == int(color)] or pool
    lo, hi = 50000, 400000
    ranged = [c for c in pool if lo < c[0] < hi] or pool
    if target_ha:
        t = target_ha * 10000
        best = min(ranged, key=lambda c: abs(c[0] - t))
    else:
        best = max(ranged, key=lambda c: c[0])
    poly = Polygon(best[3])
    if not poly.is_valid:
        poly = poly.buffer(0)
    return poly, best[0]

def build_plan(site, front=20.0, depth=45.0, road_hw=7.0, connect_w=12.0,
               setback=4.0, min_parcel=250.0):
    from shapely.geometry import box
    from shapely.ops import unary_union
    from shapely.affinity import rotate
    cx, cy = site.centroid.x, site.centroid.y
    pts = np.array(site.exterior.coords)[:-1] - [cx, cy]
    _, _, vt = np.linalg.svd(pts - pts.mean(0), full_matrices=False)
    ang = math.degrees(math.atan2(vt[0][1], vt[0][0]))
    R = rotate(site, -ang, origin=(cx, cy))
    minx, miny, maxx, maxy = R.bounds
    L = maxx - minx
    inset = R.buffer(-setback)
    BLOCK = 2 * depth + 2 * road_hw

    def zrect(fx, fy, w, h):
        x = minx + fx * L; y = miny + fy * (maxy - miny)
        return box(x - w / 2, y - h / 2, x + w / 2, y + h / 2)

    socials = [
        ("Школа – детский сад", "school", zrect(0.50, 0.62, 70, 45), "#ff45ff"),
        ("Мечеть", "mosque", zrect(0.72, 0.70, 26, 26), "#8a2be2"),
        ("Здание бытового обслуж. с магазином", "shop", zrect(0.60, 0.33, 34, 22), "#00c0c0"),
        ("Спортивная площадка", "sport", zrect(0.45, 0.30, 40, 28), "#c0e0ff"),
        ("Детская площадка", "kids", zrect(0.55, 0.70, 26, 20), "#c0e0ff"),
    ]
    social_zone = unary_union([s[2] for s in socials]).buffer(6)

    road_cells = []
    road_ys = list(np.arange(miny + road_hw + depth, maxy, BLOCK))
    for ry in road_ys:
        road_cells.append(box(minx - 5, ry - road_hw, maxx + 5, ry + road_hw))
    for rx in np.arange(minx + 70, maxx, 150):
        road_cells.append(box(rx - connect_w / 2, miny - 5, rx + connect_w / 2, maxy + 5))
    roads = unary_union(road_cells).intersection(inset).difference(social_zone)
    buildable = inset.difference(roads.buffer(0.01)).difference(social_zone)

    HOUSE = {"1F": (10, 10), "2F": (10, 18), "TH": (10, 28)}
    COLOR = {"1F": "#e000e0", "2F": "#1e6ec8", "TH": "#e8896a"}
    items = []
    for ry in road_ys:
        for side in (+1, -1):
            y0, y1 = sorted([ry + side * road_hw, ry + side * (road_hw + depth)])
            x = minx
            while x < maxx:
                cell = box(x, y0, x + front, y1).intersection(buildable)
                if cell.geom_type == "MultiPolygon":
                    cell = max(cell.geoms, key=lambda g: g.area)
                if cell.geom_type == "Polygon" and cell.area >= min_parcel:
                    rx = (cell.centroid.x - minx) / L
                    t = "TH" if rx > 0.80 else ("2F" if 0.63 < rx < 0.72 else "1F")
                    b = cell.bounds; pw = b[2] - b[0]; pd = b[3] - b[1]
                    hw, hl = HOUSE[t]
                    w, l = (max(hw, hl), min(hw, hl)) if pw >= pd else (min(hw, hl), max(hw, hl))
                    ccx, ccy = cell.centroid.x, cell.centroid.y
                    house = box(ccx - w / 2, ccy - l / 2, ccx + w / 2, ccy + l / 2)
                    if not cell.buffer(-1).contains(house):
                        house = house.intersection(cell.buffer(-1))
                    items.append((cell, house, t))
                x += front
    back = lambda g: rotate(g, ang, origin=(cx, cy))
    from collections import Counter
    counts = dict(Counter(t for _, _, t in items))
    return {
        "site": site, "roads": back(roads),
        "parcels": [(back(c), back(h), t) for c, h, t in items],
        "socials": [(n, k, back(r), col) for n, k, r, col in socials],
        "COLOR": COLOR, "counts": counts,
    }

def compute_tep(plan):
    area = lambda g: 0 if g.is_empty else g.area
    S_site = area(plan["site"]); S_roads = area(plan["roads"])
    S = {"1F": 0, "2F": 0, "TH": 0}
    for c, h, t in plan["parcels"]:
        S[t] += area(c)
    S_res = sum(S.values())
    S_soc = sum(area(r) for _, _, r, _ in plan["socials"])
    S_green = max(S_site - S_roads - S_res - S_soc, 0)
    n = plan["counts"]
    pct = lambda x: x / S_site * 100 if S_site else 0
    return [
        ("1", "Общая площадь территории", S_site, 100),
        ("2", "Участки жилой застройки, всего", S_res, pct(S_res)),
        ("2.1", "— одноквартирные (%d уч.)" % n.get("1F", 0), S["1F"], pct(S["1F"])),
        ("2.2", "— двухквартирные 10×18 (%d уч.)" % n.get("2F", 0), S["2F"], pct(S["2F"])),
        ("2.3", "— таунхаусы (%d уч.)" % n.get("TH", 0), S["TH"], pct(S["TH"])),
        ("3", "Участки соц. инфраструктуры", S_soc, pct(S_soc)),
        ("4", "Улицы, проезды, площадки", S_roads, pct(S_roads)),
        ("5", "Озеленение, тер. общего польз.", S_green, pct(S_green)),
    ]

def export_dxf(plan, out_path):
    import ezdxf
    p = plan
    doc = ezdxf.new("R2010", setup=True); doc.header["$INSUNITS"] = 6
    msp = doc.modelspace()
    layers = {"Граница_участка": 1, "Дороги_проезды": 8, "Участки": 94,
              "Дом_1кв": 6, "Дом_2кв": 5, "Таунхаус": 30, "Соцобъект": 211, "Подписи": 7}
    for name, col in layers.items():
        doc.layers.add(name, color=col)

    def poly(g, layer):
        if g.is_empty: return
        for gg in ([g] if g.geom_type == "Polygon" else list(g.geoms)):
            msp.add_lwpolyline([(x, y) for x, y in gg.exterior.coords],
                               dxfattribs={"layer": layer, "closed": True})
    poly(p["site"], "Граница_участка"); poly(p["roads"], "Дороги_проезды")
    lay = {"1F": "Дом_1кв", "2F": "Дом_2кв", "TH": "Таунхаус"}
    for c, h, t in p["parcels"]:
        poly(c, "Участки"); poly(h, lay[t])
    for name, k, rect, col in p["socials"]:
        poly(rect, "Соцобъект")
    doc.saveas(out_path)

def compose_sheet(plan, tep, out_pdf, out_png):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.font_manager import FontProperties
    FP = FontProperties(family="DejaVu Sans")
    site, roads, parcels, socials, COLOR = (plan["site"], plan["roads"],
        plan["parcels"], plan["socials"], plan["COLOR"])
    fig = plt.figure(figsize=(16.5, 11.7), dpi=100); fig.patch.set_facecolor("white")
    fig.add_artist(Rectangle((0.012, 0.012), 0.976, 0.976, fill=False, ec="black",
                             lw=1.5, transform=fig.transFigure))
    axp = fig.add_axes([0.03, 0.06, 0.63, 0.88]); axp.set_aspect("equal"); axp.axis("off")

    def pp(g, **kw):
        if g.is_empty: return
        for gg in ([g] if g.geom_type == "Polygon" else list(g.geoms)):
            xs, ys = gg.exterior.xy; axp.fill(xs, ys, **kw)
    pp(roads, fc="#c8c8c8", ec="none", zorder=1)
    for c, h, t in parcels:
        pp(c, fc="#e8f6d8", ec="#3a7d1e", lw=0.4, zorder=2)
        pp(h, fc=COLOR[t], ec="#333", lw=0.3, zorder=3)
    for name, k, rect, col in socials:
        pp(rect, fc=col, ec="#222", lw=0.8, zorder=3)
        cc = rect.centroid
        axp.annotate(name.split(" с ")[0], (cc.x, cc.y), ha="center", va="center",
                     fontsize=6, zorder=5)
    pp(site, fc="none", ec="red", lw=1.8, zorder=6)
    axp.set_title("Схема планировочной организации земельного участка", fontproperties=FP)
    fig.text(0.67, 0.955, "Пилотный проект коттеджного посёлка", fontproperties=FP,
             fontsize=13, weight="bold")
    fig.text(0.67, 0.90, "Технико-экономические показатели", fontproperties=FP,
             fontsize=10, weight="bold")
    axt = fig.add_axes([0.665, 0.60, 0.325, 0.28]); axt.axis("off")
    tbl = [["№", "Наименование", "м²", "%"]] + \
          [[a, b, f"{s:,.0f}".replace(",", " "), f"{pc:.2f}"] for a, b, s, pc in tep]
    T = axt.table(cellText=tbl, cellLoc="left", colWidths=[0.06, 0.60, 0.20, 0.14],
                  loc="upper left")
    T.auto_set_font_size(False); T.set_fontsize(5.6); T.scale(1, 1.25)
    for (r, c), cell in T.get_celld().items():
        cell.set_linewidth(0.4); cell.get_text().set_fontproperties(FP)
        if r == 0:
            cell.set_facecolor("#dddddd"); cell.set_text_props(weight="bold")
    fig.savefig(out_pdf, facecolor="white"); fig.savefig(out_png, dpi=110, facecolor="white")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("survey", help="топосъёмка .dwg или .dxf")
    ap.add_argument("--out", default="output")
    ap.add_argument("--boundary-layer", default=None)
    ap.add_argument("--boundary-color", default=None)
    ap.add_argument("--target-ha", type=float, default=None,
                    help="ориентир площади участка, га (помогает выбрать контур)")
    ap.add_argument("--front", type=float, default=20.0)
    ap.add_argument("--depth", type=float, default=45.0)
    ap.add_argument("--road", type=float, default=7.0)
    args = ap.parse_args()

    _patch_ezdxf()
    os.makedirs(args.out, exist_ok=True)
    dxf = dwg_to_dxf(args.survey, os.path.join(args.out, "_survey.dxf"))
    site, area = extract_boundary(dxf, args.boundary_layer, args.boundary_color, args.target_ha)
    print(f"Граница: {area/10000:.2f} га")
    plan = build_plan(site, front=args.front, depth=args.depth, road_hw=args.road)
    print("Участки:", plan["counts"])
    tep = compute_tep(plan)
    export_dxf(plan, os.path.join(args.out, "Генплан_МСК16.dxf"))
    compose_sheet(plan, tep, os.path.join(args.out, "СПОЗУ.pdf"),
                  os.path.join(args.out, "СПОЗУ.png"))
    with open(os.path.join(args.out, "ТЭП.json"), "w") as f:
        json.dump([{"№": a, "наим": b, "м2": round(s, 1), "%": round(p, 2)}
                   for a, b, s, p in tep], f, ensure_ascii=False, indent=2)
    print("Готово ->", args.out)

if __name__ == "__main__":
    main()
