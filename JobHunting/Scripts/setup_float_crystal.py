# The moving islands' floating crystal (BP_MovingIsland, areas 3 and 4; the user, 2026-11-19): told apart from the
# islands that stay put by a glowing gold crystal cluster under them, the thing that keeps them afloat.
#   Gimmicks/Sky/SM_FloatCrystal   from build_float_crystal.py (pivot at its top, hanging down -Z)
#   Gimmicks/Sky/M_FloatCrystal + MI_FloatCrystal   glassy gold (Color, Roughness) glowing and slowly pulsing:
#       emissive = Color x Glow x (0.6 + 0.4 sin(time x Speed + phase)) + a bright Fresnel rim; each island out of step
#       (its phase from where it stands)
#   BP_MovingIsland: Crystal (on Lift, so it moves with the island, its top 20 cm into the rock's underside at -250 cm)
#       and CrystalLight (a soft gold point light just under it, no shadows).
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_float_crystal.py -unattended -nop4 -nosplash -stdout
import os

import unreal

SKY = "/Game/ThirdPerson/Blueprints/Gimmicks/Sky"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Crystal", "SM_FloatCrystal.fbx")
ISLAND_BOTTOM = -250.0   # SM_SkyIsland (-100..0 cm) at the BP's scale 2.5 in Z

unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

# ----- the mesh -----
task = unreal.AssetImportTask()
task.filename = SOURCE
task.destination_path = SKY
task.automated = True
task.save = True
task.replace_existing = True
options = unreal.FbxImportUI()
options.set_editor_property("import_materials", False)
options.set_editor_property("import_textures", False)
task.options = options
tools.import_asset_tasks([task])
crystal_mesh = unreal.load_asset(SKY + "/SM_FloatCrystal")
lines.append("SM_FloatCrystal bounds {}".format(crystal_mesh.get_bounds().box_extent))

# ----- the material -----
path = SKY + "/M_FloatCrystal"
if not library.does_asset_exist(path):
    m = tools.create_asset("M_FloatCrystal", SKY, unreal.Material, unreal.MaterialFactoryNew())

    def node(kind, x, y):
        return editing.create_material_expression(m, kind, x, y)

    def param(kind, name, value, x, y):
        n = node(kind, x, y)
        n.set_editor_property("parameter_name", name)
        n.set_editor_property("default_value", value)
        return n

    color = param(unreal.MaterialExpressionVectorParameter, "Color", unreal.LinearColor(1.0, 0.72, 0.28, 1.0), -900, -200)
    glow = param(unreal.MaterialExpressionScalarParameter, "Glow", 3.0, -900, 0)
    speed = param(unreal.MaterialExpressionScalarParameter, "Speed", 1.8, -900, 300)
    rough = param(unreal.MaterialExpressionScalarParameter, "Roughness", 0.15, -400, -350)
    time = node(unreal.MaterialExpressionTime, -900, 200)
    timed = node(unreal.MaterialExpressionMultiply, -700, 250)
    origin = node(unreal.MaterialExpressionObjectPositionWS, -900, 450)
    mask = node(unreal.MaterialExpressionComponentMask, -750, 450)
    for channel, on in (("r", True), ("g", False), ("b", False), ("a", False)):
        mask.set_editor_property(channel, on)
    phase_scale = node(unreal.MaterialExpressionConstant, -750, 550)
    phase_scale.set_editor_property("r", 0.003)
    phase = node(unreal.MaterialExpressionMultiply, -600, 500)
    angle = node(unreal.MaterialExpressionAdd, -500, 300)
    wave = node(unreal.MaterialExpressionSine, -400, 300)
    wave.set_editor_property("period", 6.283185)
    depth = node(unreal.MaterialExpressionConstant, -400, 420)
    depth.set_editor_property("r", 0.4)
    pulse_part = node(unreal.MaterialExpressionMultiply, -250, 300)
    base = node(unreal.MaterialExpressionConstant, -250, 420)
    base.set_editor_property("r", 0.6)
    pulse = node(unreal.MaterialExpressionAdd, -100, 300)
    lit = node(unreal.MaterialExpressionMultiply, -400, -100)
    glowing = node(unreal.MaterialExpressionMultiply, 50, 0)
    fresnel = node(unreal.MaterialExpressionFresnel, -400, 600)
    fresnel.set_editor_property("exponent", 3.0)
    rim = node(unreal.MaterialExpressionMultiply, -100, 600)
    rim_strength = node(unreal.MaterialExpressionConstant, -250, 700)
    rim_strength.set_editor_property("r", 4.0)
    emissive = node(unreal.MaterialExpressionAdd, 200, 200)
    editing.connect_material_expressions(time, "", timed, "A")
    editing.connect_material_expressions(speed, "", timed, "B")
    editing.connect_material_expressions(origin, "", mask, "")
    editing.connect_material_expressions(mask, "", phase, "A")
    editing.connect_material_expressions(phase_scale, "", phase, "B")
    editing.connect_material_expressions(timed, "", angle, "A")
    editing.connect_material_expressions(phase, "", angle, "B")
    editing.connect_material_expressions(angle, "", wave, "")
    editing.connect_material_expressions(wave, "", pulse_part, "A")
    editing.connect_material_expressions(depth, "", pulse_part, "B")
    editing.connect_material_expressions(pulse_part, "", pulse, "A")
    editing.connect_material_expressions(base, "", pulse, "B")
    editing.connect_material_expressions(color, "", lit, "A")
    editing.connect_material_expressions(glow, "", lit, "B")
    editing.connect_material_expressions(lit, "", glowing, "A")
    editing.connect_material_expressions(pulse, "", glowing, "B")
    editing.connect_material_expressions(fresnel, "", rim, "A")
    editing.connect_material_expressions(rim_strength, "", rim, "B")
    editing.connect_material_expressions(glowing, "", emissive, "A")
    editing.connect_material_expressions(rim, "", emissive, "B")
    editing.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    editing.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    editing.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.recompile_material(m)
    library.save_asset(path, False)
    lines.append("created " + path)
