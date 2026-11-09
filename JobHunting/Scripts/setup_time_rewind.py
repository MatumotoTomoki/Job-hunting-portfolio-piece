# Sets up the time rewind area: BP_TimeRewindArea (a 10 m box and the countdown text, plus its variables), a movable sun
# in LV_Debug so the area can turn it into night, and one area placed before the goal. Safe to run again: whatever
# already exists is left alone. The Event Graph comes from BP_TimeRewindArea_EventGraph.txt. With the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=setup_time_rewind.py -unattended -nop4 -nosplash -stdout
import os

import unreal

BLUEPRINT_DIR = "/Game/ThirdPerson/Blueprints/Gimmicks"
BLUEPRINT_NAME = "BP_TimeRewindArea"
BLUEPRINT_PATH = "{}/{}".format(BLUEPRINT_DIR, BLUEPRINT_NAME)
HALF_SIZE = 500.0
# Per placed area: seconds counted down, seconds before it can rewind again, the sun's pitch at night (above 0 is under
# the horizon), how much of the day-to-night change happens per second, and how high above the player the count floats.
SETTINGS = {"CountSeconds": 3.0, "CooldownSeconds": 10.0, "NightSunPitch": 15.0, "NightBlendSpeed": 1.0, "TextHeight": 140.0}
library = unreal.EditorAssetLibrary
bp_library = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def add_component(blueprint, parent_handle, component_class, name):
    params = unreal.AddNewSubobjectParams(parent_handle=parent_handle, new_class=component_class, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add component " + name)
    subsystem.rename_subobject(handle, unreal.Text(name))
    return data_library.get_object(data_library.get_data(handle))


if library.does_asset_exist(BLUEPRINT_PATH):
    blueprint = unreal.load_asset(BLUEPRINT_PATH)
    lines.append(BLUEPRINT_NAME + ": already there")
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    blueprint = unreal.AssetToolsHelpers.get_asset_tools().create_asset(BLUEPRINT_NAME, BLUEPRINT_DIR, unreal.Blueprint, factory)
    root = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
    # The area itself; its outline shows in game while this is a trial.
    area = add_component(blueprint, root, unreal.BoxComponent, "Area")
    area.set_editor_property("box_extent", unreal.Vector(HALF_SIZE, HALF_SIZE, HALF_SIZE))
    area.set_editor_property("hidden_in_game", False)
    area.set_editor_property("line_thickness", 4.0)
    area.set_editor_property("shape_color", unreal.Color(r=120, g=90, b=255, a=255))
    text = add_component(blueprint, root, unreal.TextRenderComponent, "CountText")
    text.set_text(unreal.Text("3"))
    text.set_editor_property("world_size", 120.0)
    text.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    text.set_editor_property("vertical_alignment", unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
    text.set_editor_property("text_render_color", unreal.Color(r=120, g=220, b=255, a=255))
    lines.append(BLUEPRINT_NAME + ": created")

real = bp_library.get_basic_type_by_name("real")
rotator = bp_library.get_struct_type(unreal.Rotator.static_struct())
variables = [(name, real, True) for name in SETTINGS] + [
    ("Counting", bp_library.get_basic_type_by_name("bool"), False),
    ("CountTime", real, False),
    ("Cooldown", real, False),
    ("RewindPoint", bp_library.get_struct_type(unreal.Vector.static_struct()), False),
    ("NightAlpha", real, False),
    ("Sun", bp_library.get_object_reference_type(unreal.Actor), False),
    ("DayRotation", rotator, False),
    ("NightRotation", rotator, False),
]
defaults = unreal.get_default_object(blueprint.generated_class())
for name, pin_type, editable in variables:
    # add_member_variable would quietly add Name_0 next to an existing one, so check first.
    try:
        defaults.get_editor_property(name)
        continue
    except Exception:
        pass
    if not bp_library.add_member_variable(blueprint, name, pin_type):
        raise RuntimeError("Could not add " + name)
    if editable:
        bp_library.set_blueprint_variable_instance_editable(blueprint, name, True)
    lines.append("  variable " + name)
bp_library.compile_blueprint(blueprint)
defaults = unreal.get_default_object(blueprint.generated_class())
for name, value in SETTINGS.items():
    defaults.set_editor_property(name, value)
library.save_asset(BLUEPRINT_PATH, False)

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.load_level("/Game/LV_Debug"):
    raise RuntimeError("Could not open LV_Debug")
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
by_label = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
# A stationary sun cannot turn at run time.
sun = by_label["Sun"].get_editor_property("light_component")
sun.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
sun.set_editor_property("atmosphere_sun_light", True)
lines.append("LV_Debug: sun movable")
if "Time Rewind Area" in by_label:
    lines.append("LV_Debug: area already placed")
else:
    spacing, row_length = 800.0, 15
    goal, goal_label = by_label["Goal"], by_label["Label Goal"]
    area_x = goal.get_actor_location().x
    for actor in (goal, goal_label):
        location = actor.get_actor_location()
        actor.set_actor_location(unreal.Vector(area_x + spacing, location.y, location.z), False, False)
    # Same formula as build_debug_level.py, so a rebuilt level matches.
    ground = by_label["Floor"]
    ground_length = spacing * (row_length + 3)
    ground.set_actor_location(unreal.Vector(ground_length / 2.0 - spacing * 2.0, 0.0, -50.0), False, False)
    ground.set_actor_scale3d(unreal.Vector(ground_length / 100.0, 16.0, 1.0))
    # The box's floor on the ground.
    area = actors.spawn_actor_from_class(blueprint.generated_class(), unreal.Vector(area_x, 0.0, HALF_SIZE))
    area.set_actor_label("Time Rewind Area")
    label = actors.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(area_x - HALF_SIZE - 20.0, 0.0, 320.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
    label.set_actor_label("Label Time Rewind Area")
    text = label.get_editor_property("text_render")
    text.set_text(unreal.Text("Time Rewind Area"))
    text.set_editor_property("world_size", 50.0)
    text.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    lines.append("LV_Debug: area at x {}, goal moved to x {}".format(area_x, area_x + spacing))
lines.append("LV_Debug saved {}".format(level.save_current_level()))
with open(os.path.join(unreal.Paths.project_saved_dir(), "time_rewind_setup.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
