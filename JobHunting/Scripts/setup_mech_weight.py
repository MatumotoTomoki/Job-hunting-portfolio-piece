# More weight for the big mechanisms as they move (BP_Mechanism; the user, 2026-11-20), on top of setup_lever_sounds.py:
#   CS_MechRumble  a small camera shake (0.6 s), played again and again while parts move - near the player only
#   CS_MechThud    a short knock (0.35 s) as a part comes to rest
#   (LegacyCameraShake Blueprints in Gimmicks/Area; the graph plays them with PlayWorldCameraShake, so the shake fades
#   with the distance from the moving part.)
#   Effects /Game/FX/Effekseer/MechDust (build_mech_dust_effect.ps1): MechDust (loops) and MechThud (one shot)
#   BP_Mechanism: MoveFx (MechDust, off until it moves), StopFx (MechThud), both at world scale 1
#   BP_MyGameInstance: MechShakeAt - the game time the next rumble shake may play, shared by every part, so twelve
#   steps moving at once shake no harder than one.
# Graph: BP_Mechanism_EventGraph.txt (Generators/gen_area_foundation.ps1). Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_mech_weight.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
FX = "/Game/FX/Effekseer/MechDust"
GI = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
PROJECT = os.path.abspath(unreal.Paths.project_dir())
FX_SCALE = 2.5        # the dust drawn 2.5x (the user, 2026-11-20: too small at 1)
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


def oscillator(amplitude, frequency):
    o = unreal.FOscillator()
    o.set_editor_property("amplitude", amplitude)
    o.set_editor_property("frequency", frequency)
    return o


def shake(name, duration, blend_in, blend_out, pitch, yaw, up):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        bp = unreal.load_asset(path)
    else:
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", unreal.LegacyCameraShake)
        bp = tools.create_asset(name, DIR, unreal.Blueprint, factory)
        lines.append("created " + path)
    pins.compile_blueprint(bp)
    cdo = unreal.get_default_object(bp.generated_class())
    cdo.set_editor_property("oscillation_duration", duration)
    cdo.set_editor_property("oscillation_blend_in_time", blend_in)
    cdo.set_editor_property("oscillation_blend_out_time", blend_out)
    rot = unreal.ROscillator()
    rot.set_editor_property("pitch", oscillator(*pitch))
    rot.set_editor_property("yaw", oscillator(*yaw))
    cdo.set_editor_property("rot_oscillation", rot)
    loc = unreal.VOscillator()
    loc.set_editor_property("z", oscillator(*up))
    cdo.set_editor_property("loc_oscillation", loc)
    library.save_asset(path, False)
    return bp


shake("CS_MechRumble", 0.6, 0.1, 0.3, (0.35, 22.0), (0.25, 17.0), (1.2, 28.0))
shake("CS_MechThud", 0.35, 0.02, 0.25, (1.1, 30.0), (0.3, 24.0), (3.5, 34.0))

import_file(os.path.join(PROJECT, "SourceArt", "Effects", "MechDust", "Texture", "CloudPuff.png"), FX + "/Texture")
dust = import_file(os.path.join(PROJECT, "SourceArt", "Effects", "MechDust", "MechDust.efk"), FX)
thud = import_file(os.path.join(PROJECT, "SourceArt", "Effects", "MechDust", "MechThud.efk"), FX)

# ----- BP_Mechanism -----
bp = unreal.load_asset(DIR + "/BP_Mechanism")
emitter_class = unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent")
found = {}
for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
    c = data_library.get_associated_object(data_library.get_data(h))
    if c is not None:
        found[c.get_name().replace("_GEN_VARIABLE", "")] = (h, c)
root = found["DefaultSceneRoot"][0] if "DefaultSceneRoot" in found else subsystem.k2_gather_subobject_data_for_blueprint(bp)[0]
for name, effect, looping in (("MoveFx", dust, True), ("StopFx", thud, False)):
    if name in found:
        fx = found[name][1]
    else:
        handle, _ = subsystem.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=emitter_class, blueprint_context=bp))
        subsystem.rename_subobject(handle, unreal.Text(name))
        fx = data_library.get_associated_object(data_library.get_data(handle))
        lines.append("BP_Mechanism: component " + name)
    fx.set_editor_property("Effect", effect)
    fx.set_editor_property("IsLooping", looping)
    fx.set_editor_property("auto_activate", False)
    fx.set_editor_property("absolute_scale", True)
    fx.set_editor_property("relative_scale3d", unreal.Vector(FX_SCALE, FX_SCALE, FX_SCALE))
pins.compile_blueprint(bp)
library.save_asset(DIR + "/BP_Mechanism", False)

# ----- the shared shake clock -----
gi = unreal.load_asset(GI)
try:
    unreal.get_default_object(gi.generated_class()).get_editor_property("MechShakeAt")
except Exception:
    if not pins.add_member_variable(gi, "MechShakeAt", pins.get_basic_type_by_name("real")):
        raise RuntimeError("Could not add MechShakeAt")
    lines.append("BP_MyGameInstance: variable MechShakeAt")
    pins.compile_blueprint(gi)
    library.save_asset(GI, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "mech_weight.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
