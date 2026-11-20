# Silence for the big mechanisms' show (BP_Lever with a ShowCamera; the user, 2026-11-20: "fully silent - more
# impact"). Same pattern as the gear arrival (setup_gear_arrival_sound.py): every sound plays under the engine's Master
# class, so a SoundMix turning Master to 0 silences the game; the machine's own sounds get a class outside Master.
#   Gimmicks/Area/SC_MechShow         the class of S_LeverPull, S_LeverReturn, S_MechRumble, S_MechStop
#   Gimmicks/Area/SM_MechShowMute     Master -> 0, in over 0.4 s, back over 1.5 s when popped
#   BP_Lever: ShowMix (SoundMix) = SM_MechShowMute; the graph pushes it as the view cuts to the show camera and pops it
#   as the view comes back (BP_Lever_EventGraph.txt, Generators/gen_area_foundation.ps1).
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_mech_show_mute.py -unattended -nop4 -nosplash -stdout
import os

import unreal

AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
pins = unreal.BlueprintEditorLibrary
lines = []


def made(name, asset_class, factory):
    path = AREA + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    lines.append("created " + path)
    return tools.create_asset(name, AREA, asset_class, factory)


show_class = made("SC_MechShow", unreal.SoundClass, unreal.SoundClassFactory())
library.save_asset(AREA + "/SC_MechShow", False)
for name in ("S_LeverPull", "S_LeverReturn", "S_MechRumble", "S_MechStop"):
    sound = unreal.load_asset(AREA + "/" + name)
    sound.set_editor_property("sound_class_object", show_class)
    library.save_asset(AREA + "/" + name, False)
    lines.append(name + " -> SC_MechShow")

mute = made("SM_MechShowMute", unreal.SoundMix, unreal.SoundMixFactory())
adjuster = unreal.SoundClassAdjuster()
adjuster.set_editor_property("sound_class_object", unreal.load_asset("/Engine/EngineSounds/Master"))
adjuster.set_editor_property("volume_adjuster", 0.0)
adjuster.set_editor_property("apply_to_children", True)
mute.set_editor_property("sound_class_effects", [adjuster])
mute.set_editor_property("fade_in_time", 0.4)
mute.set_editor_property("fade_out_time", 1.5)
library.save_asset(AREA + "/SM_MechShowMute", False)

bp = unreal.load_asset(AREA + "/BP_Lever")
try:
    unreal.get_default_object(bp.generated_class()).get_editor_property("ShowMix")
except Exception:
    if not pins.add_member_variable(bp, "ShowMix", pins.get_object_reference_type(unreal.SoundMix.static_class())):
        raise RuntimeError("Could not add ShowMix")
    lines.append("BP_Lever: variable ShowMix")
pins.compile_blueprint(bp)
unreal.get_default_object(bp.generated_class()).set_editor_property("ShowMix", mute)
library.save_asset(AREA + "/BP_Lever", False)
lines.append("ShowMix = SM_MechShowMute")

with open(os.path.join(unreal.Paths.project_saved_dir(), "mech_show_mute.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
