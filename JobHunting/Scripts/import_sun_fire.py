# Imports the burning-sun effect from build_sun_fire_effect.ps1 (textures first, so the effect finds them) and puts it
# on BP_Sun as the SunFire emitter, which starts by itself and keeps looping. The level also needs BP_EffekseerSystem,
# as for the other effects. Safe to run again. In the editor's Python console:
#   exec(open(r"C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\import_sun_fire.py", encoding="utf-8").read())
# or with the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=import_sun_fire.py -unattended -nop4 -nosplash -stdout
import os

import unreal

EFFECT_DIR = "/Game/FX/Effekseer"
TEXTURE_DIR = EFFECT_DIR + "/Texture"
SUN_PATH = "/Game/ThirdPerson/Blueprints/Gimmicks/Sun/BP_Sun"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Effects", "SunFire")
library = unreal.EditorAssetLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def import_file(path, destination, replace=False):
    # Textures are imported once; the effect is replaced every run, so a rebuilt SunFire.efk comes through.
    asset_path = destination + "/" + os.path.splitext(os.path.basename(path))[0]
    if library.does_asset_exist(asset_path) and not replace:
        return unreal.load_asset(asset_path)
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = destination
    task.automated = True
    task.save = True
    task.replace_existing = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    lines.append("imported " + asset_path)
    return unreal.load_asset(asset_path)


for name in ("SunGlow", "SunFlame", "SunRays", "SunPuff"):
    import_file(os.path.join(SOURCE, "Texture", name + ".png"), TEXTURE_DIR)
effect = import_file(os.path.join(SOURCE, "SunFire.efk"), EFFECT_DIR, replace=True)
lines.append("effect {} textures {}".format(effect, effect.get_editor_property("ColorTextures")))

blueprint = unreal.load_asset(SUN_PATH)
handles = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)
names = [data_library.get_object(data_library.get_data(h)).get_name().replace("_GEN_VARIABLE", "") for h in handles]
if "SunFire" in names:
    lines.append("BP_Sun: SunFire already there")
else:
    emitter_class = unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent")
    params = unreal.AddNewSubobjectParams(parent_handle=handles[0], new_class=emitter_class, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("SunFire"))
    emitter = data_library.get_object(data_library.get_data(handle))
    emitter.set_editor_property("Effect", effect)
    emitter.set_editor_property("IsLooping", True)
    emitter.set_editor_property("auto_activate", True)
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    library.save_asset(SUN_PATH, False)
    lines.append("BP_Sun: SunFire added")

with open(os.path.join(unreal.Paths.project_saved_dir(), "sun_fire_import_report.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
