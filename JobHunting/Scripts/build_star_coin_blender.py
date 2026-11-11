# Builds the star coin (three hidden in each area) in Blender: a gold coin standing on edge, both faces showing a
# raised rim, a puffy five-pointed star and, above the star, a small halo (the game climbs to heaven). One material
# slot (M_StarCoin, gold in UE). The coin faces +X / -X, so spinning it about Z turns it like a coin on a stand; its
# centre is at the origin. Saves StarCoin.blend and SM_StarCoin.fbx in SourceArt/Models/StarCoin and renders
# previews. Run:
#   blender --background --factory-startup --python build_star_coin_blender.py [-- <preview folder>]
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SourceArt", "Models", "StarCoin"))
CM = 0.01
SEGMENTS = 96

RADIUS = 35.0          # the coin
FIELD = 3.5            # half the thickness of the flat field
RIM_IN = 30.0          # the raised rim, RIM_IN..RADIUS
RIM = 5.5              # half the thickness at the rim
STAR_OUT = 18.0        # star point radius
STAR_IN = 7.6          # star notch radius
STAR_Z = -2.5          # star centre, below the middle to leave room for the halo
STAR_RAISE = 3.6       # how far the star's middle stands off the field
HALO_Z = 21.0          # halo centre
HALO_A, HALO_B = 8.0, 2.8      # outer half-width, half-height (an ellipse: a ring seen at a slant)
HALO_WIDTH = 1.4
HALO_RAISE = 1.8


def add_face(bm, verts, expect):
    # A face turned to look along `expect`.
    face = bm.faces.new(verts)
    face.normal_update()
    if face.normal.dot(expect) < 0.0:
        face.normal_flip()
    return face


def vert(bm, x, y, z):
    return bm.verts.new((x * CM, y * CM, z * CM))


def disc(bm):
    # The flat body: a short cylinder along X.
    for side in (-1, 1):
        # Only as wide as the rim's inside (plus a little hidden in it): the rim alone makes the edge.
        ring = [vert(bm, side * FIELD, (RIM_IN + 1.0) * math.cos(a), (RIM_IN + 1.0) * math.sin(a)) for a in angles(SEGMENTS)]
        if side < 0:
            back = ring
        else:
            front = ring
    add_face(bm, front, Vector((1, 0, 0)))
    add_face(bm, back, Vector((-1, 0, 0)))
    walls(bm, back, front, outward=True)


def angles(count, start=0.0):
    return [start + 2.0 * math.pi * i / count for i in range(count)]


def walls(bm, lower, upper, outward, centre=(0.0, 0.0)):
    # Quads between two matching loops; facing away from (outward) or toward the axis through `centre`.
    n = len(lower)
    for i in range(n):
        j = (i + 1) % n
        quad = [lower[i], lower[j], upper[j], upper[i]]
        mid = sum((v.co for v in quad), Vector()) / 4.0
        radial = Vector((0.0, mid.y - centre[0] * CM, mid.z - centre[1] * CM))
        add_face(bm, quad, radial if outward else -radial)


def band(bm, outer, inner, expect):
    n = len(outer)
    for i in range(n):
        j = (i + 1) % n
        add_face(bm, [outer[i], outer[j], inner[j], inner[i]], expect)


def rim(bm):
    for side in (-1, 1):
        outer_low = [vert(bm, 0.0, RADIUS * math.cos(a), RADIUS * math.sin(a)) for a in angles(SEGMENTS)]
        outer = [vert(bm, side * RIM, RADIUS * math.cos(a), RADIUS * math.sin(a)) for a in angles(SEGMENTS)]
        inner = [vert(bm, side * RIM, RIM_IN * math.cos(a), RIM_IN * math.sin(a)) for a in angles(SEGMENTS)]
        inner_low = [vert(bm, side * FIELD, RIM_IN * math.cos(a), RIM_IN * math.sin(a)) for a in angles(SEGMENTS)]
        band(bm, outer, inner, Vector((side, 0, 0)))
        walls(bm, outer_low, outer, outward=True)
        walls(bm, inner_low, inner, outward=False)


def star(bm):
    # A puffy star: its outline on the field, a smaller copy raised part way, a point raised in the middle.
    points = []
    for i in range(10):
        a = math.pi / 2.0 + math.pi * i / 5.0
        r = STAR_OUT if i % 2 == 0 else STAR_IN
        points.append((r * math.cos(a), STAR_Z + r * math.sin(a)))
    for side in (-1, 1):
        expect = Vector((side, 0, 0))
        base = [vert(bm, side * FIELD, y, z) for y, z in points]
        mid = [vert(bm, side * (FIELD + STAR_RAISE * 0.7), 0.55 * y, STAR_Z + 0.55 * (z - STAR_Z)) for y, z in points]
        top = vert(bm, side * (FIELD + STAR_RAISE), 0.0, STAR_Z)
        band(bm, base, mid, expect)
        for i in range(10):
            add_face(bm, [mid[i], mid[(i + 1) % 10], top], expect)


