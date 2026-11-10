# Makes the hell lava look like lava: M_HellLavaFlow, a dark cooled crust broken by glowing cracks, both drifting
# slowly, with the glow pulsing. Two noises in world space (so the size of the surface does not matter), moving in
# different directions; where they sum above CrackLevel the crust gives way to the hot colour.
# MI_HellLavaFlow carries the knobs, to tune by eye with the game running:
#   CrustColor, HotColor, Glow (emissive strength), CrackLevel (higher = less lava showing), CrackSharpness,
#   PlateSize (bigger = larger crust plates), FlowSpeed, PulseSpeed.
# BP_HellLava's Surface is switched to it. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\build_lava_material.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Hell"
MATERIAL = DIR + "/M_HellLavaFlow"
INSTANCE = DIR + "/MI_HellLavaFlow"
LAVA = DIR + "/BP_HellLava"

library = unreal.EditorAssetLibrary
edit = unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def node(material, kind, x, y, **props):
    expression = edit.create_material_expression(material, kind, x, y)
    for key, value in props.items():
        expression.set_editor_property(key, value)
    return expression


def scalar(material, name, value, x, y):
    return node(material, unreal.MaterialExpressionScalarParameter, x, y, parameter_name=name, default_value=value)


def color(material, name, rgb, x, y):
    return node(material, unreal.MaterialExpressionVectorParameter, x, y, parameter_name=name,
                default_value=unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))


def op(material, kind, a, b, x, y):
    expression = node(material, kind, x, y)
    edit.connect_material_expressions(a, "", expression, "A")
    edit.connect_material_expressions(b, "", expression, "B")
    return expression


def drifting_noise(material, position, time, speed, direction, scale, function, levels, y):
    # position + time * FlowSpeed * direction, into a noise of the given scale.
    way = node(material, unreal.MaterialExpressionConstant3Vector, -1400, y + 100,
               constant=unreal.LinearColor(direction[0], direction[1], direction[2], 0.0))
    moving = op(material, unreal.MaterialExpressionMultiply, way, op(material, unreal.MaterialExpressionMultiply, time, speed, -1400, y + 220), -1200, y + 100)
    where = op(material, unreal.MaterialExpressionAdd, position, moving, -1000, y)
    noise = node(material, unreal.MaterialExpressionNoise, -800, y, scale=scale, levels=levels,
                 noise_function=function, output_min=0.0, output_max=1.0, quality=1)
    edit.connect_material_expressions(where, "", noise, "Position")
    return noise


if library.does_asset_exist(MATERIAL):
    material = unreal.load_asset(MATERIAL)
    lines.append("M_HellLavaFlow: already there, left as it is")
