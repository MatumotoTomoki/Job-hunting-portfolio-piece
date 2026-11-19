# The vanishing cloud's look (BP_VanishCloud, area 3; the user, 2026-11-19): told apart from ordinary clouds at a
# glance, and a "poof" as it goes.
#   Gimmicks/Sky/M_VanishCloud + MI_VanishCloud  a see-through pastel pink cloud (Translucent, Opacity) whose rim
#       glows gold (Fresnel x RimColor x Glow) and that "breathes": World Position Offset swells it in and out
#       (Amount, Speed), each cloud out of step with the others (its phase from where it stands). Collision unchanged.
#       SM_SkyCloud's Nanite is turned off (Nanite draws no translucent materials).
#   Effects /Game/FX/Effekseer/CloudPoof (build_cloud_poof_effect.ps1): CloudPoof as it vanishes, CloudForm as it returns.
#   Sounds S_CloudPoof, S_CloudForm (make_cloud_sounds.ps1) with SA_CloudPoof (full within 4 m, gone 30 m on).
#   BP_VanishCloud: Cloud wears MI_VanishCloud; PoofFx, FormFx (emitters, off until played), PoofSound, FormSound.
# Graph: BP_VanishCloud_EventGraph.txt (Generators/gen_area3_gimmicks.ps1). Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_vanish_cloud_look.py -unattended -nop4 -nosplash -stdout
import os

import unreal

