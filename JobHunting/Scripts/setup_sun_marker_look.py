# The tower sun's landing marker and landing effect (BP_SunMarker, area 4; the user, 2026-11-20). The flat orange
# cylinder becomes a sun sigil on the ground, and the landing gets a shock of light and dust.
#   Gimmicks/Heaven/M_SunSigil + MI_SunSigil  translucent unlit, drawn in the material (a Custom node, no texture) on a
#       flat plane: an outer ring of ticks turning one way, twelve sun rays turning the other, a bold ring at the sun's
#       hit (HitRadius 110 of the 150 cm radius), a faint fill, and a ring of light closing in on the middle again and
#       again. Charge (0 while the sun aims, 1 while it charges; set by the marker's graph) blends ColorAim -> ColorCharge,
#       GlowAim -> GlowCharge, and makes the closing ring faster.
#   Effect /Game/FX/Effekseer/SunImpact (build_sun_impact_effect.ps1).
#   BP_SunMarker: Disk becomes the 300 cm plane with MI_SunSigil, hidden until the graph shows it (the actor itself no
#       longer starts hidden, so the effect can play while the disk is away); Impact (emitter, off until played);
#       variables DiskMaterial, LastPhase.
# Graph: BP_SunMarker_EventGraph.txt (Generators/gen_sun_marker.ps1). Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_sun_marker_look.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
FX = "/Game/FX/Effekseer/SunImpact"
PLANE = "/Engine/BasicShapes/Plane"
SIZE = 300.0
PROJECT = os.path.abspath(unreal.Paths.project_dir())
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

SIGIL = """
float2 p = UV * 2.0 - 1.0;
float r = length(p);
float a = atan2(p.y, p.x);
float inside = 1.0 - smoothstep(0.98, 1.0, r);
float rings = saturate(1.0 - abs(r - 0.955) / 0.018) + saturate(1.0 - abs(r - 0.735) / 0.03) + saturate(1.0 - abs(r - 0.36) / 0.016);
float tickBand = smoothstep(0.80, 0.81, r) * (1.0 - smoothstep(0.89, 0.90, r));
float ticks = tickBand * saturate((cos((a + T * 0.5) * 24.0) - 0.8) * 6.0);
float rayAngle = abs(frac((a - T * 0.8) * 12.0 / 6.2831853) - 0.5) * 2.0;
float rayWidth = 0.42 * (1.0 - saturate((r - 0.40) / 0.30));
float rays = smoothstep(0.40, 0.41, r) * (1.0 - smoothstep(0.69, 0.70, r)) * saturate((rayWidth - rayAngle) * 12.0);
float closing = 1.0 - frac(T * (0.7 + 1.3 * Charge));
float pulse = saturate(1.0 - abs(r - closing) * 12.0) * (0.4 + 0.6 * closing);
float fill = (1.0 - r) * 0.18 + 0.06;
return (saturate(rings + ticks + rays) + pulse * 0.8 + fill) * inside;
"""


def import_file(path, destination):
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = destination
    task.automated = True
    task.save = True
    task.replace_existing = True
    tools.import_asset_tasks([task])
    asset = destination + "/" + os.path.splitext(os.path.basename(path))[0]
    lines.append("imported " + asset)
    return unreal.load_asset(asset)


