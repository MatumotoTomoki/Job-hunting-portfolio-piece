# Checkpoints, new rules (the user, 2026-11-19; the later areas are hard): no more pickup item and planting. The flags
# stand in the levels from the start, broken; touched, a flag stands up, and from then on every fall comes back to it
# (no longer breaking after one use).
#   BP_CheckpointFlag: a "Touch" box round it (overlaps the player) and Raised (bool). Its graph:
#     BP_CheckpointFlag_EventGraph.txt (Generators/gen_checkpoint_post.ps1).
#   The levels (LV_Area1..4, LV_Debug): every BP_CheckpointItem gives way to a BP_CheckpointFlag stuck in the ground
#     under it (the items floated 100 cm up), "... Checkpoint Flag". The build scripts place flags too now.
#   BP_ThirdPersonCharacter1 (by hand): in the fall check, after the player is moved to ActiveFlag's RespawnPoint,
#     delete "Break Flag" and the "Set Active Flag" after it, so the flag stays and is used again.
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_checkpoint_flags.py -unattended -nop4 -nosplash -stdout
import os

import unreal

FLAG = "/Game/ThirdPerson/Item/Checkpoint/BP_CheckpointFlag"
LEVELS = ["/Game/LV_Area1_Ruins", "/Game/LV_Area2_Tower", "/Game/LV_Area3_Sky", "/Game/LV_Area4_Heaven", "/Game/LV_Debug"]
ITEM_LIFT = 100.0
library = unreal.EditorAssetLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

bp = unreal.load_asset(FLAG)
found = {}
for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
    c = data_library.get_associated_object(data_library.get_data(h))
    if c is not None:
        found[c.get_name().replace("_GEN_VARIABLE", "")] = (h, c)
if "Touch" not in found:
    params = unreal.AddNewSubobjectParams(parent_handle=found["DefaultSceneRoot"][0], new_class=unreal.BoxComponent, blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("Touch"))
    touch = data_library.get_associated_object(data_library.get_data(handle))
    lines.append("BP_CheckpointFlag: Touch added")
else:
    touch = found["Touch"][1]
touch.set_editor_property("box_extent", unreal.Vector(70.0, 70.0, 110.0))
touch.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 110.0))
touch.set_collision_profile_name("OverlapOnlyPawn")
defaults = unreal.get_default_object(bp.generated_class())
# Raised: stood up by a touch. Broken: knocked down again with E (2026-11-19) - for good.
for name in ("Raised", "Broken"):
    try:
        defaults.get_editor_property(name)
    except Exception:
        if not pins.add_member_variable(bp, name, pins.get_basic_type_by_name("bool")):
            raise RuntimeError("Could not add " + name)
        lines.append("BP_CheckpointFlag: {} added".format(name))
pins.compile_blueprint(bp)
library.save_asset(FLAG, False)

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
flag_class = bp.generated_class()
for path in LEVELS:
    if not level.load_level(path):
        lines.append("could not open " + path)
        continue
    swapped = 0
    for actor in actors.get_all_level_actors():
        if actor.get_class().get_name() != "BP_CheckpointItem_C":
            continue
        where = actor.get_actor_location()
        label, folder = actor.get_actor_label(), actor.get_folder_path()
        actors.destroy_actor(actor)
        flag = actors.spawn_actor_from_class(flag_class, unreal.Vector(where.x, where.y, where.z - ITEM_LIFT), unreal.Rotator(0.0, 0.0, 0.0))
        flag.set_actor_label(label.replace("Checkpoint Item", "Checkpoint Flag"))
        flag.set_folder_path(str(folder))
        swapped += 1
        lines.append("  {}: {} -> flag at ({:.0f}, {:.0f}, {:.0f})".format(path, label, where.x, where.y, where.z - ITEM_LIFT))
    if swapped:
        lines.append("{}: {} items -> flags, saved {}".format(path, swapped, level.save_current_level()))
    else:
        lines.append("{}: no items".format(path))

with open(os.path.join(unreal.Paths.project_saved_dir(), "checkpoint_flags.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
