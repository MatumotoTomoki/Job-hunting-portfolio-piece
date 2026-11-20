# The spider thread's look (BP_SpiderThread, area 4; the user, 2026-11-20): a fine silver thread let down from heaven
# with glints of light running down it.
#   Gimmicks/Heaven/M_SpiderSilk  unlit: Color x Glow, plus glints - thin bright bands that travel down the thread
#       (by world height, so they look the same whatever the thread's length): GlintColor x GlintGlow x
#       saturate(sin(2 pi (Z + time x GlintSpeed) / GlintSpacing)) ^ GlintSharpness.
#   MI_ThreadSilver (the thread) and MI_ThreadFray (the red one shown as it is about to snap) are re-made on it with
#   their colours as before; nothing in the BP or its graph changes.
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_spider_silk.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
lines = []

path = DIR + "/M_SpiderSilk"
if not library.does_asset_exist(path):
    m = tools.create_asset("M_SpiderSilk", DIR, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)

    def node(kind, x, y):
        return editing.create_material_expression(m, kind, x, y)

    def param(kind, name, value, x, y):
        n = node(kind, x, y)
        n.set_editor_property("parameter_name", name)
        n.set_editor_property("default_value", value)
        return n

    def link(a, b, pin, out=""):
        editing.connect_material_expressions(a, out, b, pin)

    color = param(unreal.MaterialExpressionVectorParameter, "Color", unreal.LinearColor(0.92, 0.95, 1.0, 1.0), -900, -300)
    glow = param(unreal.MaterialExpressionScalarParameter, "Glow", 4.0, -900, -150)
    glint_color = param(unreal.MaterialExpressionVectorParameter, "GlintColor", unreal.LinearColor(1.0, 0.95, 0.8, 1.0), -900, 0)
    glint_glow = param(unreal.MaterialExpressionScalarParameter, "GlintGlow", 14.0, -900, 150)
    spacing = param(unreal.MaterialExpressionScalarParameter, "GlintSpacing", 350.0, -900, 300)
    speed = param(unreal.MaterialExpressionScalarParameter, "GlintSpeed", 180.0, -900, 400)
    sharp = param(unreal.MaterialExpressionScalarParameter, "GlintSharpness", 40.0, -900, 500)
    world = node(unreal.MaterialExpressionWorldPosition, -1100, 600)
    z = node(unreal.MaterialExpressionComponentMask, -950, 600)
    for channel, on in (("r", False), ("g", False), ("b", True), ("a", False)):
        z.set_editor_property(channel, on)
    time = node(unreal.MaterialExpressionTime, -1100, 750)
    moved = node(unreal.MaterialExpressionMultiply, -800, 750)
    height = node(unreal.MaterialExpressionAdd, -650, 650)
    phase = node(unreal.MaterialExpressionDivide, -500, 600)
    wave = node(unreal.MaterialExpressionSine, -350, 600)          # period 1: one glint every GlintSpacing cm
    wave.set_editor_property("period", 1.0)
    clamp = node(unreal.MaterialExpressionSaturate, -200, 600)
    peak = node(unreal.MaterialExpressionPower, -50, 600)
    tint = node(unreal.MaterialExpressionMultiply, -500, 50)
    glint = node(unreal.MaterialExpressionMultiply, 100, 300)
    base = node(unreal.MaterialExpressionMultiply, -600, -250)
    total = node(unreal.MaterialExpressionAdd, 250, 0)
    link(world, z, "")
    link(time, moved, "A")
    link(speed, moved, "B")
    link(z, height, "A")
    link(moved, height, "B")
    link(height, phase, "A")
    link(spacing, phase, "B")
    link(phase, wave, "")
    link(wave, clamp, "")
    link(clamp, peak, "Base")
    link(sharp, peak, "Exp")
    link(glint_color, tint, "A")
    link(glint_glow, tint, "B")
    link(tint, glint, "A")
    link(peak, glint, "B")
    link(color, base, "A")
    link(glow, base, "B")
    link(base, total, "A")
    link(glint, total, "B")
    editing.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    editing.connect_material_property(total, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.recompile_material(m)
    library.save_asset(path, False)
    lines.append("created " + path)
parent = unreal.load_asset(path)

for name, colour, glow_value, glint_colour in (("MI_ThreadSilver", (0.92, 0.95, 1.0), 4.0, (1.0, 0.95, 0.8)),
                                               ("MI_ThreadFray", (1.0, 0.25, 0.12), 5.0, (1.0, 0.6, 0.3))):
    mi = unreal.load_asset(DIR + "/" + name)
    if mi.get_editor_property("parent") != parent:
        editing.clear_all_material_instance_parameters(mi)
        editing.set_material_instance_parent(mi, parent)
        lines.append(name + " re-parented to M_SpiderSilk")
    editing.set_material_instance_vector_parameter_value(mi, "Color", unreal.LinearColor(*colour, 1.0))
    editing.set_material_instance_scalar_parameter_value(mi, "Glow", glow_value)
    editing.set_material_instance_vector_parameter_value(mi, "GlintColor", unreal.LinearColor(*glint_colour, 1.0))
    library.save_asset(DIR + "/" + name, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "spider_silk.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
