# Imports Heaven's Gate's sounds (make_gate_sounds.ps1) into Gimmicks/Heaven: S_GateOpen (the doors) and S_GateLight
# (the light pouring out). BP_HeavenGate's graph (gen_heaven_gate.ps1) plays both, 2D, at SE Volume x Master Volume,
# as the view cuts to the gate. Safe to run again. From the Output Log (Python):
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\setup_gate_sounds.py', encoding='utf-8').read())
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
SOURCE = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()), "SourceArt", "Sounds")
tools = unreal.AssetToolsHelpers.get_asset_tools()
lines = []
for name in ("S_GateOpen", "S_GateLight"):
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", os.path.join(SOURCE, name + ".wav"))
    task.set_editor_property("destination_path", DIR)
    task.set_editor_property("destination_name", name)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", True)
    tools.import_asset_tasks([task])
    wave = unreal.load_asset(DIR + "/" + name)
    if not wave:
        raise RuntimeError("Could not import " + name)
    lines.append("imported {}/{} ({:.1f} s)".format(DIR, name, wave.get_editor_property("duration")))

with open(os.path.join(unreal.Paths.project_saved_dir(), "setup_gate_sounds.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(lines) + "\n")
unreal.log("\n".join(lines))
