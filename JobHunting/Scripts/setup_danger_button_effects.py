# What the danger button (import_danger_button.py) does to the screen, in /Game/ThirdPerson/Blueprints/Gimmicks/DangerButton:
#   T_Crack1, T_Crack2   the screen cracks (build_screen_cracks.ps1)
#   T_DangerLogo         the picture shown in the finale (from the brief)
#   S_DangerButton       the sound of the third press (from the brief)
#   S_GlassCrack         the "baki!" of the first and second presses (build_crack_sound.ps1)
#   S_DangerNoise        the broken-radio noise under the finale (the brief's AS_131639 noise from 7 s on)
#   M_DangerFinale       a UI material showing the picture on old paper, run by one parameter, T (seconds since the
#                        finale began): a glitching, flickering picture, a dark spell, worse glitching, a white flash
#                        (like an old TV switching off) at 2.25 s, black from 2.4 s.
#   WBP_DangerOverlay    full-screen layer for the HUD: shows the cracks and the finale by the game instance's
#                        DangerStage (0 nothing, 1 and 2 cracks, 3 the sound plays, 4 the finale). Its designer part
#                        (Crack1, Crack2, Finale images) is made by hand; its graph is WBP_DangerOverlay_EventGraph.txt.
#   BP_MyGameInstance    DangerStage.  BP_DangerButton: Busy, PressSound, SoundSeconds, FinaleSeconds, CrackSound, FinaleSound,
#                        FinaleMute (SM_DangerFinaleMute: all but SC_DangerFinale silent, so the BGM stops).
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_danger_button_effects.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/DangerButton"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "DangerButton")
GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
WIDGET = "/Game/UI/WBP_DangerOverlay"
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
lines = []

FINALE_HLSL = r"""
float t = T;
float tick = floor(t * 14.0);
float band = floor(UV.y * 26.0);
float r = frac(sin(band * 12.9898 + tick * 78.233) * 43758.5453);
float r2 = frac(sin(floor(UV.y * 9.0) * 3.17 + tick * 1.71) * 9631.13);
// How badly it glitches: a little at first, hard from 1.0 to 2.1 s.
float glitch = 0.25 + 0.75 * step(1.0, t) * step(t, 2.1);
float shift = (r > 0.72 ? (r - 0.86) * 0.22 : 0.0) * glitch;
float2 uv = float2(UV.x + shift, UV.y);
// The picture, square, in the middle of a 16:9 screen, 70 % of its height; old paper round it.
float2 p = float2((uv.x - 0.5) * (16.0 / 9.0) / 0.7 + 0.5, (uv.y - 0.5) / 0.7 + 0.5);
float inside = step(0.0, p.x) * step(p.x, 1.0) * step(0.0, p.y) * step(p.y, 1.0);
float4 pic = Texture2DSample(Tex, TexSampler, saturate(p));
float3 paper = float3(0.80, 0.72, 0.58) * (1.0 - 0.45 * length(UV - 0.5));
float3 col = paper * lerp(float3(1, 1, 1), pic.rgb, inside * pic.a);
// Greenish blocks and colour fringes while it glitches.
float block = step(0.78, r2) * glitch;
col = lerp(col, col * float3(0.55, 0.78, 0.5), block);
col.r *= 1.0 + 0.25 * glitch * (r - 0.5);
// Scan lines and flicker.
col *= 0.88 + 0.12 * sin(UV.y * 900.0);
col *= 0.85 + 0.15 * r;
// Dark spells.
float dark = (t > 0.6 && t < 1.0) ? 0.12 : ((t > 1.6 && t < 2.1) ? 0.3 : 1.0);
col *= dark;
// The white flash, squeezed into a band like an old TV going off, then black.
float flash = saturate(1.0 - abs(t - 2.25) / 0.15);
float squeeze = step(abs(UV.y - 0.5), 0.5 - 0.45 * saturate((t - 2.25) / 0.15));
col = lerp(col, float3(0.95, 0.95, 0.95) * (0.8 + 0.2 * r) * squeeze, flash);
col *= (t < 2.4) ? 1.0 : 0.0;
return col;
"""


def import_file(name, folder=DIR):
    task = unreal.AssetImportTask()
    task.filename = os.path.join(SOURCE, name)
    task.destination_path = folder
    task.automated = True
    task.save = True
    task.replace_existing = True
    tools.import_asset_tasks([task])
    path = folder + "/" + os.path.splitext(name)[0]
    lines.append("imported " + path)
    return unreal.load_asset(path)


def ui_texture(name):
    texture = import_file(name + ".png")
    texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    texture.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
    texture.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    library.save_asset(DIR + "/" + name, False)
    return texture


def add_variables(blueprint, variables):
    defaults = unreal.get_default_object(blueprint.generated_class())
    for name, pin_type, editable in variables:
        try:
            defaults.get_editor_property(name)
            continue
        except Exception:
            pass
        if not pins.add_member_variable(blueprint, name, pin_type):
            raise RuntimeError("Could not add {} to {}".format(name, blueprint.get_name()))
        if editable:
            pins.set_blueprint_variable_instance_editable(blueprint, name, True)
        lines.append("{}: variable {}".format(blueprint.get_name(), name))
    pins.compile_blueprint(blueprint)
    return unreal.get_default_object(blueprint.generated_class())


