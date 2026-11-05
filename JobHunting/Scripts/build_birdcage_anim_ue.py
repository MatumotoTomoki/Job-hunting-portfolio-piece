# Builds the two door-opening birdcages to compare. Run after build_birdcage_anim_blender.py, with the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=build_birdcage_anim_ue.py -unattended -nop4 -nosplash -stdout
# BP_BirdcageDoor_UE turns a separate door mesh with MoveComponentTo; BP_BirdcageDoor_Blender plays Blender's Door_Open.
# The Event Graphs come from BP_BirdcageDoor_*_EventGraph.txt, which rely on the component names used here.
# Never recreates an existing asset: that would wipe a pasted Event Graph.
import os
import sys

import unreal

SCRIPT_DIR = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "Scripts")
# Keeps a __pycache__ folder out of Scripts.
sys.dont_write_bytecode = True
sys.path.insert(0, SCRIPT_DIR)
import build_birdcage_ue as shape

ASSET_DIR = shape.ASSET_DIR
SK_FBX_PATH = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Birdcage", "SK_Birdcage.fbx")
TRIGGER_RADIUS = 250.0
TRIGGER_HEIGHT = 60.0

DATA_LIBRARY = unreal.SubobjectDataBlueprintFunctionLibrary
SUBOBJECT_SUBSYSTEM = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)


def add_component(blueprint, parent_handle, component_class, name):
    params = unreal.AddNewSubobjectParams(parent_handle=parent_handle, new_class=component_class, blueprint_context=blueprint)
    handle, _ = SUBOBJECT_SUBSYSTEM.add_new_subobject(params)
    if not DATA_LIBRARY.is_handle_valid(handle):
        raise RuntimeError("Could not add component {}".format(name))
    SUBOBJECT_SUBSYSTEM.rename_subobject(handle, unreal.Text(name))
    return handle, DATA_LIBRARY.get_object(DATA_LIBRARY.get_data(handle))


def new_blueprint(name):
    path = ASSET_DIR + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return None, None
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    blueprint = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, ASSET_DIR, unreal.Blueprint, factory)
    if not blueprint:
        raise RuntimeError("Could not create " + path)
    return blueprint, SUBOBJECT_SUBSYSTEM.k2_gather_subobject_data_for_blueprint(blueprint)[0]


def add_trigger(blueprint, root):
    # Overlapping decides everything; the cage itself has no collision, so the door cannot shove the player.
    _, trigger = add_component(blueprint, root, unreal.SphereComponent, "Trigger")
    trigger.set_editor_property("sphere_radius", TRIGGER_RADIUS)
    trigger.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, TRIGGER_HEIGHT))
    trigger.set_collision_profile_name("OverlapOnlyPawn")


def finish_blueprint(blueprint, name):
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    unreal.EditorAssetLibrary.save_asset(ASSET_DIR + "/" + name, False)


def assign_static_materials(mesh, brass, wood):
    for index, slot in enumerate(mesh.get_editor_property("static_materials")):
        mesh.set_material(index, wood if "wood" in str(slot.get_editor_property("material_slot_name")).lower() else brass)
    unreal.EditorAssetLibrary.save_asset(mesh.get_path_name().split(".")[0], False)


def build_ue_version(brass, wood, report):
    # The door mesh's origin is its hinge, so turning the component turns the door on the hinge.
    shape.DOOR_OPEN_DEGREES = 0.0
    body = shape.Mesh()
    shape.add_body(body)
    door = shape.Mesh()
    shape.add_door(door)
    hinge = shape.door_hinge()
    door.verts = [shape.sub(v, hinge) for v in door.verts]
    intermediate = os.path.abspath(unreal.Paths.project_intermediate_dir())
    body_path = os.path.join(intermediate, "SM_BirdcageBody_UE.obj")
    door_path = os.path.join(intermediate, "SM_BirdcageDoor_UE.obj")
    shape.write_obj(body, body_path)
    shape.write_obj(door, door_path)
    body_asset = shape.import_mesh(body_path, "SM_BirdcageBody_UE")
    door_asset = shape.import_mesh(door_path, "SM_BirdcageDoor_UE")
    assign_static_materials(body_asset, brass, wood)
    assign_static_materials(door_asset, brass, wood)
    box = door_asset.get_bounding_box()
    report.append("door mesh: min {} max {}".format(box.min, box.max))

    name = "BP_BirdcageDoor_UE"
    blueprint, root = new_blueprint(name)
    if not blueprint:
        report.append(name + " already exists")
        return
    _, body_component = add_component(blueprint, root, unreal.StaticMeshComponent, "Body")
    body_component.set_editor_property("static_mesh", body_asset)
    body_component.set_collision_profile_name("NoCollision")
    # The OBJ importer mirrors Y into Unreal's coordinates, and so the hinge sits at +Y here.
    hinge_handle, hinge_component = add_component(blueprint, root, unreal.SceneComponent, "DoorHinge")
    hinge_component.set_editor_property("relative_location", unreal.Vector(hinge[0], -hinge[1], 0.0))
    # MoveComponentTo also sets the location: a child at zero lets it target (0,0,0) wherever the hinge is.
    pivot_handle, pivot = add_component(blueprint, hinge_handle, unreal.SceneComponent, "DoorPivot")
    pivot.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    _, door_component = add_component(blueprint, pivot_handle, unreal.StaticMeshComponent, "Door")
    door_component.set_editor_property("static_mesh", door_asset)
    door_component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    door_component.set_collision_profile_name("NoCollision")
    add_trigger(blueprint, root)
    finish_blueprint(blueprint, name)
    report.append("created " + name)


