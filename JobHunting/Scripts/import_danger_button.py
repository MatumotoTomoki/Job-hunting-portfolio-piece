# Imports the danger button (build_danger_button_blender.py, build_danger_button_textures.ps1) into
# /Game/ThirdPerson/Blueprints/Gimmicks/DangerButton and makes BP_DangerButton (Body; Cap, the part that goes down,
# sitting on it; Trigger, in front of it), then puts one in LV_Debug beside the newer gimmicks to look at.
# Meshes and textures are re-imported every run. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\import_danger_button.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/DangerButton"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "DangerButton")
FLAT_COLOR = "/Game/LevelPrototyping/Materials/M_FlatCol"
DEBUG_LEVEL = "/Game/LV_Debug"
CAP_Z = 162.0
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def import_file(name, mesh=True):
    task = unreal.AssetImportTask()
    task.filename = os.path.join(SOURCE, name)
    task.destination_path = DIR
    task.automated = True
    task.save = True
    task.replace_existing = True
    if mesh:
        options = unreal.FbxImportUI()
        options.set_editor_property("import_materials", False)
        options.set_editor_property("import_textures", False)
        task.options = options
    tools.import_asset_tasks([task])
    path = DIR + "/" + os.path.splitext(name)[0]
    lines.append("imported " + path)
    return unreal.load_asset(path)


def flat(name, color):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    instance = tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(instance, unreal.load_asset(FLAT_COLOR))
    editing.set_material_instance_vector_parameter_value(instance, "Base Color", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    library.save_asset(path, False)
    return instance


def textured_master():
    path = DIR + "/M_DangerTexture"
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    material = tools.create_asset("M_DangerTexture", DIR, unreal.Material, unreal.MaterialFactoryNew())
    sample = editing.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -500, 0)
    sample.set_editor_property("parameter_name", "Tex")
    rough = editing.create_material_expression(material, unreal.MaterialExpressionConstant, -300, 250)
    rough.set_editor_property("r", 0.45)
    editing.connect_material_property(sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    editing.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    editing.recompile_material(material)
    library.save_asset(path, False)
    return material


def textured(name, texture):
    path = DIR + "/" + name
    instance = unreal.load_asset(path) if library.does_asset_exist(path) else \
        tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(instance, textured_master())
    editing.set_material_instance_texture_parameter_value(instance, "Tex", texture)
    library.save_asset(path, False)
    return instance


textures = {name: import_file(name + ".png", mesh=False) for name in ("T_DangerStripes", "T_DangerSign", "T_DangerLabel")}
body_mesh = import_file("SM_DangerButton_Body.fbx")
cap_mesh = import_file("SM_DangerButton_Cap.fbx")
by_slot = {
    "M_DangerYellow": flat("MI_DangerYellow", (0.92, 0.62, 0.0)),
    "M_DangerBlack": flat("MI_DangerBlack", (0.02, 0.02, 0.02)),
    "M_DangerSteel": flat("MI_DangerSteel", (0.22, 0.23, 0.25)),
    "M_DangerRedDark": flat("MI_DangerRedDark", (0.35, 0.02, 0.02)),
    "M_DangerRed": flat("MI_DangerRed", (0.85, 0.02, 0.02)),
    "M_DangerStripes": textured("MI_DangerStripes", textures["T_DangerStripes"]),
    "M_DangerSign": textured("MI_DangerSign", textures["T_DangerSign"]),
    "M_DangerLabel": textured("MI_DangerLabel", textures["T_DangerLabel"]),
}
for mesh, path in ((body_mesh, DIR + "/SM_DangerButton_Body"), (cap_mesh, DIR + "/SM_DangerButton_Cap")):
    for index, slot in enumerate(mesh.get_editor_property("static_materials")):
        name = str(slot.get_editor_property("material_slot_name"))
        if name in by_slot:
            mesh.set_material(index, by_slot[name])
        else:
            lines.append("WARNING: no material for slot " + name)
    library.save_asset(path, False)
lines.append("body bounds {}".format(body_mesh.get_bounds().box_extent))


def components(blueprint):
    found = {}
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_associated_object(data_library.get_data(handle))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = (handle, component)
    return found


def add_component(blueprint, component_class, name):
    existing = components(blueprint)
    if name in existing:
        return existing[name][1], False
    root = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=component_class, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("component " + name)
    return data_library.get_associated_object(data_library.get_data(handle)), True


path = DIR + "/BP_DangerButton"
if library.does_asset_exist(path):
    button = unreal.load_asset(path)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    button = tools.create_asset("BP_DangerButton", DIR, unreal.Blueprint, factory)
body, _ = add_component(button, unreal.StaticMeshComponent, "Body")
body.set_editor_property("static_mesh", body_mesh)
cap, _ = add_component(button, unreal.StaticMeshComponent, "Cap")
cap.set_editor_property("static_mesh", cap_mesh)
cap.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, CAP_Z))
trigger, made = add_component(button, unreal.BoxComponent, "Trigger")
if made:
    # In front of the sign (+X): where the player stands to press it.
    trigger.set_editor_property("box_extent", unreal.Vector(60.0, 80.0, 90.0))
    trigger.set_editor_property("relative_location", unreal.Vector(110.0, 0.0, 90.0))
    trigger.set_collision_profile_name("OverlapOnlyPawn")
pins.compile_blueprint(button)
library.save_asset(path, False)

# One in LV_Debug, by the newer gimmicks (add_new_gimmicks_to_debug.py), its front toward the PlayerStart side (-X).
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level(DEBUG_LEVEL):
    raise RuntimeError("Could not open " + DEBUG_LEVEL)
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith("DB "):
        actors.destroy_actor(actor)
placed = actors.spawn_actor_from_class(button.generated_class(), unreal.Vector(4200.0, -3200.0, 0.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
placed.set_actor_label("DB Danger Button")
placed.set_folder_path("NewGimmicks")
sign = actors.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(4200.0, -3200.0, 320.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
sign.set_actor_label("DB Label Danger Button")
sign.set_folder_path("NewGimmicks")
render = sign.get_editor_property("text_render")
render.set_text(unreal.Text("Danger Button"))
render.set_editor_property("world_size", 50.0)
render.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
lines.append("LV_Debug saved {}".format(level.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "danger_button_import.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
