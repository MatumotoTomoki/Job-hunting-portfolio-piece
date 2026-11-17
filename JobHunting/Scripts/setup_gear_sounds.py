# Imports the gear exit's sounds (SourceArt/Sounds/S_Gear*.wav, from make_gear_sounds.ps1) into Gimmicks/Area and
# gives BP_GearExit an audio component for each, all silent until the graph plays them:
#   ClunkSound  S_GearClunk, once, on stepping on        } on Lift, 2D (no attenuation): they ride up with the
#   HissSound   S_GearHiss, once, at the same time       } player and the camera, so they would sound the same
#   SpinSound   S_GearSpin, looping, from stepping on    } anyway
#   SparkSound  S_GearSparks, looping, from the rise: on the root at floor level, where the sparks are, with
#               SA_GearSparks (full within 3 m, gone 3 + 20 m away), so it fades as the gear carries the player up.
# The graph sets each one's volume to the game instance's SE Volume x Master Volume first (BP_GearExit_EventGraph.txt).
# The sounds are re-imported every run. Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_gear_sounds.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
GEAR_EXIT = DIR + "/BP_GearExit"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Sounds")
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

sounds = {}
for name, looping in (("S_GearClunk", False), ("S_GearHiss", False), ("S_GearSpin", True), ("S_GearSparks", True)):
    path = os.path.join(SOURCE, name + ".wav")
    if not os.path.isfile(path):
        raise RuntimeError("Missing " + path + "; run make_gear_sounds.ps1 first")
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = DIR
    task.destination_name = name
    task.automated = True
    task.save = True
    task.replace_existing = True
    tools.import_asset_tasks([task])
    sound = unreal.load_asset(DIR + "/" + name)
    if sound is None:
        raise RuntimeError(name + " did not import")
    sound.set_editor_property("looping", looping)
    library.save_asset(DIR + "/" + name, False)
    sounds[name] = sound
    lines.append("imported {} ({:.2f} s, looping {})".format(name, sound.get_editor_property("duration"), looping))

path = DIR + "/SA_GearSparks"
if library.does_asset_exist(path):
    attenuation = unreal.load_asset(path)
else:
    attenuation = tools.create_asset("SA_GearSparks", DIR, unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
    settings = attenuation.get_editor_property("attenuation")
    settings.set_editor_property("attenuation_shape_extents", unreal.Vector(300.0, 0.0, 0.0))
    settings.set_editor_property("falloff_distance", 2000.0)
    attenuation.set_editor_property("attenuation", settings)
    library.save_asset(path, False)
    lines.append("created " + path)

blueprint = unreal.load_asset(GEAR_EXIT)
if blueprint is None:
    raise RuntimeError(GEAR_EXIT + " not found; run setup_gear_exit.py first")


def gather():
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_associated_object(data_library.get_data(h))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = (h, component)
    return found


for name, sound_name, parent, z, spatial in (("ClunkSound", "S_GearClunk", "Lift", 30.0, None),
                                              ("HissSound", "S_GearHiss", "Lift", 30.0, None),
                                              ("SpinSound", "S_GearSpin", "Lift", 30.0, None),
                                              ("SparkSound", "S_GearSparks", "DefaultSceneRoot", 2.0, attenuation)):
    components = gather()
    if name in components:
        audio = components[name][1]
    else:
        params = unreal.AddNewSubobjectParams(parent_handle=components[parent][0], new_class=unreal.AudioComponent, blueprint_context=blueprint)
        handle, _ = subsystem.add_new_subobject(params)
        if not data_library.is_handle_valid(handle):
            raise RuntimeError("Could not add " + name)
        subsystem.rename_subobject(handle, unreal.Text(name))
        audio = data_library.get_associated_object(data_library.get_data(handle))
        lines.append("BP_GearExit: {} added under {}".format(name, parent))
    audio.set_editor_property("sound", sounds[sound_name])
    audio.set_editor_property("auto_activate", False)
    audio.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, z))
    if spatial is not None:
        audio.set_editor_property("attenuation_settings", spatial)
        audio.set_editor_property("allow_spatialization", True)
    else:
        audio.set_editor_property("allow_spatialization", False)
unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
library.save_asset(GEAR_EXIT, False)

# Check where each ended up (a script's hierarchy change can fail without a word).
for h in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
    data = data_library.get_data(h)
    component = data_library.get_associated_object(data)
    if component and component.get_name().replace("_GEN_VARIABLE", "") in ("ClunkSound", "HissSound", "SpinSound", "SparkSound"):
        parent = data_library.get_associated_object(data_library.get_data(data_library.get_parent_handle(data)))
        lines.append("  {} <- {}".format(component.get_name(), parent.get_name() if parent else None))

with open(os.path.join(unreal.Paths.project_saved_dir(), "gear_sounds.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