def import_skeletal(report):
    existing = {}
    for path in unreal.EditorAssetLibrary.list_assets(ASSET_DIR, recursive=False):
        asset = unreal.load_asset(path)
        if isinstance(asset, (unreal.SkeletalMesh, unreal.AnimSequence)):
            existing[type(asset)] = asset
    if unreal.SkeletalMesh in existing and unreal.AnimSequence in existing:
        return existing[unreal.SkeletalMesh], existing[unreal.AnimSequence]
    task = unreal.AssetImportTask()
    task.filename = SK_FBX_PATH
    task.destination_path = ASSET_DIR
    task.automated = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    report.append("skeletal import: {}".format(list(task.imported_object_paths)))
    mesh, animation = None, None
    for path in task.imported_object_paths:
        asset = unreal.load_asset(path)
        if isinstance(asset, unreal.SkeletalMesh):
            mesh = asset
        elif isinstance(asset, unreal.AnimSequence):
            animation = asset
    if not mesh or not animation:
        raise RuntimeError("Expected a skeletal mesh and an animation from " + SK_FBX_PATH)
    return mesh, animation


def assign_skeletal_materials(mesh, brass, wood):
    for material in (brass, wood):
        material.set_editor_property("used_with_skeletal_mesh", True)
        unreal.MaterialEditingLibrary.recompile_material(material)
        unreal.EditorAssetLibrary.save_asset(material.get_path_name().split(".")[0], False)
    # Items of a struct array are copies: each one has to be written back by index.
    materials = mesh.get_editor_property("materials")
    for index in range(len(materials)):
        slot = materials[index]
        slot.set_editor_property("material_interface", wood if "wood" in str(slot.get_editor_property("material_slot_name")).lower() else brass)
        materials[index] = slot
    mesh.set_editor_property("materials", materials)
    # remove_import_materials deletes what the import created, so make sure the mesh really let go of it.
    for slot in mesh.get_editor_property("materials"):
        if slot.get_editor_property("material_interface") not in (brass, wood):
            raise RuntimeError("Could not assign the materials of " + mesh.get_name())


def build_blender_version(brass, wood, report):
    mesh, animation = import_skeletal(report)
    assign_skeletal_materials(mesh, brass, wood)
    unreal.EditorAssetLibrary.save_asset(mesh.get_path_name().split(".")[0], False)
    unreal.EditorAssetLibrary.save_asset(animation.get_path_name().split(".")[0], False)

    bounds = mesh.get_bounds()
    report.append("skeletal mesh {}: origin {} extent {}".format(mesh.get_name(), bounds.origin, bounds.box_extent))
    report.append("animation {}: length {} s".format(animation.get_name(), animation.get_play_length()))
    library = unreal.AnimationLibrary
    report.append("bones: {}".format(library.get_animation_track_names(animation)))
    for frame in (0, 14, 20, 30):
        report.append("  frame {}: {}".format(frame, library.get_bone_pose_for_frame(animation, "Door", frame, False)))

    name = "BP_BirdcageDoor_Blender"
    blueprint, root = new_blueprint(name)
    if not blueprint:
        report.append(name + " already exists")
        return
    _, cage = add_component(blueprint, root, unreal.SkeletalMeshComponent, "Cage")
    cage.set_editor_property("skeletal_mesh_asset", mesh)
    cage.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    # Loaded but not playing: the door waits closed on the first frame until the graph calls Play.
    play_data = cage.get_editor_property("animation_data")
    play_data.set_editor_property("anim_to_play", animation)
    play_data.set_editor_property("saved_looping", False)
    play_data.set_editor_property("saved_playing", False)
    cage.set_editor_property("animation_data", play_data)
    cage.set_collision_profile_name("NoCollision")
    add_trigger(blueprint, root)
    finish_blueprint(blueprint, name)
    report.append("created " + name)


brass_material = shape.make_material("M_Birdcage_Brass", (0.78, 0.56, 0.22), 1.0, 0.28)
wood_material = shape.make_material("M_Birdcage_Wood", (0.33, 0.17, 0.07), 0.0, 0.55)
results = []
build_ue_version(brass_material, wood_material, results)
build_blender_version(brass_material, wood_material, results)
shape.remove_import_materials()

with open(os.path.join(unreal.Paths.project_saved_dir(), "birdcage_anim_report.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(results))
unreal.log("\n".join(results))
