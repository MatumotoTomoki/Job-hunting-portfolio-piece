# Area 2's gimmicks as "cleaner heaven's debris" (the user, 2026-11-17: heaven's debris like area 1's, a little more
# beautiful). The textures come from build_heaven_clean_textures.py (SourceArt/Models/HeavenDebris/Textures); the
# material is area 1's M_HeavenDebris (/Game/Art/Ruins: Color, Normal, Mask x GoldColor x Glow, Roughness, Fade).
# The level LV_Area2_Tower is NOT touched (another session is rebuilding its art): only assets change.
#   /Game/Art/HeavenDebris: the textures, and
#     MI_HeavenClean   polished marble, gold inlay glowing softly      MI_HeavenMarble  marble alone (no inlay)
#     MI_HeavenGold    brushed gold, a faint glow all over
#   MI_SwitchRed / MI_SwitchBlue (Gimmicks/Machine) are re-made on M_HeavenDebris: marble with the inlay glowing red
#     or blue. They are used only by the red/blue switch blocks' solid part and the switches' buttons, in every level
#     (the build scripts set them per block), so all red/blue blocks change, areas 2 and 4 and LV_Debug alike.
#   Blueprint defaults (no level overrides them): BP_ToggleSwitch base -> clean; BP_SpinGear wheel -> marble, gold hub,
#     shadow; BP_Gondola floor and roof -> clean, posts and hanger -> gold.
# Not here yet: the moving/falling/timed platforms and the lever (also in area 3), and area 2's brass mechanism steps
# and great gear (their materials are set per actor in the level).
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_heaven_clean_debris.py -unattended -nop4 -nosplash -stdout
import glob
import os

import unreal

DIR = "/Game/Art/HeavenDebris"
TEX_DIR = DIR + "/Textures"
MACHINE = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine"
PARENT = "/Game/Art/Ruins/M_HeavenDebris"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "HeavenDebris", "Textures")
GOLD = unreal.LinearColor(1.0, 0.7, 0.3, 1.0)
RED = unreal.LinearColor(1.0, 0.1, 0.06, 1.0)
BLUE = unreal.LinearColor(0.08, 0.32, 1.0, 1.0)

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

# ----- textures -----
textures = {}
for path in sorted(glob.glob(os.path.join(SOURCE, "T_Heaven*.png"))):
    name = os.path.splitext(os.path.basename(path))[0]
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = TEX_DIR
    task.automated = True
    task.save = True
    task.replace_existing = True
    tools.import_asset_tasks([task])
    texture = unreal.load_asset(TEX_DIR + "/" + name)
    if name.endswith("_N"):
        texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
        texture.set_editor_property("srgb", False)
    elif name.endswith("_E"):
        texture.set_editor_property("srgb", False)
    library.save_asset(TEX_DIR + "/" + name, False)
    textures[name] = texture
lines.append("{} textures".format(len(textures)))

# The gear mesh is Nanite: a masked material on it needs the Nanite usage.
parent = unreal.load_asset(PARENT)
if parent is None:
    raise RuntimeError(PARENT + " missing; run import_ruins_art.py first")
if not parent.get_editor_property("used_with_nanite"):
    parent.set_editor_property("used_with_nanite", True)
    editing.recompile_material(parent)
    library.save_asset(PARENT, False)
    lines.append("M_HeavenDebris: used with Nanite")


def make(path, color, normal, mask, glow_color, glow, roughness):
    if library.does_asset_exist(path):
        mi = unreal.load_asset(path)
    else:
        folder, name = path.rsplit("/", 1)
        mi = tools.create_asset(name, folder, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        lines.append("created " + path)
    if mi.get_editor_property("parent") != parent:
        editing.clear_all_material_instance_parameters(mi)   # (old parameters of another parent)
        editing.set_material_instance_parent(mi, parent)
        lines.append("re-parented " + path)
    editing.set_material_instance_texture_parameter_value(mi, "Color", textures[color])
    editing.set_material_instance_texture_parameter_value(mi, "Normal", textures[normal])
    editing.set_material_instance_texture_parameter_value(mi, "Mask", textures[mask])
    editing.set_material_instance_vector_parameter_value(mi, "GoldColor", glow_color)
    editing.set_material_instance_scalar_parameter_value(mi, "Glow", glow)
    editing.set_material_instance_scalar_parameter_value(mi, "Roughness", roughness)
    library.save_asset(path, False)
    return mi


clean = make(DIR + "/MI_HeavenClean", "T_HeavenClean_C", "T_HeavenClean_N", "T_HeavenClean_E", GOLD, 1.0, 0.3)
marble = make(DIR + "/MI_HeavenMarble", "T_HeavenMarble_C", "T_HeavenMarble_N", "T_HeavenBlack_E", GOLD, 0.0, 0.3)
gold = make(DIR + "/MI_HeavenGold", "T_HeavenGold_C", "T_HeavenMarble_N", "T_HeavenWhite_E", GOLD, 0.15, 0.25)
make(MACHINE + "/MI_SwitchRed", "T_HeavenTint_C", "T_HeavenClean_N", "T_HeavenClean_E", RED, 2.5, 0.3)
make(MACHINE + "/MI_SwitchBlue", "T_HeavenTint_C", "T_HeavenClean_N", "T_HeavenClean_E", BLUE, 2.5, 0.3)

# ----- Blueprint defaults -----
shadow = unreal.load_asset(MACHINE + "/MI_MachineShadow")
LOOKS = {
    "BP_ToggleSwitch": {"Base": [clean]},
    "BP_SpinGear": {"Wheel": [marble, gold, shadow]},
    "BP_Gondola": {"Floor": [clean], "Roof": [clean], "Post1": [gold], "Post2": [gold], "Post3": [gold], "Post4": [gold],
                   "Hanger": [gold]},
}
for name, parts in LOOKS.items():
    path = MACHINE + "/" + name
    blueprint = unreal.load_asset(path)
    done = []
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_associated_object(data_library.get_data(handle))
        if component is None:
            continue
        key = component.get_name().replace("_GEN_VARIABLE", "")
        if key in parts:
            for slot, material in enumerate(parts[key]):
                component.set_material(slot, material)
            done.append(key)
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    library.save_asset(path, False)
    lines.append("{}: {}".format(name, ", ".join(sorted(set(done)))))

with open(os.path.join(unreal.Paths.project_saved_dir(), "heaven_clean_debris.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
