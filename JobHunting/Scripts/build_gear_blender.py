# Builds the gear for the machine tower (area 2) in Blender: a flat toothed wheel lying in XY (turning about Z), with
# a raised hub. Used for the spinning gear platforms (BP_SpinGear) and, stood on edge, for decoration. Its outer radius
# (tooth tips) is 100 cm and it is 30 cm thick, centred on the origin, so the top is at Z +15: scale the actor for
# other sizes. Material slots: 0 M_GearIron (the wheel), 1 M_GearBrass (the hub and the teeth faces). Saves
# Gear.blend and SM_Gear.fbx in SourceArt/Models/Gear and renders a preview. Run:
#   blender --background --factory-startup --python build_gear_blender.py [-- <preview folder>]
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SourceArt", "Models", "Gear"))
CM = 0.01
TEETH = 14
OUTER = 100.0      # tooth tips
ROOT = 84.0        # between the teeth
HALF = 15.0        # half the thickness
HUB = 26.0         # hub radius
HUB_RAISE = 6.0
SPOKE_HOLES = 6
HOLE_R = 13.0
HOLE_AT = 52.0


def outline():
    # The toothed rim as one loop: each tooth a flat-topped trapezoid.
    points = []
    step = 2.0 * math.pi / TEETH
    for i in range(TEETH):
        a = i * step
        for frac, r in ((0.0, ROOT), (0.18, OUTER), (0.47, OUTER), (0.65, ROOT)):
            t = a + frac * step
            points.append((r * math.cos(t), r * math.sin(t)))
    return points


def add_face(bm, verts, expect, slot=0):
    face = bm.faces.new(verts)
    face.normal_update()
    if face.normal.dot(expect) < 0.0:
        face.normal_flip()
    face.material_index = slot
    return face


def prism(bm, loop, z0, z1, slot_side, slot_cap):
    # A solid from a 2D loop: caps at z0 and z1, sides between. Caps are fanned from the centre.
    low = [bm.verts.new((x * CM, y * CM, z0 * CM)) for x, y in loop]
    high = [bm.verts.new((x * CM, y * CM, z1 * CM)) for x, y in loop]
    cx = sum(p[0] for p in loop) / len(loop)
    cy = sum(p[1] for p in loop) / len(loop)
    centre_low = bm.verts.new((cx * CM, cy * CM, z0 * CM))
    centre_high = bm.verts.new((cx * CM, cy * CM, z1 * CM))
    n = len(loop)
    for i in range(n):
        j = (i + 1) % n
        mid = (Vector(low[i].co) + Vector(low[j].co)) / 2.0
        add_face(bm, [low[i], low[j], high[j], high[i]], Vector((mid.x - cx * CM, mid.y - cy * CM, 0.0)), slot_side)
        add_face(bm, [high[i], high[j], centre_high], Vector((0, 0, 1)), slot_cap)
        add_face(bm, [low[i], low[j], centre_low], Vector((0, 0, -1)), slot_cap)


def circle(r, count, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(2.0 * math.pi * i / count), cy + r * math.sin(2.0 * math.pi * i / count)) for i in range(count)]


def build():
    bm = bmesh.new()
    prism(bm, outline(), -HALF, HALF, 1, 0)
    prism(bm, circle(HUB, 32), -HALF - HUB_RAISE, HALF + HUB_RAISE, 1, 1)
    # Dark discs standing in for spoke holes (a hole would make the platform hard to read from above).
    for i in range(SPOKE_HOLES):
        a = 2.0 * math.pi * (i + 0.5) / SPOKE_HOLES
        prism(bm, circle(HOLE_R, 20, HOLE_AT * math.cos(a), HOLE_AT * math.sin(a)), HALF - 0.01, HALF + 0.6, 0, 2)
    mesh = bpy.data.meshes.new("SM_Gear")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("SM_Gear", mesh)
    bpy.context.collection.objects.link(obj)
    split = obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
    split.split_angle = math.radians(30.0)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    for name, color, metal, rough in (("M_GearIron", (0.16, 0.16, 0.17, 1.0), 0.9, 0.5),
                                     ("M_GearBrass", (0.75, 0.5, 0.18, 1.0), 1.0, 0.35),
                                     ("M_GearShadow", (0.03, 0.03, 0.03, 1.0), 0.0, 0.9)):
        material = bpy.data.materials.new(name)
        material.use_nodes = True
        shader = material.node_tree.nodes["Principled BSDF"]
        shader.inputs["Base Color"].default_value = color
        shader.inputs["Metallic"].default_value = metal
        shader.inputs["Roughness"].default_value = rough
        obj.data.materials.append(material)
    return obj


def render_preview(folder):
    scene = bpy.context.scene
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.4, 0.38, 0.36, 1.0)
    scene.world = world
    light = bpy.data.objects.new("Key", bpy.data.lights.new("Key", "SUN"))
    light.data.energy = 4.0
    light.rotation_euler = (math.radians(40.0), 0.0, math.radians(30.0))
    scene.collection.objects.link(light)
    camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.location = Vector((2.2, -2.2, 2.0))
    camera.rotation_euler = (-camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.render.resolution_x = 480
    scene.render.resolution_y = 480
    scene.render.filepath = os.path.join(folder, "gear.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for existing in list(bpy.data.objects):
        bpy.data.objects.remove(existing)
    gear = build()
    bpy.ops.object.select_all(action="DESELECT")
    gear.select_set(True)
    bpy.context.view_layer.objects.active = gear
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT_DIR, "SM_Gear.fbx"), use_selection=True, apply_unit_scale=True,
                             mesh_smooth_type="FACE", use_mesh_modifiers=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "Gear.blend"))
    render_preview(sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else OUT_DIR)
    print("GEAR done")
