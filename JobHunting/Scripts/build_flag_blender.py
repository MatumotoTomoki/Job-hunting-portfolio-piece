# Builds the checkpoint flag in Blender: a metal pole in two halves (the top half is what tips over when the flag
# breaks) and a triangular pennant on a chain of four bones with a looping flutter. Saves Flag.blend and the FBX files
# in SourceArt/Models/Flag, and renders preview frames. Sizes match BP_CheckpointFlag: the lower pole stands 0-55 cm,
# the upper pole and pennant sit on the Upper component 55 cm up; the pennant points toward +Y. Run:
#   blender --background --factory-startup --python build_flag_blender.py [-- <preview folder>]
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SourceArt", "Models", "Flag"))
CM = 0.01
POLE_RADIUS = 2.2
POLE_HALF = 55.0
FPS = 30
FLUTTER_FRAMES = 30

# The pennant: its edge on the pole from HOIST_LOW to HOIST_HIGH (cm, on the upper pole), the tip LENGTH out along +Y.
HOIST_LOW = 25.0
HOIST_HIGH = 54.0
LENGTH = 50.0
COLUMNS = 16
ROWS = 8
BONES = 4


def lathe(name, profile, segments=32):
    # Spins (radius, z) points around Z, bottom to top; a radius of 0 closes the end.
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for radius, z in profile:
        count = 1 if radius == 0.0 else segments
        rings.append([bm.verts.new((radius * CM * math.cos(2 * math.pi * i / count), radius * CM * math.sin(2 * math.pi * i / count), z * CM)) for i in range(count)])
    for lower, upper in zip(rings, rings[1:]):
        for i in range(segments):
            corners = [lower[i % len(lower)], lower[(i + 1) % len(lower)], upper[(i + 1) % len(upper)], upper[i % len(upper)]]
            bm.faces.new(list(dict.fromkeys(corners)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for face in bm.faces:
        face.smooth = True
    # Rings and steps keep a crisp edge; the round pole stays smooth.
    for edge in bm.edges:
        edge.smooth = len(edge.link_faces) == 2 and edge.calc_face_angle(0.0) < math.radians(40.0)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def sphere(name, center, radius):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=radius * CM)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(center) * CM)
    for face in bm.faces:
        face.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def material(name, color, metallic, roughness):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    shader = result.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def join(objects, name, mat):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = objects[0]
    if len(objects) > 1:
        bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    joined.name = name
    joined.data.name = name
    return joined


def build_poles(metal):
    r = POLE_RADIUS
    # Lower half: a spike driven a little into the ground, a collar at ground level, the shaft, and the joint sleeve.
    lower = lathe("PoleLower", [(0.0, -8.0), (r * 0.6, -4.0), (r, -1.0), (r * 1.7, 0.0), (r * 1.7, 1.5), (r, 2.5),
                               (r, POLE_HALF - 4.0), (r * 1.45, POLE_HALF - 3.5), (r * 1.45, POLE_HALF), (0.0, POLE_HALF)])
    # Upper half, from the joint: shaft, a ring under the knob, and the knob on top.
    upper = lathe("PoleUpperShaft", [(0.0, 0.0), (r, 0.0), (r, POLE_HALF - 2.5), (r * 1.5, POLE_HALF - 2.0),
                                     (r * 1.5, POLE_HALF - 0.5), (r * 0.8, POLE_HALF), (0.0, POLE_HALF)])
    knob = sphere("Knob", (0.0, 0.0, POLE_HALF + 3.5), 4.2)
    return join([lower], "SM_FlagPoleLower", metal), join([upper, knob], "SM_FlagPoleUpper", metal)


