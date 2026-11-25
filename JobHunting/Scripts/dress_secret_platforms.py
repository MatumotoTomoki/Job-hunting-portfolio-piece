# The hidden stages' own new platforms in area 4's look (the user, 2026-11-25): in LV_Secret..LV_Secret4, every moving,
# falling and timed platform (pistons too) and lever the build scripts added - labelled "S ", "S2 ", "S3 ", "S4 " -
# gets area 4's MI_HeavenHoly (levers: the base Holy, the handle MI_HeavenGold, the knob MI_HeavenGoldGlow), as
# setup_heaven_tier_platforms.py dresses area 4. The pieces copied from the real areas ("A1 ".."A4 ") keep their own
# area's look. Run it again after rebuilding a hidden stage (a rebuild brings back the plain look).
# Safe to run again. Save your work first (it opens each level in turn). From the Output Log (Python), or as a commandlet:
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\dress_secret_platforms.py', encoding='utf-8').read())
import os

import unreal

DIR = "/Game/Art/HeavenDebris"
LEVELS = [("/Game/LV_Secret", "S "), ("/Game/LV_Secret2", "S2 "), ("/Game/LV_Secret3", "S3 "), ("/Game/LV_Secret4", "S4 ")]
CLASSES = ("BP_MovingPlatform_C", "BP_FallingFloor_C", "BP_TimedPlatform_C")
HOLY = unreal.load_asset(DIR + "/MI_HeavenHoly")
GOLD = unreal.load_asset(DIR + "/MI_HeavenGold")
KNOB = unreal.load_asset(DIR + "/MI_HeavenGoldGlow")
if not (HOLY and GOLD and KNOB):
    raise RuntimeError("MI_HeavenHoly / MI_HeavenGold / MI_HeavenGoldGlow missing")

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lines = []
for level_path, prefix in LEVELS:
    if not level.load_level(level_path):
        raise RuntimeError("Could not open " + level_path)
    platforms, levers = 0, 0
    for actor in actors.get_all_level_actors():
        if not actor.get_actor_label().startswith(prefix):
            continue
        kind = actor.get_class().get_name()
        if kind in CLASSES:
            for component in actor.get_components_by_class(unreal.StaticMeshComponent):
                if component.get_editor_property("static_mesh") is None:
                    continue
                for i in range(component.get_num_materials()):
                    component.set_material(i, HOLY)
            platforms += 1
        elif kind == "BP_Lever_C":
            for component in actor.get_components_by_class(unreal.StaticMeshComponent):
                part = component.get_name()
                component.set_material(0, GOLD if part.startswith("Handle") else KNOB if part.startswith("Knob") else HOLY)
            levers += 1
    lines.append("{}: {} platforms, {} levers -> area 4's look (saved {})".format(
        level_path, platforms, levers, level.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "dress_secret_platforms.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(lines) + "\n")
unreal.log("\n".join(lines))
