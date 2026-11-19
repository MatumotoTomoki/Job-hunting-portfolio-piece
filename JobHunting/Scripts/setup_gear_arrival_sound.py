# Silence for area 2's gear arrival (the user, 2026-11-18: "while it plays, the volume at 0", so the change of mood
# is felt). As for the danger button's finale (setup_danger_button_effects.py): the project's sounds, BGM included,
# all play under the engine's Master class, so a SoundMix that turns Master (and its children) to 0 silences them;
# the gear's own sounds get a class of their own outside Master and keep playing.
#   Gimmicks/Area/SC_GearShow           the class of S_GearClunk, S_GearHiss, S_GearSpin (also heard at area 1's exit)
#   Gimmicks/Area/SM_GearArrivalMute    Master -> 0 (fades in at once, back out over 2 s when popped)
#   BP_GearArrival: ArrivalMix (SoundMix) = SM_GearArrivalMute; the graph pushes it as the arrival starts and pops it
#   once the seal has shut (BP_GearArrival_EventGraph.txt).
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_gear_arrival_sound.py -unattended -nop4 -nosplash -stdout
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


show_class = made("SC_GearShow", unreal.SoundClass, unreal.SoundClassFactory())
library.save_asset(AREA + "/SC_GearShow", False)
for name in ("S_GearClunk", "S_GearHiss", "S_GearSpin"):
    sound = unreal.load_asset(AREA + "/" + name)
    sound.set_editor_property("sound_class_object", show_class)
    library.save_asset(AREA + "/" + name, False)
    lines.append(name + " -> SC_GearShow")

mute = made("SM_GearArrivalMute", unreal.SoundMix, unreal.SoundMixFactory())
adjuster = unreal.SoundClassAdjuster()
adjuster.set_editor_property("sound_class_object", unreal.load_asset("/Engine/EngineSounds/Master"))
adjuster.set_editor_property("volume_adjuster", 0.0)
adjuster.set_editor_property("apply_to_children", True)
mute.set_editor_property("sound_class_effects", [adjuster])
mute.set_editor_property("fade_in_time", 0.1)
mute.set_editor_property("fade_out_time", 2.0)
library.save_asset(AREA + "/SM_GearArrivalMute", False)

bp = unreal.load_asset(AREA + "/BP_GearArrival")
defaults = unreal.get_default_object(bp.generated_class())
try:
    defaults.get_editor_property("ArrivalMix")
except Exception:
    if not pins.add_member_variable(bp, "ArrivalMix", pins.get_object_reference_type(unreal.SoundMix.static_class())):
        raise RuntimeError("Could not add ArrivalMix")
    lines.append("BP_GearArrival: variable ArrivalMix")
pins.compile_blueprint(bp)
unreal.get_default_object(bp.generated_class()).set_editor_property("ArrivalMix", mute)
library.save_asset(AREA + "/BP_GearArrival", False)
lines.append("ArrivalMix = SM_GearArrivalMute")

with open(os.path.join(unreal.Paths.project_saved_dir(), "gear_arrival_sound.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
