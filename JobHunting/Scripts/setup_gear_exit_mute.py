# Silence for area 1's gear exit ride (BP_GearExit; the user, 2026-11-20: "mute it as you step on too", like the lever
# shows and the gear arrival). Every sound but the gear's own goes to 0 as the player steps on:
#   S_GearSparks joins S_GearClunk / S_GearHiss / S_GearSpin in SC_GearShow (setup_gear_arrival_sound.py)
#   Gimmicks/Area/SM_GearExitMute   Master -> 0, in over 0.4 s; popped just before the next level opens (the screen is
#                                   black by then), so no modifier is left over for the arrival's own mix
#   BP_GearExit: ExitMix (SoundMix) = SM_GearExitMute
# Graph: BP_GearExit_EventGraph.txt (Generators/gen_gear_exit.ps1). Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_gear_exit_mute.py -unattended -nop4 -nosplash -stdout
import os

import unreal

AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
pins = unreal.BlueprintEditorLibrary
lines = []

show_class = unreal.load_asset(AREA + "/SC_GearShow")
if show_class is None:
    raise RuntimeError("Run setup_gear_arrival_sound.py first (no SC_GearShow)")
sparks = unreal.load_asset(AREA + "/S_GearSparks")
sparks.set_editor_property("sound_class_object", show_class)
library.save_asset(AREA + "/S_GearSparks", False)
lines.append("S_GearSparks -> SC_GearShow")

path = AREA + "/SM_GearExitMute"
if library.does_asset_exist(path):
    mute = unreal.load_asset(path)
else:
    mute = tools.create_asset("SM_GearExitMute", AREA, unreal.SoundMix, unreal.SoundMixFactory())
    lines.append("created " + path)
adjuster = unreal.SoundClassAdjuster()
adjuster.set_editor_property("sound_class_object", unreal.load_asset("/Engine/EngineSounds/Master"))
adjuster.set_editor_property("volume_adjuster", 0.0)
adjuster.set_editor_property("apply_to_children", True)
mute.set_editor_property("sound_class_effects", [adjuster])
mute.set_editor_property("fade_in_time", 0.4)
mute.set_editor_property("fade_out_time", 0.5)
library.save_asset(path, False)

bp = unreal.load_asset(AREA + "/BP_GearExit")
try:
    unreal.get_default_object(bp.generated_class()).get_editor_property("ExitMix")
except Exception:
    if not pins.add_member_variable(bp, "ExitMix", pins.get_object_reference_type(unreal.SoundMix.static_class())):
        raise RuntimeError("Could not add ExitMix")
    lines.append("BP_GearExit: variable ExitMix")
pins.compile_blueprint(bp)
unreal.get_default_object(bp.generated_class()).set_editor_property("ExitMix", mute)
library.save_asset(AREA + "/BP_GearExit", False)
lines.append("ExitMix = SM_GearExitMute")

with open(os.path.join(unreal.Paths.project_saved_dir(), "gear_exit_mute.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
