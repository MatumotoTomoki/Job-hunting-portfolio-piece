# Sounds and effects for the timed platform (BP_TimedPlatform, Gimmicks; the user, 2026-11-22):
#   S_TimedVanish, S_TimedAppear  from make_timed_sounds.ps1 (SourceArt/Sounds)
#   SA_TimedPlatform   full within 3 m, silent 20 m on (they play every cycle, so they stay close)
#   SCON_TimedPlatform at most 3 at once, the farthest dropped (a staggered row cycles together)
#   Effects /Game/FX/Effekseer/TimedFx/TimedVanish, TimedAppear (build_timed_effects.ps1)
#   BP_TimedPlatform: VanishSound, AppearSound, VanishFx, AppearFx at its middle, effects at world scale FX_SCALE
# Graph: BP_TimedPlatform_EventGraph.txt (Generators/gen_timed_platform.ps1). Safe to run again. Run it in the
# editor's Output Log (Python):
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\setup_timed_effects.py', encoding='utf-8').read())
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks"
FX = "/Game/FX/Effekseer/TimedFx"
FX_SCALE = 1.0   # the effects are sized for the 3 x 3 m slab
PROJECT = os.path.abspath(unreal.Paths.project_dir())
SOURCE_FX = os.path.join(PROJECT, "SourceArt", "Effects", "TimedFx")
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


def asset(name, asset_class, factory):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    lines.append("created " + path)
    return tools.create_asset(name, DIR, asset_class, factory)


sounds = {name: import_file(os.path.join(PROJECT, "SourceArt", "Sounds", name + ".wav"), DIR)
          for name in ("S_TimedVanish", "S_TimedAppear")}

att = asset("SA_TimedPlatform", unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
settings = att.get_editor_property("attenuation")
settings.set_editor_property("attenuation_shape_extents", unreal.Vector(300.0, 0.0, 0.0))
settings.set_editor_property("falloff_distance", 1700.0)
att.set_editor_property("attenuation", settings)
library.save_asset(DIR + "/SA_TimedPlatform", False)

concurrency = asset("SCON_TimedPlatform", unreal.SoundConcurrency, unreal.SoundConcurrencyFactory())
rules = concurrency.get_editor_property("concurrency")
rules.set_editor_property("max_count", 3)
rules.set_editor_property("resolution_rule", unreal.MaxConcurrentResolutionRule.STOP_FARTHEST_THEN_OLDEST)
concurrency.set_editor_property("concurrency", rules)
library.save_asset(DIR + "/SCON_TimedPlatform", False)
for name, sound in sounds.items():
    try:
        sound.set_editor_property("concurrency_set", [concurrency])
        lines.append(name + " -> SCON_TimedPlatform")
    except Exception as error:
        lines.append("{}: concurrency not set ({})".format(name, error))
    library.save_asset(DIR + "/" + name, False)

for name in ("CloudPuff", "Glint"):
    import_file(os.path.join(SOURCE_FX, "Texture", name + ".png"), FX + "/Texture")
effects = {name: import_file(os.path.join(SOURCE_FX, name + ".efk"), FX) for name in ("TimedVanish", "TimedAppear")}
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
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add " + name)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("{}: component {}".format(bp.get_name(), name))
    return data_library.get_associated_object(data_library.get_data(handle))


bp = unreal.load_asset(DIR + "/BP_TimedPlatform")
for name, sound in (("VanishSound", "S_TimedVanish"), ("AppearSound", "S_TimedAppear")):
    a = add(bp, unreal.AudioComponent, name)
    a.set_editor_property("sound", sounds[sound])
    a.set_editor_property("auto_activate", False)
    a.set_editor_property("attenuation_settings", att)
for name, effect in (("VanishFx", "TimedVanish"), ("AppearFx", "TimedAppear")):
    fx = add(bp, emitter_class, name)
    fx.set_editor_property("Effect", effects[effect])
    fx.set_editor_property("IsLooping", False)
    fx.set_editor_property("auto_activate", False)
    fx.set_editor_property("absolute_scale", True)
    fx.set_editor_property("relative_scale3d", unreal.Vector(FX_SCALE, FX_SCALE, FX_SCALE))
pins.compile_blueprint(bp)
library.save_asset(DIR + "/BP_TimedPlatform", False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "timed_effects.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
