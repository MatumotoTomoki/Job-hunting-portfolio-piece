# Builds the danger button in Blender, about the player's height (1.84 m to the top of the button), facing +X:
#   SM_DangerButton_Body  a yellow pedestal on a black plinth: a black panel with a "do not press" sign on the front,
#                         a band of hazard stripes all round near the top, a dark steel top plate and the red base of
#                         the button with "BUTTON" round it. Origin at the bottom centre.
#   SM_DangerButton_Cap   the red button itself, which goes down when pressed. Origin at its bottom centre; it sits
#                         at Z CAP_Z on the body.
# Textures from build_danger_button_textures.ps1 (T_DangerStripes, T_DangerSign, T_DangerLabel).
# Body material slots: 0 M_DangerYellow, 1 M_DangerBlack, 2 M_DangerSteel, 3 M_DangerRedDark, 4 M_DangerStripes,
# 5 M_DangerSign, 6 M_DangerLabel. Cap: 0 M_DangerRed. Saves DangerButton.blend and both FBX in
# SourceArt/Models/DangerButton and renders a preview. Run:
#   blender --background --factory-startup --python build_danger_button_blender.py [-- <preview folder>]
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SourceArt", "Models", "DangerButton"))
CM = 0.01
HALF = 45.0          # the pedestal is 90 x 90
BODY_TOP = 140.0
PLATE = (140.0, 148.0)
BASE_R, BASE_TOP = 34.0, 162.0
CAP_Z = BASE_TOP
CAP_R, CAP_H, CAP_DOME = 28.0, 16.0, 6.0
STRIPES = (100.0, 118.0)
LIFT = 0.3           # decals stand this far off the faces they sit on

YELLOW, BLACK, STEEL, RED_DARK, STRIPE, SIGN, LABEL = range(7)


class Mesh:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")

    def face(self, points, uvs, slot, expect):
        # A face turned to look along `expect` (the meshes are not all closed, so normals cannot be worked out).
        verts = [self.bm.verts.new((p[0] * CM, p[1] * CM, p[2] * CM)) for p in points]
        face = self.bm.faces.new(verts)
        face.normal_update()
        if face.normal.dot(Vector(expect)) < 0.0:
            face.normal_flip()
        face.material_index = slot
        # By vertex, not by loop order: a flipped face runs its loops the other way round.
        for loop in face.loops:
            loop[self.uv].uv = uvs[verts.index(loop.vert)]
        return face

    def box(self, x0, x1, y0, y1, z0, z1, slot):
        c = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        square = [(0, 0), (1, 0), (1, 1), (0, 1)]
        mid = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
        for idx in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            pts = [c[i] for i in idx]
            centre = [sum(p[k] for p in pts) / 4 - mid[k] for k in range(3)]
            self.face(pts, square, slot, centre)

    def cylinder(self, r, z0, z1, side_slot, cap_slot, segments=48, wrap=1.0, bottom=True, u_shift=0.0):
        ring0 = [(r * math.cos(2 * math.pi * i / segments), r * math.sin(2 * math.pi * i / segments)) for i in range(segments + 1)]
        for i in range(segments):
            (ax, ay), (bx, by) = ring0[i], ring0[i + 1]
            u0, u1 = wrap * i / segments + u_shift, wrap * (i + 1) / segments + u_shift
            self.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], [(u0, 0), (u1, 0), (u1, 1), (u0, 1)], side_slot, ((ax + bx) / 2, (ay + by) / 2, 0))
        top = [(x, y, z1) for x, y in ring0[:-1]]
        self.face(top, [((x / r + 1) / 2, (y / r + 1) / 2) for x, y, _ in top], cap_slot, (0, 0, 1))
        if bottom:
            low = [(x, y, z0) for x, y in reversed(ring0[:-1])]
            self.face(low, [((x / r + 1) / 2, (y / r + 1) / 2) for x, y, _ in low], cap_slot, (0, 0, -1))

    def finish(self, name, materials):
        bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=0.0001)
        mesh = bpy.data.meshes.new(name)
        self.bm.to_mesh(mesh)
        self.bm.free()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        for material in materials:
            obj.data.materials.append(material)
        split = obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
        split.split_angle = math.radians(40.0)
        for polygon in mesh.polygons:
            polygon.use_smooth = True
        return obj


def decal_side(m, axis, sign, a0, a1, z0, z1, slot, u_repeat=1.0):
    # A flat quad just off one side face of the pedestal: axis "x" or "y", sign +1 / -1, spanning a0..a1 across.
    d = sign * (HALF + LIFT)
    if axis == "x":
        pts = [(d, a0, z0), (d, a1, z0), (d, a1, z1), (d, a0, z1)]
    else:
        pts = [(a0, d, z0), (a1, d, z0), (a1, d, z1), (a0, d, z1)]
    if sign < 0:
        pts = [pts[1], pts[0], pts[3], pts[2]]
    m.face(pts, [(0, 0), (u_repeat, 0), (u_repeat, 1), (0, 1)], slot, (sign, 0, 0) if axis == "x" else (0, sign, 0))


