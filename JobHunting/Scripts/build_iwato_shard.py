# Builds area 4's light shard and the Iwato's rock (the user, 2026-11-20: shards beautiful, the Iwato weighty) in
# Blender, into SourceArt/Models/Heaven:
#   SM_LightShard.fbx  a long faceted crystal of light (an eight-sided bipyramid, 70 cm tall), two small ones beside
#                      it; pivot at its middle. Slot M_Shard.
#   SM_IwatoRock.fbx   the great stone door: a rough boulder slab 200 x 700 x 1300 cm (X thick, Y wide), lumpy and
#                      chipped, its front (-X, where the player comes from) hung with a shimenawa - a thick straw rope of
#                      two twisted strands sagging across it - and four zigzag paper shide. Its pivot is 50 cm under its
#                      top (it replaces BP_Mechanism's Body, which sits 50 cm down from the actor). Slots M_IwatoRock,
#                      M_IwatoRope, M_IwatoPaper.
#   blender --background --factory-startup --python build_iwato_shard.py [-- --preview out.png]
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "Heaven")
os.makedirs(OUT, exist_ok=True)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREVIEW = args[args.index("--preview") + 1] if "--preview" in args else None
bpy.ops.wm.read_factory_settings(use_empty=True)
CM = 0.01


def new_object(name, bm, slots):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for slot in slots:
        obj.data.materials.append(bpy.data.materials.get(slot) or bpy.data.materials.new(slot))
    return obj


def export(obj, name):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, name + ".fbx"), use_selection=True, apply_unit_scale=True,
                             mesh_smooth_type="FACE")


def planar_uv(bm, size):
    uv = bm.loops.layers.uv.new("UVMap")
    for face in bm.faces:
        n = face.normal
        for loop in face.loops:
            c = loop.vert.co
            if abs(n.z) > 0.7:
                loop[uv].uv = (c.x / size, c.y / size)
            elif abs(n.x) > abs(n.y):
                loop[uv].uv = (c.y / size, c.z / size)
            else:
                loop[uv].uv = (c.x / size, c.z / size)


# ----- the shard -----
def bipyramid(bm, centre, radius, half, sides=8, twist=0.0):
    ring = [bm.verts.new(centre + Vector((radius * math.cos(2 * math.pi * k / sides + twist), radius * math.sin(2 * math.pi * k / sides + twist), 0.0)))
            for k in range(sides)]
    top = bm.verts.new(centre + Vector((0.0, 0.0, half)))
    bottom = bm.verts.new(centre + Vector((0.0, 0.0, -half)))
    for k in range(sides):
        j = (k + 1) % sides
        bm.faces.new((ring[k], ring[j], top))
        bm.faces.new((ring[j], ring[k], bottom))


bm = bmesh.new()
bipyramid(bm, Vector((0.0, 0.0, 0.0)), 15 * CM, 35 * CM)
bipyramid(bm, Vector((12 * CM, 5 * CM, -14 * CM)), 6 * CM, 14 * CM, 6, 0.3)
bipyramid(bm, Vector((-10 * CM, -7 * CM, -18 * CM)), 5 * CM, 11 * CM, 6, 0.7)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
planar_uv(bm, 0.5)
shard = new_object("SM_LightShard", bm, ["M_Shard"])
export(shard, "SM_LightShard")

# ----- the Iwato rock -----
W, D, H = 7.0, 2.0, 13.0          # metres: Y wide, X thick, Z tall
TOP = 0.5                          # the pivot is 50 cm under the top
rng = random.Random(7)
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co = Vector((v.co.x * D, v.co.y * W, v.co.z * H - H / 2.0 + TOP))
# Cut it fine, then push the surface about: big lumps, a rounded crown, chipped edges; kept inside its box.
for axis, n in ((0, 3), (1, 10), (2, 18)):
    for k in range(1, n):
        co, no = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
        lo, hi = ((-D / 2, D / 2), (-W / 2, W / 2), (TOP - H, TOP))[axis]
        co[axis] = lo + (hi - lo) * k / n
        no[axis] = 1.0
        bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), plane_co=co, plane_no=no)
for v in bm.verts:
    p = v.co
    lump = noise.noise(Vector((p.x * 0.35, p.y * 0.35, p.z * 0.35))) * 0.35 + noise.noise(Vector((p.x * 1.2, p.y * 1.2, p.z * 1.2)) + Vector((5, 1, 3))) * 0.12
    out = Vector((p.x / (D / 2), p.y / (W / 2), 0.0))
    crown = max(0.0, (p.z - (TOP - 2.5)) / 2.5)                 # round off the top corners
    shrink = 1.0 - 0.18 * crown * crown * min(1.0, out.length)
    v.co.x = max(-D / 2, min(D / 2, p.x * shrink + (math.copysign(lump, p.x) if abs(p.x) > D * 0.3 else 0.0) * 0.6))
    v.co.y = max(-W / 2, min(W / 2, p.y * (1.0 - 0.1 * crown * crown) + (math.copysign(lump, p.y) * 0.5 if abs(p.y) > W * 0.42 else 0.0)))
    v.co.z = max(TOP - H, min(TOP, p.z - (0.35 * crown * abs(out.y) if p.z > TOP - 2.5 else 0.0)))
    if abs(p.x) > D * 0.45:                                      # the faces are lumpy, inward only
        dent = 0.5 * (noise.noise(Vector((p.y * 0.45, p.z * 0.3, p.x))) + 1.0) * 0.55
        dent += 0.5 * (noise.noise(Vector((p.y * 1.6, p.z * 1.4, 9.0 + p.x))) + 1.0) * 0.18
        if p.x < 0 and TOP - 4.4 < p.z < TOP - 2.6:
            dent *= 0.25                                           # flat where the rope lies against it
        v.co.x -= math.copysign(dent, p.x)
    if abs(p.y) > W * 0.45:
        v.co.y -= math.copysign(0.5 * (noise.noise(Vector((p.x * 0.6, p.z * 0.4, 3.0))) + 1.0) * 0.4, p.y)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
