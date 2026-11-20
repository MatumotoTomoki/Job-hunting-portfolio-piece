# Sounds and effects for the toggle switch and the switch blocks (Gimmicks/Machine; the user, 2026-11-20):
#   S_SwitchClick, S_BlockForm, S_BlockVanish  from make_switch_sounds.ps1 (SourceArt/Sounds)
#   SA_Switch         full within 4 m, silent 30 m on
#   SCON_SwitchBlock  at most 4 block sounds at once (a switch flips every block in the area together), the farthest
#                     dropped
#   Effects /Game/FX/Effekseer/SwitchFx/{SwitchBurst,BlockForm,BlockVanish}{Red,Blue} (build_switch_effects.ps1)
#   BP_ToggleSwitch: ClickSound; BurstRed, BurstBlue (emitters at the button, off until played)
#   BP_SwitchBlock:  FormSound, VanishSound; FormRed, FormBlue, VanishRed, VanishBlue (emitters at the middle, their
#                    own size whatever the block's scale)
# Graphs: BP_ToggleSwitch_EventGraph.txt, BP_SwitchBlock_EventGraph.txt (Generators/gen_area2_gimmicks.ps1). Safe to
# run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_switch_effects.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine"
FX = "/Game/FX/Effekseer/SwitchFx"
PROJECT = os.path.abspath(unreal.Paths.project_dir())
SOURCE_FX = os.path.join(PROJECT, "SourceArt", "Effects", "SwitchFx")
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
          for name in ("S_SwitchClick", "S_BlockForm", "S_BlockVanish")}

path = DIR + "/SA_Switch"
if library.does_asset_exist(path):
    att = unreal.load_asset(path)
else:
    att = tools.create_asset("SA_Switch", DIR, unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
    lines.append("created " + path)
settings = att.get_editor_property("attenuation")
settings.set_editor_property("attenuation_shape_extents", unreal.Vector(400.0, 0.0, 0.0))
settings.set_editor_property("falloff_distance", 2600.0)
att.set_editor_property("attenuation", settings)
library.save_asset(path, False)

path = DIR + "/SCON_SwitchBlock"
if library.does_asset_exist(path):
    concurrency = unreal.load_asset(path)
else:
    concurrency = tools.create_asset("SCON_SwitchBlock", DIR, unreal.SoundConcurrency, unreal.SoundConcurrencyFactory())
    lines.append("created " + path)
rules = concurrency.get_editor_property("concurrency")
rules.set_editor_property("max_count", 4)
rules.set_editor_property("resolution_rule", unreal.MaxConcurrentResolutionRule.STOP_FARTHEST_THEN_OLDEST)
concurrency.set_editor_property("concurrency", rules)
library.save_asset(path, False)
for name in ("S_BlockForm", "S_BlockVanish"):
    try:
        sounds[name].set_editor_property("concurrency_set", [concurrency])
        lines.append(name + " -> SCON_SwitchBlock")
    except Exception as error:
        lines.append("{}: concurrency not set ({})".format(name, error))
    library.save_asset(DIR + "/" + name, False)

for name in ("CloudPuff", "Glint"):
    import_file(os.path.join(SOURCE_FX, "Texture", name + ".png"), FX + "/Texture")
effects = {}
for kind in ("SwitchBurst", "BlockForm", "BlockVanish"):
    for colour in ("Red", "Blue"):
        effects[kind + colour] = import_file(os.path.join(SOURCE_FX, kind + colour + ".efk"), FX)
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


def audio(bp, name, sound, z):
    a = add(bp, unreal.AudioComponent, name)
    a.set_editor_property("sound", sound)
    a.set_editor_property("auto_activate", False)
    a.set_editor_property("attenuation_settings", att)
    a.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, z))
    return a


def emitter(bp, name, effect, z):
    fx = add(bp, emitter_class, name)
    fx.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, z))
    fx.set_editor_property("Effect", effect)
    fx.set_editor_property("IsLooping", False)
    fx.set_editor_property("auto_activate", False)
    fx.set_editor_property("absolute_scale", True)
    fx.set_editor_property("relative_scale3d", unreal.Vector(1.0, 1.0, 1.0))
    return fx


# ----- BP_ToggleSwitch -----
switch = unreal.load_asset(DIR + "/BP_ToggleSwitch")
audio(switch, "ClickSound", sounds["S_SwitchClick"], 36.0)
for colour in ("Red", "Blue"):
    emitter(switch, "Burst" + colour, effects["SwitchBurst" + colour], 40.0)
pins.compile_blueprint(switch)
library.save_asset(DIR + "/BP_ToggleSwitch", False)

# ----- BP_SwitchBlock -----
block = unreal.load_asset(DIR + "/BP_SwitchBlock")
audio(block, "FormSound", sounds["S_BlockForm"], 0.0)
audio(block, "VanishSound", sounds["S_BlockVanish"], 0.0)
for kind, effect_kind in (("Form", "BlockForm"), ("Vanish", "BlockVanish")):
    for colour in ("Red", "Blue"):
        emitter(block, kind + colour, effects[effect_kind + colour], 0.0)
pins.compile_blueprint(block)
library.save_asset(DIR + "/BP_SwitchBlock", False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "switch_effects.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
