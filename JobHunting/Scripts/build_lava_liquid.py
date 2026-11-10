# Makes the hell lava read as a liquid, not a glowing floor:
#   SM_LavaGrid       a finely divided flat sheet (written here as SourceArt/Meshes/LavaGrid.obj and imported), so the
#                     surface can actually move: the cube it replaces has only its corners.
#   M_HellLavaLiquid  slow swells (three sine waves, World Position Offset) with matching world-space normals, so the
#                     light slides over them; the crust plates are dragged and stretched by the flow (domain warp);
#                     the molten part is glossy, the crust duller. MI_HellLavaLiquid carries the knobs:
#                     CrustColor, HotColor, Glow, CrackLevel, CrackSharpness, PlateSize, FlowSpeed, PulseSpeed,
#                     WaveHeight (0 = flat), WaveSpeed, Warp (how far the flow drags the crust).
# BP_HellLava's Surface becomes SM_LavaGrid with MI_HellLavaLiquid. M_HellLavaFlow is left as it was, to go back to.
# With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\build_lava_liquid.py -unattended -nop4 -nosplash -stdout
import math
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Hell"
MATERIAL = DIR + "/M_HellLavaLiquid"
INSTANCE = DIR + "/MI_HellLavaLiquid"
GRID = DIR + "/SM_LavaGrid"
LAVA = DIR + "/BP_HellLava"
GRID_X, GRID_Y = 256, 48     # the lava sea is about 216 m x 40 m: cells of roughly 85 cm both ways

library = unreal.EditorAssetLibrary
edit = unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


# ----- the sheet -----
def write_grid(path):
    # 100 x 100 units centred on the origin, flat, facing up; the actor's scale stretches it.
    out = ["# lava grid {} x {}".format(GRID_X, GRID_Y)]
    for j in range(GRID_Y + 1):
        for i in range(GRID_X + 1):
            out.append("v {:.4f} {:.4f} 0".format(-50.0 + 100.0 * i / GRID_X, -50.0 + 100.0 * j / GRID_Y))
    for j in range(GRID_Y + 1):
        for i in range(GRID_X + 1):
            out.append("vt {:.5f} {:.5f}".format(i / GRID_X, j / GRID_Y))
    out.append("vn 0 0 1")
    row = GRID_X + 1
    for j in range(GRID_Y):
        for i in range(GRID_X):
            a = j * row + i + 1
            b, c, d = a + 1, a + row + 1, a + row
            out.append("f {0}/{0}/1 {1}/{1}/1 {2}/{2}/1 {3}/{3}/1".format(a, b, c, d))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="ascii") as f:
        f.write("\n".join(out) + "\n")


if library.does_asset_exist(GRID):
    grid = unreal.load_asset(GRID)
    lines.append("SM_LavaGrid: already there")
else:
    source = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()), "SourceArt", "Meshes", "LavaGrid.obj")
    write_grid(source)
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", source)
    task.set_editor_property("destination_path", DIR)
    task.set_editor_property("destination_name", "SM_LavaGrid")
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)
    tools.import_asset_tasks([task])
    grid = unreal.load_asset(GRID)
    if not grid:
        raise RuntimeError("SM_LavaGrid did not import; imported: {}".format(task.get_editor_property("imported_object_paths")))
    lines.append("imported " + GRID)
try:
    nanite = grid.get_editor_property("nanite_settings")
    if nanite.get_editor_property("enabled"):
        nanite.set_editor_property("enabled", False)
        grid.set_editor_property("nanite_settings", nanite)
        lines.append("SM_LavaGrid: Nanite off")
except Exception as error:
    lines.append("nanite setting not changed: {}".format(error))
library.save_asset(GRID, False)
bounds = grid.get_bounds()
extent = bounds.box_extent
lines.append("SM_LavaGrid bounds origin {} extent {}".format(bounds.origin, extent))

# How the importer laid it out: find the flat axis and the size, and fit the component to a 100 x 100 sheet.
axes = {"x": extent.x, "y": extent.y, "z": extent.z}
flat = min(axes, key=axes.get)
span = max(axes.values())
fit = 50.0 / span if span > 0 else 1.0
rotation = {"z": unreal.Rotator(0.0, 0.0, 0.0), "y": unreal.Rotator(roll=90.0, pitch=0.0, yaw=0.0), "x": unreal.Rotator(roll=0.0, pitch=90.0, yaw=0.0)}[flat]
lines.append("flat axis {}, fit scale {:.4f}".format(flat, fit))


# ----- the material -----
def node(m, kind, x, y, **props):
    expression = edit.create_material_expression(m, kind, x, y)
    for key, value in props.items():
        expression.set_editor_property(key, value)
    return expression


def const(m, value, x, y):
    return node(m, unreal.MaterialExpressionConstant, x, y, r=value)


def scalar(m, name, value, x, y):
    return node(m, unreal.MaterialExpressionScalarParameter, x, y, parameter_name=name, default_value=value)


