# Imports the same birdcage twice, for comparison: SM_Birdcage_UE, built here in plain Python, and
# SM_Birdcage_Blender from build_birdcage_blender.py. Shape values match that script (cm here, m there).
# Never overwrites an existing asset. With the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=build_birdcage_ue.py -unattended -nop4 -nosplash -stdout
import math
import os

import unreal

ASSET_DIR = "/Game/Prototype/Birdcage"
PROJECT_DIR = os.path.abspath(unreal.Paths.project_dir())
FBX_PATH = os.path.join(PROJECT_DIR, "SourceArt", "Models", "Birdcage", "SM_Birdcage.fbx")

RADIUS = 30.0
BAR_BOTTOM = 6.5
SHOULDER = 62.0
DOME_HEIGHT = 33.0
TOP_OPENING = 3.0
BAR_COUNT = 20
BAR_RADIUS = 0.45
RING_RADIUS = 0.65

FRONT = -90.0
BAR_STEP = 360.0 / BAR_COUNT
DOOR_SPAN = 54.0
DOOR_BOTTOM = 14.0
DOOR_TOP = 50.0
DOOR_OFFSET = 1.2
DOOR_INSET = 1.2
DOOR_FRAME_RADIUS = 0.65
DOOR_OPEN_DEGREES = 50.0

