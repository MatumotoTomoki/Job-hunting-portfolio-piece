# The ringing jewels' look (BP_ChimeJewel, area 4; the user, 2026-11-20): real gems, each note its own colour, and a
# ripple of light as one rings.
#   SM_ChimeJewel  from build_chime_gem_blender.py: a brilliant-cut gem in the old cylinder's box (placed jewels keep
#       their scale), its own convex collision (UCX), Nanite off (two of its materials are see-through).
#   Colour: the jewel's Pitch goes to its parts as custom primitive data 0 (the graph does it at Begin Play); both
#       materials turn it into a hue - log2(Pitch) x 0.85 round the colour wheel from cyan (A5) - softened by Saturation.
#   M_ChimeGem (Solid; MI_JewelSolid)  lit, glassy (low Roughness), glowing more at its edges (Glow, EdgeGlow) and with
#       glints that sweep across the facets as two slow lights turn (SparkleGlow).
#   M_ChimeGemGhost (Ghost, Hint; MI_JewelGhost, MI_JewelHint)  translucent unlit, a faint body and brighter edges
#       (Opacity, EdgeOpacity, Glow); the hint brighter.
#   Effect /Game/FX/Effekseer/ChimeRipple (build_chime_ripple_effect.ps1) on RingFx (world scale 1, off until played).
# Graph: BP_ChimeJewel_EventGraph.txt (Generators/gen_heaven_chime.ps1). Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_chime_gem_look.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
FX = "/Game/FX/Effekseer/ChimeRipple"
PROJECT = os.path.abspath(unreal.Paths.project_dir())
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")   # keeps the UCX collision

HUE = """
float h = frac(log2(max(P, 0.01)) * 0.85 + 0.52);
float3 rgb = saturate(abs(frac(h + float3(1.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0) - 1.0);
return lerp(float3(1.0, 1.0, 1.0), rgb, Sat);
"""
SPARKLE = """
float3 d1 = normalize(float3(cos(T * 1.1), sin(T * 1.1), 0.5));
float3 d2 = normalize(float3(cos(2.0 - T * 0.7), sin(2.0 - T * 0.7), 0.3));
return pow(saturate(dot(N, d1)), 60.0) + pow(saturate(dot(N, d2)), 60.0);
"""


def material(name, translucent, build):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    m = tools.create_asset(name, DIR, unreal.Material, unreal.MaterialFactoryNew())
    if translucent:
        m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
        m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)

    def node(kind, x, y):
        return editing.create_material_expression(m, kind, x, y)

    def param(kind, name, value, x, y):
        n = node(kind, x, y)
        n.set_editor_property("parameter_name", name)
        n.set_editor_property("default_value", value)
        return n

    def custom(code, inputs, output, x, y):
        n = node(unreal.MaterialExpressionCustom, x, y)
        n.set_editor_property("code", code)
        n.set_editor_property("output_type", output)
        items = []
        for input_name in inputs:
            item = unreal.CustomInput()
            item.set_editor_property("input_name", input_name)
            items.append(item)
        n.set_editor_property("inputs", items)
        return n

    def link(a, b, pin, out=""):
        editing.connect_material_expressions(a, out, b, pin)

    # The jewel's colour from its Pitch (custom primitive data 0).
    pitch = param(unreal.MaterialExpressionScalarParameter, "Pitch", 1.0, -1200, -300)
    pitch.set_editor_property("use_custom_primitive_data", True)
    pitch.set_editor_property("primitive_data_index", 0)
    saturation = param(unreal.MaterialExpressionScalarParameter, "Saturation", 0.6, -1200, -200)
    colour = custom(HUE, ("P", "Sat"), unreal.CustomMaterialOutputType.CMOT_FLOAT3, -950, -250)
    link(pitch, colour, "P")
    link(saturation, colour, "Sat")
    build(m, node, param, custom, link, colour)
    editing.recompile_material(m)
    library.save_asset(path, False)
    lines.append("created " + path)
    return m


