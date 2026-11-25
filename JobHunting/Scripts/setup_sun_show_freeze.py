# The sun stands still during a show (the user, 2026-11-25: "change the sun itself"): a component of its own,
# Gimmicks/Sun/BPC_SunShowFreeze (an ActorComponent blueprint), is added to BP_Sun and BP_TowerSun. Its own tick (a
# component ticks apart from its actor) turns the owner's Tick off while the camera is away from the player (a show:
# SetViewTargetWithBlend) and back on after. The sun runs only on its Tick (PhaseTime counts DeltaSeconds), so it stops
# where it is and goes on from there. The suns' graphs are not touched (their hooks and sounds stay).
#   BPC_SunShowFreeze: variable Frozen (bool).  Graph: BPC_SunShowFreeze_EventGraph.txt (gen_sun_show_freeze.ps1).
# Safe to run again. Editor closed (it changes BP_Sun / BP_TowerSun), as a commandlet:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_sun_show_freeze.py -unattended -nop4 -nosplash -stdout
import os

import unreal

SUN_DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Sun"
PATH = SUN_DIR + "/BPC_SunShowFreeze"
SUNS = [SUN_DIR + "/BP_Sun", "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven/BP_TowerSun"]
library = unreal.EditorAssetLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

if library.does_asset_exist(PATH):
    comp_bp = unreal.load_asset(PATH)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.ActorComponent)
    comp_bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset("BPC_SunShowFreeze", SUN_DIR, unreal.Blueprint, factory)
    lines.append("created " + PATH)
defaults = unreal.get_default_object(comp_bp.generated_class())
try:
    defaults.get_editor_property("Frozen")
except Exception:
    if not pins.add_member_variable(comp_bp, "Frozen", pins.get_basic_type_by_name("bool")):
        raise RuntimeError("Could not add Frozen")
    lines.append("BPC_SunShowFreeze: variable Frozen")
pins.compile_blueprint(comp_bp)
library.save_asset(PATH, False)

for sun_path in SUNS:
    sun = unreal.load_asset(sun_path)
    handles = subsystem.k2_gather_subobject_data_for_blueprint(sun)
    names = [data_library.get_associated_object(data_library.get_data(h)).get_name().replace("_GEN_VARIABLE", "")
             for h in handles if data_library.get_associated_object(data_library.get_data(h)) is not None]
    if "ShowFreeze" in names:
        lines.append("{}: ShowFreeze already there".format(sun_path))
        continue
    handle, _ = subsystem.add_new_subobject(unreal.AddNewSubobjectParams(
        parent_handle=handles[0], new_class=comp_bp.generated_class(), blueprint_context=sun))
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add ShowFreeze to " + sun_path)
    subsystem.rename_subobject(handle, unreal.Text("ShowFreeze"))
    pins.compile_blueprint(sun)
    library.save_asset(sun_path, False)
    lines.append("{}: ShowFreeze added".format(sun_path))

with open(os.path.join(unreal.Paths.project_saved_dir(), "sun_show_freeze.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(lines) + "\n")
unreal.log("\n".join(lines))
