# Sounds and effects for area 4's wings (BP_Wings, Gimmicks/Heaven; the user, 2026-11-21):
#   S_WingsGet, S_WingFlap, S_WingGlide (looping)  from make_wings_sounds.ps1 (SourceArt/Sounds)
#   Effects /Game/FX/Effekseer/WingsFx/WingsGet, WingGlide (build_wings_effects.ps1)
#   BP_Wings: GetSound, FlapSound, GlideSound (audio, off until played; no attenuation - they ride on the player);
#             GetFx (one shot), GlideFx (looping, on while spread), both behind the shoulders like the Wings pivot,
#             world scale FX_SCALE; variable WasSpread
# Graph: BP_Wings_EventGraph.txt (Generators/gen_heaven_wings.ps1). Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_wings_effects.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
FX = "/Game/FX/Effekseer/WingsFx"
FX_SCALE = 2.0
AT = unreal.Vector(-20.0, 0.0, 0.0)   # the Wings pivot (setup_heaven_wings.py)
PROJECT = os.path.abspath(unreal.Paths.project_dir())
SOURCE_FX = os.path.join(PROJECT, "SourceArt", "Effects", "WingsFx")
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
          for name in ("S_WingsGet", "S_WingFlap", "S_WingGlide")}
# Since 2026-11-21 both come from bought files (make_wings_stock_sounds.ps1): the basa, then the wind looping
# (faded in by the graph).
sounds["S_WingGlide"].set_editor_property("looping", True)
sounds["S_WingGlide"].set_editor_property("volume", 1.0)
library.save_asset(DIR + "/S_WingGlide", False)
sounds["S_WingFlap"].set_editor_property("volume", 1.0)
library.save_asset(DIR + "/S_WingFlap", False)
for name in ("CloudPuff", "Glint", "Feather"):
    import_file(os.path.join(SOURCE_FX, "Texture", name + ".png"), FX + "/Texture")
get_fx = import_file(os.path.join(SOURCE_FX, "WingsGet.efk"), FX)
glide_fx = import_file(os.path.join(SOURCE_FX, "WingGlide.efk"), FX)
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


bp = unreal.load_asset(DIR + "/BP_Wings")
for name, sound in (("GetSound", "S_WingsGet"), ("FlapSound", "S_WingFlap"), ("GlideSound", "S_WingGlide")):
    a = add(bp, unreal.AudioComponent, name)
    a.set_editor_property("sound", sounds[sound])
    a.set_editor_property("auto_activate", False)
for name, effect, looping in (("GetFx", get_fx, False), ("GlideFx", glide_fx, True)):
    fx = add(bp, emitter_class, name)
    fx.set_editor_property("relative_location", AT)
    fx.set_editor_property("Effect", effect)
    fx.set_editor_property("IsLooping", looping)
    fx.set_editor_property("auto_activate", False)
    fx.set_editor_property("absolute_scale", True)
    fx.set_editor_property("relative_scale3d", unreal.Vector(FX_SCALE, FX_SCALE, FX_SCALE))
try:
    unreal.get_default_object(bp.generated_class()).get_editor_property("WasSpread")
except Exception:
    if not pins.add_member_variable(bp, "WasSpread", pins.get_basic_type_by_name("bool")):
        raise RuntimeError("Could not add WasSpread")
    lines.append("BP_Wings: variable WasSpread")
pins.compile_blueprint(bp)
library.save_asset(DIR + "/BP_Wings", False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "wings_effects.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
