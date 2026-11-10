# Imports the CageFire effect (SourceArt/Effects/CageFire) and puts it on the black birdcage, BP_BirdcageDoor_Black
# (make_black_birdcage.py), as the CageFire emitter at the cage's base: it starts by itself and keeps looping. The flames
# rise from horizontal circles around the cage (CageFire.efkproj, AxisDirection Y), so one emitter rings the whole cage.
# The CageFire_1.. emitters an earlier version stood in a ring are removed.
# CageFire gets its own folder, /Game/FX/Effekseer/CageFire with its textures in Texture/ under it: Effekseer looks
# textures up relative to the effect, and its Particle_Soft.png differs from the one other effects already use at
# /Game/FX/Effekseer/Texture/Particle_Soft, which must stay as it is. The level also needs BP_EffekseerSystem.
# Safe to run again. In the editor's Python console:
#   exec(open(r"C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\import_cage_fire.py", encoding="utf-8").read())
import os

import unreal

EFFECT_DIR = "/Game/FX/Effekseer/CageFire"
TEXTURE_DIR = EFFECT_DIR + "/Texture"
CAGE_PATH = "/Game/Prototype/Birdcage/BP_BirdcageDoor_Black"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Effects", "CageFire")
library = unreal.EditorAssetLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def import_file(path, destination, replace=False):
    # Textures are imported once; the effect is replaced every run, so an updated CageFire.efk comes through.
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


for name in ("Fire", "Particle_Soft", "Smoke"):
    import_file(os.path.join(SOURCE, "Texture", name + ".png"), TEXTURE_DIR)
effect = import_file(os.path.join(SOURCE, "CageFire.efk"), EFFECT_DIR, replace=True)
lines.append("effect {} textures {}".format(effect, effect.get_editor_property("ColorTextures")))

blueprint = unreal.load_asset(CAGE_PATH)
if blueprint is None:
    raise RuntimeError(CAGE_PATH + " not found; run make_black_birdcage.py first")
def gather():
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_associated_object(data_library.get_data(h))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = (h, component)
    return found


root = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
components = gather()
extras = [h for name, (h, _) in components.items() if name.startswith("CageFire_")]
if extras:
    subsystem.delete_subobjects(root, extras, blueprint)
    lines.append("removed {} ring emitters".format(len(extras)))
    components = gather()
if "CageFire" in components:
    emitter = components["CageFire"][1]
else:
    emitter_class = unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent")
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=emitter_class, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("CageFire"))
    emitter = data_library.get_associated_object(data_library.get_data(handle))
    emitter.set_editor_property("IsLooping", True)
    emitter.set_editor_property("auto_activate", True)
    lines.append("BP_BirdcageDoor_Black: CageFire added")
emitter.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
emitter.set_editor_property("relative_scale3d", unreal.Vector(1.0, 1.0, 1.0))
emitter.set_editor_property("Effect", effect)
unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
library.save_asset(CAGE_PATH, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "cage_fire_import_report.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
