# Builds the floating crystal cluster for the moving islands (BP_MovingIsland; the user, 2026-11-19: "a glowing crystal
# under the island, that keeps it afloat"): SourceArt/Models/Crystal/SM_FloatCrystal.fbx, one material slot
# (M_FloatCrystal). Its pivot is at the top, where it goes into the island's rock; it hangs down -Z: a long hexagonal
# crystal (1.4 m, pointed at both ends) and two shorter ones leaning out of it. Flat-shaded facets. Run:
#   blender --background --factory-startup --python build_float_crystal.py
import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "Crystal")
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)


def crystal(bm, length, radius, tilt_deg, yaw_deg, start):
    # A hexagonal prism with a point at each end, along -Z from `start`, then tilted and turned.
    tip = radius * 1.6
    rings = []
    for z in (-tip * 0.5, -(length - tip)):
        rings.append([bm.verts.new((radius * math.cos(math.radians(60 * k + 30)), radius * math.sin(math.radians(60 * k + 30)), z)) for k in range(6)])
    top = bm.verts.new((0.0, 0.0, 0.0))
    bottom = bm.verts.new((0.0, 0.0, -length))
    a, b = rings
    for k in range(6):
        j = (k + 1) % 6
        bm.faces.new((a[j], a[k], top))
        bm.faces.new((a[k], a[j], b[j], b[k]))
        bm.faces.new((b[k], b[j], bottom))
    turn = Matrix.Translation(start) @ Matrix.Rotation(math.radians(yaw_deg), 4, "Z") @ Matrix.Rotation(math.radians(tilt_deg), 4, "X")
    for v in list(a) + list(b) + [top, bottom]:
        v.co = turn @ v.co


bm = bmesh.new()
crystal(bm, 1.4, 0.2, 0.0, 0.0, Vector((0.0, 0.0, 0.0)))
crystal(bm, 0.8, 0.12, 28.0, 30.0, Vector((0.08, 0.0, -0.15)))
crystal(bm, 0.65, 0.1, 32.0, 200.0, Vector((-0.07, 0.03, -0.1)))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
uv = bm.loops.layers.uv.new("UVMap")
for face in bm.faces:
    for loop in face.loops:
        loop[uv].uv = (loop.vert.co.x + 0.5, loop.vert.co.z + 0.5)
mesh = bpy.data.meshes.new("SM_FloatCrystal")
bm.to_mesh(mesh)
bm.free()
obj = bpy.data.objects.new("SM_FloatCrystal", mesh)
bpy.context.scene.collection.objects.link(obj)
obj.data.materials.append(bpy.data.materials.new("M_FloatCrystal"))
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, "SM_FloatCrystal.fbx"), use_selection=True, apply_unit_scale=True,
                         mesh_smooth_type="FACE")
print("crystal", os.path.join(OUT, "SM_FloatCrystal.fbx"), len(mesh.polygons), "faces")