def color(m, name, rgb, x, y):
    return node(m, unreal.MaterialExpressionVectorParameter, x, y, parameter_name=name,
                default_value=unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))


def vec3(m, v, x, y):
    return node(m, unreal.MaterialExpressionConstant3Vector, x, y, constant=unreal.LinearColor(v[0], v[1], v[2], 0.0))


def op(m, kind, a, b, x, y):
    expression = node(m, kind, x, y)
    edit.connect_material_expressions(a, "", expression, "A")
    edit.connect_material_expressions(b, "", expression, "B")
    return expression


def one(m, kind, source, x, y, **props):
    # (Not "a": ComponentMask takes a=... as a property.)
    expression = node(m, kind, x, y, **props)
    edit.connect_material_expressions(source, "", expression, "")
    return expression


def mul(m, a, b, x, y): return op(m, unreal.MaterialExpressionMultiply, a, b, x, y)
def add(m, a, b, x, y): return op(m, unreal.MaterialExpressionAdd, a, b, x, y)


def noise(m, where, scale, function, levels, x, y):
    n = node(m, unreal.MaterialExpressionNoise, x, y, scale=scale, levels=levels, noise_function=function,
             output_min=0.0, output_max=1.0, quality=1)
    edit.connect_material_expressions(where, "", n, "Position")
    return n


if library.does_asset_exist(MATERIAL):
    material = unreal.load_asset(MATERIAL)
    lines.append("M_HellLavaLiquid: already there, left as it is")
