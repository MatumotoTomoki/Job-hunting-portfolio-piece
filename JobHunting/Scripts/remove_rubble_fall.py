# Undoes the falling-rubble hazard (the user, 2026-11-25: dropped - the hidden stages are long enough already):
# takes BP_RubbleFall out of LV_Secret, saves the level, and deletes the blueprint. Delete this script afterwards.
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\remove_rubble_fall.py', encoding='utf-8').read())
import unreal

LEVEL = "/Game/LV_Secret"
BP = "/Game/ThirdPerson/Blueprints/Gimmicks/Area/BP_RubbleFall"
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not world.get_path_name().startswith(LEVEL + "."):
    if not level_subsystem.load_level(LEVEL):
        raise RuntimeError("Could not open " + LEVEL)
removed = 0
for actor in actors.get_all_level_actors():
    if actor.get_class().get_name() == "BP_RubbleFall_C":
        actors.destroy_actor(actor)
        removed += 1
level_subsystem.save_current_level()
deleted = unreal.EditorAssetLibrary.delete_asset(BP) if unreal.EditorAssetLibrary.does_asset_exist(BP) else "not there"
unreal.log("rubble fall: {} removed from {}, blueprint deleted: {}".format(removed, LEVEL, deleted))
