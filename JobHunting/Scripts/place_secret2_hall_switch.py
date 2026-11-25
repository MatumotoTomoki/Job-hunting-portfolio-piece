# Hidden area 2: a toggle switch on the hall's way in (the Hall Fragment, before the upside-down hall; the user,
# 2026-11-24), so the red and blue blocks can be set right again after a fall. Puts that one switch into the built
# LV_Secret2 without rebuilding it (secret2_collapse.py has it too, for the next rebuild). Safe to run again.
# From the Output Log (Python), with LV_Secret2 open or not:
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\place_secret2_hall_switch.py', encoding='utf-8').read())
import os

import unreal

LEVEL = "/Game/LV_Secret2"
LABEL = "S2 Hall Way-in Switch"
WHERE = unreal.Vector(18231.0, 6300.0, 13510.0)     # the Hall Fragment's top (x 17931..18831, y 6050..6950)

level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not world.get_path_name().startswith(LEVEL + "."):
    if not level_subsystem.load_level(LEVEL):
        raise RuntimeError("Could not open " + LEVEL)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if not world.get_path_name().startswith(LEVEL + "."):
        raise RuntimeError("{} is open, not {}".format(world.get_path_name(), LEVEL))

existing = [a for a in actors.get_all_level_actors() if a.get_actor_label() == LABEL]
if existing:
    switch = existing[0]
    switch.set_actor_location(WHERE, False, False)
    message = "moved"
else:
    cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/ThirdPerson/Blueprints/Gimmicks/Machine/BP_ToggleSwitch")
    switch = actors.spawn_actor_from_class(cls, WHERE, unreal.Rotator(0.0, 0.0, 0.0))
    switch.set_actor_label(LABEL)
    switch.set_folder_path("Secret2/2 Clock Ruin")
    message = "placed"
level_subsystem.save_current_level()
line = "{} {} at {}".format(LABEL, message, switch.get_actor_location())
with open(os.path.join(unreal.Paths.project_saved_dir(), "secret2_hall_switch.txt"), "w", encoding="utf-8") as out:
    out.write(line + "\n")
unreal.log(line)
