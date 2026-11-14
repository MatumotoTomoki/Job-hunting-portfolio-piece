# Builds the sky area's (area 3) models in Blender, saved as FBX in SourceArt/Models/Sky:
#   SM_SkyCloud   a puffy cloud 100 cm across (radius 50) for footing: its top surface is at Z 0, the puffs rise a little
#                 above it (the feet sink in) and hang 35 cm below. Collision is a flat box (UBX_), 80 x 80 cm, Z -30..0,
#                 so the player stands on an even floor, not on the bumps. One material slot: M_SkyCloud.
#   SM_SkyIsland  a floating island 100 cm across: a flat grass top at Z 0 over a rough rock cone hanging 100 cm down.
#                 Collision is a convex cylinder (UCX_) r 48, Z -60..0. Slots: 0 M_SkyGrass, 1 M_SkyRock.
# Scale them in UE: X/Y for the size; Z as wished. Also renders previews. Run:
#   blender --background --factory-startup --python build_sky_blender.py [-- <preview folder>]
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SourceArt", "Models", "Sky"))
CM = 0.01


def material(name, color, rough=0.8):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = rough
    return mat


def link(name, bm, materials=()):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for m in materials:
        obj.data.materials.append(m)
    return obj


def cloud():
    rand = random.Random(4)
    bm = bmesh.new()
    # Puffs: one big in the middle, a ring round it, a few small on top; flattened a little.
    puffs = [(0.0, 0.0, -2.0, 30.0)]
    for i in range(7):
        a = 2 * math.pi * i / 7 + rand.uniform(-0.2, 0.2)
        r = rand.uniform(26.0, 32.0)
        puffs.append((math.cos(a) * r, math.sin(a) * r, rand.uniform(-8.0, -3.0), rand.uniform(18.0, 23.0)))
    for i in range(3):
        a = 2 * math.pi * i / 3 + 0.5
        puffs.append((math.cos(a) * 12.0, math.sin(a) * 12.0, 4.0, rand.uniform(14.0, 17.0)))
    for x, y, z, r in puffs:
        result = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r * CM)
        verts = result["verts"]
        for v in verts:
            v.co.z *= 0.62
            v.co += Vector((x * CM, y * CM, z * CM))
    obj = link("SM_SkyCloud", bm, [material("M_SkyCloud", (0.95, 0.96, 1.0, 1.0), 1.0)])
    for p in obj.data.polygons:
        p.use_smooth = True
    # The flat floor the player stands on.
    col = bmesh.new()
    bmesh.ops.create_cube(col, size=1.0)
    for v in col.verts:
        v.co = Vector((v.co.x * 80.0 * CM, v.co.y * 80.0 * CM, (v.co.z * 30.0 - 15.0) * CM))
    link("UBX_SM_SkyCloud", col)
    return obj


def island():
    rand = random.Random(9)
    bm = bmesh.new()
    sides = 14
    # Grass top: a flat disc with a thin edge.
    top = [bm.verts.new((50.0 * math.cos(2 * math.pi * i / sides) * CM, 50.0 * math.sin(2 * math.pi * i / sides) * CM, 0.0)) for i in range(sides)]
    lip = [bm.verts.new((49.0 * math.cos(2 * math.pi * i / sides) * CM, 49.0 * math.sin(2 * math.pi * i / sides) * CM, -8.0 * CM)) for i in range(sides)]
    f = bm.faces.new(top)
    f.material_index = 0
    for i in range(sides):
        j = (i + 1) % sides
        f = bm.faces.new((top[j], top[i], lip[i], lip[j]))
        f.material_index = 0
    # Rock: rings narrowing to a point, each jittered.
    rings = [lip]
    for z, r in ((-30.0, 44.0), (-55.0, 32.0), (-80.0, 16.0)):
        ring = []
        for i in range(sides):
            a = 2 * math.pi * i / sides + rand.uniform(-0.08, 0.08)
            rr = r * rand.uniform(0.85, 1.1)
            ring.append(bm.verts.new((rr * math.cos(a) * CM, rr * math.sin(a) * CM, (z + rand.uniform(-5.0, 5.0)) * CM)))
        rings.append(ring)
    for upper, lower in zip(rings, rings[1:]):
        for i in range(sides):
            j = (i + 1) % sides
            f = bm.faces.new((upper[j], upper[i], lower[i], lower[j]))
            f.material_index = 1 if upper is not lip else 1
    tip = bm.verts.new((rand.uniform(-4, 4) * CM, rand.uniform(-4, 4) * CM, -100.0 * CM))
    last = rings[-1]
    for i in range(sides):
        f = bm.faces.new((last[(i + 1) % sides], last[i], tip))
        f.material_index = 1
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = link("SM_SkyIsland", bm, [material("M_SkyGrass", (0.25, 0.6, 0.2, 1.0)), material("M_SkyRock", (0.55, 0.5, 0.45, 1.0))])
    # Convex collision: a short cylinder under the top.
    col = bmesh.new()
    ring_top = [col.verts.new((48.0 * math.cos(2 * math.pi * i / 10) * CM, 48.0 * math.sin(2 * math.pi * i / 10) * CM, 0.0)) for i in range(10)]
    ring_low = [col.verts.new((48.0 * math.cos(2 * math.pi * i / 10) * CM, 48.0 * math.sin(2 * math.pi * i / 10) * CM, -60.0 * CM)) for i in range(10)]
    col.faces.new(ring_top)
    col.faces.new(list(reversed(ring_low)))
    for i in range(10):
        j = (i + 1) % 10
        col.faces.new((ring_top[i], ring_top[j], ring_low[j], ring_low[i]))
    bmesh.ops.recalc_face_normals(col, faces=col.faces)
    link("UCX_SM_SkyIsland", col)
    return obj


def export(objects, name):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT_DIR, name + ".fbx"), use_selection=True, apply_unit_scale=True,
                             mesh_smooth_type="FACE", use_mesh_modifiers=True)


def render_preview(folder, shown):
    scene = bpy.context.scene
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.45, 0.65, 0.95, 1.0)
    scene.world = world
    sun = bpy.data.objects.new("Key", bpy.data.lights.new("Key", "SUN"))
    sun.data.energy = 4.0
    sun.rotation_euler = (math.radians(40.0), math.radians(10.0), math.radians(50.0))
    scene.collection.objects.link(sun)
    camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.render.resolution_x = 640
    scene.render.resolution_y = 400
    scene.view_settings.view_transform = "Standard"
    for obj in bpy.data.objects:
        if obj.name.startswith(("UBX_", "UCX_")):
            obj.hide_render = True
    for name, obj in shown:
        for other in shown:
            other[1].hide_render = other[1] is not obj
        target = obj.location + Vector((0.0, 0.0, -0.2))
        camera.location = target + Vector((1.4, -1.4, 0.7))
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = os.path.join(folder, "sky_{}.png".format(name))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for existing in list(bpy.data.objects):
        bpy.data.objects.remove(existing)
    c = cloud()
    i = island()
    export([c, bpy.data.objects["UBX_SM_SkyCloud"]], "SM_SkyCloud")
    export([i, bpy.data.objects["UCX_SM_SkyIsland"]], "SM_SkyIsland")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "Sky.blend"))
    render_preview(sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else OUT_DIR, [("cloud", c), ("island", i)])
    print("SKY done")
