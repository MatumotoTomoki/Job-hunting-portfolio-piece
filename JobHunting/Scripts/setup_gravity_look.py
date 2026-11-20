# The gravity zone's look (BP_GravityZone, area 4; the user, 2026-11-20): the faint violet box was hard to see and
# didn't say "up is down here". M_GravityFlow, two-sided translucent unlit:
#   a violet haze (Color, Opacity) with streaks of light flowing UP its faces - Sky's T_WindStreak laid along world
#   height (so they are long and upright) and scrolled up by Speed tiles a second; StreakOpacity, StreakGlow; the
#   pattern is TileSize cm across, the same whatever the zone's size.
# MI_GravityField (on every zone's Field) is re-made on it; nothing in the BP or its graph changes.
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_gravity_look.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
STREAK = "/Game/ThirdPerson/Blueprints/Gimmicks/Sky/T_WindStreak"
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
lines = []

path = DIR + "/M_GravityFlow"
if not library.does_asset_exist(path):
    m = tools.create_asset("M_GravityFlow", DIR, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("two_sided", True)

    def node(kind, x, y):
        return editing.create_material_expression(m, kind, x, y)

    def param(kind, name, value, x, y):
        n = node(kind, x, y)
        n.set_editor_property("parameter_name", name)
        n.set_editor_property("default_value", value)
        return n

    def mask(x, y, channels):
        n = node(unreal.MaterialExpressionComponentMask, x, y)
        for channel in ("r", "g", "b", "a"):
            n.set_editor_property(channel, channel in channels)
        return n

    def link(a, b, pin, out=""):
        editing.connect_material_expressions(a, out, b, pin)

    color = param(unreal.MaterialExpressionVectorParameter, "Color", unreal.LinearColor(0.6, 0.35, 1.0, 1.0), -900, -300)
    opacity = param(unreal.MaterialExpressionScalarParameter, "Opacity", 0.12, -900, -150)
    streak_opacity = param(unreal.MaterialExpressionScalarParameter, "StreakOpacity", 0.4, -900, -50)
    streak_glow = param(unreal.MaterialExpressionScalarParameter, "StreakGlow", 3.0, -900, 50)
    tile = param(unreal.MaterialExpressionScalarParameter, "TileSize", 300.0, -1300, 400)
    speed = param(unreal.MaterialExpressionScalarParameter, "Speed", 0.5, -1300, 650)
    world = node(unreal.MaterialExpressionWorldPosition, -1500, 250)
    across_xy = mask(-1300, 200, "rg")
    across = node(unreal.MaterialExpressionDotProduct, -1150, 200)      # x + y: along any side of the box
    ones = node(unreal.MaterialExpressionConstant2Vector, -1300, 300)
    ones.set_editor_property("r", 1.0)
    ones.set_editor_property("g", 1.0)
    height = mask(-1300, 500, "b")
    time = node(unreal.MaterialExpressionTime, -1300, 750)
    across_tiles = node(unreal.MaterialExpressionDivide, -1000, 250)
    height_tiles = node(unreal.MaterialExpressionDivide, -1000, 500)
    scroll = node(unreal.MaterialExpressionMultiply, -1000, 700)
    upward = node(unreal.MaterialExpressionSubtract, -850, 550)
    uv = node(unreal.MaterialExpressionAppendVector, -700, 400)          # texture U along height: the streaks stand up
    sample = node(unreal.MaterialExpressionTextureSample, -550, 400)
    sample.set_editor_property("texture", unreal.load_asset(STREAK))
    lit = node(unreal.MaterialExpressionMultiply, -350, 300)
    one = node(unreal.MaterialExpressionConstant, -350, 150)
    one.set_editor_property("r", 1.0)
    brighten = node(unreal.MaterialExpressionAdd, -200, 200)
    emissive = node(unreal.MaterialExpressionMultiply, -50, 0)
    see = node(unreal.MaterialExpressionMultiply, -350, 500)
    alpha = node(unreal.MaterialExpressionAdd, -200, 450)
    link(world, across_xy, "")
    link(across_xy, across, "A")
    link(ones, across, "B")
    link(world, height, "")
    link(across, across_tiles, "A")
    link(tile, across_tiles, "B")
    link(height, height_tiles, "A")
    link(tile, height_tiles, "B")
    link(time, scroll, "A")
    link(speed, scroll, "B")
    link(height_tiles, upward, "A")
    link(scroll, upward, "B")
    link(upward, uv, "A")
    link(across_tiles, uv, "B")
    link(uv, sample, "UVs")
    editing.connect_material_expressions(sample, "A", lit, "A")
    link(streak_glow, lit, "B")
    link(one, brighten, "A")
    link(lit, brighten, "B")
    link(color, emissive, "A")
    link(brighten, emissive, "B")
    editing.connect_material_expressions(sample, "A", see, "A")
    link(streak_opacity, see, "B")
    link(opacity, alpha, "A")
    link(see, alpha, "B")
    editing.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.connect_material_property(alpha, "", unreal.MaterialProperty.MP_OPACITY)
    editing.recompile_material(m)
    library.save_asset(path, False)
    lines.append("created " + path)

mi = unreal.load_asset(DIR + "/MI_GravityField")
parent = unreal.load_asset(path)
if mi.get_editor_property("parent") != parent:
    editing.clear_all_material_instance_parameters(mi)
    editing.set_material_instance_parent(mi, parent)
    lines.append("MI_GravityField re-parented to M_GravityFlow")
library.save_asset(DIR + "/MI_GravityField", False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "gravity_look.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
