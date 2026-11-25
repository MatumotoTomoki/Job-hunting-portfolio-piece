# Hidden area 4: puts back the upside-down zones' ceiling fall catchers (A4 081/104/107/129/132/145, section 3) that
# build_secret4_stage.py took out by mistake (fixed there 11-25), into the built LV_Secret4 without rebuilding it.
# Each goes where area 4 has it (Saved/level_dump_LV_Area4_Heaven.json), moved as section 3 was moved (measured from
# a section 3 actor in the level). Safe to run again (ones already there are moved into place). From the Output Log (Python):
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\restore_secret4_catchers.py', encoding='utf-8').read())
import json
import os

import unreal

LEVEL = "/Game/LV_Secret4"
CATCHER = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine/BP_FallCatcher"
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not world.get_path_name().startswith(LEVEL + "."):
    if not level_subsystem.load_level(LEVEL):
        raise RuntimeError("Could not open " + LEVEL)

with open(os.path.join(unreal.Paths.project_saved_dir(), "level_dump_LV_Area4_Heaven.json"), encoding="utf-8") as f:
    dump = json.load(f)
source = {d["label"]: d for d in dump}
wanted = [d for d in dump if d["class"] == "BP_FallCatcher_C" and d["folder"].startswith("Area4/3")]
in_level = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
# The reference: an actor of section 3 itself that is in both (11-25: A4 072 is section 2's - the catchers landed
# one section short).
reference = next((d["label"] for d in dump if d["folder"].startswith("Area4/3") and d["class"] != "BP_FallCatcher_C"
                  and d["label"] in in_level), None)
if reference is None:
    raise RuntimeError("No section 3 actor found in " + LEVEL)
now = in_level[reference].get_actor_location()
was = source[reference]["location"]
dx, dy, dz = now.x - was[0], now.y - was[1], now.z - was[2]
cls = unreal.EditorAssetLibrary.load_blueprint_class(CATCHER)
lines = ["section 3 moved by ({:.0f}, {:.0f}, {:.0f}), measured from {}".format(dx, dy, dz, reference)]
for d in wanted:
    where = unreal.Vector(d["location"][0] + dx, d["location"][1] + dy, d["location"][2] + dz)
    actor = in_level.get(d["label"])
    if actor is None:
        actor = actors.spawn_actor_from_class(cls, where, unreal.Rotator(0.0, 0.0, 0.0))
        actor.set_actor_label(d["label"])
        actor.set_folder_path(d["folder"])
        lines.append("put back " + d["label"])
    else:
        actor.set_actor_location(where, False, False)
        lines.append("already there (moved into place): " + d["label"])
    actor.set_actor_rotation(unreal.Rotator(roll=d["rotation"][0], pitch=d["rotation"][1], yaw=d["rotation"][2]), False)
    actor.set_actor_scale3d(unreal.Vector(*d["scale"]))
level_subsystem.save_current_level()
with open(os.path.join(unreal.Paths.project_saved_dir(), "restore_secret4_catchers.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(lines) + "\n")
unreal.log("\n".join(lines))