def halo(bm):
    # A raised elliptic ring above the star.
    count = 48
    for side in (-1, 1):
        expect = Vector((side, 0, 0))
        def loop(a, b, x):
            return [vert(bm, x, a * math.cos(t), HALO_Z + b * math.sin(t)) for t in angles(count)]
        outer_low = loop(HALO_A, HALO_B, side * FIELD)
        inner_low = loop(HALO_A - HALO_WIDTH, max(HALO_B - HALO_WIDTH, 0.6), side * FIELD)
        outer = loop(HALO_A, HALO_B, side * (FIELD + HALO_RAISE))
        inner = loop(HALO_A - HALO_WIDTH, max(HALO_B - HALO_WIDTH, 0.6), side * (FIELD + HALO_RAISE))
        band(bm, outer, inner, expect)
        walls(bm, outer_low, outer, outward=True, centre=(0.0, HALO_Z))
        walls(bm, inner_low, inner, outward=False, centre=(0.0, HALO_Z))


def build():
    bm = bmesh.new()
    disc(bm)
    rim(bm)
    star(bm)
    halo(bm)
    mesh = bpy.data.meshes.new("SM_StarCoin")
    bm.to_mesh(mesh)
    bm.free()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    obj = bpy.data.objects.new("SM_StarCoin", mesh)
    bpy.context.collection.objects.link(obj)
    # Hard edges where faces meet sharply (rim corners, star ridges), smooth elsewhere.
    split = obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
    split.split_angle = math.radians(35.0)
    gold = bpy.data.materials.new("M_StarCoin")
    gold.use_nodes = True
    shader = gold.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (1.0, 0.68, 0.16, 1.0)
    shader.inputs["Metallic"].default_value = 1.0
    shader.inputs["Roughness"].default_value = 0.28
    obj.data.materials.append(gold)
    return obj


def render_preview(folder):
    scene = bpy.context.scene
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.35, 0.3, 0.28, 1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    scene.world = world
    light = bpy.data.objects.new("Key", bpy.data.lights.new("Key", "SUN"))
    light.data.energy = 4.0
    light.rotation_euler = (math.radians(50.0), math.radians(20.0), math.radians(60.0))
    scene.collection.objects.link(light)
    camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    camera.data.lens = 50.0
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.render.resolution_x = 480
    scene.render.resolution_y = 480
    for label, direction in (("front", Vector((1.0, 0.0, 0.0))), ("angle", Vector((0.75, -0.6, 0.25)))):
        camera.location = direction.normalized() * 1.9
        camera.rotation_euler = (-camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = os.path.join(folder, "star_coin_{}.png".format(label))
        bpy.ops.render.render(write_still=True)


def render_icon(path):
    # The HUD icon: the coin face on, on a transparent background.
    scene = bpy.context.scene
    world = bpy.data.worlds.new("IconWorld")
    world.use_nodes = True
    # Warm surroundings: the metal shows them, so a grey world makes the gold look pale.
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.3, 0.08, 1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    scene.world = world
    light = bpy.data.objects.new("IconKey", bpy.data.lights.new("IconKey", "SUN"))
    light.data.energy = 6.0
    light.rotation_euler = (math.radians(60.0), math.radians(-25.0), math.radians(110.0))
    scene.collection.objects.link(light)
    camera = bpy.data.objects.new("IconCamera", bpy.data.cameras.new("IconCamera"))
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 2.0 * RADIUS * CM * 1.04
    camera.location = Vector((1.0, 0.0, 0.0))
    camera.rotation_euler = (-camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 48
    scene.render.film_transparent = True
    # Standard, not AgX: AgX washes the gold out toward beige.
    scene.view_settings.view_transform = "Standard"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.resolution_x = 256
    scene.render.resolution_y = 256
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    scene.render.film_transparent = False
    bpy.data.objects.remove(light)
    bpy.data.objects.remove(camera)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for existing in list(bpy.data.objects):
        bpy.data.objects.remove(existing)
    coin = build()
    bpy.ops.object.select_all(action="DESELECT")
    coin.select_set(True)
    bpy.context.view_layer.objects.active = coin
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT_DIR, "SM_StarCoin.fbx"), use_selection=True, apply_unit_scale=True,
                             mesh_smooth_type="FACE", use_mesh_modifiers=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "StarCoin.blend"))
    render_icon(os.path.join(OUT_DIR, "T_StarCoinIcon.png"))
    preview = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else OUT_DIR
    render_preview(preview)
    print("STAR COIN done")
