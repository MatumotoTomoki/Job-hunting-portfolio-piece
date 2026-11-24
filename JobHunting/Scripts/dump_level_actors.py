# Read-only: writes every actor of the given levels to Saved/level_dump_<level>.json (label, class, folder, location,
# rotation, scale, bounds, hidden, and the editable settings of blueprint actors that point at other actors or hold
# offsets), for planning the hidden stages built from the real areas (2026-11-22). Opens each level, saves nothing,
# and goes back to the level that was open. From the Output Log (Python):
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\dump_level_actors.py', encoding='utf-8').read())
import json
import os

import unreal

LEVELS = ["/Game/LV_Area3_Sky", "/Game/LV_Area4_Heaven"]   # (areas 1 and 2 dumped 2026-11-22 for hidden areas 1-2)
PROPS = ("MoveOffset", "MoveSeconds", "WaitSeconds", "TravelOffset", "TravelSeconds", "NextLevel", "Lever", "Duration",
         "StartDelay", "Returns", "ReturnAfter", "IsRed", "SpinSpeed", "Destination", "PairId", "RespawnLocation",
         "VisibleSeconds", "HiddenSeconds", "ShowCamera", "ResetAfter", "RiseHeight", "RiseSeconds",
         "StaySeconds", "GoneSeconds", "Strength", "MaxSpeed", "GustOn", "GustOff", "RespawnPoint", "Beam", "NextLevel")

level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
start = unreal.EditorLevelLibrary.get_editor_world().get_path_name().split(".")[0]
lines = []


def plain(value):
    if isinstance(value, (bool, int, float, str)) or value is None:
        return value
    if isinstance(value, unreal.Vector):
        return [value.x, value.y, value.z]
    if isinstance(value, unreal.Actor):
        return "actor:" + value.get_actor_label()
    return str(value)


for level in LEVELS:
    if not level_editor.load_level(level):
        lines.append("could not open " + level)
        continue
    out = []
    for actor in actors.get_all_level_actors():
        origin, extent = actor.get_actor_bounds(False)
        location, rotation, scale = actor.get_actor_location(), actor.get_actor_rotation(), actor.get_actor_scale3d()
        entry = {"label": actor.get_actor_label(), "class": actor.get_class().get_name(), "folder": str(actor.get_folder_path()),
                 "location": [location.x, location.y, location.z], "rotation": [rotation.roll, rotation.pitch, rotation.yaw],
                 "scale": [scale.x, scale.y, scale.z],
                 "min": [origin.x - extent.x, origin.y - extent.y, origin.z - extent.z],
                 "max": [origin.x + extent.x, origin.y + extent.y, origin.z + extent.z],
                 "hidden": actor.is_hidden_ed() or actor.get_editor_property("hidden")}
        if isinstance(actor, unreal.StaticMeshActor):
            component = actor.get_editor_property("static_mesh_component")
            mesh = component.get_editor_property("static_mesh")
            entry["mesh"] = mesh.get_path_name() if mesh else None
            entry["collision"] = str(component.get_collision_profile_name())
        settings = {}
        for name in PROPS:
            try:
                settings[name] = plain(actor.get_editor_property(name))
            except Exception:
                pass
        if settings:
            entry["settings"] = settings
        out.append(entry)
    name = level.split("/")[-1]
    with open(os.path.join(unreal.Paths.project_saved_dir(), "level_dump_{}.json".format(name)), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    lines.append("{}: {} actors".format(name, len(out)))
if start:
    level_editor.load_level(start)
unreal.log("\n".join(lines))
with open(os.path.join(unreal.Paths.project_saved_dir(), "level_dump.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
