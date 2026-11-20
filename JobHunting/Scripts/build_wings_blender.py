# Builds area 4's wings (BP_Wings; the user, 2026-11-20) in Blender: SourceArt/Models/Heaven/SM_AngelWings.fbx.
# A pair of feathered wings, each three rows of leaf-shaped feathers laid along an arm that sweeps out and up from
# the root: small coverts on top, secondaries below them, and long primaries fanning out from the wrist. Feathers
# are thin curved blades (the material is two-sided). Vertex colour: white, warming to pale gold at the primaries'
# tips. Pivot at the wings' root (between the shoulders); Y is out to the sides (left wing -Y), X forward, Z up,
# about 2 m across. Slot M_WingFeather.
#   blender --background --factory-startup --python build_wings_blender.py [-- --preview out.png]
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "Heaven")
os.makedirs(OUT, exist_ok=True)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREVIEW = args[args.index("--preview") + 1] if "--preview" in args else None
bpy.ops.wm.read_factory_settings(use_empty=True)
CM = 0.01 * 0.65                       # drawn ~3 m across, built at ~2 m
WHITE = (1.0, 1.0, 1.0, 1.0)
GOLD = (1.0, 0.72, 0.3, 1.0)

bm = bmesh.new()
colour = bm.loops.layers.color.new("Col")
uv = bm.loops.layers.uv.new("UVMap")


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(4))


def feather(side, base, angle, length, width, layer, tip_gold):
    """A leaf-shaped blade in the wing's plane: from base (s outwards, z up) along angle (degrees, 0 = straight
    out, -90 = down), cupped back a little. side -1 is the left wing (-Y)."""
    d = Vector((math.cos(math.radians(angle)), math.sin(math.radians(angle))))
    n = Vector((-d.y, d.x))
    steps = 7
    rows = []
    for i in range(steps + 1):
        t = i / steps
        half = width * 0.5 * (math.sin(math.pi * min(1.0, t * 0.85 + 0.08)) ** 0.6) * (1.0 - 0.75 * t ** 3)
        spine = base + d * (length * t)
        back = -layer - 3.0 * t * t                       # cupped backwards towards the tip, layered in X
        row = []
        for k in (-1, 0, 1):
            p = spine + n * (half * k)
            x = back - (1.2 * abs(k) * (1.0 - t))           # a slight V across the blade
            row.append((bm.verts.new((x * CM, side * p.x * CM, p.y * CM)), t, k))
        rows.append(row)
    c_root = WHITE
    c_tip = mix(WHITE, GOLD, tip_gold)
    for i in range(steps):
        for k in range(2):
            quad = [rows[i][k], rows[i][k + 1], rows[i + 1][k + 1], rows[i + 1][k]]
            if side > 0:
                quad.reverse()
            f = bm.faces.new([q[0] for q in quad])
            for loop, (_, t, kk) in zip(f.loops, quad):
                loop[colour] = mix(c_root, c_tip, t ** 1.5)
                loop[uv].uv = ((kk + 1) * 0.5, t)


def arm(t):
    """The wing's leading edge, root (t 0) to wrist (t 1), in (out, up) cm."""
    return Vector((10.0 + 58.0 * t, 6.0 + 44.0 * math.sin(t * math.pi * 0.55)))


for side in (-1, 1):
    # Primaries: from the wrist, fanning from down-and-out to out-and-up, longest at the outside.
    wrist = arm(1.0)
    for i in range(8):
        f = i / 7
        feather(side, wrist + Vector((-4.0 * (1 - f), -6.0 * (1 - f))), -100 + 92 * f,
                52.0 + 38.0 * math.sin(f * math.pi * 0.6), 13.0, 0.0, 0.5 + 0.5 * f)
    # Secondaries along the arm, hanging down, a little outward.
    for i in range(9):
        t = 0.08 + 0.92 * i / 8
        feather(side, arm(t) + Vector((0.0, -4.0)), -96 + 14 * t, 40.0 + 10.0 * t, 14.0, 1.5, 0.25 * t)
    # Coverts on top: short, rounded.
    for i in range(10):
        t = 0.04 + 0.96 * i / 9
        feather(side, arm(t) + Vector((0.0, 2.0)), -100 + 30 * t, 20.0 + 6.0 * t, 12.0, 3.0, 0.0)

bm.normal_update()
mesh = bpy.data.meshes.new("SM_AngelWings")
bm.to_mesh(mesh)
bm.free()
obj = bpy.data.objects.new("SM_AngelWings", mesh)
bpy.context.scene.collection.objects.link(obj)
mat = bpy.data.materials.new("M_WingFeather")
obj.data.materials.append(mat)
for poly in mesh.polygons:
    poly.use_smooth = True
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, "SM_AngelWings.fbx"), use_selection=True, apply_unit_scale=True,
                         mesh_smooth_type="FACE", colors_type="LINEAR")
print("built SM_AngelWings", len(mesh.vertices), "vertices, size", tuple(round(v, 2) for v in obj.dimensions))

if PREVIEW:
    scene = bpy.context.scene
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 960, 600
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    attr = nodes.new("ShaderNodeVertexColor")
    attr.layer_name = "Col"
    mat.node_tree.links.new(attr.outputs["Color"], nodes["Principled BSDF"].inputs["Base Color"])
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(40), 0.0, math.radians(-120)))
    bpy.context.object.data.energy = 3.0
    world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.3, 0.4, 0.6, 1.0)
    bpy.ops.object.camera_add(location=(-2.2, 0.4, 0.4))
    cam = bpy.context.object
    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.05))
    look = cam.constraints.new("TRACK_TO"); look.target = bpy.context.object
    scene.camera = cam
    scene.render.filepath = PREVIEW
    bpy.ops.render.render(write_still=True)
