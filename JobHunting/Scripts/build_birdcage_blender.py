# Builds a brass birdcage in Blender, saves SourceArt/Models/Birdcage/Birdcage.blend and .fbx and renders a preview.
# Run without opening Blender:
#   blender --background --factory-startup --python build_birdcage_blender.py
import math
import os

import bmesh
import bpy
from mathutils import Vector

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SourceArt", "Models", "Birdcage"))

# Shape (m). The bars rise straight from the tray, then curve over the dome to the top cap.
RADIUS = 0.30
BAR_BOTTOM = 0.065
SHOULDER = 0.62
DOME_HEIGHT = 0.33
TOP_OPENING = 0.03
BAR_COUNT = 20
BAR_RADIUS = 0.0045
RING_RADIUS = 0.0065

# The door spans three gaps on the front (-Y); the two bars inside it stop above and below the opening.
FRONT = -90.0
BAR_STEP = 360.0 / BAR_COUNT
DOOR_SPAN = 54.0
DOOR_BOTTOM = 0.14
DOOR_TOP = 0.50
DOOR_OFFSET = 0.012
DOOR_INSET = 0.012
DOOR_FRAME_RADIUS = 0.0065
DOOR_OPEN_DEGREES = 50.0


def on_cylinder(angle, z, radius=RADIUS):
    a = math.radians(angle)
    return Vector((radius * math.cos(a), radius * math.sin(a), z))


def swing_open(points, hinge):
    # Clockwise seen from above moves the door's free edge outward, away from the cage.
    a = math.radians(-DOOR_OPEN_DEGREES)
    swung = []
    for p in points:
        x, y = p.x - hinge.x, p.y - hinge.y
        swung.append(Vector((hinge.x + x * math.cos(a) - y * math.sin(a), hinge.y + x * math.sin(a) + y * math.cos(a), p.z)))
    return swung


def bar_points(angle, z_from, z_to):
    # Straight part, then a quarter ellipse that stops at the top opening.
    points = [on_cylinder(angle, z) for z in (z_from, z_to) if z <= SHOULDER]
    if z_to > SHOULDER:
        if z_from < SHOULDER:
            points = [on_cylinder(angle, z_from)]
        end = math.acos(TOP_OPENING / RADIUS)
        start = math.asin(max(0.0, z_from - SHOULDER) / DOME_HEIGHT)
        for i in range(25):
            t = start + (end - start) * i / 24
            points.append(on_cylinder(angle, SHOULDER + DOME_HEIGHT * math.sin(t), RADIUS * math.cos(t)))
    return points


def add_tube(name, points, radius, material, closed=False):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 1
    curve.use_fill_caps = True
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, position in zip(spline.points, points):
        point.co = (*position, 1.0)
    spline.use_cyclic_u = closed
    curve.materials.append(material)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    return obj


def add_ring(name, center, radius, tube, material, vertical=False, segments=64):
    points = []
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        offset = Vector((radius * math.cos(a), 0.0, radius * math.sin(a))) if vertical else Vector((radius * math.cos(a), radius * math.sin(a), 0.0))
        points.append(center + offset)
    return add_tube(name, points, tube, material, closed=True)