def build_solid(m, node, param, custom, link, colour):
    glow = param(unreal.MaterialExpressionScalarParameter, "Glow", 1.2, -900, 0)
    edge = param(unreal.MaterialExpressionScalarParameter, "EdgeGlow", 2.5, -900, 100)
    sparkle_glow = param(unreal.MaterialExpressionScalarParameter, "SparkleGlow", 12.0, -900, 400)
    rough = param(unreal.MaterialExpressionScalarParameter, "Roughness", 0.08, -900, 550)
    fresnel = node(unreal.MaterialExpressionFresnel, -900, 200)
    normal = node(unreal.MaterialExpressionVertexNormalWS, -1100, 300)
    time = node(unreal.MaterialExpressionTime, -1100, 400)
    sparkle = custom(SPARKLE, ("N", "T"), unreal.CustomMaterialOutputType.CMOT_FLOAT1, -900, 300)
    link(normal, sparkle, "N")
    link(time, sparkle, "T")
    rim = node(unreal.MaterialExpressionMultiply, -700, 150)
    link(fresnel, rim, "A")
    link(edge, rim, "B")
    base_amount = node(unreal.MaterialExpressionConstant, -700, 50)
    base_amount.set_editor_property("r", 0.4)
    body = node(unreal.MaterialExpressionAdd, -550, 100)
    link(base_amount, body, "A")
    link(rim, body, "B")
    lit = node(unreal.MaterialExpressionMultiply, -400, 50)
    link(body, lit, "A")
    link(glow, lit, "B")
    glint = node(unreal.MaterialExpressionMultiply, -550, 350)
    link(sparkle, glint, "A")
    link(sparkle_glow, glint, "B")
    amount = node(unreal.MaterialExpressionAdd, -250, 150)
    link(lit, amount, "A")
    link(glint, amount, "B")
    emissive = node(unreal.MaterialExpressionMultiply, -100, 0)
    link(colour, emissive, "A")
    link(amount, emissive, "B")
    dim = node(unreal.MaterialExpressionMultiply, -500, -300)
    link(colour, dim, "A")
    dim_amount = node(unreal.MaterialExpressionConstant, -700, -350)
    dim_amount.set_editor_property("r", 0.4)
    link(dim_amount, dim, "B")
    editing.connect_material_property(dim, "", unreal.MaterialProperty.MP_BASE_COLOR)
    editing.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    editing.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)


def build_ghost(m, node, param, custom, link, colour):
    glow = param(unreal.MaterialExpressionScalarParameter, "Glow", 2.0, -900, 0)
    opacity = param(unreal.MaterialExpressionScalarParameter, "Opacity", 0.06, -900, 150)
    edge_opacity = param(unreal.MaterialExpressionScalarParameter, "EdgeOpacity", 0.35, -900, 250)
    fresnel = node(unreal.MaterialExpressionFresnel, -900, 350)
    emissive = node(unreal.MaterialExpressionMultiply, -500, -100)
    link(colour, emissive, "A")
    link(glow, emissive, "B")
    edge = node(unreal.MaterialExpressionMultiply, -650, 300)
    link(fresnel, edge, "A")
    link(edge_opacity, edge, "B")
    alpha = node(unreal.MaterialExpressionAdd, -450, 200)
    link(opacity, alpha, "A")
    link(edge, alpha, "B")
    editing.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.connect_material_property(alpha, "", unreal.MaterialProperty.MP_OPACITY)


solid_material = material("M_ChimeGem", False, build_solid)
ghost_material = material("M_ChimeGemGhost", True, build_ghost)
looks = {}
for name, parent, scalars in (("MI_JewelSolid", solid_material, ()),
                              ("MI_JewelGhost", ghost_material, ()),
                              ("MI_JewelHint", ghost_material, (("Opacity", 0.25), ("EdgeOpacity", 0.7), ("Glow", 5.0)))):
    mi = unreal.load_asset(DIR + "/" + name)
    if mi.get_editor_property("parent") != parent:
        editing.clear_all_material_instance_parameters(mi)
        editing.set_material_instance_parent(mi, parent)
        lines.append(name + " re-parented to " + parent.get_name())
    for key, value in scalars:
        editing.set_material_instance_scalar_parameter_value(mi, key, value)
    library.save_asset(DIR + "/" + name, False)
    looks[name] = mi

