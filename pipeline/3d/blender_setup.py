"""
Авто-настройка сцены Blender из village.obj: импорт, нормали, солнце, небо,
камера, материалы, рендер кадра. Blender 4.x.

Запуск (без окна):
  blender --background --python blender_setup.py -- village.obj out.png [--anim]

Или в Blender: вкладка Scripting → Open → Run (пути правь в CONFIG ниже).

ВНИМАНИЕ: скрипт не тестировался в среде, где он был написан (там нет Blender).
Если упадёт — пришлите текст ошибки, поправим. Логика простая и стандартная.
"""
import bpy, sys, math
from mathutils import Vector

# ---- аргументы после "--" ----
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
OBJ = argv[0] if len(argv) > 0 else "village.obj"
OUT = argv[1] if len(argv) > 1 else "/tmp/render.png"
ANIM = "--anim" in argv

# ---- чистая сцена ----
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

# ---- импорт OBJ (высота = Z) ----
try:
    bpy.ops.wm.obj_import(filepath=OBJ, up_axis="Z", forward_axis="Y")
except Exception:
    bpy.ops.import_scene.obj(filepath=OBJ)   # старый API (Blender 3.x)

meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]

# ---- пересчёт нормалей наружу ----
for o in meshes:
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

# ---- материалы (по имени объекта/материала) ----
def mat(name, rgba, rough=0.8):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = rough
    return m
m_terrain = mat("terrain", (0.28, 0.42, 0.18, 1), 0.95)
m_wall    = mat("wall",    (0.80, 0.66, 0.48, 1), 0.7)
for o in meshes:
    o.data.materials.clear()
    o.data.materials.append(m_terrain if "terrain" in o.name.lower() else m_wall)

# ---- габариты всей сцены ----
mn = Vector(( 1e18,  1e18,  1e18)); mx = Vector((-1e18, -1e18, -1e18))
for o in meshes:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
center = (mn + mx) / 2
size = (mx - mn).length

# ---- пустышка-цель в центре ----
tgt = bpy.data.objects.new("target", None)
bpy.context.collection.objects.link(tgt)
tgt.location = center

# ---- солнце + небо ----
sun_data = bpy.data.lights.new("Sun", type="SUN")
sun_data.energy = 3.0; sun_data.angle = math.radians(3)
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(55), 0, math.radians(35))
world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.55, 0.7, 0.95, 1)   # небо
bg.inputs[1].default_value = 0.5

# ---- камера ----
cam_data = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = center + Vector((size * 0.6, -size * 0.7, size * 0.45))
con = cam.constraints.new("TRACK_TO")
con.target = tgt; con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"
bpy.context.scene.camera = cam

# ---- рендер ----
sc = bpy.context.scene
sc.render.engine = "CYCLES"
try: sc.cycles.samples = 256; sc.cycles.use_denoising = True
except Exception: pass
sc.render.resolution_x = 1920; sc.render.resolution_y = 1080
sc.render.filepath = OUT

if ANIM:
    # облёт: камера по окружности вокруг центра
    sc.frame_start = 1; sc.frame_end = 120
    for f in range(1, 121):
        a = 2 * math.pi * (f - 1) / 120
        cam.location = center + Vector((math.cos(a) * size * 0.6,
                                        math.sin(a) * size * 0.6, size * 0.4))
        cam.keyframe_insert("location", frame=f)
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"
    bpy.ops.render.render(animation=True)
else:
    bpy.ops.render.render(write_still=True)
print("готово ->", OUT)