crack1 = ui_texture("T_Crack1")
crack2 = ui_texture("T_Crack2")
logo = ui_texture("T_DangerLogo")
sound = import_file("S_DangerButton.wav")
lines.append("sound {} s".format(sound.get_editor_property("duration")))
crack_sound = import_file("S_GlassCrack.wav")
finale_sound = import_file("S_DangerNoise.wav")

# ----- the finale's silence: everything under the engine's Master class (all the game's sounds, BGM too) goes to
# 0 while SM_DangerFinaleMute is pushed; the finale's noise has a class of its own outside Master, so it still plays.
def made(name, asset_class, factory):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    lines.append("created " + path)
    return tools.create_asset(name, DIR, asset_class, factory)


finale_class = made("SC_DangerFinale", unreal.SoundClass, unreal.SoundClassFactory())
library.save_asset(DIR + "/SC_DangerFinale", False)
finale_sound.set_editor_property("sound_class_object", finale_class)
library.save_asset(DIR + "/S_DangerNoise", False)
mute = made("SM_DangerFinaleMute", unreal.SoundMix, unreal.SoundMixFactory())
master = unreal.load_asset("/Engine/EngineSounds/Master")
adjuster = unreal.SoundClassAdjuster()
adjuster.set_editor_property("sound_class_object", master)
adjuster.set_editor_property("volume_adjuster", 0.0)
adjuster.set_editor_property("apply_to_children", True)
mute.set_editor_property("sound_class_effects", [adjuster])
mute.set_editor_property("fade_in_time", 0.3)
library.save_asset(DIR + "/SM_DangerFinaleMute", False)

# ----- the finale material -----
path = DIR + "/M_DangerFinale"
# Made only once: WBP_DangerOverlay's Finale image points at it (delete it by hand to rebuild it).
material = None if library.does_asset_exist(path) else tools.create_asset("M_DangerFinale", DIR, unreal.Material, unreal.MaterialFactoryNew())
if material is not None:
    material.set_editor_property("material_domain", unreal.MaterialDomain.MD_UI)
    tex = editing.create_material_expression(material, unreal.MaterialExpressionTextureObjectParameter, -900, 0)
    tex.set_editor_property("parameter_name", "Picture")
    tex.set_editor_property("texture", logo)
    time = editing.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -900, 250)
    time.set_editor_property("parameter_name", "T")
    time.set_editor_property("default_value", 0.0)
    uv = editing.create_material_expression(material, unreal.MaterialExpressionTextureCoordinate, -900, 400)
    custom = editing.create_material_expression(material, unreal.MaterialExpressionCustom, -500, 100)
    custom.set_editor_property("code", FINALE_HLSL)
    custom.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    inputs = []
    for name in ("Tex", "T", "UV"):
        item = unreal.CustomInput()
        item.set_editor_property("input_name", name)
        inputs.append(item)
    custom.set_editor_property("inputs", inputs)
    editing.connect_material_expressions(tex, "", custom, "Tex")
    editing.connect_material_expressions(time, "", custom, "T")
    editing.connect_material_expressions(uv, "", custom, "UV")
    editing.connect_material_property(custom, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.recompile_material(material)
    library.save_asset(path, False)
    lines.append("created " + path)

# ----- the stage, the button's settings, the overlay -----
game_instance = unreal.load_asset(GAME_INSTANCE)
add_variables(game_instance, [("DangerStage", pins.get_basic_type_by_name("int"), False)])
library.save_asset(GAME_INSTANCE, False)

button = unreal.load_asset(DIR + "/BP_DangerButton")
defaults = add_variables(button, [
    ("Busy", pins.get_basic_type_by_name("bool"), False),
    ("PressSound", pins.get_object_reference_type(unreal.SoundBase.static_class()), True),
    ("SoundSeconds", pins.get_basic_type_by_name("real"), True),
    ("FinaleSeconds", pins.get_basic_type_by_name("real"), True),
    ("CrackSound", pins.get_object_reference_type(unreal.SoundBase.static_class()), True),
    ("FinaleSound", pins.get_object_reference_type(unreal.SoundBase.static_class()), True),
    ("FinaleMute", pins.get_object_reference_type(unreal.SoundMix.static_class()), True),
])
defaults.set_editor_property("FinaleMute", mute)
defaults.set_editor_property("FinaleSound", finale_sound)
defaults.set_editor_property("PressSound", sound)
defaults.set_editor_property("CrackSound", crack_sound)
defaults.set_editor_property("SoundSeconds", round(sound.get_editor_property("duration"), 2))
if defaults.get_editor_property("FinaleSeconds") == 0.0:
    defaults.set_editor_property("FinaleSeconds", 3.2)
pins.compile_blueprint(button)
library.save_asset(DIR + "/BP_DangerButton", False)

if library.does_asset_exist(WIDGET):
    widget = unreal.load_asset(WIDGET)
else:
    factory = unreal.WidgetBlueprintFactory()
    factory.set_editor_property("parent_class", unreal.UserWidget)
    widget = tools.create_asset("WBP_DangerOverlay", "/Game/UI", unreal.WidgetBlueprint, factory)
    lines.append("created " + WIDGET)
add_variables(widget, [("FinaleTime", pins.get_basic_type_by_name("real"), False)])
library.save_asset(WIDGET, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "danger_button_effects.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