# ----- the mesh -----
task = unreal.AssetImportTask()
task.filename = os.path.join(PROJECT, "SourceArt", "Models", "Heaven", "SM_ChimeJewel.fbx")
task.destination_path = DIR
task.automated = True
task.save = True
task.replace_existing = True
options = unreal.FbxImportUI()
options.set_editor_property("import_materials", False)
options.set_editor_property("import_textures", False)
data = options.get_editor_property("static_mesh_import_data")
data.set_editor_property("combine_meshes", True)
data.set_editor_property("auto_generate_collision", False)
task.options = options
tools.import_asset_tasks([task])
mesh = unreal.load_asset(DIR + "/SM_ChimeJewel")
if mesh is None:
    raise RuntimeError("SM_ChimeJewel did not import")
nanite = mesh.get_editor_property("nanite_settings")
if nanite.get_editor_property("enabled"):
    nanite.set_editor_property("enabled", False)
    mesh.set_editor_property("nanite_settings", nanite)
mesh.set_material(0, looks["MI_JewelSolid"])
library.save_asset(DIR + "/SM_ChimeJewel", False)
lines.append("SM_ChimeJewel bounds {} collision shapes {}".format(
    mesh.get_bounds().box_extent, unreal.EditorStaticMeshLibrary.get_convex_collision_count(mesh)))

# ----- the effect -----
for name in ("ShockRing", "Glint"):
    task = unreal.AssetImportTask()
    task.filename = os.path.join(PROJECT, "SourceArt", "Effects", "ChimeRipple", "Texture", name + ".png")
    task.destination_path = FX + "/Texture"
    task.automated = True
    task.save = True
    task.replace_existing = True
    tools.import_asset_tasks([task])
task = unreal.AssetImportTask()
task.filename = os.path.join(PROJECT, "SourceArt", "Effects", "ChimeRipple", "ChimeRipple.efk")
task.destination_path = FX
task.automated = True
task.save = True
task.replace_existing = True
tools.import_asset_tasks([task])
ripple = unreal.load_asset(FX + "/ChimeRipple")

# ----- BP_ChimeJewel -----
bp = unreal.load_asset(DIR + "/BP_ChimeJewel")
found = {}
for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
    c = data_library.get_associated_object(data_library.get_data(h))
    if c is not None:
        found[c.get_name().replace("_GEN_VARIABLE", "")] = (h, c)
for name, look in (("Solid", "MI_JewelSolid"), ("Ghost", "MI_JewelGhost"), ("Hint", "MI_JewelHint")):
    part = found[name][1]
    part.set_editor_property("static_mesh", mesh)
    part.set_material(0, looks[look])
if "RingFx" in found:
    fx = found["RingFx"][1]
else:
    root = found["DefaultSceneRoot"][0] if "DefaultSceneRoot" in found else subsystem.k2_gather_subobject_data_for_blueprint(bp)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent"), blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("RingFx"))
    fx = data_library.get_associated_object(data_library.get_data(handle))
    lines.append("BP_ChimeJewel: component RingFx")
fx.set_editor_property("Effect", ripple)
fx.set_editor_property("IsLooping", False)
fx.set_editor_property("auto_activate", False)
fx.set_editor_property("absolute_scale", True)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
library.save_asset(DIR + "/BP_ChimeJewel", False)
lines.append("BP_ChimeJewel: parts are SM_ChimeJewel, RingFx added")

with open(os.path.join(unreal.Paths.project_saved_dir(), "chime_gem_look.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
