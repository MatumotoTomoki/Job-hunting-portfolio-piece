# Area 4's spider thread (the way in), in /Game/ThirdPerson/Blueprints/Gimmicks/Heaven:
#   BP_SpiderThread  a thin shining thread hanging Length cm down from the actor's origin (its top). Jumped at, the
#                    player catches hold: W / stick up climbs (ClimbSpeed), S / stick down goes down, otherwise the
#                    player slides slowly (SlideSpeed). Jump lets go, leaping the way the camera faces plus the
#                    thread's own swing. With SwingDegrees above 0 the thread swings along the actor's X axis, SwingSeconds
#                    a swing (SwingOffset shifts it). With HoldSeconds above 0 it turns red after 60 % of that and snaps
#                    when the player has held on that long, then is back RespawnSeconds later.
# Graph: BP_SpiderThread_EventGraph.txt from gen_heaven_thread.ps1. Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_heaven_thread.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
GLOW = "/Game/ThirdPerson/Blueprints/Gimmicks/Hell/M_HellGlow"
CYLINDER = "/Engine/BasicShapes/Cylinder"

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

REAL = pins.get_basic_type_by_name("real")
BOOL = pins.get_basic_type_by_name("bool")
VECTOR = pins.get_struct_type(unreal.Vector.static_struct())


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


def glow(name, color, strength):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    made = tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(made, unreal.load_asset(GLOW))
    editing.set_material_instance_vector_parameter_value(made, "Color", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    editing.set_material_instance_scalar_parameter_value(made, "Glow", strength)
    library.save_asset(path, False)
    lines.append("created " + path)
    return made


silver = glow("MI_ThreadSilver", (0.92, 0.95, 1.0), 4.0)
fray = glow("MI_ThreadFray", (1.0, 0.25, 0.12), 5.0)

THREAD = DIR + "/BP_SpiderThread"
if library.does_asset_exist(THREAD):
    thread = unreal.load_asset(THREAD)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    thread = tools.create_asset("BP_SpiderThread", DIR, unreal.Blueprint, factory)
    lines.append("created " + THREAD)
add_component(thread, unreal.SceneComponent, "Swing")
for name, look, visible in (("Thread", silver, True), ("Fray", fray, False)):
    part, made = add_component(thread, unreal.StaticMeshComponent, name, "Swing")
    if made:
        # Begin Play stretches it to Length.
        part.set_editor_property("static_mesh", unreal.load_asset(CYLINDER))
        part.set_material(0, look)
        part.set_editor_property("relative_scale3d", unreal.Vector(0.04, 0.04, 15.0))
        part.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -750.0))
        part.set_editor_property("visible", visible)
        part.set_collision_profile_name("NoCollision")
        part.set_editor_property("cast_shadow", False)
zone, made = add_component(thread, unreal.BoxComponent, "Zone", "Swing")
if made:
    zone.set_editor_property("box_extent", unreal.Vector(45.0, 45.0, 750.0))
    zone.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -750.0))
    zone.set_collision_profile_name("OverlapOnlyPawn")
defaults = add_variables(thread, [
    ("Length", REAL, True), ("SwingDegrees", REAL, True), ("SwingSeconds", REAL, True), ("SwingOffset", REAL, True),
    ("ClimbSpeed", REAL, True), ("SlideSpeed", REAL, True), ("HoldSeconds", REAL, True), ("RespawnSeconds", REAL, True),
    ("Holding", BOOL, False), ("Broken", BOOL, False), ("JumpWas", BOOL, False), ("HeldFor", REAL, False),
    ("GrabT", REAL, False), ("ReleasedAt", REAL, False), ("LastPoint", VECTOR, False),
])
for name, value in (("Length", 1500.0), ("SwingSeconds", 4.0), ("ClimbSpeed", 260.0), ("SlideSpeed", 60.0),
                    ("RespawnSeconds", 4.0)):
    if defaults.get_editor_property(name) == 0.0:
        defaults.set_editor_property(name, value)
pins.compile_blueprint(thread)
library.save_asset(THREAD, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "heaven_thread.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