else:
    folder, name = MATERIAL.rsplit("/", 1)
    material = tools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
    m = material
    # The noise's Scale is fixed, so PlateSize shrinks the world position instead.
    world = node(m, unreal.MaterialExpressionWorldPosition, -1900, 0)
    plate = scalar(m, "PlateSize", 1.0, -1900, 150)
    position = op(m, unreal.MaterialExpressionDivide, world, plate, -1700, 0)
    time = node(m, unreal.MaterialExpressionTime, -1700, 300)
    speed = scalar(m, "FlowSpeed", 1.0, -1700, 450)
    # Big plates of crust (cellular) and finer swirls (gradient), drifting apart.
    plates = drifting_noise(m, position, time, speed, (14.0, 6.0, 0.0), 0.004, unreal.NoiseFunction.NOISEFUNCTION_VORONOI_ALU, 2, -200)
    swirls = drifting_noise(m, position, time, speed, (-9.0, 12.0, 4.0), 0.012, unreal.NoiseFunction.NOISEFUNCTION_GRADIENT_ALU, 4, 400)
    mixed = op(m, unreal.MaterialExpressionAdd,
               op(m, unreal.MaterialExpressionMultiply, plates, node(m, unreal.MaterialExpressionConstant, -600, -100, r=0.7), -500, -200),
               op(m, unreal.MaterialExpressionMultiply, swirls, node(m, unreal.MaterialExpressionConstant, -600, 500, r=0.45), -500, 400),
               -300, 100)
    # Cracks: saturate((mixed - CrackLevel) * CrackSharpness).
    level = scalar(m, "CrackLevel", 0.55, -500, 650)
    sharp = scalar(m, "CrackSharpness", 6.0, -500, 800)
    hot = node(m, unreal.MaterialExpressionSaturate, 100, 200)
    edit.connect_material_expressions(op(m, unreal.MaterialExpressionMultiply, op(m, unreal.MaterialExpressionSubtract, mixed, level, -150, 300), sharp, -50, 350), "", hot, "")
    crust = color(m, "CrustColor", (0.03, 0.008, 0.005), 100, -300)
    lava = color(m, "HotColor", (1.0, 0.28, 0.03), 100, -100)
    look = node(m, unreal.MaterialExpressionLinearInterpolate, 400, -200)
    edit.connect_material_expressions(crust, "", look, "A")
    edit.connect_material_expressions(lava, "", look, "B")
    edit.connect_material_expressions(hot, "", look, "Alpha")
    # Glow pulses: Glow * (0.85 + 0.15 * sin(time * PulseSpeed)).
    pulse_speed = scalar(m, "PulseSpeed", 1.5, -200, 1000)
    wave = node(m, unreal.MaterialExpressionSine, 100, 1000, period=6.283185)
    edit.connect_material_expressions(op(m, unreal.MaterialExpressionMultiply, time, pulse_speed, -50, 1000), "", wave, "")
    pulse = op(m, unreal.MaterialExpressionAdd, node(m, unreal.MaterialExpressionConstant, 250, 950, r=0.85),
               op(m, unreal.MaterialExpressionMultiply, wave, node(m, unreal.MaterialExpressionConstant, 250, 1100, r=0.15), 300, 1050), 450, 1000)
    glow = op(m, unreal.MaterialExpressionMultiply, scalar(m, "Glow", 8.0, 450, 850), pulse, 600, 900)
    # Only the cracks glow; a little heat stays in the crust (hot^2 keeps the crack edges soft).
    heat = op(m, unreal.MaterialExpressionMultiply, hot, hot, 400, 300)
    emissive = op(m, unreal.MaterialExpressionMultiply, op(m, unreal.MaterialExpressionMultiply, lava, heat, 600, 100), glow, 800, 300)
    rough = node(m, unreal.MaterialExpressionLinearInterpolate, 600, 500)
    edit.connect_material_expressions(node(m, unreal.MaterialExpressionConstant, 450, 500, r=0.85), "", rough, "A")
    edit.connect_material_expressions(node(m, unreal.MaterialExpressionConstant, 450, 600, r=0.35), "", rough, "B")
    edit.connect_material_expressions(hot, "", rough, "Alpha")
    edit.connect_material_property(look, "", unreal.MaterialProperty.MP_BASE_COLOR)
    edit.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    edit.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    edit.recompile_material(m)
    library.save_asset(MATERIAL, False)
    lines.append("created " + MATERIAL)

if library.does_asset_exist(INSTANCE):
    instance = unreal.load_asset(INSTANCE)
else:
    folder, name = INSTANCE.rsplit("/", 1)
    instance = tools.create_asset(name, folder, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    edit.set_material_instance_parent(instance, material)
    library.save_asset(INSTANCE, False)
    lines.append("created " + INSTANCE)

lava_bp = unreal.load_asset(LAVA)
for handle in subsystem.k2_gather_subobject_data_for_blueprint(lava_bp):
    component = data_library.get_associated_object(data_library.get_data(handle))
    if component is not None and component.get_name().startswith("Surface"):
        component.set_material(0, instance)
        lines.append("BP_HellLava Surface -> MI_HellLavaFlow")
unreal.BlueprintEditorLibrary.compile_blueprint(lava_bp)
library.save_asset(LAVA, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "lava_material_build.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
