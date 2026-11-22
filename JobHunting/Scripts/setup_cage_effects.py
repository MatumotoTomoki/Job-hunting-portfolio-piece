# Sounds and effect for the heaven-or-hell birdcage (BP_BirdcageDoor_Blender, Prototype/Birdcage; the user, 2026-11-22):
#   S_CageCreak, S_CageLock, S_CageRise, S_CageLand  from make_cage_sounds.ps1 (SourceArt/Sounds), next to the cage
#   SA_Cage   full within 5 m, silent 30 m on
#   Effect /Game/FX/Effekseer/CageFx/CageLand (build_cage_effects.ps1)
#   BP_BirdcageDoor_Blender: DoorSound (the creak), LockSound, RiseSound, LandSound, LandFx at its base (they travel
#                            with the cage to its destination)
# Graph: BP_BirdcageDoor_Blender_EventGraph.txt (Generators/gen_hell_cage.ps1). Safe to run again. Run it in the
# editor's Output Log (Python):
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\setup_cage_effects.py', encoding='utf-8').read())
import os

import unreal

DIR = "/Game/Prototype/Birdcage"
FX = "/Game/FX/Effekseer/CageFx"
FX_SCALE = 1.0
PROJECT = os.path.abspath(unreal.Paths.project_dir())
SOURCE_FX = os.path.join(PROJECT, "SourceArt", "Effects", "CageFx")
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
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
          for name in ("S_CageCreak", "S_CageLock", "S_CageRise", "S_CageLand")}

path = DIR + "/SA_Cage"
if library.does_asset_exist(path):
    att = unreal.load_asset(path)
else:
    att = tools.create_asset("SA_Cage", DIR, unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
    lines.append("created " + path)
settings = att.get_editor_property("attenuation")
settings.set_editor_property("attenuation_shape_extents", unreal.Vector(500.0, 0.0, 0.0))
settings.set_editor_property("falloff_distance", 2500.0)
att.set_editor_property("attenuation", settings)
library.save_asset(path, False)

import_file(os.path.join(SOURCE_FX, "Texture", "CloudPuff.png"), FX + "/Texture")
land_fx = import_file(os.path.join(SOURCE_FX, "CageLand.efk"), FX)
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


bp = unreal.load_asset(DIR + "/BP_BirdcageDoor_Blender")
for name, sound in (("DoorSound", "S_CageCreak"), ("LockSound", "S_CageLock"), ("RiseSound", "S_CageRise"),
                    ("LandSound", "S_CageLand")):
    a = add(bp, unreal.AudioComponent, name)
    a.set_editor_property("sound", sounds[sound])
    a.set_editor_property("auto_activate", False)
    a.set_editor_property("attenuation_settings", att)
fx = add(bp, emitter_class, "LandFx")
fx.set_editor_property("Effect", land_fx)
fx.set_editor_property("IsLooping", False)
fx.set_editor_property("auto_activate", False)
fx.set_editor_property("absolute_scale", True)
fx.set_editor_property("relative_scale3d", unreal.Vector(FX_SCALE, FX_SCALE, FX_SCALE))
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
library.save_asset(DIR + "/BP_BirdcageDoor_Blender", False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "cage_effects.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
