# Imports the Blender flag from build_flag_blender.py and puts it on BP_CheckpointFlag and BP_CheckpointItem: the poles
# replace the cylinders, the fluttering SK_FlagPennant replaces the box cloth, and the knob is now part of the upper
# pole. The pasted Event Graphs use only Base, Upper and Trigger, so they keep working. With the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=import_flag_models.py -unattended -nop4 -nosplash -stdout
# Importing over an existing skeletal mesh would not update its animation, so to re-import a changed flutter, delete
# the SK_FlagPennant assets in Model first.
import os

import unreal

DIR = "/Game/ThirdPerson/Item/Checkpoint"
MODEL_DIR = DIR + "/Model"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Flag")
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def import_fbx(file_name, destination_name=None):
    task = unreal.AssetImportTask()
    task.filename = os.path.join(SOURCE, file_name)
    task.destination_path = MODEL_DIR
    if destination_name:
        task.destination_name = destination_name
    task.automated = True
    task.save = True
    tools.import_asset_tasks([task])
    return [unreal.load_asset(p) for p in task.imported_object_paths]


def static_mesh(name):
    path = MODEL_DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    return next(a for a in import_fbx(name + ".fbx", name) if isinstance(a, unreal.StaticMesh))


def pennant():
    if library.does_asset_exist(MODEL_DIR + "/SK_FlagPennant"):
        anims = [unreal.load_asset(p) for p in library.list_assets(MODEL_DIR, recursive=False) if "Anim" in p]
        return unreal.load_asset(MODEL_DIR + "/SK_FlagPennant"), next(a for a in anims if isinstance(a, unreal.AnimSequence))
    imported = import_fbx("SK_FlagPennant.fbx")
    mesh = next(a for a in imported if isinstance(a, unreal.SkeletalMesh))
    anim = next(a for a in imported if isinstance(a, unreal.AnimSequence))
    return mesh, anim


def pennant_material():
    # Its own material: a single sheet of cloth needs both sides drawn, and a skinned mesh needs the skeletal usage.
    path = DIR + "/M_FlagPennant"
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    material = tools.create_asset("M_FlagPennant", DIR, unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property("two_sided", True)
    material.set_editor_property("used_with_skeletal_mesh", True)
    color = editing.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -500, 0)
    color.set_editor_property("parameter_name", "Base Color")
    color.set_editor_property("default_value", unreal.LinearColor(0.85, 0.1, 0.1, 1.0))
    editing.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    rough = editing.create_material_expression(material, unreal.MaterialExpressionConstant, -500, 250)
    rough.set_editor_property("r", 0.6)
    editing.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    editing.recompile_material(material)
    library.save_asset(path, False)
    return material


def metal_pole_material():
    # The flat-colour instance the pole already used, turned into polished steel.
    instance = unreal.load_asset(DIR + "/MI_FlagPole")
    editing.set_material_instance_vector_parameter_value(instance, "Base Color", unreal.LinearColor(0.62, 0.64, 0.67, 1.0))
    editing.set_material_instance_scalar_parameter_value(instance, "Metallic", 1.0)
    editing.set_material_instance_scalar_parameter_value(instance, "Roughness", 0.3)
    library.save_asset(DIR + "/MI_FlagPole", False)
    return instance


def components(blueprint):
    found = {}
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_object(data_library.get_data(handle))
        if component is not None:
            found.setdefault(component.get_name().replace("_GEN_VARIABLE", ""), (handle, component))
    return found


def restyle(path, size, meshes, pole_material, cloth_material, flutter):
    blueprint = unreal.load_asset(path)
    parts = components(blueprint)
    if "Pennant" in parts:
        lines.append("{}: already restyled".format(path.split("/")[-1]))
        return
    scale = unreal.Vector(size, size, size)
    for name, mesh in (("PoleLower", meshes[0]), ("PoleUpper", meshes[1])):
        component = parts[name][1]
        component.set_editor_property("static_mesh", mesh)
        component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
        component.set_editor_property("relative_scale3d", scale)
        component.set_material(0, pole_material)
    root = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
    removed = subsystem.delete_subobjects(root, [parts["Cloth"][0], parts["Knob"][0]], blueprint)
    params = unreal.AddNewSubobjectParams(parent_handle=parts["Upper"][0], new_class=unreal.SkeletalMeshComponent, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("Pennant"))
    cloth = data_library.get_object(data_library.get_data(handle))
    cloth.set_editor_property("skeletal_mesh_asset", meshes[2])
    cloth.set_editor_property("relative_scale3d", scale)
    cloth.set_material(0, cloth_material)
    cloth.set_collision_profile_name("NoCollision")
    cloth.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    play = cloth.get_editor_property("animation_data")
    play.set_editor_property("anim_to_play", flutter)
    play.set_editor_property("saved_looping", True)
    play.set_editor_property("saved_playing", True)
    cloth.set_editor_property("animation_data", play)
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    library.save_asset(path, False)
    lines.append("{}: restyled, removed {} old parts".format(path.split("/")[-1], removed))


lower = static_mesh("SM_FlagPoleLower")
upper = static_mesh("SM_FlagPoleUpper")
cloth_mesh, flutter_anim = pennant()
pole = metal_pole_material()
cloth_mat = pennant_material()
for mesh in (lower, upper):
    mesh.set_material(0, pole)
    library.save_asset(mesh.get_path_name().split(".")[0], False)
# Items of a struct array are copies: each one is written back by index.
slots = cloth_mesh.get_editor_property("materials")
for index in range(len(slots)):
    slot = slots[index]
    slot.set_editor_property("material_interface", cloth_mat)
    slots[index] = slot
cloth_mesh.set_editor_property("materials", slots)
library.save_asset(cloth_mesh.get_path_name().split(".")[0], False)

restyle(DIR + "/BP_CheckpointFlag", 1.0, (lower, upper, cloth_mesh), pole, cloth_mat, flutter_anim)
restyle(DIR + "/BP_CheckpointItem", 0.6, (lower, upper, cloth_mesh), pole, cloth_mat, flutter_anim)

# The FBX imports bring their own materials; the meshes were just given the shared ones above.
for path in library.list_assets(MODEL_DIR, recursive=False):
    asset_data = library.find_asset_data(path.split(".")[0])
    if str(asset_data.asset_class_path.asset_name) in ("Material", "MaterialInstanceConstant") and not library.find_package_referencers_for_asset(path.split(".")[0]):
        lines.append("removed import material {}: {}".format(path.split(".")[-1], library.delete_asset(path.split(".")[0])))
if library.does_asset_exist(DIR + "/MI_FlagKnob") and not library.find_package_referencers_for_asset(DIR + "/MI_FlagKnob"):
    lines.append("removed MI_FlagKnob (the knob is metal now): {}".format(library.delete_asset(DIR + "/MI_FlagKnob")))

for name, mesh in (("lower", lower), ("upper", upper)):
    box = mesh.get_bounding_box()
    lines.append("{} pole: z {:.1f}..{:.1f}, radius {:.1f}".format(name, box.min.z, box.max.z, box.max.x))
bounds = cloth_mesh.get_bounds()
lines.append("pennant: origin {} extent {}, flutter {:.2f} s".format(bounds.origin, bounds.box_extent, flutter_anim.get_play_length()))
lines.append("model folder: {}".format([p.split(".")[-1] for p in library.list_assets(MODEL_DIR, recursive=False)]))
with open(os.path.join(unreal.Paths.project_saved_dir(), "flag_models_report.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