TUBE_SIDES = 8
HARD_EDGE_DEGREES = 50.0


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def scale(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def normalize(a):
    length = math.sqrt(dot(a, a))
    return scale(a, 1.0 / length) if length > 0.0 else (0.0, 0.0, 1.0)


class Mesh:
    def __init__(self):
        self.verts = []
        self.normals = []
        self.faces = {"M_Brass": [], "M_Wood": []}
        self.material = "M_Brass"

    def vert(self, position, normal):
        self.verts.append(position)
        self.normals.append(normal)
        return len(self.verts)

    def face(self, *indices):
        self.faces[self.material].append(indices)

    def triangle_count(self):
        return sum(len(f) - 2 for faces in self.faces.values() for f in faces)


def add_tube(mesh, points, radius, closed=False):
    count = len(points)
    tangents = []
    for i in range(count):
        before = points[(i - 1) % count] if closed or i > 0 else points[i]
        after = points[(i + 1) % count] if closed or i < count - 1 else points[i]
        tangents.append(normalize(sub(after, before)))

    # Carries a side vector along the tube, so the sections do not twist.
    side = cross(tangents[0], (0.0, 0.0, 1.0) if abs(tangents[0][2]) < 0.9 else (1.0, 0.0, 0.0))
    side = normalize(side)
    rings = []
    for point, tangent in zip(points, tangents):
        side = normalize(sub(side, scale(tangent, dot(side, tangent))))
        other = cross(tangent, side)
        ring = []
        for j in range(TUBE_SIDES):
            a = 2.0 * math.pi * j / TUBE_SIDES
            normal = add(scale(side, math.cos(a)), scale(other, math.sin(a)))
            ring.append(mesh.vert(add(point, scale(normal, radius)), normal))
        rings.append(ring)

    for i in range(count if closed else count - 1):
        lower, upper = rings[i], rings[(i + 1) % count]
        for j in range(TUBE_SIDES):
            k = (j + 1) % TUBE_SIDES
            mesh.face(lower[j], lower[k], upper[k], upper[j])

    if not closed:
        for point, tangent, ring, sign in ((points[0], tangents[0], rings[0], -1.0), (points[-1], tangents[-1], rings[-1], 1.0)):
            normal = scale(tangent, sign)
            center = mesh.vert(point, normal)
            cap = [mesh.vert(mesh.verts[v - 1], normal) for v in ring]
            for j in range(TUBE_SIDES):
                k = (j + 1) % TUBE_SIDES
                if sign > 0.0:
                    mesh.face(center, cap[j], cap[k])
                else:
                    mesh.face(center, cap[k], cap[j])


def add_ring(mesh, center, radius, tube, vertical=False, segments=64):
    points = []
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        offset = (radius * math.cos(a), 0.0, radius * math.sin(a)) if vertical else (radius * math.cos(a), radius * math.sin(a), 0.0)
        points.append(add(center, offset))
    add_tube(mesh, points, tube, closed=True)


def add_lathe(mesh, profile, segments=64):
    # Spins (radius, z) points around Z, bottom to top. Each band gets its own vertices so steps stay hard edged.
    slopes = []
    for (r0, z0), (r1, z1) in zip(profile, profile[1:]):
        length = math.hypot(r1 - r0, z1 - z0)
        slopes.append(((z1 - z0) / length, (r0 - r1) / length))

    def blended(band, other):
        # Rounds the edge between two bands only when they meet at a shallow angle.
        if other < 0 or other >= len(slopes):
            return slopes[band]
        a, b = slopes[band], slopes[other]
        if a[0] * b[0] + a[1] * b[1] < math.cos(math.radians(HARD_EDGE_DEGREES)):
            return a
        length = math.hypot(a[0] + b[0], a[1] + b[1])
        return ((a[0] + b[0]) / length, (a[1] + b[1]) / length)

    def ring(radius, z, normal):
        result = []
        for i in range(segments):
            t = 2.0 * math.pi * i / segments
            result.append(mesh.vert((radius * math.cos(t), radius * math.sin(t), z), (normal[0] * math.cos(t), normal[0] * math.sin(t), normal[1])))
        return result

    for band, ((r0, z0), (r1, z1)) in enumerate(zip(profile, profile[1:])):
        lower = ring(r0, z0, blended(band, band - 1))
        upper = ring(r1, z1, blended(band, band + 1))
        for i in range(segments):
            k = (i + 1) % segments
            if r0 == 0.0:
                mesh.face(lower[i], upper[k], upper[i])
            elif r1 == 0.0:
                mesh.face(lower[i], lower[k], upper[i])
            else:
                mesh.face(lower[i], lower[k], upper[k], upper[i])


def on_cylinder(angle, z, radius=RADIUS):
    a = math.radians(angle)
    return (radius * math.cos(a), radius * math.sin(a), z)


def swing_open(points, hinge):
    # Clockwise seen from above moves the door's free edge outward, away from the cage.
    a = math.radians(-DOOR_OPEN_DEGREES)
    swung = []
    for p in points:
        x, y = p[0] - hinge[0], p[1] - hinge[1]
        swung.append((hinge[0] + x * math.cos(a) - y * math.sin(a), hinge[1] + x * math.sin(a) + y * math.cos(a), p[2]))
    return swung


def bar_points(angle, z_from, z_to):
    # Straight part, then a quarter ellipse that stops at the top opening.
    if z_to <= SHOULDER:
        return [on_cylinder(angle, z_from), on_cylinder(angle, z_to)]
    points = [on_cylinder(angle, z_from)] if z_from < SHOULDER else []
    end = math.acos(TOP_OPENING / RADIUS)
    start = math.asin(max(0.0, z_from - SHOULDER) / DOME_HEIGHT)
    for i in range(25):
        t = start + (end - start) * i / 24
        points.append(on_cylinder(angle, SHOULDER + DOME_HEIGHT * math.sin(t), RADIUS * math.cos(t)))
    return points


def door_angles():
    return [FRONT - DOOR_SPAN / 2.0 + 1.0 + (DOOR_SPAN - 2.0) * i / 16 for i in range(17)]


def door_hinge():
    return on_cylinder(door_angles()[0], 0.0, RADIUS + DOOR_OFFSET)


def add_body(mesh):
    half_door = DOOR_SPAN / 2.0

    for i in range(BAR_COUNT):
        angle = FRONT + BAR_STEP / 2.0 + i * BAR_STEP
        relative = (angle - FRONT + 180.0) % 360.0 - 180.0
        if abs(relative) < half_door - 1.0:
            add_tube(mesh, bar_points(angle, BAR_BOTTOM, DOOR_BOTTOM), BAR_RADIUS)
            add_tube(mesh, bar_points(angle, DOOR_TOP, SHOULDER + DOME_HEIGHT), BAR_RADIUS)
        else:
            add_tube(mesh, bar_points(angle, BAR_BOTTOM, SHOULDER + DOME_HEIGHT), BAR_RADIUS)

    for z in (8.5, DOOR_BOTTOM, DOOR_TOP, SHOULDER):
        add_ring(mesh, (0.0, 0.0, z), RADIUS, RING_RADIUS)
    for degrees in (32.0, 58.0):
        t = math.radians(degrees)
        add_ring(mesh, (0.0, 0.0, SHOULDER + DOME_HEIGHT * math.sin(t)), RADIUS * math.cos(t), RING_RADIUS * 0.8)

    add_lathe(mesh, [(0.0, 0.0), (32.5, 0.0), (34.5, 0.8), (34.5, 3.0), (33.0, 4.0), (31.8, 7.5), (0.0, 7.5)])
    top = SHOULDER + DOME_HEIGHT
    add_lathe(mesh, [(0.0, top - 1.2), (4.2, top - 1.2), (4.6, top - 0.2), (3.0, top + 1.2), (1.2, top + 2.5), (1.2, top + 4.0), (2.4, top + 5.0), (2.8, top + 6.2), (2.4, top + 7.4), (1.2, top + 8.4), (0.0, top + 8.6)], segments=32)
    add_ring(mesh, (0.0, 0.0, top + 12.8), 4.2, 0.6, vertical=True, segments=40)

    mesh.material = "M_Wood"
    perch_y = 5.0
    perch_x = math.sqrt(RADIUS ** 2 - perch_y ** 2)
    add_tube(mesh, [(-perch_x, perch_y, 31.0), (perch_x, perch_y, 31.0)], 1.1)
    mesh.material = "M_Brass"


def add_door(mesh):
    angles = door_angles()
    door_radius = RADIUS + DOOR_OFFSET
    hinge = door_hinge()
    frame = [on_cylinder(a, DOOR_BOTTOM + DOOR_INSET, door_radius) for a in angles]
    frame += [on_cylinder(a, DOOR_TOP - DOOR_INSET, door_radius) for a in reversed(angles)]
    add_tube(mesh, swing_open(frame, hinge), DOOR_FRAME_RADIUS, closed=True)
    for relative in (-13.5, 0.0, 13.5):
        points = [on_cylinder(FRONT + relative, z, door_radius) for z in (DOOR_BOTTOM + DOOR_INSET, DOOR_TOP - DOOR_INSET)]
        add_tube(mesh, swing_open(points, hinge), BAR_RADIUS)
    latch = on_cylinder(angles[-1], (DOOR_BOTTOM + DOOR_TOP) / 2.0, door_radius + 1.8)
    add_ring(mesh, swing_open([latch], hinge)[0], 1.6, 0.4, vertical=True, segments=20)


def build_cage():
    mesh = Mesh()
    add_body(mesh)
    add_door(mesh)
    return mesh


def write_obj(mesh, path):
    mtl_name = os.path.splitext(os.path.basename(path))[0] + ".mtl"
    lines = ["mtllib " + mtl_name]
    lines += ["v {:.4f} {:.4f} {:.4f}".format(*v) for v in mesh.verts]
    lines += ["vn {:.4f} {:.4f} {:.4f}".format(*n) for n in mesh.normals]
    for material, faces in mesh.faces.items():
        lines.append("usemtl " + material)
        lines += ["f " + " ".join("{0}//{0}".format(i) for i in face) for face in faces]
    with open(path, "w") as out:
        out.write("\n".join(lines) + "\n")
    with open(os.path.join(os.path.dirname(path), mtl_name), "w") as out:
        out.write("newmtl M_Brass\nKd 0.78 0.56 0.22\nnewmtl M_Wood\nKd 0.33 0.17 0.07\n")


def import_mesh(source, name):
    path = ASSET_DIR + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.log(path + " already exists, reusing it")
        return unreal.load_asset(path)
    task = unreal.AssetImportTask()
    task.filename = source
    task.destination_path = ASSET_DIR
    task.destination_name = name
    task.automated = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    for imported in task.imported_object_paths:
        asset = unreal.load_asset(imported)
        if isinstance(asset, unreal.StaticMesh):
            return asset
    raise RuntimeError("Could not import " + source)


def make_material(name, color, metallic, roughness):
    path = ASSET_DIR + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.load_asset(path)
    library = unreal.MaterialEditingLibrary
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, ASSET_DIR, unreal.Material, unreal.MaterialFactoryNew())
    base = library.create_material_expression(material, unreal.MaterialExpressionConstant3Vector, -400, 0)
    base.set_editor_property("constant", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    library.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    for value, target, y in ((metallic, unreal.MaterialProperty.MP_METALLIC, 200), (roughness, unreal.MaterialProperty.MP_ROUGHNESS, 350)):
        constant = library.create_material_expression(material, unreal.MaterialExpressionConstant, -400, y)
        constant.set_editor_property("r", value)
        library.connect_material_property(constant, "", target)
    library.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(path, False)
    return material


def remove_import_materials():
    # An FBX import creates its own materials; the meshes use the shared ones instead.
    for leftover in ("M_Brass", "M_Wood"):
        leftover_path = ASSET_DIR + "/" + leftover
        if unreal.EditorAssetLibrary.does_asset_exist(leftover_path) and not unreal.EditorAssetLibrary.find_package_referencers_for_asset(leftover_path):
            unreal.EditorAssetLibrary.delete_asset(leftover_path)


if __name__ == "__main__":
    cage = build_cage()
    obj_path = os.path.join(os.path.abspath(unreal.Paths.project_intermediate_dir()), "SM_Birdcage_UE.obj")
    write_obj(cage, obj_path)

    brass = make_material("M_Birdcage_Brass", (0.78, 0.56, 0.22), 1.0, 0.28)
    wood = make_material("M_Birdcage_Wood", (0.33, 0.17, 0.07), 0.0, 0.55)

    report = ["python triangles: {}".format(cage.triangle_count())]
    for source, name in ((obj_path, "SM_Birdcage_UE"), (FBX_PATH, "SM_Birdcage_Blender")):
        mesh_asset = import_mesh(source, name)
        slots = mesh_asset.get_editor_property("static_materials")
        for index, slot in enumerate(slots):
            slot_name = str(slot.get_editor_property("material_slot_name")).lower()
            mesh_asset.set_material(index, wood if "wood" in slot_name else brass)
        unreal.EditorAssetLibrary.save_asset(ASSET_DIR + "/" + name, False)
        box = mesh_asset.get_bounding_box()
        report.append("{}: tris {}, min {}, max {}, slots {}".format(
            name, mesh_asset.get_num_triangles(0), box.min, box.max,
            [str(s.get_editor_property("material_slot_name")) for s in slots]))
    remove_import_materials()

    with open(os.path.join(unreal.Paths.project_saved_dir(), "birdcage_report.txt"), "w", encoding="utf-8") as out:
        out.write("\n".join(report))
    unreal.log("\n".join(report))