def build_pennant(cloth):
    # A grid that narrows to the tip, in the YZ plane, then four bones along it; each vertex follows the two bones
    # nearest along the length, so the cloth bends smoothly.
    mesh = bpy.data.meshes.new("SK_FlagPennant")
    bm = bmesh.new()
    middle = (HOIST_LOW + HOIST_HIGH) / 2.0
    half = (HOIST_HIGH - HOIST_LOW) / 2.0
    grid = []
    for c in range(COLUMNS + 1):
        u = c / COLUMNS
        column = []
        for r in range(ROWS + 1):
            v = r / ROWS * 2.0 - 1.0
            column.append(bm.verts.new((0.0, (POLE_RADIUS + LENGTH * u) * CM, (middle + v * half * (1.0 - u)) * CM)))
        grid.append(column)
    for c in range(COLUMNS):
        for r in range(ROWS):
            corners = [grid[c][r], grid[c + 1][r], grid[c + 1][r + 1], grid[c][r + 1]]
            bm.faces.new(list(dict.fromkeys(corners)))
    for face in bm.faces:
        face.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    pennant = bpy.data.objects.new("SK_FlagPennant", mesh)
    bpy.context.collection.objects.link(pennant)
    mesh.materials.append(cloth)

    data = bpy.data.armatures.new("PennantRig")
    rig = bpy.data.objects.new("Armature", data)
    bpy.context.collection.objects.link(rig)
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    step = LENGTH / BONES
    root = data.edit_bones.new("root")
    root.head = (0.0, 0.0, middle * CM)
    root.tail = (0.0, POLE_RADIUS * CM, middle * CM)
    parent = root
    starts = []
    for i in range(BONES):
        bone = data.edit_bones.new("cloth_{:02d}".format(i + 1))
        start = POLE_RADIUS + step * i
        starts.append(start)
        bone.head = (0.0, start * CM, middle * CM)
        bone.tail = (0.0, (start + step) * CM, middle * CM)
        bone.parent = parent
        bone.use_connect = i > 0
        parent = bone
    bpy.ops.object.mode_set(mode="OBJECT")

    groups = [pennant.vertex_groups.new(name="cloth_{:02d}".format(i + 1)) for i in range(BONES)]
    root_group = pennant.vertex_groups.new(name="root")
    for vertex in mesh.vertices:
        along = vertex.co.y / CM - POLE_RADIUS
        if along < 0.5:
            root_group.add([vertex.index], 1.0, "REPLACE")  # The hoisted edge stays on the pole.
            continue
        position = along / step - 0.5
        low = max(0, min(BONES - 1, int(math.floor(position))))
        high = min(BONES - 1, low + 1)
        t = max(0.0, min(1.0, position - low))
        groups[low].add([vertex.index], 1.0 - t, "ADD")
        if high != low:
            groups[high].add([vertex.index], t, "ADD")
    pennant.parent = rig
    modifier = pennant.modifiers.new("Armature", "ARMATURE")
    modifier.object = rig
    return pennant, rig


def key_flutter(rig):
    # A wave running from the pole to the tip: each bone sways about Z (in and out of the cloth's plane) a little later
    # and wider than the one before, with a smaller ripple about Y. The 30 frames loop seamlessly.
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start = 0
    scene.frame_end = FLUTTER_FRAMES
    for frame in range(FLUTTER_FRAMES + 1):
        phase = 2.0 * math.pi * frame / FLUTTER_FRAMES
        for i in range(BONES):
            bone = rig.pose.bones["cloth_{:02d}".format(i + 1)]
            bone.rotation_mode = "XYZ"
            lag = 0.9 * i
            # Bones point along +Y, so their local X/Z are the world X/Z here.
            sway = math.radians((9.0 + 5.0 * i) * math.sin(phase - lag))
            ripple = math.radians((2.0 + 1.5 * i) * math.sin(2.0 * phase - lag))
            bone.rotation_euler = (ripple, 0.0, sway)
            bone.keyframe_insert("rotation_euler", frame=frame)
    rig.animation_data.action.name = "Flutter"


def export_static(obj, path):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_unit_scale=True, add_leaf_bones=False, mesh_smooth_type="EDGE")


def render_preview(folder, objects):
    scene = bpy.context.scene
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.8, 0.84, 0.9, 1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    scene.world = world
    key = bpy.data.objects.new("Key", bpy.data.lights.new("Key", "AREA"))
    key.data.energy = 60.0
    key.data.size = 1.5
    scene.collection.objects.link(key)
    key.location = (1.2, -1.0, 1.6)
    key.rotation_euler = (Vector((0.0, 0.2, 0.6)) - key.location).to_track_quat("-Z", "Y").to_euler()
    camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    camera.data.lens = 50.0
    scene.collection.objects.link(camera)
    camera.location = (1.6, -0.6, 0.95)
    camera.rotation_euler = (Vector((0.0, 0.2, 0.68)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 48
    scene.render.resolution_x = 360
    scene.render.resolution_y = 480
    for frame in (0, 8, 15, 23):
        scene.frame_set(frame)
        scene.render.filepath = os.path.join(folder, "flag_{:02d}.png".format(frame))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for existing in list(bpy.data.objects):
        bpy.data.objects.remove(existing)
    metal = material("M_FlagMetal", (0.62, 0.64, 0.67), 1.0, 0.3)
    cloth = material("M_FlagCloth", (0.85, 0.1, 0.1), 0.0, 0.6)
    pole_lower, pole_upper = build_poles(metal)
    pennant, rig = build_pennant(cloth)
    key_flutter(rig)

    export_static(pole_lower, os.path.join(OUT_DIR, "SM_FlagPoleLower.fbx"))
    export_static(pole_upper, os.path.join(OUT_DIR, "SM_FlagPoleUpper.fbx"))
    bpy.ops.object.select_all(action="DESELECT")
    pennant.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(OUT_DIR, "SK_FlagPennant.fbx"), use_selection=True, object_types={"ARMATURE", "MESH"},
        apply_unit_scale=True, add_leaf_bones=False, mesh_smooth_type="EDGE", use_armature_deform_only=True,
        bake_anim=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True,
    )
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "Flag.blend"))

    # For the preview only: the upper half and pennant raised onto the lower pole, as they sit in the Blueprint.
    pole_upper.location.z += POLE_HALF * CM
    rig.location.z += POLE_HALF * CM
    preview = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else OUT_DIR
    render_preview(preview, [pole_lower, pole_upper, pennant])
    print("FLAG done")
