# Imports the burning-sun effects from build_sun_fire_effect.ps1 (textures first, so the effects find them) and puts
# them on BP_Sun, attached to SunMesh so they travel with it: SunFire (orange) and SunFireBlue (the same fire in blue),
# both starting by themselves and looping. SunFireBlue starts invisible (AllColor alpha 0); BP_Sun's Event Graph fades
# from one to the other with its anger. The level also needs BP_EffekseerSystem, as for the other effects. Safe to run
# again. In the editor's Python console:
#   exec(open(r"C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\import_sun_fire.py", encoding="utf-8").read())
# or with the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=import_sun_fire.py -unattended -nop4 -nosplash -stdout
import os

import unreal

EFFECT_DIR = "/Game/FX/Effekseer"
TEXTURE_DIR = EFFECT_DIR + "/Texture"
SUN_PATH = "/Game/ThirdPerson/Blueprints/Gimmicks/Sun/BP_Sun"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Effects", "SunFire")
# Emitter name -> starting AllColor (the effect's colours are multiplied by it; alpha 0 hides it).
EMITTERS = {"SunFire": unreal.Color(r=255, g=255, b=255, a=255), "SunFireBlue": unreal.Color(r=255, g=255, b=255, a=0)}
library = unreal.EditorAssetLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def import_file(path, destination, replace=False):
    # Textures are imported once; the effects are replaced every run, so a rebuilt .efk comes through.
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
effects = {name: import_file(os.path.join(SOURCE, name + ".efk"), EFFECT_DIR, replace=True) for name in EMITTERS}

blueprint = unreal.load_asset(SUN_PATH)


def gather():
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_object(data_library.get_data(h))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = (h, component)
    return found


root = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
emitter_class = unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent")
for name, color in EMITTERS.items():
    handles = gather()
    if name in handles:
        emitter = handles[name][1]
    else:
        params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=emitter_class, blueprint_context=blueprint)
        handle, _ = subsystem.add_new_subobject(params)
        subsystem.rename_subobject(handle, unreal.Text(name))
        emitter = data_library.get_object(data_library.get_data(handle))
        emitter.set_editor_property("IsLooping", True)
        emitter.set_editor_property("auto_activate", True)
        emitter.set_editor_property("AllColor", color)
        lines.append("BP_Sun: {} added".format(name))
    emitter.set_editor_property("Effect", effects[name])
    handles = gather()
    if "SunMesh" in handles and subsystem.attach_subobject(handles["SunMesh"][0], handles[name][0]):
        lines.append("BP_Sun: {} attached to SunMesh".format(name))
unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
library.save_asset(SUN_PATH, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "sun_fire_import_report.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
