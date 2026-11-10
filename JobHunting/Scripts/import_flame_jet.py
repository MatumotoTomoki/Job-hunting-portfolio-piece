# Imports the FlameJet effect (SourceArt/Effects/FlameJet, from build_flame_jet_effect.ps1) into
# /Game/FX/Effekseer/FlameJet and gives BP_FlameJet a Jet emitter at the vent: the column of fire the graph turns on
# for BurnSeconds (BP_FlameJet_EventGraph.txt), in place of the glowing Column cylinder, which is removed. The Fire
# emitter (CageFire) stays as the warning before each eruption. Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\import_flame_jet.py -unattended -nop4 -nosplash -stdout
import os

import unreal

EFFECT_DIR = "/Game/FX/Effekseer/FlameJet"
TEXTURE_DIR = EFFECT_DIR + "/Texture"
FLAME = "/Game/ThirdPerson/Blueprints/Gimmicks/Hell/BP_FlameJet"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Effects", "FlameJet")
library = unreal.EditorAssetLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def import_file(path, destination):
    # Replaced every run, so a rebuilt effect or texture comes through.
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = destination
    task.automated = True
    task.save = True
    task.replace_existing = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    asset_path = destination + "/" + os.path.splitext(os.path.basename(path))[0]
    lines.append("imported " + asset_path)
    return unreal.load_asset(asset_path)


# Textures first: the effect looks them up relative to itself when it imports.
for name in ("JetGlow", "JetPuff"):
    import_file(os.path.join(SOURCE, "Texture", name + ".png"), TEXTURE_DIR)
effect = import_file(os.path.join(SOURCE, "FlameJet.efk"), EFFECT_DIR)
lines.append("effect {} textures {}".format(effect, effect.get_editor_property("ColorTextures")))

blueprint = unreal.load_asset(FLAME)


def gather():
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_associated_object(data_library.get_data(h))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = (h, component)
    return found


root = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
components = gather()
if "Column" in components:
    subsystem.delete_subobjects(root, [components["Column"][0]], blueprint)
    lines.append("BP_FlameJet: Column removed")
    components = gather()
if "Jet" in components:
    jet = components["Jet"][1]
else:
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent"), blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("Jet"))
    jet = data_library.get_associated_object(data_library.get_data(handle))
    lines.append("BP_FlameJet: Jet added")
jet.set_editor_property("Effect", effect)
jet.set_editor_property("IsLooping", True)
jet.set_editor_property("auto_activate", False)
jet.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
library.save_asset(FLAME, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "flame_jet_import.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
