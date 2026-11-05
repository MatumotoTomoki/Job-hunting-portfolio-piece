# Imports the Blender birdcage: SM_Birdcage_Blender, and the skeletal SK_Birdcage with its door animation, played by
# BP_BirdcageDoor_Blender. Run build_birdcage_blender.py and build_birdcage_anim_blender.py first. With the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=import_birdcage_blender.py -unattended -nop4 -nosplash -stdout
# The Event Graph comes from BP_BirdcageDoor_Blender_EventGraph.txt, which relies on the names Cage and Trigger.
# Never recreates an existing asset: that would wipe a pasted Event Graph. Importing over an existing skeletal mesh would
# not update its animation either, so a changed animation means deleting the SK_Birdcage assets first.
import os

import unreal

ASSET_DIR = "/Game/Prototype/Birdcage"
SOURCE_DIR = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Birdcage")
BP_NAME = "BP_BirdcageDoor_Blender"
TRIGGER_RADIUS = 250.0
TRIGGER_HEIGHT = 60.0

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
DATA_LIBRARY = unreal.SubobjectDataBlueprintFunctionLibrary
SUBOBJECT_SUBSYSTEM = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)


def asset_path(asset):
    return asset.get_path_name().split(".")[0]


def make_material(name, color, metallic, roughness):
    path = ASSET_DIR + "/" + name
    if library.does_asset_exist(path):
        material = unreal.load_asset(path)
    else:
        editing = unreal.MaterialEditingLibrary
        material = tools.create_asset(name, ASSET_DIR, unreal.Material, unreal.MaterialFactoryNew())
        base = editing.create_material_expression(material, unreal.MaterialExpressionConstant3Vector, -400, 0)
        base.set_editor_property("constant", unreal.LinearColor(color[0], color[1], color[2], 1.0))
        editing.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
        for value, target, y in ((metallic, unreal.MaterialProperty.MP_METALLIC, 200), (roughness, unreal.MaterialProperty.MP_ROUGHNESS, 350)):
            constant = editing.create_material_expression(material, unreal.MaterialExpressionConstant, -400, y)
            constant.set_editor_property("r", value)
            editing.connect_material_property(constant, "", target)
    material.set_editor_property("used_with_skeletal_mesh", True)
    unreal.MaterialEditingLibrary.recompile_material(material)
    library.save_asset(path, False)
    return material


def import_fbx(file_name, destination_name=None):
    task = unreal.AssetImportTask()
    task.filename = os.path.join(SOURCE_DIR, file_name)
    task.destination_path = ASSET_DIR
    if destination_name:
        task.destination_name = destination_name
    task.automated = True
    task.save = True
    tools.import_asset_tasks([task])
    return [unreal.load_asset(path) for path in task.imported_object_paths]


def material_for(slot_name, brass, wood):
    return wood if "wood" in str(slot_name).lower() else brass


def import_static(brass, wood):
    path = ASSET_DIR + "/SM_Birdcage_Blender"
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    mesh = next(asset for asset in import_fbx("SM_Birdcage.fbx", "SM_Birdcage_Blender") if isinstance(asset, unreal.StaticMesh))
    for index, slot in enumerate(mesh.get_editor_property("static_materials")):
        mesh.set_material(index, material_for(slot.get_editor_property("material_slot_name"), brass, wood))
    library.save_asset(path, False)
    return mesh


def import_skeletal(brass, wood):
    if library.does_asset_exist(ASSET_DIR + "/SK_Birdcage") and library.does_asset_exist(ASSET_DIR + "/SK_Birdcage_Anim"):
        return unreal.load_asset(ASSET_DIR + "/SK_Birdcage"), unreal.load_asset(ASSET_DIR + "/SK_Birdcage_Anim")
    imported = import_fbx("SK_Birdcage.fbx")
    mesh = next(asset for asset in imported if isinstance(asset, unreal.SkeletalMesh))
    animation = next(asset for asset in imported if isinstance(asset, unreal.AnimSequence))
    # Items of a struct array are copies: each one has to be written back by index.
    materials = mesh.get_editor_property("materials")
    for index in range(len(materials)):
        slot = materials[index]
        slot.set_editor_property("material_interface", material_for(slot.get_editor_property("material_slot_name"), brass, wood))
        materials[index] = slot
    mesh.set_editor_property("materials", materials)
    library.save_asset(asset_path(mesh), False)
    library.save_asset(asset_path(animation), False)
    return mesh, animation


def add_component(blueprint, parent_handle, component_class, name):
    params = unreal.AddNewSubobjectParams(parent_handle=parent_handle, new_class=component_class, blueprint_context=blueprint)
    handle, _ = SUBOBJECT_SUBSYSTEM.add_new_subobject(params)
    if not DATA_LIBRARY.is_handle_valid(handle):
        raise RuntimeError("Could not add component {}".format(name))
    SUBOBJECT_SUBSYSTEM.rename_subobject(handle, unreal.Text(name))
    return DATA_LIBRARY.get_object(DATA_LIBRARY.get_data(handle))


def build_blueprint(mesh, animation):
    path = ASSET_DIR + "/" + BP_NAME
    if library.does_asset_exist(path):
        return
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    blueprint = tools.create_asset(BP_NAME, ASSET_DIR, unreal.Blueprint, factory)
    if not blueprint:
        raise RuntimeError("Could not create " + path)
    root = SUBOBJECT_SUBSYSTEM.k2_gather_subobject_data_for_blueprint(blueprint)[0]
    cage = add_component(blueprint, root, unreal.SkeletalMeshComponent, "Cage")
    cage.set_editor_property("skeletal_mesh_asset", mesh)
    cage.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    # Loaded but not playing: the door waits closed on the first frame until the graph calls Play.
    play_data = cage.get_editor_property("animation_data")
    play_data.set_editor_property("anim_to_play", animation)
    play_data.set_editor_property("saved_looping", False)
    play_data.set_editor_property("saved_playing", False)
    cage.set_editor_property("animation_data", play_data)
    # Overlapping decides everything; the cage itself has no collision, so the door cannot shove the player.
    cage.set_collision_profile_name("NoCollision")
    trigger = add_component(blueprint, root, unreal.SphereComponent, "Trigger")
    trigger.set_editor_property("sphere_radius", TRIGGER_RADIUS)
    trigger.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, TRIGGER_HEIGHT))
    trigger.set_collision_profile_name("OverlapOnlyPawn")
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    library.save_asset(path, False)


brass_material = make_material("M_Birdcage_Brass", (0.78, 0.56, 0.22), 1.0, 0.28)
wood_material = make_material("M_Birdcage_Wood", (0.33, 0.17, 0.07), 0.0, 0.55)
import_static(brass_material, wood_material)
skeletal_mesh, door_animation = import_skeletal(brass_material, wood_material)
build_blueprint(skeletal_mesh, door_animation)

# An FBX import creates its own materials; the meshes use the shared ones above instead.
for leftover in ("M_Brass", "M_Wood"):
    if library.does_asset_exist(ASSET_DIR + "/" + leftover):
        library.delete_asset(ASSET_DIR + "/" + leftover)
unreal.log("Birdcage assets ready in " + ASSET_DIR)