# ----- the material -----
path = DIR + "/M_SunSigil"
if not library.does_asset_exist(path):
    m = tools.create_asset("M_SunSigil", DIR, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
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

    charge = param(unreal.MaterialExpressionScalarParameter, "Charge", 0.0, -1000, 300)
    color_aim = param(unreal.MaterialExpressionVectorParameter, "ColorAim", unreal.LinearColor(1.0, 0.45, 0.08, 1.0), -700, -350)
    color_charge = param(unreal.MaterialExpressionVectorParameter, "ColorCharge", unreal.LinearColor(1.0, 0.82, 0.45, 1.0), -700, -200)
    glow_aim = param(unreal.MaterialExpressionScalarParameter, "GlowAim", 3.0, -700, -50)
    glow_charge = param(unreal.MaterialExpressionScalarParameter, "GlowCharge", 8.0, -700, 50)
    opacity = param(unreal.MaterialExpressionScalarParameter, "Opacity", 0.9, -300, 400)
    uv = node(unreal.MaterialExpressionTextureCoordinate, -1000, 100)
    time = node(unreal.MaterialExpressionTime, -1000, 200)
    sigil = node(unreal.MaterialExpressionCustom, -750, 150)
    sigil.set_editor_property("code", SIGIL)
    sigil.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    inputs = []
    for name in ("UV", "T", "Charge"):
        item = unreal.CustomInput()
        item.set_editor_property("input_name", name)
        inputs.append(item)
    sigil.set_editor_property("inputs", inputs)
    link(uv, sigil, "UV")
    link(time, sigil, "T")
    link(charge, sigil, "Charge")
    colour = node(unreal.MaterialExpressionLinearInterpolate, -450, -300)
    link(color_aim, colour, "A")
    link(color_charge, colour, "B")
    link(charge, colour, "Alpha")
    glow = node(unreal.MaterialExpressionLinearInterpolate, -450, -50)
    link(glow_aim, glow, "A")
    link(glow_charge, glow, "B")
    link(charge, glow, "Alpha")
    bright = node(unreal.MaterialExpressionMultiply, -250, -200)
    link(colour, bright, "A")
    link(glow, bright, "B")
    emissive = node(unreal.MaterialExpressionMultiply, -50, -100)
    link(bright, emissive, "A")
    link(sigil, emissive, "B")
    see = node(unreal.MaterialExpressionMultiply, -100, 300)
    link(sigil, see, "A")
    link(opacity, see, "B")
    clamp = node(unreal.MaterialExpressionSaturate, 50, 300)
    link(see, clamp, "")
    editing.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.connect_material_property(clamp, "", unreal.MaterialProperty.MP_OPACITY)
    editing.recompile_material(m)
    library.save_asset(path, False)
    lines.append("created " + path)
mi_path = DIR + "/MI_SunSigil"
look = unreal.load_asset(mi_path) if library.does_asset_exist(mi_path) else \
    tools.create_asset("MI_SunSigil", DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
editing.set_material_instance_parent(look, unreal.load_asset(path))
library.save_asset(mi_path, False)

# ----- the effect -----
for name in ("CloudPuff", "Glint", "ShockRing"):
    import_file(os.path.join(PROJECT, "SourceArt", "Effects", "SunImpact", "Texture", name + ".png"), FX + "/Texture")
impact_fx = import_file(os.path.join(PROJECT, "SourceArt", "Effects", "SunImpact", "SunImpact.efk"), FX)

# ----- BP_SunMarker -----
bp = unreal.load_asset(DIR + "/BP_SunMarker")


def gather():
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
        c = data_library.get_associated_object(data_library.get_data(h))
        if c is not None:
            found[c.get_name().replace("_GEN_VARIABLE", "")] = (h, c)
    return found


found = gather()
disk = found["Disk"][1]
disk.set_editor_property("static_mesh", unreal.load_asset(PLANE))
disk.set_material(0, look)
disk.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 3.0))
disk.set_editor_property("relative_scale3d", unreal.Vector(SIZE / 100.0, SIZE / 100.0, 1.0))
disk.set_editor_property("visible", False)
if "Impact" in found:
    impact = found["Impact"][1]
else:
    root = found["DefaultSceneRoot"][0] if "DefaultSceneRoot" in found else subsystem.k2_gather_subobject_data_for_blueprint(bp)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent"), blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("Impact"))
    impact = data_library.get_associated_object(data_library.get_data(handle))
    lines.append("BP_SunMarker: component Impact")
impact.set_editor_property("Effect", impact_fx)
impact.set_editor_property("IsLooping", False)
impact.set_editor_property("auto_activate", False)
defaults = unreal.get_default_object(bp.generated_class())
for name, pin_type in (("DiskMaterial", pins.get_object_reference_type(unreal.MaterialInstanceDynamic.static_class())),
                       ("LastPhase", pins.get_basic_type_by_name("int"))):
    try:
        defaults.get_editor_property(name)
    except Exception:
        if not pins.add_member_variable(bp, name, pin_type):
            raise RuntimeError("Could not add " + name)
        lines.append("BP_SunMarker: variable " + name)
pins.compile_blueprint(bp)
defaults = unreal.get_default_object(bp.generated_class())
defaults.set_editor_property("hidden", False)
library.save_asset(DIR + "/BP_SunMarker", False)
lines.append("BP_SunMarker: Disk is the sigil, Impact added")

with open(os.path.join(unreal.Paths.project_saved_dir(), "sun_marker_look.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