mi_path = SKY + "/MI_FloatCrystal"
if library.does_asset_exist(mi_path):
    mi = unreal.load_asset(mi_path)
else:
    mi = tools.create_asset("MI_FloatCrystal", SKY, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(mi, unreal.load_asset(path))
    library.save_asset(mi_path, False)
    lines.append("created " + mi_path)
crystal_mesh.set_material(0, mi)
library.save_asset(SKY + "/SM_FloatCrystal", False)

# ----- BP_MovingIsland -----
bp = unreal.load_asset(SKY + "/BP_MovingIsland")


def gather():
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
        c = data_library.get_associated_object(data_library.get_data(h))
        if c is not None:
            found[c.get_name().replace("_GEN_VARIABLE", "")] = (h, c)
    return found


def add(component_class, name, parent):
    found = gather()
    if name in found:
        return found[name][1]
    params = unreal.AddNewSubobjectParams(parent_handle=found[parent][0], new_class=component_class, blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("BP_MovingIsland: component " + name)
    return data_library.get_associated_object(data_library.get_data(handle))


crystal = add(unreal.StaticMeshComponent, "Crystal", "Lift")
crystal.set_editor_property("static_mesh", crystal_mesh)
crystal.set_material(0, mi)
crystal.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, ISLAND_BOTTOM + 20.0))
crystal.set_collision_profile_name("NoCollision")
crystal.set_editor_property("cast_shadow", False)
light = add(unreal.PointLightComponent, "CrystalLight", "Lift")
light.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, ISLAND_BOTTOM - 80.0))
light.set_editor_property("light_color", unreal.Color(r=255, g=190, b=100, a=255))
light.set_editor_property("intensity", 1500.0)
light.set_editor_property("attenuation_radius", 700.0)
light.set_editor_property("cast_shadows", False)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
library.save_asset(SKY + "/BP_MovingIsland", False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "float_crystal.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