SKY = "/Game/ThirdPerson/Blueprints/Gimmicks/Sky"
FX = "/Game/FX/Effekseer/CloudPoof"
PROJECT = os.path.abspath(unreal.Paths.project_dir())
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


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
path = SKY + "/M_VanishCloud"
if not library.does_asset_exist(path):
    m = tools.create_asset("M_VanishCloud", SKY, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)

    def node(kind, x, y):
        return editing.create_material_expression(m, kind, x, y)

    def param(kind, name, value, x, y):
        n = node(kind, x, y)
        n.set_editor_property("parameter_name", name)
        n.set_editor_property("default_value", value)
        return n

    tint = param(unreal.MaterialExpressionVectorParameter, "Tint", unreal.LinearColor(1.0, 0.86, 0.92, 1.0), -900, -300)
    rim_color = param(unreal.MaterialExpressionVectorParameter, "RimColor", unreal.LinearColor(1.0, 0.78, 0.42, 1.0), -900, -100)
    glow = param(unreal.MaterialExpressionScalarParameter, "Glow", 1.6, -900, 50)
    opacity = param(unreal.MaterialExpressionScalarParameter, "Opacity", 0.78, -900, 150)
    amount = param(unreal.MaterialExpressionScalarParameter, "Amount", 0.04, -900, 450)
    speed = param(unreal.MaterialExpressionScalarParameter, "Speed", 1.6, -900, 550)
    fresnel = node(unreal.MaterialExpressionFresnel, -700, -150)
    fresnel.set_editor_property("exponent", 2.5)
    rim = node(unreal.MaterialExpressionMultiply, -500, -150)
    rim_glow = node(unreal.MaterialExpressionMultiply, -350, -100)
    base_glow = node(unreal.MaterialExpressionMultiply, -500, -300)
    quarter = node(unreal.MaterialExpressionConstant, -700, -250)
    quarter.set_editor_property("r", 0.25)
    emissive = node(unreal.MaterialExpressionAdd, -200, -200)
    editing.connect_material_expressions(fresnel, "", rim, "A")
    editing.connect_material_expressions(rim_color, "", rim, "B")
    editing.connect_material_expressions(rim, "", rim_glow, "A")
    editing.connect_material_expressions(glow, "", rim_glow, "B")
    editing.connect_material_expressions(tint, "", base_glow, "A")
    editing.connect_material_expressions(quarter, "", base_glow, "B")
    editing.connect_material_expressions(base_glow, "", emissive, "A")
    editing.connect_material_expressions(rim_glow, "", emissive, "B")
    # breathing: (world position - object position) * sin(time * Speed + phase) * Amount
    world = node(unreal.MaterialExpressionWorldPosition, -900, 700)
    origin = node(unreal.MaterialExpressionObjectPositionWS, -900, 850)
    offset = node(unreal.MaterialExpressionSubtract, -700, 750)
    time = node(unreal.MaterialExpressionTime, -900, 1000)
    timed = node(unreal.MaterialExpressionMultiply, -700, 1000)
    mask = node(unreal.MaterialExpressionComponentMask, -700, 900)
    mask.set_editor_property("r", True)
    mask.set_editor_property("g", False)
    mask.set_editor_property("b", False)
    mask.set_editor_property("a", False)
    phase_scale = node(unreal.MaterialExpressionConstant, -700, 1150)
    phase_scale.set_editor_property("r", 0.003)
    phase = node(unreal.MaterialExpressionMultiply, -550, 950)
    angle = node(unreal.MaterialExpressionAdd, -400, 1000)
    wave = node(unreal.MaterialExpressionSine, -250, 1000)
    wave.set_editor_property("period", 6.283185)
    swell = node(unreal.MaterialExpressionMultiply, -100, 950)
    wpo = node(unreal.MaterialExpressionMultiply, 50, 800)
    editing.connect_material_expressions(world, "", offset, "A")
    editing.connect_material_expressions(origin, "", offset, "B")
    editing.connect_material_expressions(time, "", timed, "A")
    editing.connect_material_expressions(speed, "", timed, "B")
    editing.connect_material_expressions(origin, "", mask, "")
    editing.connect_material_expressions(mask, "", phase, "A")
    editing.connect_material_expressions(phase_scale, "", phase, "B")
    editing.connect_material_expressions(timed, "", angle, "A")
    editing.connect_material_expressions(phase, "", angle, "B")
    editing.connect_material_expressions(angle, "", wave, "")
    editing.connect_material_expressions(wave, "", swell, "A")
    editing.connect_material_expressions(amount, "", swell, "B")
    editing.connect_material_expressions(offset, "", wpo, "A")
    editing.connect_material_expressions(swell, "", wpo, "B")
    editing.connect_material_property(tint, "", unreal.MaterialProperty.MP_BASE_COLOR)
    editing.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.connect_material_property(opacity, "", unreal.MaterialProperty.MP_OPACITY)
    editing.connect_material_property(wpo, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    editing.recompile_material(m)
    library.save_asset(path, False)
    lines.append("created " + path)
mi_path = SKY + "/MI_VanishCloud"
if library.does_asset_exist(mi_path):
    mi = unreal.load_asset(mi_path)
else:
    mi = tools.create_asset("MI_VanishCloud", SKY, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(mi, unreal.load_asset(path))
    library.save_asset(mi_path, False)
    lines.append("created " + mi_path)

cloud_mesh = unreal.load_asset(SKY + "/SM_SkyCloud")
nanite = cloud_mesh.get_editor_property("nanite_settings")
if nanite.get_editor_property("enabled"):
    nanite.set_editor_property("enabled", False)
    cloud_mesh.set_editor_property("nanite_settings", nanite)
    library.save_asset(SKY + "/SM_SkyCloud", False)
    lines.append("SM_SkyCloud: Nanite off (translucent material)")

# ----- effects, sounds -----
for name in ("CloudPuff", "Glint"):
    import_file(os.path.join(PROJECT, "SourceArt", "Effects", "CloudPoof", "Texture", name + ".png"), FX + "/Texture")
poof_fx = import_file(os.path.join(PROJECT, "SourceArt", "Effects", "CloudPoof", "CloudPoof.efk"), FX)
form_fx = import_file(os.path.join(PROJECT, "SourceArt", "Effects", "CloudPoof", "CloudForm.efk"), FX)
poof_sound = import_file(os.path.join(PROJECT, "SourceArt", "Sounds", "S_CloudPoof.wav"), SKY)
form_sound = import_file(os.path.join(PROJECT, "SourceArt", "Sounds", "S_CloudForm.wav"), SKY)
att_path = SKY + "/SA_CloudPoof"
if library.does_asset_exist(att_path):
    attenuation = unreal.load_asset(att_path)
else:
    attenuation = tools.create_asset("SA_CloudPoof", SKY, unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
    settings = attenuation.get_editor_property("attenuation")
    settings.set_editor_property("attenuation_shape_extents", unreal.Vector(400.0, 0.0, 0.0))
    settings.set_editor_property("falloff_distance", 3000.0)
    attenuation.set_editor_property("attenuation", settings)
    library.save_asset(att_path, False)
    lines.append("created " + att_path)

# ----- BP_VanishCloud -----
bp = unreal.load_asset(SKY + "/BP_VanishCloud")


def gather():
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
        c = data_library.get_associated_object(data_library.get_data(h))
        if c is not None:
            found[c.get_name().replace("_GEN_VARIABLE", "")] = (h, c)
    return found


def add(component_class, name):
    found = gather()
    if name in found:
        return found[name][1]
    root = found["DefaultSceneRoot"][0] if "DefaultSceneRoot" in found else subsystem.k2_gather_subobject_data_for_blueprint(bp)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=component_class, blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("BP_VanishCloud: component " + name)
    return data_library.get_associated_object(data_library.get_data(handle))


gather()["Cloud"][1].set_material(0, mi)
emitter_class = unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent")
for name, effect in (("PoofFx", poof_fx), ("FormFx", form_fx)):
    emitter = add(emitter_class, name)
    emitter.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 10.0))
    emitter.set_editor_property("Effect", effect)
    emitter.set_editor_property("IsLooping", False)
    emitter.set_editor_property("auto_activate", False)
for name, sound in (("PoofSound", poof_sound), ("FormSound", form_sound)):
    audio = add(unreal.AudioComponent, name)
    audio.set_editor_property("sound", sound)
    audio.set_editor_property("auto_activate", False)
    audio.set_editor_property("attenuation_settings", attenuation)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
library.save_asset(SKY + "/BP_VanishCloud", False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "vanish_cloud_look.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