for f in bm.faces:
    f.material_index = 0
planar_uv(bm, 2.0)


def tube(bm, a, b, r, slot, segments=10):
    axis = (b - a)
    length = axis.length
    axis.normalize()
    helper = Vector((0.0, 0.0, 1.0)) if abs(axis.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    u = axis.cross(helper).normalized()
    w = axis.cross(u)
    lo, hi = [], []
    for i in range(segments):
        ang = 2 * math.pi * i / segments
        ring = u * math.cos(ang) + w * math.sin(ang)
        lo.append(bm.verts.new(a + ring * r))
        hi.append(bm.verts.new(b + ring * r))
    for i in range(segments):
        j = (i + 1) % segments
        f = bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
        f.material_index = slot


# The shimenawa: two twisted strands sagging across the front, 3.2 m under the top, 0.6 m of sag.
FRONT = -D / 2 - 0.12
Y0, Y1 = -W / 2 + 0.2, W / 2 - 0.2
def rope_point(t, phase):
    y = Y0 + (Y1 - Y0) * t
    z = TOP - 3.2 - 0.6 * (1.0 - (2.0 * t - 1.0) ** 2)
    ang = t * 34.0 + phase
    return Vector((FRONT + 0.1 * math.cos(ang), y, z + 0.1 * math.sin(ang)))
steps = 70
for phase in (0.0, math.pi):
    for s in range(steps):
        tube(bm, rope_point(s / steps, phase), rope_point((s + 1) / steps, phase), 0.13, 1)
# Tassels of straw hanging from it, and four zigzag shide.
for t in (0.12, 0.37, 0.63, 0.88):
    p = rope_point(t, 0.0)
    for k in range(5):
        a = Vector((p.x - 0.02, p.y + (k - 2) * 0.05, p.z - 0.1))
        tube(bm, a, a + Vector((0.0, 0.0, -0.55 - 0.1 * (k % 2))), 0.02, 1, 5)
for t in (0.25, 0.5, 0.75, 0.0):
    if t == 0.0:
        continue
    p = rope_point(t, 0.0)
    x = p.x - 0.05
    zz = p.z - 0.15
    pts = []
    for k in range(5):
        pts.append((p.y + (0.16 if k % 2 else -0.04), zz - 0.32 * k))
    for k in range(len(pts) - 1):
        (y0, z0), (y1, z1) = pts[k], pts[k + 1]
        quad = [bm.verts.new((x, y0, z0)), bm.verts.new((x, y0 + 0.16, z0)), bm.verts.new((x, y1 + 0.16, z1)), bm.verts.new((x, y1, z1))]
        f = bm.faces.new(quad)
        f.material_index = 2
        f2 = bm.faces.new(list(reversed([bm.verts.new((x + 0.005, *v.co.yz)) for v in quad])))
        f2.material_index = 2
bm.normal_update()
rock = new_object("SM_IwatoRock", bm, ["M_IwatoRock", "M_IwatoRope", "M_IwatoPaper"])
for poly in rock.data.polygons:
    poly.use_smooth = poly.material_index == 1
export(rock, "SM_IwatoRock")
print("built SM_LightShard, SM_IwatoRock", len(rock.data.vertices), "vertices")

if PREVIEW:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 960, 720
    colours = {"M_IwatoRock": (0.18, 0.17, 0.16, 1), "M_IwatoRope": (0.75, 0.62, 0.35, 1), "M_IwatoPaper": (0.95, 0.95, 0.92, 1), "M_Shard": (1.0, 0.85, 0.5, 1)}
    for name, c in colours.items():
        m = bpy.data.materials[name]
        m.use_nodes = True
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = c
    shard.location = (-3.0, -2.0, -8.0)
    shard.scale = (4, 4, 4)
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0.0, math.radians(-60)))
    bpy.context.object.data.energy = 4.0
    world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.35, 0.4, 1.0)
    bpy.ops.object.camera_add(location=(-24.0, -10.0, -3.0))
    cam = bpy.context.object
    bpy.ops.object.empty_add(location=(0.0, 0.0, -6.0))
    look = cam.constraints.new("TRACK_TO"); look.target = bpy.context.object
    scene.camera = cam
    scene.render.filepath = PREVIEW
    bpy.ops.render.render(write_still=True)
