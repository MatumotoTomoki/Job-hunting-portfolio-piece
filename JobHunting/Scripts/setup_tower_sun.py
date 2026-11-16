# BP_TowerSun (Gimmicks/Heaven): BP_Sun copied for area 4's dark tower, its range the whole tower. Changing the placed
# sun's components did not stick (the placed one kept BP_Sun's 10 m box, 2026-11-16), so the copy carries the sizes in
# its own components:
#   Area      a box AREA_HALF wide each way, sitting on the actor's origin (the tower's floor); its outline hidden in game
#   SunMesh   HOME up (where the ball waits), Platform on top of it
# The graph comes along with the copy. Copied once (an existing BP_TowerSun is kept and only resized). Run again after
# BP_Sun's graph changes: delete BP_TowerSun first. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_tower_sun.py -unattended -nop4 -nosplash -stdout
import os

import unreal

SOURCE = "/Game/ThirdPerson/Blueprints/Gimmicks/Sun/BP_Sun"
TARGET = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven/BP_TowerSun"
AREA_HALF = unreal.Vector(2000.0, 2000.0, 2000.0)
HOME = 3000.0
PLATFORM_ABOVE = 42.0

library = unreal.EditorAssetLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

if not library.does_asset_exist(TARGET):
    if not library.duplicate_asset(SOURCE, TARGET):
        raise RuntimeError("Could not copy " + SOURCE)
    lines.append("copied {} -> {}".format(SOURCE, TARGET))
blueprint = unreal.load_asset(TARGET)
found = {}
for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
    component = data_library.get_associated_object(data_library.get_data(handle))
    if component is not None:
        found[component.get_name().replace("_GEN_VARIABLE", "")] = component
for name in ("Area", "SunMesh", "Platform"):
    if name not in found:
        raise RuntimeError("BP_TowerSun has no " + name + " (has " + ", ".join(sorted(found)) + ")")
found["Area"].set_editor_property("box_extent", AREA_HALF)
found["Area"].set_editor_property("relative_location", unreal.Vector(0.0, 0.0, AREA_HALF.z))
found["Area"].set_editor_property("hidden_in_game", True)
found["SunMesh"].set_editor_property("relative_location", unreal.Vector(0.0, 0.0, HOME))
found["Platform"].set_editor_property("relative_location", unreal.Vector(0.0, 0.0, HOME + PLATFORM_ABOVE))
pins.compile_blueprint(blueprint)
library.save_asset(TARGET, False)
lines.append("area {} home {}".format(found["Area"].get_editor_property("box_extent"), found["SunMesh"].get_editor_property("relative_location")))

with open(os.path.join(unreal.Paths.project_saved_dir(), "tower_sun.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