def material(name, color, image=None, metal=0.0, rough=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = rough
    if image:
        tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(os.path.join(OUT_DIR, image))
        mat.node_tree.links.new(tex.outputs["Color"], shader.inputs["Base Color"])
    else:
        shader.inputs["Base Color"].default_value = color
    return mat


def build():
    mats = [material("M_DangerYellow", (0.92, 0.66, 0.0, 1)), material("M_DangerBlack", (0.02, 0.02, 0.02, 1)),
            material("M_DangerSteel", (0.25, 0.26, 0.28, 1), metal=0.8, rough=0.4),
            material("M_DangerRedDark", (0.35, 0.02, 0.02, 1), rough=0.4),
            material("M_DangerStripes", None, "T_DangerStripes.png"), material("M_DangerSign", None, "T_DangerSign.png"),
            material("M_DangerLabel", None, "T_DangerLabel.png", rough=0.35)]
    body = Mesh()
    body.box(-HALF, HALF, -HALF, HALF, 18.0, BODY_TOP, YELLOW)
    body.box(-HALF - 3, HALF + 3, -HALF - 3, HALF + 3, 0.0, 18.0, BLACK)                   # plinth
    body.box(-HALF - 3, HALF + 3, -HALF - 3, HALF + 3, PLATE[0], PLATE[1], STEEL)          # top plate
    # The label's first BUTTON is centred a quarter of the way along: shift it round to the front (+X).
    body.cylinder(BASE_R, PLATE[1], BASE_TOP, LABEL, RED_DARK, bottom=False, u_shift=0.25)  # the button's base
    # Hazard stripes all round; one stripe tile is 4x as wide as it is high.
    tiles = 2.0 * HALF / ((STRIPES[1] - STRIPES[0]) * 4.0)
    for axis in ("x", "y"):
        for s in (1, -1):
            decal_side(body, axis, s, -HALF, HALF, STRIPES[0], STRIPES[1], STRIPE, tiles)
    # The front: a black panel and the sign on it.
    decal_side(body, "x", 1, -36.0, 36.0, 28.0, 94.0, BLACK)
    front = HALF + 2 * LIFT
    body.face([(front, -26.0, 35.0), (front, 26.0, 35.0), (front, 26.0, 87.0), (front, -26.0, 87.0)],
              [(0, 0), (1, 0), (1, 1), (0, 1)], SIGN, (1, 0, 0))
    body_obj = body.finish("SM_DangerButton_Body", mats)

    cap = Mesh()
    cap.cylinder(CAP_R, 0.0, CAP_H, 0, 0)
    cap_obj = cap.finish("SM_DangerButton_Cap", [material("M_DangerRed", (0.85, 0.02, 0.02, 1), rough=0.25)])
    cap_obj.location = (0.0, 0.0, CAP_Z * CM)
    return body_obj, cap_obj, mats


def dome_top(obj):
    # Raise the top face's middle: inset the top and lift it.
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    tops = [f for f in bm.faces if f.normal.z > 0.9]
    for face in tops:
        result = bmesh.ops.inset_region(bm, faces=[face], thickness=CAP_R * 0.35 * CM, depth=0.0)
        bmesh.ops.translate(bm, verts=list(face.verts), vec=(0, 0, CAP_DOME * CM))
    bm.to_mesh(obj.data)
    bm.free()


def export(obj, name):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    saved = obj.location.copy()
    obj.location = (0.0, 0.0, 0.0)
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT_DIR, name + ".fbx"), use_selection=True, apply_unit_scale=True,
                             mesh_smooth_type="FACE", use_mesh_modifiers=True)
    obj.location = saved


def render_preview(folder):
    scene = bpy.context.scene
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.35, 0.35, 0.38, 1.0)
    scene.world = world
    light = bpy.data.objects.new("Key", bpy.data.lights.new("Key", "SUN"))
    light.data.energy = 4.0
    light.rotation_euler = (math.radians(45.0), math.radians(10.0), math.radians(60.0))
    scene.collection.objects.link(light)
    camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.render.resolution_x = 480
    scene.render.resolution_y = 640
    scene.view_settings.view_transform = "Standard"
    for label, direction in (("front", Vector((1.0, 0.0, 0.15))), ("angle", Vector((0.8, -0.6, 0.5)))):
        camera.location = Vector((0.0, 0.0, 0.95)) + direction.normalized() * 4.0
        camera.rotation_euler = (Vector((0.0, 0.0, 0.95)) - camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = os.path.join(folder, "danger_button_{}.png".format(label))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for existing in list(bpy.data.objects):
        bpy.data.objects.remove(existing)
    body, cap, _ = build()
    dome_top(cap)
    export(body, "SM_DangerButton_Body")
    export(cap, "SM_DangerButton_Cap")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "DangerButton.blend"))
    render_preview(sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else OUT_DIR)
    print("DANGER BUTTON done")
