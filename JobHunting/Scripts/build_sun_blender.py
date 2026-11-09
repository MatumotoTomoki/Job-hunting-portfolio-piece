# Builds the sun in Blender: a glowing ball with a thin face patch on its front that shows one face of the atlas
# T_SunFaces.png (drawn by build_sun_faces.ps1; M_SunFace in UE picks which). The glow, rays and flames around it come
# from Effekseer, so the model is only the ball and the patch. Saves Sun.blend and SM_Sun.fbx in SourceArt/Models/Sun
# and renders a preview with the first face. The ball is RADIUS cm around the origin and the face looks toward +X (the
# actor's forward in Unreal). Material slots: 0 M_SunBody, 1 M_SunFace. Run:
#   blender --background --factory-startup --python build_sun_blender.py [-- <preview folder>]
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SourceArt", "Models", "Sun"))
CM = 0.01
RADIUS = 50.0

# The face patch, seen from the front: it spans -SPAN..SPAN of the radius across and up, the same square one atlas
# cell covers, but only out to EDGE from the middle (the cells are empty beyond that). LIFT keeps it just off the ball.
SPAN = 0.8
EDGE = 0.86
STEPS = 48
LIFT = 0.01
ATLAS_COLUMNS = 4
ATLAS_ROWS = 2


def new_object(name, bm):
    mesh = bpy.data.meshes.new(name)
    for face in bm.faces:
        face.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def build_ball():
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, radius=RADIUS * CM)
    return new_object("Ball", bm)


def build_face_patch():
    # A grid over the front, each point pushed onto the ball along the view direction (+X), so from the front the
    # atlas cell shows undistorted. x is the viewer's right, which is +Y here; UV (0..1) maps -SPAN..SPAN.
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    grid = {}
    for i in range(STEPS + 1):
        for j in range(STEPS + 1):
            x = -SPAN + 2.0 * SPAN * i / STEPS
            y = -SPAN + 2.0 * SPAN * j / STEPS
            if x * x + y * y > EDGE * EDGE:
                continue
            depth = math.sqrt(1.0 - x * x - y * y)
            grid[i, j] = bm.verts.new(Vector((depth, x, y)).normalized() * RADIUS * (1.0 + LIFT) * CM)
    for i in range(STEPS):
        for j in range(STEPS):
            corners = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            if all(c in grid for c in corners):
                face = bm.faces.new([grid[c] for c in corners])
                for loop, (ci, cj) in zip(face.loops, corners):
                    loop[uv_layer].uv = (ci / STEPS, cj / STEPS)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_object("FacePatch", bm)


def material(name, color, emission):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    shader = result.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = 0.5
    shader.inputs["Emission Color"].default_value = (*color, 1.0)
    shader.inputs["Emission Strength"].default_value = emission
    return result


def face_preview_material(name):
    # For the preview only: the atlas's first cell, cut out by its alpha. UE gets its own M_SunFace.
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    nodes, links = result.node_tree.nodes, result.node_tree.links
    shader = nodes["Principled BSDF"]
    image = nodes.new("ShaderNodeTexImage")
    image.image = bpy.data.images.load(os.path.join(OUT_DIR, "T_SunFaces.png"))
    image.extension = "CLIP"
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1.0 / ATLAS_COLUMNS, 1.0 / ATLAS_ROWS, 1.0)
    mapping.inputs["Location"].default_value = (0.0, 1.0 - 1.0 / ATLAS_ROWS, 0.0)  # Top-left cell.
    coords = nodes.new("ShaderNodeTexCoord")
    links.new(coords.outputs["UV"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], image.inputs["Vector"])
    links.new(image.outputs["Color"], shader.inputs["Base Color"])
    links.new(image.outputs["Color"], shader.inputs["Emission Color"])
    shader.inputs["Emission Strength"].default_value = 1.0
    links.new(image.outputs["Alpha"], shader.inputs["Alpha"])
    return result


def join(objects, name, materials):
    # objects: (object, material slot) pairs.
    bpy.ops.object.select_all(action="DESELECT")
    for obj, slot in objects:
        obj.data.materials.clear()
        for mat in materials:
            obj.data.materials.append(mat)
        for polygon in obj.data.polygons:
            polygon.material_index = slot
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0][0]
    bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    joined.name = name
    joined.data.name = name
    return joined


def render_preview(folder):
    scene = bpy.context.scene
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.45, 0.22, 0.2, 1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    scene.world = world
    camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    camera.data.lens = 50.0
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.render.resolution_x = 480
    scene.render.resolution_y = 480
    for label, direction in (("front", Vector((1.0, 0.0, 0.0))), ("side", Vector((0.6, -0.8, 0.25)))):
        camera.location = direction.normalized() * 2.6
        camera.rotation_euler = (-camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = os.path.join(folder, "sun_{}.png".format(label))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for existing in list(bpy.data.objects):
        bpy.data.objects.remove(existing)
    body = material("M_SunBody", (1.0, 0.42, 0.1), 1.5)
    face = material("M_SunFace", (0.62, 0.06, 0.1), 0.0)
    sun = join([(build_ball(), 0), (build_face_patch(), 1)], "SM_Sun", [body, face])
    # Only the patch brought a UV map; after the join it must be made the active one, or the face reads UV (0, 0).
    uv = sun.data.uv_layers["UVMap"]
    sun.data.uv_layers.active = uv
    uv.active_render = True

    bpy.ops.object.select_all(action="DESELECT")
    sun.select_set(True)
    bpy.context.view_layer.objects.active = sun
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT_DIR, "SM_Sun.fbx"), use_selection=True, apply_unit_scale=True, mesh_smooth_type="FACE")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "Sun.blend"))

    # The preview swaps in a material that shows the first face; the saved files keep the plain slots.
    sun.data.materials[1] = face_preview_material("SunFacePreview")
    preview = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else OUT_DIR
    render_preview(preview)
    print("SUN done")
