# The gears as heaven's debris (the user, 2026-11-18): SM_Gear had no UVs, so any texture came out as one flat colour
# and the "marble" gears looked plain. build_gear_blender.py now gives it UVs seen from above, and
# build_heaven_clean_textures.py paints T_HeavenGear_* for them (marble, gold band and line inside the teeth, gold
# hub ring, rims round the spoke holes, thin spokes). This script:
#   - re-imports SM_Gear (Gimmicks/Machine) over the old one: its default materials and its complex-as-simple
#     collision as setup_area2_gimmicks.py sets them;
#   - imports T_HeavenGear_C / _N / _E and makes /Game/Art/HeavenDebris/MI_HeavenGearClean (M_HeavenDebris, Glow 1);
#   - BP_SpinGear's Wheel: MI_HeavenGearClean, MI_HeavenGold, MI_MachineShadow.
# Area 2's Great Gear (per actor in the level) gets it from setup_heaven_tier_platforms.py --area2.
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_heaven_gear.py -unattended -nop4 -nosplash -stdout
import os

import unreal

MACHINE = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine"
DIR = "/Game/Art/HeavenDebris"
TEX_DIR = DIR + "/Textures"
PROJECT = os.path.abspath(unreal.Paths.project_dir())
GEAR_FBX = os.path.join(PROJECT, "SourceArt", "Models", "Gear", "SM_Gear.fbx")
TEX_SOURCE = os.path.join(PROJECT, "SourceArt", "Models", "HeavenDebris", "Textures")

unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def import_task(path, destination, options=None):
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = destination
    task.automated = True
    task.save = True
    task.replace_existing = True
    if options:
        task.options = options
    tools.import_asset_tasks([task])


# ----- the gear mesh, now with UVs -----
options = unreal.FbxImportUI()
options.set_editor_property("import_materials", False)
options.set_editor_property("import_textures", False)
import_task(GEAR_FBX, MACHINE, options)
gear = unreal.load_asset(MACHINE + "/SM_Gear")
iron, brass, shadow = (unreal.load_asset(MACHINE + "/" + n) for n in ("MI_MachineIron", "MI_MachineBrass", "MI_MachineShadow"))
for slot, material in enumerate((iron, brass, shadow)):
    gear.set_material(slot, material)
gear.get_editor_property("body_setup").set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
library.save_asset(MACHINE + "/SM_Gear", False)
try:
    channels = unreal.EditorStaticMeshLibrary.get_num_uv_channels(gear, 0)
except Exception as error:
    channels = "unknown ({})".format(error)
lines.append("SM_Gear re-imported, UV channels {}".format(channels))

# ----- textures and the material -----
textures = {}
for suffix in ("C", "N", "E"):
    name = "T_HeavenGear_" + suffix
    import_task(os.path.join(TEX_SOURCE, name + ".png"), TEX_DIR)
    texture = unreal.load_asset(TEX_DIR + "/" + name)
    if suffix == "N":
        texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
        texture.set_editor_property("srgb", False)
    elif suffix == "E":
        texture.set_editor_property("srgb", False)
    library.save_asset(TEX_DIR + "/" + name, False)
    textures[suffix] = texture
path = DIR + "/MI_HeavenGearClean"
if library.does_asset_exist(path):
    mi = unreal.load_asset(path)
else:
    mi = tools.create_asset("MI_HeavenGearClean", DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(mi, unreal.load_asset("/Game/Art/Ruins/M_HeavenDebris"))
    lines.append("created " + path)
editing.set_material_instance_texture_parameter_value(mi, "Color", textures["C"])
editing.set_material_instance_texture_parameter_value(mi, "Normal", textures["N"])
editing.set_material_instance_texture_parameter_value(mi, "Mask", textures["E"])
editing.set_material_instance_vector_parameter_value(mi, "GoldColor", unreal.LinearColor(1.0, 0.7, 0.3, 1.0))
editing.set_material_instance_scalar_parameter_value(mi, "Glow", 1.0)
editing.set_material_instance_scalar_parameter_value(mi, "Roughness", 0.3)
library.save_asset(path, False)

# ----- BP_SpinGear -----
spin = unreal.load_asset(MACHINE + "/BP_SpinGear")
gold = unreal.load_asset(DIR + "/MI_HeavenGold")
for handle in subsystem.k2_gather_subobject_data_for_blueprint(spin):
    component = data_library.get_associated_object(data_library.get_data(handle))
    if component is not None and component.get_name().replace("_GEN_VARIABLE", "") == "Wheel":
        for slot, material in enumerate((mi, gold, shadow)):
            component.set_material(slot, material)
        lines.append("BP_SpinGear Wheel: MI_HeavenGearClean, MI_HeavenGold, MI_MachineShadow")
unreal.BlueprintEditorLibrary.compile_blueprint(spin)
library.save_asset(MACHINE + "/BP_SpinGear", False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "heaven_gear.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
