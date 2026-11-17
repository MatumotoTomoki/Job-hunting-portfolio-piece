# The platforms get cleaner area by area (the user, 2026-11-17): moving, falling and timed platforms wear heaven's
# debris in four steps, set per actor in each area's level:
#   area 1  MI_HeavenDebris (worn; import_ruins_art.py)      area 3  MI_HeavenPure (whiter, more inlay)
#   area 2  MI_HeavenClean  (setup_heaven_clean_debris.py)    area 4  MI_HeavenHoly (almost new, a medallion, glowing)
# Textures from build_heaven_clean_textures.py; material M_HeavenDebris (its Fade keeps the timed platforms fading).
# This script: the area 3 and 4 textures and MIs, and LV_Area3_Sky / LV_Area4_Heaven. Area 2's level is dressed by
# the same script with --area2 (only when nothing else is working on LV_Area2_Tower). Safe to run again. Editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript "-script=<full path>\setup_heaven_tier_platforms.py [--area2]" -unattended -nop4 -nosplash -stdout
import glob
import os
import sys

import unreal

DIR = "/Game/Art/HeavenDebris"
TEX_DIR = DIR + "/Textures"
PARENT = "/Game/Art/Ruins/M_HeavenDebris"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "HeavenDebris", "Textures")
CLASSES = ("BP_MovingPlatform_C", "BP_FallingFloor_C", "BP_TimedPlatform_C")
LEVELS = [("/Game/LV_Area3_Sky", "MI_HeavenPure"), ("/Game/LV_Area4_Heaven", "MI_HeavenHoly")]
if "--area2" in " ".join(sys.argv):
    LEVELS.insert(0, ("/Game/LV_Area2_Tower", "MI_HeavenClean"))

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
lines = []

textures = {}
for path in sorted(glob.glob(os.path.join(SOURCE, "T_Heaven*.png"))):
    name = os.path.splitext(os.path.basename(path))[0]
    if not (name.startswith("T_HeavenPure") or name.startswith("T_HeavenHoly")) and library.does_asset_exist(TEX_DIR + "/" + name):
        textures[name] = unreal.load_asset(TEX_DIR + "/" + name)
        continue
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
    lines.append("imported " + name)

parent = unreal.load_asset(PARENT)
looks = {}
for name, tex, glow, rough, gold in (("MI_HeavenPure", "Pure", 0.9, 0.25, (1.0, 0.72, 0.32)),
                                     ("MI_HeavenHoly", "Holy", 1.1, 0.2, (1.0, 0.78, 0.4))):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        mi = unreal.load_asset(path)
    else:
        mi = tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        editing.set_material_instance_parent(mi, parent)
        lines.append("created " + path)
    editing.set_material_instance_texture_parameter_value(mi, "Color", textures["T_Heaven" + tex + "_C"])
    editing.set_material_instance_texture_parameter_value(mi, "Normal", textures["T_Heaven" + tex + "_N"])
    editing.set_material_instance_texture_parameter_value(mi, "Mask", textures["T_Heaven" + tex + "_E"])
    editing.set_material_instance_vector_parameter_value(mi, "GoldColor", unreal.LinearColor(gold[0], gold[1], gold[2], 1.0))
    editing.set_material_instance_scalar_parameter_value(mi, "Glow", glow)
    editing.set_material_instance_scalar_parameter_value(mi, "Roughness", rough)
    library.save_asset(path, False)
    looks[name] = mi
looks["MI_HeavenClean"] = unreal.load_asset(DIR + "/MI_HeavenClean")
# Area 2's big mechanism (the drawer steps and the Great Gear on the spire): the showpiece, so its inlay glows a little
# more, as area 1's giant steps do (MI_HeavenDebrisBright). The gear is dressed like BP_SpinGear: marble, gold, shadow.
bright_path = DIR + "/MI_HeavenCleanBright"
if library.does_asset_exist(bright_path):
    bright = unreal.load_asset(bright_path)
else:
    bright = tools.create_asset("MI_HeavenCleanBright", DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(bright, looks["MI_HeavenClean"])
    lines.append("created " + bright_path)
editing.set_material_instance_scalar_parameter_value(bright, "Glow", 2.0)
library.save_asset(bright_path, False)
# Levers (and pressure plates, which are levers with the handle hidden): the base in the area's step, the handle gold,
# the knob a softly glowing gold so it reads as the thing to touch.
knob_path = DIR + "/MI_HeavenGoldGlow"
if library.does_asset_exist(knob_path):
    knob = unreal.load_asset(knob_path)
else:
    knob = tools.create_asset("MI_HeavenGoldGlow", DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(knob, unreal.load_asset(DIR + "/MI_HeavenGold"))
    lines.append("created " + knob_path)
editing.set_material_instance_scalar_parameter_value(knob, "Glow", 1.0)
library.save_asset(knob_path, False)
GOLD_LOOK = unreal.load_asset(DIR + "/MI_HeavenGold")
GEAR_LOOK = [unreal.load_asset(DIR + "/MI_HeavenMarble"), unreal.load_asset(DIR + "/MI_HeavenGold"),
             unreal.load_asset("/Game/ThirdPerson/Blueprints/Gimmicks/Machine/MI_MachineShadow")]

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for level_path, look_name in LEVELS:
    if not level.load_level(level_path):
        raise RuntimeError("Could not open " + level_path)
    look = looks[look_name]
    dressed = 0
    for actor in actors.get_all_level_actors():
        if actor.get_class().get_name() not in CLASSES:
            continue
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            if component.get_editor_property("static_mesh") is None:
                continue
            for i in range(component.get_num_materials()):
                component.set_material(i, look)
        dressed += 1
    levers = 0
    for actor in actors.get_all_level_actors():
        if actor.get_class().get_name() != "BP_Lever_C":
            continue
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            part = component.get_name()
            component.set_material(0, GOLD_LOOK if part.startswith("Handle") else knob if part.startswith("Knob") else look)
        levers += 1
    lines.append("   {} levers".format(levers))
    if level_path.endswith("LV_Area2_Tower"):
        steps = 0
        for actor in actors.get_all_level_actors():
            if actor.get_class().get_name() != "BP_Mechanism_C":
                continue
            label = actor.get_actor_label()
            for component in actor.get_components_by_class(unreal.StaticMeshComponent):
                if "Drawer Step" in label:
                    component.set_material(0, bright)
                    steps += 1
                elif "Great Gear" in label:
                    for slot, material in enumerate(GEAR_LOOK[:component.get_num_materials()]):
                        component.set_material(slot, material)
                    lines.append("   Great Gear dressed: " + label)
        lines.append("   {} drawer steps -> MI_HeavenCleanBright".format(steps))
    lines.append("{}: {} platforms -> {} (saved {})".format(level_path, dressed, look_name, level.save_current_level()))
    # Check it stuck.
    level.load_level(level_path)
    for actor in actors.get_all_level_actors():
        if actor.get_class().get_name() in CLASSES:
            material = actor.get_components_by_class(unreal.StaticMeshComponent)[0].get_material(0)
            lines.append("   after reload {}: {}".format(actor.get_actor_label(), material.get_name() if material else None))
            break

with open(os.path.join(unreal.Paths.project_saved_dir(), "heaven_tier_platforms.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
