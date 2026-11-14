# Area 4's wings, in /Game/ThirdPerson/Blueprints/Gimmicks/Heaven:
#   BP_Wings  a pair of glowing wings to pick up. Touched by the player they fix onto the player's back for the rest
#             of the run (game instance HasWings, so they are back after a trip to hell). While the player is falling
#             and holds Jump (Space / gamepad bottom button) the wings spread and the fall is held to GlideFall cm/s.
# Graph: BP_Wings_EventGraph.txt from gen_heaven_wings.ps1. Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_heaven_wings.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
GLOW = "/Game/ThirdPerson/Blueprints/Gimmicks/Hell/M_HellGlow"
GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
SPHERE = "/Engine/BasicShapes/Sphere"

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

REAL = pins.get_basic_type_by_name("real")
BOOL = pins.get_basic_type_by_name("bool")


def add_variables(blueprint, variables):
    defaults = unreal.get_default_object(blueprint.generated_class())
    for name, pin_type, editable in variables:
        try:
            defaults.get_editor_property(name)
            continue
        except Exception:
            pass
        if not pins.add_member_variable(blueprint, name, pin_type):
            raise RuntimeError("Could not add {} to {}".format(name, blueprint.get_name()))
        if editable:
            pins.set_blueprint_variable_instance_editable(blueprint, name, True)
        lines.append("{}: variable {}".format(blueprint.get_name(), name))
    pins.compile_blueprint(blueprint)
    return unreal.get_default_object(blueprint.generated_class())


def components(blueprint):
    found = {}
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_associated_object(data_library.get_data(handle))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = (handle, component)
    return found


def add_component(blueprint, component_class, name, parent=None):
    existing = components(blueprint)
    if name in existing:
        return existing[name][1], False
    parent_handle = existing[parent][0] if parent else subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=parent_handle, new_class=component_class, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add {} to {}".format(name, blueprint.get_name()))
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("{}: component {}".format(blueprint.get_name(), name))
    return data_library.get_associated_object(data_library.get_data(handle)), True


path = DIR + "/MI_WingGlow"
if library.does_asset_exist(path):
    feather_look = unreal.load_asset(path)
else:
    feather_look = tools.create_asset("MI_WingGlow", DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(feather_look, unreal.load_asset(GLOW))
    editing.set_material_instance_vector_parameter_value(feather_look, "Color", unreal.LinearColor(1.0, 0.97, 0.88, 1.0))
    editing.set_material_instance_scalar_parameter_value(feather_look, "Glow", 3.0)
    library.save_asset(path, False)
    lines.append("created " + path)

# ----- the run's wings -----
game_instance = unreal.load_asset(GAME_INSTANCE)
add_variables(game_instance, [("HasWings", BOOL, False)])
library.save_asset(GAME_INSTANCE, False)

# ----- BP_Wings -----
WINGS = DIR + "/BP_Wings"
if library.does_asset_exist(WINGS):
    wings = unreal.load_asset(WINGS)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    wings = tools.create_asset("BP_Wings", DIR, unreal.Blueprint, factory)
    lines.append("created " + WINGS)
pivot, made = add_component(wings, unreal.SceneComponent, "Wings")
if made:
    # Behind the player's shoulders once worn (the actor is snapped onto the player's capsule centre).
    # (Tuned in the editor 2026-11-14: z 38 sat above this character's head.)
    pivot.set_editor_property("relative_location", unreal.Vector(-20.0, 0.0, 0.0))
# Two feathers a side: flattened spheres swept up and out.
for name, location, scale, roll in (
        ("FeatherL1", (0.0, -48.0, 14.0), (0.06, 0.58, 0.26), -22.0),
        ("FeatherL2", (0.0, -38.0, -10.0), (0.05, 0.42, 0.17), 12.0),
        ("FeatherR1", (0.0, 48.0, 14.0), (0.06, 0.58, 0.26), 22.0),
        ("FeatherR2", (0.0, 38.0, -10.0), (0.05, 0.42, 0.17), -12.0)):
    feather, made = add_component(wings, unreal.StaticMeshComponent, name, "Wings")
    if made:
        feather.set_editor_property("static_mesh", unreal.load_asset(SPHERE))
        feather.set_material(0, feather_look)
        feather.set_editor_property("relative_location", unreal.Vector(*location))
        feather.set_editor_property("relative_scale3d", unreal.Vector(*scale))
        feather.set_editor_property("relative_rotation", unreal.Rotator(roll=roll, pitch=0.0, yaw=0.0))
        feather.set_collision_profile_name("NoCollision")
        feather.set_editor_property("cast_shadow", False)
grab, made = add_component(wings, unreal.SphereComponent, "Grab")
if made:
    grab.set_editor_property("sphere_radius", 90.0)
    grab.set_collision_profile_name("OverlapOnlyPawn")
defaults = add_variables(wings, [("GlideFall", REAL, True), ("Owned", BOOL, False), ("Open", REAL, False)])
if defaults.get_editor_property("GlideFall") == 0.0:
    defaults.set_editor_property("GlideFall", 160.0)
pins.compile_blueprint(wings)
library.save_asset(WINGS, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "heaven_wings.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
