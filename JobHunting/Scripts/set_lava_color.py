# Turns the lava's molten parts from yellow-orange to a dark, smouldering red: MI_HellLavaLiquid's HotColor deep red
# and Glow lowered (a strong glow washes any red out towards yellow-white). With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\set_lava_color.py -unattended -nop4 -nosplash -stdout
import unreal

INSTANCE = "/Game/ThirdPerson/Blueprints/Gimmicks/Hell/MI_HellLavaLiquid"
HOT_COLOR = unreal.LinearColor(0.45, 0.025, 0.008, 1.0)
GLOW = 2.5

edit = unreal.MaterialEditingLibrary
instance = unreal.load_asset(INSTANCE)
edit.set_material_instance_vector_parameter_value(instance, "HotColor", HOT_COLOR)
edit.set_material_instance_scalar_parameter_value(instance, "Glow", GLOW)
unreal.EditorAssetLibrary.save_asset(INSTANCE, False)
unreal.log("MI_HellLavaLiquid: HotColor {} Glow {}".format(
    edit.get_material_instance_vector_parameter_value(instance, "HotColor"),
    edit.get_material_instance_scalar_parameter_value(instance, "Glow")))
