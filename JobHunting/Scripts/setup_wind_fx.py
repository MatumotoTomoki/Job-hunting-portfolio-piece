# Puts the wind's new look on BP_WindZone (the user, 2026-11-19): WindFlow (build_wind_effect.ps1) imported into
# /Game/FX/Effekseer/Wind (its textures in Texture/ under it) and played by a "WindFx" emitter at the box's middle. It
# loops and starts by itself; BP_WindZone's graph turns it off while a gust rests and on while it blows
# (BP_WindZone_EventGraph.txt from Generators/gen_area3_gimmicks.ps1). The actor's scale stretches it with the box.
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_wind_fx.py -unattended -nop4 -nosplash -stdout
import os

import unreal

FX = "/Game/FX/Effekseer/Wind"
WIND = "/Game/ThirdPerson/Blueprints/Gimmicks/Sky/BP_WindZone"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Effects", "Wind")
library = unreal.EditorAssetLibrary
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
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    asset = destination + "/" + os.path.splitext(os.path.basename(path))[0]
    lines.append("imported " + asset)
    return unreal.load_asset(asset)


for name in ("WindLine", "WindPuff"):
    import_file(os.path.join(SOURCE, "Texture", name + ".png"), FX + "/Texture")
effect = import_file(os.path.join(SOURCE, "WindFlow.efk"), FX)
lines.append("textures {}".format(effect.get_editor_property("ColorTextures")))

bp = unreal.load_asset(WIND)
found = {}
for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
    c = data_library.get_associated_object(data_library.get_data(h))
    if c is not None:
        found[c.get_name().replace("_GEN_VARIABLE", "")] = (h, c)
if "WindFx" in found:
    emitter = found["WindFx"][1]
else:
    root = found["DefaultSceneRoot"][0] if "DefaultSceneRoot" in found else subsystem.k2_gather_subobject_data_for_blueprint(bp)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent"), blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("WindFx"))
    emitter = data_library.get_associated_object(data_library.get_data(handle))
    lines.append("BP_WindZone: WindFx added")
emitter.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
emitter.set_editor_property("Effect", effect)
emitter.set_editor_property("IsLooping", True)
emitter.set_editor_property("auto_activate", True)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
library.save_asset(WIND, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "wind_fx.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
