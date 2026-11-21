# Sound and effects for area 4's light shard (BP_LightShard, Gimmicks/Heaven; the user, 2026-11-21):
#   S_ShardGet  from make_shard_sounds.ps1 (SourceArt/Sounds). BP_LightShard plays it with PlaySoundAtLocation (its
#               GetSound variable), so it rings on after the shard is destroyed.
#   Effects /Game/FX/Effekseer/ShardFx/ShardIdle, ShardGet (build_shard_effects.ps1)
#   BP_LightShard: IdleFx (ShardIdle, looping, on from the start), GetFx (ShardGet, off until it is taken), both at
#                  the shard's middle, world scale FX_SCALE; variable GetSound (SoundBase) = S_ShardGet
# Graph: BP_LightShard_EventGraph.txt (Generators/gen_heaven_light.ps1). Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_shard_effects.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
FX = "/Game/FX/Effekseer/ShardFx"
FX_SCALE = 3.0   # the switch effects ended at 3 (the user, 2026-11-21)
PROJECT = os.path.abspath(unreal.Paths.project_dir())
SOURCE_FX = os.path.join(PROJECT, "SourceArt", "Effects", "ShardFx")
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


sound = import_file(os.path.join(PROJECT, "SourceArt", "Sounds", "S_ShardGet.wav"), DIR)
for name in ("CloudPuff", "Glint"):
    import_file(os.path.join(SOURCE_FX, "Texture", name + ".png"), FX + "/Texture")
idle = import_file(os.path.join(SOURCE_FX, "ShardIdle.efk"), FX)
get = import_file(os.path.join(SOURCE_FX, "ShardGet.efk"), FX)
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


bp = unreal.load_asset(DIR + "/BP_LightShard")
for name, effect, looping in (("IdleFx", idle, True), ("GetFx", get, False)):
    fx = add(bp, emitter_class, name)
    fx.set_editor_property("Effect", effect)
    fx.set_editor_property("IsLooping", looping)
    fx.set_editor_property("auto_activate", looping)
    fx.set_editor_property("absolute_scale", True)
    fx.set_editor_property("relative_scale3d", unreal.Vector(FX_SCALE, FX_SCALE, FX_SCALE))
try:
    unreal.get_default_object(bp.generated_class()).get_editor_property("GetSound")
except Exception:
    if not pins.add_member_variable(bp, "GetSound", pins.get_object_reference_type(unreal.SoundBase.static_class())):
        raise RuntimeError("Could not add GetSound")
    lines.append("BP_LightShard: variable GetSound")
pins.compile_blueprint(bp)
unreal.get_default_object(bp.generated_class()).set_editor_property("GetSound", sound)
library.save_asset(DIR + "/BP_LightShard", False)
lines.append("GetSound = S_ShardGet")

with open(os.path.join(unreal.Paths.project_saved_dir(), "shard_effects.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