def add_lathe(name, profile, material, segments=64):
    # Spins (radius, z) points around Z. A radius of 0 closes the shape at that end.
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for radius, z in profile:
        count = 1 if radius == 0.0 else segments
        rings.append([bm.verts.new((radius * math.cos(2.0 * math.pi * i / count), radius * math.sin(2.0 * math.pi * i / count), z)) for i in range(count)])
    for lower, upper in zip(rings, rings[1:]):
        for i in range(segments):
            corners = [lower[i % len(lower)], lower[(i + 1) % len(lower)], upper[(i + 1) % len(upper)], upper[i % len(upper)]]
            # dict.fromkeys drops the repeated vertex where a ring closes to a point.
            bm.faces.new(list(dict.fromkeys(corners)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def new_material(name, color, metallic, roughness):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return material


def door_angles():
    return [FRONT - DOOR_SPAN / 2.0 + 1.0 + (DOOR_SPAN - 2.0) * i / 16 for i in range(17)]


def door_hinge():
    return on_cylinder(door_angles()[0], 0.0, RADIUS + DOOR_OFFSET)


def build_body(brass, wood):
    parts = []
    half_door = DOOR_SPAN / 2.0

    for i in range(BAR_COUNT):
        angle = FRONT + BAR_STEP / 2.0 + i * BAR_STEP
        relative = (angle - FRONT + 180.0) % 360.0 - 180.0
        if abs(relative) < half_door - 1.0:
            parts.append(add_tube("BarLow", bar_points(angle, BAR_BOTTOM, DOOR_BOTTOM), BAR_RADIUS, brass))
            parts.append(add_tube("BarHigh", bar_points(angle, DOOR_TOP, SHOULDER + DOME_HEIGHT), BAR_RADIUS, brass))
        else:
            parts.append(add_tube("Bar", bar_points(angle, BAR_BOTTOM, SHOULDER + DOME_HEIGHT), BAR_RADIUS, brass))

    for z in (0.085, DOOR_BOTTOM, DOOR_TOP, SHOULDER):
        parts.append(add_ring("Ring", Vector((0.0, 0.0, z)), RADIUS, RING_RADIUS, brass))
    for degrees in (32.0, 58.0):
        t = math.radians(degrees)
        parts.append(add_ring("DomeRing", Vector((0.0, 0.0, SHOULDER + DOME_HEIGHT * math.sin(t))), RADIUS * math.cos(t), RING_RADIUS * 0.8, brass))

    # Tray with a stepped rim, and the finial on top of the dome.
    parts.append(add_lathe("Tray", [(0.0, 0.0), (0.325, 0.0), (0.345, 0.008), (0.345, 0.03), (0.33, 0.04), (0.318, 0.075), (0.0, 0.075)], brass))
    top = SHOULDER + DOME_HEIGHT
    parts.append(add_lathe("Finial", [(0.0, top - 0.012), (0.042, top - 0.012), (0.046, top - 0.002), (0.03, top + 0.012), (0.012, top + 0.025), (0.012, top + 0.04), (0.024, top + 0.05), (0.028, top + 0.062), (0.024, top + 0.074), (0.012, top + 0.084), (0.0, top + 0.086)], brass, segments=32))
    parts.append(add_ring("Hook", Vector((0.0, 0.0, top + 0.128)), 0.042, 0.006, brass, vertical=True, segments=40))

    # Wooden perch from side to side, set back from the door.
    perch_y = 0.05
    perch_x = math.sqrt(RADIUS ** 2 - perch_y ** 2)
    parts.append(add_tube("Perch", [Vector((-perch_x, perch_y, 0.31)), Vector((perch_x, perch_y, 0.31))], 0.011, wood))
    return parts


def build_door(brass):
    # Door: a frame just outside the bars with its own bars, swung open on the hinge at its left edge.
    parts = []
    angles = door_angles()
    door_radius = RADIUS + DOOR_OFFSET
    hinge = door_hinge()
    frame = [on_cylinder(a, DOOR_BOTTOM + DOOR_INSET, door_radius) for a in angles]
    frame += [on_cylinder(a, DOOR_TOP - DOOR_INSET, door_radius) for a in reversed(angles)]
    parts.append(add_tube("DoorFrame", swing_open(frame, hinge), DOOR_FRAME_RADIUS, brass, closed=True))
    for relative in (-13.5, 0.0, 13.5):
        points = [on_cylinder(FRONT + relative, z, door_radius) for z in (DOOR_BOTTOM + DOOR_INSET, DOOR_TOP - DOOR_INSET)]
        parts.append(add_tube("DoorBar", swing_open(points, hinge), BAR_RADIUS, brass))
    latch = on_cylinder(angles[-1], (DOOR_BOTTOM + DOOR_TOP) / 2.0, door_radius + 0.018)
    parts.append(add_ring("Latch", swing_open([latch], hinge)[0], 0.016, 0.004, brass, vertical=True, segments=20))
    return parts


def join_parts(parts):
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.join()
    cage = bpy.context.view_layer.objects.active
    cage.name = "SM_Birdcage"
    cage.data.name = "SM_Birdcage"

    # Round tubes shade smooth; the tray's steps and the tube ends keep a hard edge.
    bm = bmesh.new()
    bm.from_mesh(cage.data)
    for face in bm.faces:
        face.smooth = True
    for edge in bm.edges:
        edge.smooth = len(edge.link_faces) == 2 and edge.calc_face_angle(0.0) < math.radians(50.0)
    bm.to_mesh(cage.data)
    triangles = sum(len(face.verts) - 2 for face in bm.faces)
    bm.free()
    return cage, triangles


def setup_render(path):
    scene = bpy.context.scene
    bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, 0.0))
    floor = bpy.context.active_object
    floor.data.materials.append(new_material("PreviewFloor", (0.32, 0.31, 0.3), 0.0, 0.6))

    world = bpy.data.worlds.new("PreviewWorld")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.75, 0.78, 0.85, 1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.7
    scene.world = world

    sun = bpy.data.lights.new("Key", "AREA")
    sun.energy = 90.0
    sun.size = 2.0
    light = bpy.data.objects.new("Key", sun)
    bpy.context.collection.objects.link(light)
    light.location = (-1.6, -1.8, 2.4)
    light.rotation_euler = (Vector((0.0, 0.0, 0.55)) - light.location).to_track_quat("-Z", "Y").to_euler()

    camera_data = bpy.data.cameras.new("Camera")
    camera_data.lens = 60.0
    camera = bpy.data.objects.new("Camera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (1.05, -2.45, 1.1)
    camera.rotation_euler = (Vector((0.0, 0.0, 0.53)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 96
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1100
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj)

    brass_material = new_material("M_Brass", (0.78, 0.56, 0.22), 1.0, 0.28)
    wood_material = new_material("M_Wood", (0.33, 0.17, 0.07), 0.0, 0.55)
    cage_object, triangle_count = join_parts(build_body(brass_material, wood_material) + build_door(brass_material))
    size = cage_object.dimensions
    print("BIRDCAGE triangles={} size={:.3f} x {:.3f} x {:.3f} m".format(triangle_count, size.x, size.y, size.z))

    bpy.ops.object.select_all(action="DESELECT")
    cage_object.select_set(True)
    bpy.context.view_layer.objects.active = cage_object
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT_DIR, "SM_Birdcage.fbx"), use_selection=True, apply_unit_scale=True, add_leaf_bones=False, mesh_smooth_type="EDGE")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "Birdcage.blend"))

    setup_render(os.path.join(OUT_DIR, "Birdcage_Preview.png"))
    print("BIRDCAGE done")
