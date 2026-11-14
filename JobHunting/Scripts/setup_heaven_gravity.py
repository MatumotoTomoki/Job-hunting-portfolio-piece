# Area 4's upside-down heaven (the east wing), in /Game/ThirdPerson/Blueprints/Gimmicks/Heaven:
#   M_GravityField, MI_GravityField  a faint two-sided violet haze (Color, Opacity), seen from inside and out.
#   BP_GravityZone  a 100 cm box (scale the actor). While the player is inside, the player's gravity points along
#                   Direction (0, 0, 1 = up: the player falls to the ceiling and walks on it); on leaving it is back to
#                   normal (0, 0, -1). Zones must not overlap.
# Graph: BP_GravityZone_EventGraph.txt from gen_heaven_gravity.ps1. Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_heaven_gravity.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
CUBE = "/Engine/BasicShapes/Cube"

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

BOOL = pins.get_basic_type_by_name("bool")
VECTOR = pins.get_struct_type(unreal.Vector.static_struct())


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


# ----- the haze -----
path = DIR + "/M_GravityField"
if not library.does_asset_exist(path):
    material = tools.create_asset("M_GravityField", DIR, unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    material.set_editor_property("two_sided", True)
    color = editing.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -600, 0)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("default_value", unreal.LinearColor(0.6, 0.35, 1.0, 1.0))
    opacity = editing.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -600, 250)
    opacity.set_editor_property("parameter_name", "Opacity")
    opacity.set_editor_property("default_value", 0.08)
    editing.connect_material_property(color, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.connect_material_property(opacity, "", unreal.MaterialProperty.MP_OPACITY)
    editing.recompile_material(material)
    library.save_asset(path, False)
    lines.append("created " + path)
haze_path = DIR + "/MI_GravityField"
if library.does_asset_exist(haze_path):
    haze = unreal.load_asset(haze_path)
else:
    haze = tools.create_asset("MI_GravityField", DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(haze, unreal.load_asset(path))
    library.save_asset(haze_path, False)
    lines.append("created " + haze_path)

# ----- BP_GravityZone -----
ZONE = DIR + "/BP_GravityZone"
if library.does_asset_exist(ZONE):
    zone_bp = unreal.load_asset(ZONE)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    zone_bp = tools.create_asset("BP_GravityZone", DIR, unreal.Blueprint, factory)
    lines.append("created " + ZONE)
area, made = add_component(zone_bp, unreal.BoxComponent, "Zone")
if made:
    area.set_editor_property("box_extent", unreal.Vector(50.0, 50.0, 50.0))
    area.set_collision_profile_name("OverlapOnlyPawn")
field, made = add_component(zone_bp, unreal.StaticMeshComponent, "Field")
if made:
    field.set_editor_property("static_mesh", unreal.load_asset(CUBE))
    field.set_material(0, haze)
    field.set_collision_profile_name("NoCollision")
    field.set_editor_property("cast_shadow", False)
defaults = add_variables(zone_bp, [("Direction", VECTOR, True), ("Flipped", BOOL, False)])
direction = defaults.get_editor_property("Direction")
if direction.x == 0.0 and direction.y == 0.0 and direction.z == 0.0:
    defaults.set_editor_property("Direction", unreal.Vector(0.0, 0.0, 1.0))
pins.compile_blueprint(zone_bp)
library.save_asset(ZONE, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "heaven_gravity.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
