# Sounds and effects for the crumbling floor (BP_FallingFloor, Gimmicks; the user, 2026-11-22):
#   S_FloorCrack, S_FloorFall, S_FloorReturn  from make_floor_sounds.ps1 (SourceArt/Sounds)
#   SA_FallingFloor  full within 4 m, silent 30 m on
#   Effects /Game/FX/Effekseer/FloorFx/FloorCrack, FloorFall (build_floor_effects.ps1)
#   BP_FallingFloor: CrackSound, ReturnSound, CrackFx, FallFx at its middle (they stay put); FallSound on Lift (it
#                    rides down with the floor). Effects at world scale FX_SCALE.
# Graph: BP_FallingFloor_EventGraph.txt (Generators/gen_falling_floor.ps1; it now holds the FootSmoke on return
# too). Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_floor_effects.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks"
FX = "/Game/FX/Effekseer/FloorFx"
FX_SCALE = 1.0   # the effects are sized for the 3 x 3 m slab
PROJECT = os.path.abspath(unreal.Paths.project_dir())
SOURCE_FX = os.path.join(PROJECT, "SourceArt", "Effects", "FloorFx")
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


sounds = {name: import_file(os.path.join(PROJECT, "SourceArt", "Sounds", name + ".wav"), DIR)
          for name in ("S_FloorCrack", "S_FloorFall", "S_FloorReturn")}

path = DIR + "/SA_FallingFloor"
if library.does_asset_exist(path):
    att = unreal.load_asset(path)
else:
    att = tools.create_asset("SA_FallingFloor", DIR, unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
    lines.append("created " + path)
settings = att.get_editor_property("attenuation")
settings.set_editor_property("attenuation_shape_extents", unreal.Vector(400.0, 0.0, 0.0))
settings.set_editor_property("falloff_distance", 2600.0)
att.set_editor_property("attenuation", settings)
library.save_asset(path, False)

import_file(os.path.join(SOURCE_FX, "Texture", "CloudPuff.png"), FX + "/Texture")
effects = {name: import_file(os.path.join(SOURCE_FX, name + ".efk"), FX) for name in ("FloorCrack", "FloorFall")}
emitter_class = unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent")


def gather(bp):
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
        c = data_library.get_associated_object(data_library.get_data(h))
        if c is not None:
            found[c.get_name().replace("_GEN_VARIABLE", "")] = (h, c)
    return found


def add(bp, component_class, name, parent):
    found = gather(bp)
    if name in found:
        return found[name][1]
    params = unreal.AddNewSubobjectParams(parent_handle=found[parent][0], new_class=component_class, blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add " + name)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("{}: component {}".format(bp.get_name(), name))
    return data_library.get_associated_object(data_library.get_data(handle))


bp = unreal.load_asset(DIR + "/BP_FallingFloor")
for name, sound, parent in (("CrackSound", "S_FloorCrack", "DefaultSceneRoot"), ("FallSound", "S_FloorFall", "Lift"),
                            ("ReturnSound", "S_FloorReturn", "DefaultSceneRoot")):
    a = add(bp, unreal.AudioComponent, name, parent)
    a.set_editor_property("sound", sounds[sound])
    a.set_editor_property("auto_activate", False)
    a.set_editor_property("attenuation_settings", att)
for name, effect in (("CrackFx", "FloorCrack"), ("FallFx", "FloorFall")):
    fx = add(bp, emitter_class, name, "DefaultSceneRoot")
    fx.set_editor_property("Effect", effects[effect])
    fx.set_editor_property("IsLooping", False)
    fx.set_editor_property("auto_activate", False)
    fx.set_editor_property("absolute_scale", True)
    fx.set_editor_property("relative_scale3d", unreal.Vector(FX_SCALE, FX_SCALE, FX_SCALE))
pins.compile_blueprint(bp)
library.save_asset(DIR + "/BP_FallingFloor", False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "floor_effects.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
