# BP_SunMarker (Gimmicks/Heaven): shows where a BP_TowerSun is about to land. Every Tick, while its Sun aims (Phase 1)
# or charges (Phase 2), the marker - a flat glowing disk the size of the sun's hit - sits on the sun's Target (the
# ball's aim, just above the ground) and shows; otherwise it hides. Nothing in the sun's own graph changes.
#   MI_SunMarker  orange see-through glow (Machine's M_SwitchGhost: Color, Opacity)
# Graph: BP_SunMarker_EventGraph.txt from gen_sun_marker.ps1. Safe to run again. Run after setup_tower_sun.py, with
# the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_sun_marker.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
GHOST = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine/M_SwitchGhost"
TOWER_SUN = DIR + "/BP_TowerSun"
CYLINDER = "/Engine/BasicShapes/Cylinder"
DISK = 240.0          # across: the sun's hit (HitRadius 110) and a little more

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

path = DIR + "/MI_SunMarker"
if library.does_asset_exist(path):
    look = unreal.load_asset(path)
else:
    look = tools.create_asset("MI_SunMarker", DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(look, unreal.load_asset(GHOST))
    editing.set_material_instance_vector_parameter_value(look, "Color", unreal.LinearColor(1.0, 0.45, 0.08, 1.0))
    editing.set_material_instance_scalar_parameter_value(look, "Opacity", 0.55)
    library.save_asset(path, False)
    lines.append("created " + path)

MARKER = DIR + "/BP_SunMarker"
if library.does_asset_exist(MARKER):
    marker = unreal.load_asset(MARKER)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    marker = tools.create_asset("BP_SunMarker", DIR, unreal.Blueprint, factory)
    lines.append("created " + MARKER)
found = {}
for handle in subsystem.k2_gather_subobject_data_for_blueprint(marker):
    component = data_library.get_associated_object(data_library.get_data(handle))
    if component is not None:
        found[component.get_name().replace("_GEN_VARIABLE", "")] = component
if "Disk" not in found:
    root = subsystem.k2_gather_subobject_data_for_blueprint(marker)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.StaticMeshComponent, blueprint_context=marker)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("Disk"))
    disk = data_library.get_associated_object(data_library.get_data(handle))
    disk.set_editor_property("static_mesh", unreal.load_asset(CYLINDER))
    disk.set_material(0, look)
    disk.set_editor_property("relative_scale3d", unreal.Vector(DISK / 100.0, DISK / 100.0, 0.03))
    disk.set_collision_profile_name("NoCollision")
    disk.set_editor_property("cast_shadow", False)
    lines.append("BP_SunMarker: component Disk")
defaults = unreal.get_default_object(marker.generated_class())
try:
    defaults.get_editor_property("Sun")
except Exception:
    sun_class = unreal.load_asset(TOWER_SUN).generated_class()
    if not pins.add_member_variable(marker, "Sun", pins.get_object_reference_type(sun_class)):
        raise RuntimeError("Could not add Sun")
    pins.set_blueprint_variable_instance_editable(marker, "Sun", True)
    lines.append("BP_SunMarker: variable Sun")
pins.compile_blueprint(marker)
defaults = unreal.get_default_object(marker.generated_class())
defaults.set_editor_property("hidden", True)   # (hidden until the sun aims)
library.save_asset(MARKER, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "sun_marker.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
