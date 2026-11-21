# Sounds and an effect for the lever and the big mechanisms (Gimmicks/Area; the user, 2026-11-20):
#   S_LeverPull, S_LeverReturn, S_MechRumble (looping)  from make_lever_sounds.ps1 (SourceArt/Sounds)
#   SA_Lever       full within 4 m, silent 30 m on;  SA_MechRumble  full within 10 m, silent 60 m on (big machines,
#                  often watched through the lever's show camera)
#   Effect /Game/FX/Effekseer/LeverSpark (build_lever_spark_effect.ps1)
#   BP_Lever:      PullSound, ReturnSound (audio, off until played), PullFx (emitter at the pivot, off until played)
#   BP_Mechanism:  MoveSound (the rumble, off until it moves), StopSound (S_MechStop as it comes to rest);
#                  variables LastAlpha, WasMoving
# Graphs: BP_Lever_EventGraph.txt, BP_Mechanism_EventGraph.txt (Generators/gen_area_foundation.ps1). Safe to run
# again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_lever_sounds.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
FX = "/Game/FX/Effekseer/LeverSpark"
PROJECT = os.path.abspath(unreal.Paths.project_dir())
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def import_file(path, destination):
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = destination
    task.automated = True
    task.save = True
    task.replace_existing = True
    tools.import_asset_tasks([task])
    asset = destination + "/" + os.path.splitext(os.path.basename(path))[0]
    lines.append("imported " + asset)
    return unreal.load_asset(asset)


def attenuation(name, inner, falloff):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    made = tools.create_asset(name, DIR, unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
    settings = made.get_editor_property("attenuation")
    settings.set_editor_property("attenuation_shape_extents", unreal.Vector(inner, 0.0, 0.0))
    settings.set_editor_property("falloff_distance", falloff)
    made.set_editor_property("attenuation", settings)
    library.save_asset(path, False)
    lines.append("created " + path)
    return made


sounds = {name: import_file(os.path.join(PROJECT, "SourceArt", "Sounds", name + ".wav"), DIR)
          for name in ("S_LeverPull", "S_LeverReturn", "S_MechRumble", "S_MechStop")}
rumble = sounds["S_MechRumble"]
rumble.set_editor_property("looping", True)
rumble.set_editor_property("volume", 0.85)         # several parts rumble at once (0.6 felt too light, 2026-11-20)
library.save_asset(DIR + "/S_MechRumble", False)
lever_att = attenuation("SA_Lever", 400.0, 2600.0)
mech_att = attenuation("SA_MechRumble", 1000.0, 5000.0)
for name in ("CloudPuff", "Glint"):
    import_file(os.path.join(PROJECT, "SourceArt", "Effects", "LeverSpark", "Texture", name + ".png"), FX + "/Texture")
spark = import_file(os.path.join(PROJECT, "SourceArt", "Effects", "LeverSpark", "LeverSpark.efk"), FX)
emitter_class = unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent")


def gather(bp):
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
        c = data_library.get_associated_object(data_library.get_data(h))
        if c is not None:
            found[c.get_name().replace("_GEN_VARIABLE", "")] = (h, c)
    return found


def add(bp, component_class, name):
    found = gather(bp)
    if name in found:
        return found[name][1]
    root = found["DefaultSceneRoot"][0] if "DefaultSceneRoot" in found else subsystem.k2_gather_subobject_data_for_blueprint(bp)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=component_class, blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("{}: component {}".format(bp.get_name(), name))
    return data_library.get_associated_object(data_library.get_data(handle))


def audio(bp, name, sound, att):
    a = add(bp, unreal.AudioComponent, name)
    a.set_editor_property("sound", sound)
    a.set_editor_property("auto_activate", False)
    a.set_editor_property("attenuation_settings", att)
    return a


# ----- BP_Lever -----
lever = unreal.load_asset(DIR + "/BP_Lever")
for name, sound in (("PullSound", sounds["S_LeverPull"]), ("ReturnSound", sounds["S_LeverReturn"])):
    audio(lever, name, sound, lever_att).set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 50.0))
fx = add(lever, emitter_class, "PullFx")
fx.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 50.0))
fx.set_editor_property("Effect", spark)
fx.set_editor_property("IsLooping", False)
fx.set_editor_property("auto_activate", False)
fx.set_editor_property("absolute_scale", True)
pins.compile_blueprint(lever)
library.save_asset(DIR + "/BP_Lever", False)

# ----- BP_Mechanism -----
mechanism = unreal.load_asset(DIR + "/BP_Mechanism")
audio(mechanism, "MoveSound", rumble, mech_att)
audio(mechanism, "StopSound", sounds["S_MechStop"], mech_att)
defaults = unreal.get_default_object(mechanism.generated_class())
for name, pin_type in (("LastAlpha", pins.get_basic_type_by_name("real")), ("WasMoving", pins.get_basic_type_by_name("bool"))):
    try:
        defaults.get_editor_property(name)
    except Exception:
        if not pins.add_member_variable(mechanism, name, pin_type):
            raise RuntimeError("Could not add " + name)
        lines.append("BP_Mechanism: variable " + name)
pins.compile_blueprint(mechanism)
library.save_asset(DIR + "/BP_Mechanism", False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "lever_sounds.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
