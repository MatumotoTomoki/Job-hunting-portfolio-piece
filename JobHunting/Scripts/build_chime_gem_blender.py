# Builds area 4's ringing jewel (BP_ChimeJewel; the user, 2026-11-20) in Blender: SourceArt/Models/Heaven/SM_ChimeJewel.fbx.
# A round brilliant-cut gem lying table up, in the old cylinder's box (100 cm across, 100 cm tall around its origin,
# so the placed jewels' actor scale - 220 x 220 x 40 cm - fits it as before): a flat 16-sided table on top to stand on,
# crown facets down to the girdle, a short girdle band, pavilion facets to the point underneath. Rings alternate by
# half a step, so every facet is a triangle and catches the light on its own (flat shaded). UCX_SM_ChimeJewel, the
# same gem, is its collision (it is convex). Slot M_ChimeGem.
#   blender --background --factory-startup --python build_chime_gem_blender.py [-- --preview out.png]
import math
import os
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "Heaven")
os.makedirs(OUT, exist_ok=True)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREVIEW = args[args.index("--preview") + 1] if "--preview" in args else None
bpy.ops.wm.read_factory_settings(use_empty=True)
CM = 0.01
SIDES = 16
# (radius, height, half-step turned?) from the top down; a single point closes each end.
RINGS = [(30.0, 50.0, False), (42.0, 38.0, True), (50.0, 24.0, False), (50.0, 16.0, False), (32.0, -14.0, True)]
CULET = -50.0


def gem(name):
    bm = bmesh.new()
    rings = []
    for radius, z, turned in RINGS:
        off = math.pi / SIDES if turned else 0.0
        rings.append([bm.verts.new((radius * CM * math.cos(2 * math.pi * k / SIDES + off),
                                    radius * CM * math.sin(2 * math.pi * k / SIDES + off), z * CM)) for k in range(SIDES)])
    bm.faces.new(rings[0])                                   # the table
    for upper, lower in zip(rings, rings[1:]):
        for k in range(SIDES):
            j = (k + 1) % SIDES
            bm.faces.new((upper[k], lower[k], lower[j], upper[j]))
    point = bm.verts.new((0.0, 0.0, CULET * CM))
    for k in range(SIDES):
        bm.faces.new((rings[-1][k], point, rings[-1][(k + 1) % SIDES]))
    # Split the crown and pavilion quads into triangles along their short diagonal: facets.
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) == 4])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for loop in f.loops:
            loop[uv].uv = (loop.vert.co.x + 0.5, loop.vert.co.y + 0.5)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


jewel = gem("SM_ChimeJewel")
mat = bpy.data.materials.new("M_ChimeGem")
jewel.data.materials.append(mat)
hull = gem("UCX_SM_ChimeJewel")
bpy.ops.object.select_all(action="DESELECT")
jewel.select_set(True)
hull.select_set(True)
bpy.context.view_layer.objects.active = jewel
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, "SM_ChimeJewel.fbx"), use_selection=True, apply_unit_scale=True,
                         mesh_smooth_type="FACE")
print("built SM_ChimeJewel", len(jewel.data.polygons), "faces, size", tuple(round(v, 2) for v in jewel.dimensions))

if PREVIEW:
    bpy.data.objects.remove(hull)
    scene = bpy.context.scene
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 800, 500
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.35, 0.8, 1.0, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.1
    jewel.scale = (2.2, 2.2, 0.4)
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(45), 0.0, math.radians(30)))
    bpy.context.object.data.energy = 4.0
    world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.4, 0.45, 0.55, 1.0)
    bpy.ops.object.camera_add(location=(2.6, -2.6, 1.6))
    cam = bpy.context.object
    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
    look = cam.constraints.new("TRACK_TO"); look.target = bpy.context.object
    scene.camera = cam
    scene.render.filepath = PREVIEW
    bpy.ops.render.render(write_still=True)
