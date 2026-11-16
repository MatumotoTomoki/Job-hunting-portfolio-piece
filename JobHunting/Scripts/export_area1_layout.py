# Writes SourceArt/Models/Ruins/area1_layout.json: every "A1 ..." actor of LV_Area1_Ruins, for the Blender ruins
# (build_ruins_blender.py) to dress. Per actor: label, folder, class, mesh, material, location, rotation, scale and
# world bounds (min, max). Reads only. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\export_area1_layout.py -unattended -nop4 -nosplash -stdout
import json
import os

import unreal

LEVEL = "/Game/LV_Area1_Ruins"
OUT_DIR = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Ruins")

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)

rows = []
for actor in actors.get_all_level_actors():
    label = actor.get_actor_label()
    if not label.startswith("A1 "):
        continue
    location, rotation, scale = actor.get_actor_location(), actor.get_actor_rotation(), actor.get_actor_scale3d()
    origin, extent = actor.get_actor_bounds(False)
    mesh, material = None, None
    if isinstance(actor, unreal.StaticMeshActor):
        component = actor.get_editor_property("static_mesh_component")
        if component.get_editor_property("static_mesh"):
            mesh = component.get_editor_property("static_mesh").get_path_name()
        if component.get_num_materials():
            used = component.get_material(0)
            material = used.get_name() if used else None
    rows.append({
        "label": label, "folder": str(actor.get_folder_path()), "class": actor.get_class().get_name(),
        "mesh": mesh, "material": material,
        "location": [location.x, location.y, location.z],
        "rotation": [rotation.roll, rotation.pitch, rotation.yaw],
        "scale": [scale.x, scale.y, scale.z],
        "min": [origin.x - extent.x, origin.y - extent.y, origin.z - extent.z],
        "max": [origin.x + extent.x, origin.y + extent.y, origin.z + extent.z],
        "hidden": actor.is_hidden_ed(),
    })

os.makedirs(OUT_DIR, exist_ok=True)
with open(os.path.join(OUT_DIR, "area1_layout.json"), "w", encoding="utf-8") as out:
    json.dump(rows, out, indent=1)
summary = {}
for row in rows:
    key = (row["folder"], row["class"], row["material"])
    summary[key] = summary.get(key, 0) + 1
lines = ["{} actors".format(len(rows))] + ["  {:<40} {:<28} {:<16} {}".format(*key, count) for key, count in sorted(summary.items(), key=lambda kv: str(kv[0]))]
with open(os.path.join(unreal.Paths.project_saved_dir(), "area1_layout.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
