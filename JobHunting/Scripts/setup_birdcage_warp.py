# Prepares BP_BirdcageDoor_Blender for BP_BirdcageDoor_Blender_EventGraph.txt: adds the variables and components the graph
# relies on, then, in LV_Debug, places a target point and sets it as the cage's Destination. Safe to run again.
# Run after import_birdcage_blender.py, with the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=setup_birdcage_warp.py -unattended -nop4 -nosplash -stdout
import os

import unreal

BP_PATH = "/Game/Prototype/Birdcage/BP_BirdcageDoor_Blender"
TARGET_LABEL = "Birdcage Warp Target"
# In LV_Debug: open floor beside the row of gimmicks, far enough from the cage to read as a warp.
TARGET_LOCATION = unreal.Vector(3000.0, -500.0, 0.0)

library = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
blueprint = unreal.load_asset(BP_PATH)
lines = []


def add_variable(name, pin_type, editable=False):
    # AddMemberVariable refuses a name that already exists, so this is safe to repeat.
    added = library.add_member_variable(blueprint, name, pin_type)
    lines.append("variable {}: {}".format(name, "added" if added else "already there"))
    if editable:
        library.set_blueprint_variable_instance_editable(blueprint, name, True)


def find_component(name):
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_object(data_library.get_data(handle))
        if component and component.get_name().replace("_GEN_VARIABLE", "") == name:
            return component
    return None


def add_component(component_class, name):
    if find_component(name):
        lines.append("component {}: already there".format(name))
        return None
    root = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=component_class, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add component " + name)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("component {}: added".format(name))
    return data_library.get_object(data_library.get_data(handle))


add_variable("Destination", library.get_object_reference_type(unreal.Actor.static_class()), editable=True)
add_variable("IsWarping", library.get_basic_type_by_name("bool"))
add_variable("WarpUsed", library.get_basic_type_by_name("bool"))

# In front of the door, which faces the actor's +Y.
enter_trigger = add_component(unreal.BoxComponent, "EnterTrigger")
if enter_trigger:
    enter_trigger.set_editor_property("box_extent", unreal.Vector(25.0, 18.0, 60.0))
    enter_trigger.set_editor_property("relative_location", unreal.Vector(0.0, 52.0, 60.0))
    enter_trigger.set_collision_profile_name("OverlapOnlyPawn")

# Where the player reappears: past the open door, the capsule's half height (90) above the floor.
exit_point = add_component(unreal.SceneComponent, "ExitPoint")
if exit_point:
    exit_point.set_editor_property("relative_location", unreal.Vector(0.0, 100.0, 92.0))

library.compile_blueprint(blueprint)
lines.append("bp saved: {}".format(unreal.EditorAssetLibrary.save_asset(BP_PATH, False)))

level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level_subsystem.load_level("/Game/LV_Debug"):
    raise RuntimeError("Could not open LV_Debug")
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
all_actors = actors.get_all_level_actors()
target = next((a for a in all_actors if a.get_actor_label() == TARGET_LABEL), None)
if not target:
    target = actors.spawn_actor_from_class(unreal.TargetPoint, TARGET_LOCATION, unreal.Rotator(0.0, 0.0, 0.0))
    target.set_actor_label(TARGET_LABEL)
    lines.append("target placed at {}".format(TARGET_LOCATION))
cages = [a for a in all_actors if "BP_BirdcageDoor_Blender_C" in a.get_class().get_name()]
for cage in cages:
    cage.set_editor_property("Destination", target)
    lines.append("cage {} at {} rot {} -> {}".format(cage.get_actor_label(), cage.get_actor_location(), cage.get_actor_rotation(), cage.get_editor_property("Destination").get_actor_label()))
if not cages:
    lines.append("no cage placed in this level")
lines.append("level saved: {}".format(level_subsystem.save_current_level()))
for actor in actors.get_all_level_actors():
    location = actor.get_actor_location()
    if abs(location.x - TARGET_LOCATION.x) < 500.0 and abs(location.y - TARGET_LOCATION.y) < 500.0:
        lines.append("near target: {} {}".format(actor.get_actor_label(), location))

with open(os.path.join(unreal.Paths.project_saved_dir(), "birdcage_warp_setup.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(lines))
unreal.log("\n".join(lines))
