# The heaven area's (area 4) looks, in /Game/ThirdPerson/Blueprints/Gimmicks/Heaven:
#   MI_HeavenMarble, MI_HeavenStone, MI_HeavenDarkStone, MI_HeavenSky   flat colours (M_FlatCol)
#   MI_HeavenGlow, MI_HeavenSeal                                         glowing (Hell's M_HellGlow: Color x Glow)
#   M_LightShaft, MI_LightShaft   a shaft of light for a cylinder: additive and unlit, brightest at the top and fading
#                                 to nothing at the bottom and at the edges (Color, Intensity)
# No new blueprints: area 4 reuses the gimmicks of areas 1-3. Safe to run again (existing assets are kept). With the
# editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_area4_assets.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
FLAT_COLOR = "/Game/LevelPrototyping/Materials/M_FlatCol"
GLOW = "/Game/ThirdPerson/Blueprints/Gimmicks/Hell/M_HellGlow"

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
lines = []


def instance(name, parent, vectors=(), scalars=()):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        lines.append("kept " + path)
        return unreal.load_asset(path)
    made = tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(made, unreal.load_asset(parent))
    for key, color in vectors:
        editing.set_material_instance_vector_parameter_value(made, key, unreal.LinearColor(color[0], color[1], color[2], 1.0))
    for key, value in scalars:
        editing.set_material_instance_scalar_parameter_value(made, key, value)
    library.save_asset(path, False)
    lines.append("created " + path)
    return made


instance("MI_HeavenMarble", FLAT_COLOR, [("Base Color", (0.95, 0.93, 0.88))])
instance("MI_HeavenStone", FLAT_COLOR, [("Base Color", (0.28, 0.27, 0.31))])
instance("MI_HeavenDarkStone", FLAT_COLOR, [("Base Color", (0.12, 0.12, 0.15))])
instance("MI_HeavenSky", FLAT_COLOR, [("Base Color", (0.35, 0.62, 1.0))])
instance("MI_HeavenGlow", GLOW, [("Color", (1.0, 0.86, 0.55))], [("Glow", 6.0)])
instance("MI_HeavenSeal", GLOW, [("Color", (0.45, 0.75, 1.0))], [("Glow", 4.0)])

# ----- M_LightShaft -----
path = DIR + "/M_LightShaft"
if not library.does_asset_exist(path):
    material = tools.create_asset("M_LightShaft", DIR, unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    material.set_editor_property("two_sided", False)

    def node(kind, x, y):
        return editing.create_material_expression(material, kind, x, y)

    # Height in the shaft, 0 at the bottom to 1 at the top: (pixel z - object z) / object height + 0.5.
    world = node(unreal.MaterialExpressionWorldPosition, -1600, 0)
    origin = node(unreal.MaterialExpressionObjectPositionWS, -1600, 150)
    offset = node(unreal.MaterialExpressionSubtract, -1400, 50)
    offset_z = node(unreal.MaterialExpressionComponentMask, -1250, 50)
    bounds = node(unreal.MaterialExpressionObjectBounds, -1600, 300)
    bounds_z = node(unreal.MaterialExpressionComponentMask, -1400, 300)
    for mask in (offset_z, bounds_z):
        for channel, on in (("r", False), ("g", False), ("b", True), ("a", False)):
            mask.set_editor_property(channel, on)
    ratio = node(unreal.MaterialExpressionDivide, -1100, 150)
    half = node(unreal.MaterialExpressionConstant, -1100, 300)
    half.set_editor_property("r", 0.5)
    raised = node(unreal.MaterialExpressionAdd, -950, 200)
    height = node(unreal.MaterialExpressionSaturate, -800, 200)
    height2 = node(unreal.MaterialExpressionMultiply, -650, 200)
    # Soft edges: bright where the surface faces the camera, nothing where it is seen edge-on.
    fresnel = node(unreal.MaterialExpressionFresnel, -950, 450)
    fresnel.set_editor_property("exponent", 1.5)
    core = node(unreal.MaterialExpressionOneMinus, -800, 450)
    core2 = node(unreal.MaterialExpressionMultiply, -650, 450)
    color = node(unreal.MaterialExpressionVectorParameter, -650, -150)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("default_value", unreal.LinearColor(1.0, 0.9, 0.65, 1.0))
    strength = node(unreal.MaterialExpressionScalarParameter, -650, 0)
    strength.set_editor_property("parameter_name", "Intensity")
    strength.set_editor_property("default_value", 0.6)
    tint = node(unreal.MaterialExpressionMultiply, -450, -100)
    fade = node(unreal.MaterialExpressionMultiply, -450, 300)
    out = node(unreal.MaterialExpressionMultiply, -250, 100)
    editing.connect_material_expressions(world, "", offset, "A")
    editing.connect_material_expressions(origin, "", offset, "B")
    editing.connect_material_expressions(offset, "", offset_z, "")
    editing.connect_material_expressions(bounds, "", bounds_z, "")
    editing.connect_material_expressions(offset_z, "", ratio, "A")
    editing.connect_material_expressions(bounds_z, "", ratio, "B")
    editing.connect_material_expressions(ratio, "", raised, "A")
    editing.connect_material_expressions(half, "", raised, "B")
    editing.connect_material_expressions(raised, "", height, "")
    editing.connect_material_expressions(height, "", height2, "A")
    editing.connect_material_expressions(height, "", height2, "B")
    editing.connect_material_expressions(fresnel, "", core, "")
    editing.connect_material_expressions(core, "", core2, "A")
    editing.connect_material_expressions(core, "", core2, "B")
    editing.connect_material_expressions(color, "", tint, "A")
    editing.connect_material_expressions(strength, "", tint, "B")
    editing.connect_material_expressions(height2, "", fade, "A")
    editing.connect_material_expressions(core2, "", fade, "B")
    editing.connect_material_expressions(tint, "", out, "A")
    editing.connect_material_expressions(fade, "", out, "B")
    editing.connect_material_property(out, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.recompile_material(material)
    library.save_asset(path, False)
    lines.append("created " + path)
instance("MI_LightShaft", path)

with open(os.path.join(unreal.Paths.project_saved_dir(), "area4_assets.txt"), "w", encoding="utf-8") as out_file:
    out_file.write("\n".join(lines) + "\n")
