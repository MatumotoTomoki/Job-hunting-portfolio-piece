# Imports the gear exit's effects (SourceArt/Effects/GearSteam, from build_gear_steam_effect.ps1) into
# /Game/FX/Effekseer/GearSteam (textures in Texture/ under it: Effekseer looks them up relative to the effect) and puts
# two emitters on BP_GearExit's Lift, at the middle of the gear's thickness, both off until the graph starts them:
#   SteamBurst  GearSteamBurst, once, as the player steps on the ring
#   RiseFx      GearRise, looping, from the moment the gear starts to rise (StartDelay later)
# The level needs BP_EffekseerSystem (LV_Area1_Ruins has one). The effects are re-imported every run, so a rebuilt
# .efk comes through. Graph: BP_GearExit_EventGraph.txt (gen_gear_exit.ps1). Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_gear_effects.py -unattended -nop4 -nosplash -stdout
import os

import unreal

EFFECT_DIR = "/Game/FX/Effekseer/GearSteam"
TEXTURE_DIR = EFFECT_DIR + "/Texture"
GEAR_EXIT = "/Game/ThirdPerson/Blueprints/Gimmicks/Area/BP_GearExit"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Effects", "GearSteam")
GEAR_MIDDLE = 22.5   # setup_gear_exit.py: GEAR_HALF
library = unreal.EditorAssetLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def import_file(path, destination, replace=False):
    asset_path = destination + "/" + os.path.splitext(os.path.basename(path))[0]
    if library.does_asset_exist(asset_path) and not replace:
        return unreal.load_asset(asset_path)
    if not os.path.isfile(path):
        raise RuntimeError("Missing " + path + "; run build_gear_steam_effect.ps1 first")
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = destination
    task.automated = True
    task.save = True
    task.replace_existing = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    lines.append("imported " + asset_path)
    return unreal.load_asset(asset_path)


for name in ("SteamPuff", "Spark"):
    import_file(os.path.join(SOURCE, "Texture", name + ".png"), TEXTURE_DIR)
effects = {}
for name in ("GearSteamBurst", "GearRise"):
    effects[name] = import_file(os.path.join(SOURCE, name + ".efk"), EFFECT_DIR, replace=True)
    lines.append("{} textures {}".format(name, effects[name].get_editor_property("ColorTextures")))

blueprint = unreal.load_asset(GEAR_EXIT)
if blueprint is None:
    raise RuntimeError(GEAR_EXIT + " not found; run setup_gear_exit.py first")


def gather():
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_associated_object(data_library.get_data(h))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = (h, component)
    return found


emitter_class = unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent")
root_handle = gather()["DefaultSceneRoot"][0]   # (the first gathered handle is the actor itself, not a scene parent)
# RiseFx: the sparks, where the axle rubs out of the floor; on the root, so it stays at floor level.
for name, effect_name, looping, parent, z in (("SteamBurst", "GearSteamBurst", False, "Lift", GEAR_MIDDLE),
                                              ("RiseFx", "GearRise", True, None, 2.0)):
    components = gather()
    parent_handle = components[parent][0] if parent else root_handle
    if name in components:
        emitter = components[name][1]
        # (Templates carry no attach parent to compare, so it is just put under the right parent every run.)
        # (reparent_subobject returned False and left it where it was; attach_subobject moves it.)
        moved = subsystem.attach_subobject(parent_handle, components[name][0])
        lines.append("BP_GearExit: {} under {} ({})".format(name, parent or "the root", moved))
    else:
        params = unreal.AddNewSubobjectParams(parent_handle=parent_handle, new_class=emitter_class, blueprint_context=blueprint)
        handle, _ = subsystem.add_new_subobject(params)
        if not data_library.is_handle_valid(handle):
            raise RuntimeError("Could not add " + name)
        subsystem.rename_subobject(handle, unreal.Text(name))
        emitter = data_library.get_associated_object(data_library.get_data(handle))
        lines.append("BP_GearExit: " + name + " added")
    emitter.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, z))
    emitter.set_editor_property("relative_scale3d", unreal.Vector(1.0, 1.0, 1.0))
    emitter.set_editor_property("Effect", effects[effect_name])
    emitter.set_editor_property("IsLooping", looping)
    emitter.set_editor_property("auto_activate", False)
unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
library.save_asset(GEAR_EXIT, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "gear_effects.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