else:
    folder, name = MATERIAL.rsplit("/", 1)
    m = tools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("two_sided", True)
    # Normals below are worked out in world space.
    m.set_editor_property("tangent_space_normal", False)
    world = node(m, unreal.MaterialExpressionWorldPosition, -2600, 0)
    time = node(m, unreal.MaterialExpressionTime, -2600, 200)
    flow_time = mul(m, time, scalar(m, "FlowSpeed", 1.0, -2600, 300), -2400, 250)
    wave_time = mul(m, time, scalar(m, "WaveSpeed", 1.0, -2600, 1400), -2400, 1400)
    height_knob = scalar(m, "WaveHeight", 1.0, -2600, 1550)

    # --- swells: h = sum A sin(k d.xy + w t); slope = sum A k d cos(...) ---
    flat_pos = one(m, unreal.MaterialExpressionComponentMask, world, -2400, 1200, r=True, g=True, b=False, a=False)
    height = None
    slope_x = None
    slope_y = None
    waves = (((1.0, 0.3), 900.0, 0.9, 14.0), ((-0.45, 1.0), 520.0, 1.3, 7.0), ((0.7, -0.7), 310.0, 1.9, 3.5))
    for index, (direction, length, omega, amplitude) in enumerate(waves):
        y = 1200 + 400 * index
        norm = math.hypot(direction[0], direction[1])
        dx, dy = direction[0] / norm, direction[1] / norm
        k = 2.0 * math.pi / length
        along = op(m, unreal.MaterialExpressionDotProduct, flat_pos,
                   node(m, unreal.MaterialExpressionConstant2Vector, -2300, y + 80, r=dx * k, g=dy * k), -2100, y)
        phase = add(m, along, mul(m, wave_time, const(m, omega, -2200, y + 200), -2000, y + 150), -1900, y)
        up = one(m, unreal.MaterialExpressionSine, phase, -1700, y, period=2.0 * math.pi)
        side = one(m, unreal.MaterialExpressionCosine, phase, -1700, y + 120, period=2.0 * math.pi)
        h = mul(m, up, const(m, amplitude, -1600, y + 60), -1500, y)
        sx = mul(m, side, const(m, amplitude * k * dx, -1600, y + 180), -1500, y + 120)
        sy = mul(m, side, const(m, amplitude * k * dy, -1600, y + 260), -1500, y + 220)
        height = h if height is None else add(m, height, h, -1300, y)
        slope_x = sx if slope_x is None else add(m, slope_x, sx, -1300, y + 120)
        slope_y = sy if slope_y is None else add(m, slope_y, sy, -1300, y + 220)
    height = mul(m, height, height_knob, -1100, 1200)
    slope_x = mul(m, slope_x, height_knob, -1100, 1320)
    slope_y = mul(m, slope_y, height_knob, -1100, 1420)
    zero = const(m, 0.0, -1000, 1100)
    offset = op(m, unreal.MaterialExpressionAppendVector, op(m, unreal.MaterialExpressionAppendVector, zero, zero, -900, 1100), height, -800, 1150)
    minus_one = const(m, -1.0, -1000, 1500)
    tilt = op(m, unreal.MaterialExpressionAppendVector, mul(m, slope_x, minus_one, -900, 1320), mul(m, slope_y, minus_one, -900, 1420), -800, 1350)
    surface_normal = one(m, unreal.MaterialExpressionNormalize,
                         op(m, unreal.MaterialExpressionAppendVector, tilt, const(m, 1.0, -800, 1500), -700, 1400), -550, 1400)

    # --- the flow drags the crust: swirls offset where the plates are read ---
    position = op(m, unreal.MaterialExpressionDivide, world, scalar(m, "PlateSize", 1.0, -2600, 500), -2400, 0)
    swirl_at = add(m, position, mul(m, vec3(m, (-9.0, 12.0, 4.0), -2400, 450), flow_time, -2200, 400), -2000, 350)
    swirls = noise(m, swirl_at, 0.008, unreal.NoiseFunction.NOISEFUNCTION_GRADIENT_ALU, 4, -1800, 350)
    centred = op(m, unreal.MaterialExpressionSubtract, swirls, const(m, 0.5, -1700, 500), -1600, 400)
    warp = mul(m, mul(m, vec3(m, (420.0, 300.0, 0.0), -1600, 600), centred, -1450, 500), scalar(m, "Warp", 1.0, -1600, 700), -1300, 550)
    plate_at = add(m, add(m, position, warp, -1150, 0), mul(m, vec3(m, (14.0, 6.0, 0.0), -1300, 150), flow_time, -1150, 150), -1000, 50)
    plates = noise(m, plate_at, 0.004, unreal.NoiseFunction.NOISEFUNCTION_VORONOI_ALU, 2, -800, 50)
    mixed = add(m, mul(m, plates, const(m, 0.7, -600, 150), -500, 50), mul(m, swirls, const(m, 0.45, -600, 400), -500, 350), -350, 200)
    cut = op(m, unreal.MaterialExpressionSubtract, mixed, scalar(m, "CrackLevel", 0.5, -350, 400), -200, 250)
    hot = one(m, unreal.MaterialExpressionSaturate, mul(m, cut, scalar(m, "CrackSharpness", 5.0, -200, 450), -50, 300), 100, 300)

    # --- colour, glow, gloss ---
    hot_color = color(m, "HotColor", (1.0, 0.3, 0.03), 100, -200)
    look = node(m, unreal.MaterialExpressionLinearInterpolate, 400, -200)
    edit.connect_material_expressions(color(m, "CrustColor", (0.035, 0.009, 0.005), 100, -400), "", look, "A")
    edit.connect_material_expressions(hot_color, "", look, "B")
    edit.connect_material_expressions(hot, "", look, "Alpha")
    wave = one(m, unreal.MaterialExpressionSine, mul(m, time, scalar(m, "PulseSpeed", 1.5, -50, 800), 100, 800), 250, 800, period=2.0 * math.pi)
    pulse = add(m, const(m, 0.85, 350, 750), mul(m, wave, const(m, 0.15, 350, 900), 450, 850), 550, 800)
    glow = mul(m, scalar(m, "Glow", 8.0, 550, 650), pulse, 700, 700)
    emissive = mul(m, mul(m, hot_color, mul(m, hot, hot, 300, 400), 500, 300), glow, 800, 400)
    gloss = node(m, unreal.MaterialExpressionLinearInterpolate, 600, 550)
    edit.connect_material_expressions(const(m, 0.45, 450, 500), "", gloss, "A")
    edit.connect_material_expressions(const(m, 0.08, 450, 600), "", gloss, "B")
    edit.connect_material_expressions(hot, "", gloss, "Alpha")
    edit.connect_material_property(look, "", unreal.MaterialProperty.MP_BASE_COLOR)
    edit.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    edit.connect_material_property(gloss, "", unreal.MaterialProperty.MP_ROUGHNESS)
    edit.connect_material_property(surface_normal, "", unreal.MaterialProperty.MP_NORMAL)
    edit.connect_material_property(offset, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    edit.recompile_material(m)
    library.save_asset(MATERIAL, False)
    material = m
    lines.append("created " + MATERIAL)

if library.does_asset_exist(INSTANCE):
    instance = unreal.load_asset(INSTANCE)
else:
    folder, name = INSTANCE.rsplit("/", 1)
    instance = tools.create_asset(name, folder, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    edit.set_material_instance_parent(instance, material)
    library.save_asset(INSTANCE, False)
    lines.append("created " + INSTANCE)

# ----- the lava sea uses them -----
lava_bp = unreal.load_asset(LAVA)
for handle in subsystem.k2_gather_subobject_data_for_blueprint(lava_bp):
    component = data_library.get_associated_object(data_library.get_data(handle))
    if component is not None and component.get_name().startswith("Surface"):
        component.set_editor_property("static_mesh", grid)
        component.set_material(0, instance)
        component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
        component.set_editor_property("relative_rotation", rotation)
        component.set_editor_property("relative_scale3d", unreal.Vector(fit, fit, fit))
        # The swells rise above the flat sheet: grow the bounds so it is not culled at the edges of view.
        component.set_editor_property("bounds_scale", 2.0)
        lines.append("BP_HellLava {} -> SM_LavaGrid + MI_HellLavaLiquid".format(component.get_name()))
unreal.BlueprintEditorLibrary.compile_blueprint(lava_bp)
library.save_asset(LAVA, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "lava_liquid_build.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
