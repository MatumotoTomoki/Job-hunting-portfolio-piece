# Sounds and effects for area 4's spider thread (BP_SpiderThread, Gimmicks/Heaven; the user, 2026-11-22):
#   S_ThreadGrab, S_ThreadFray, S_ThreadSnap, S_ThreadReturn  from make_thread_sounds.ps1 (SourceArt/Sounds)
#   SA_Thread   full within 4 m, silent 30 m on
#   Effects /Game/FX/Effekseer/ThreadFx/ThreadGrab, ThreadSnap, ThreadReturn (build_thread_effects.ps1)
#   BP_SpiderThread:
#     At (scene, under Swing; the graph moves it to where the player holds on) with GrabSound, FraySound, SnapSound,
#        GrabFx, SnapFx
#     ReturnSound, ReturnFx at the top (under Swing)
#     variable WasFraying (the thread was red last tick)
# Graph: BP_SpiderThread_EventGraph.txt (Generators/gen_heaven_thread.ps1). Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_thread_effects.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
FX = "/Game/FX/Effekseer/ThreadFx"
FX_SCALE = 3.0       # like the shard and the switch
RETURN_SCALE = 1.0   # the glints run ~14 m down at 1
PROJECT = os.path.abspath(unreal.Paths.project_dir())
SOURCE_FX = os.path.join(PROJECT, "SourceArt", "Effects", "ThreadFx")
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
          for name in ("S_ThreadGrab", "S_ThreadFray", "S_ThreadSnap", "S_ThreadReturn")}

path = DIR + "/SA_Thread"
if library.does_asset_exist(path):
    att = unreal.load_asset(path)
else:
    att = tools.create_asset("SA_Thread", DIR, unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
    lines.append("created " + path)
settings = att.get_editor_property("attenuation")
settings.set_editor_property("attenuation_shape_extents", unreal.Vector(400.0, 0.0, 0.0))
settings.set_editor_property("falloff_distance", 2600.0)
att.set_editor_property("attenuation", settings)
library.save_asset(path, False)

for name in ("CloudPuff", "Glint"):
    import_file(os.path.join(SOURCE_FX, "Texture", name + ".png"), FX + "/Texture")
effects = {name: import_file(os.path.join(SOURCE_FX, name + ".efk"), FX)
           for name in ("ThreadGrab", "ThreadSnap", "ThreadReturn")}
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


def audio(bp, name, sound, parent):
    a = add(bp, unreal.AudioComponent, name, parent)
    a.set_editor_property("sound", sounds[sound])
    a.set_editor_property("auto_activate", False)
    a.set_editor_property("attenuation_settings", att)


def emitter(bp, name, effect, parent, scale):
    fx = add(bp, emitter_class, name, parent)
    fx.set_editor_property("Effect", effects[effect])
    fx.set_editor_property("IsLooping", False)
    fx.set_editor_property("auto_activate", False)
    fx.set_editor_property("absolute_scale", True)
    fx.set_editor_property("relative_scale3d", unreal.Vector(scale, scale, scale))


bp = unreal.load_asset(DIR + "/BP_SpiderThread")
add(bp, unreal.SceneComponent, "At", "Swing")
audio(bp, "GrabSound", "S_ThreadGrab", "At")
audio(bp, "FraySound", "S_ThreadFray", "At")
audio(bp, "SnapSound", "S_ThreadSnap", "At")
audio(bp, "ReturnSound", "S_ThreadReturn", "Swing")
emitter(bp, "GrabFx", "ThreadGrab", "At", FX_SCALE)
emitter(bp, "SnapFx", "ThreadSnap", "At", FX_SCALE)
emitter(bp, "ReturnFx", "ThreadReturn", "Swing", RETURN_SCALE)
try:
    unreal.get_default_object(bp.generated_class()).get_editor_property("WasFraying")
except Exception:
    if not pins.add_member_variable(bp, "WasFraying", pins.get_basic_type_by_name("bool")):
        raise RuntimeError("Could not add WasFraying")
    lines.append("BP_SpiderThread: variable WasFraying")
pins.compile_blueprint(bp)
library.save_asset(DIR + "/BP_SpiderThread", False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "thread_effects.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
