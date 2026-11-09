# Sets the sun body's colour (M_SunBody's Color parameter) while the editor is open. Change COLOR and run in the
# editor's Python console:
#   exec(open(r"C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\set_sun_color.py", encoding="utf-8").read())
import unreal

PATH = "/Game/ThirdPerson/Blueprints/Gimmicks/Sun/M_SunBody"
COLOR = unreal.LinearColor(1.0, 0.42, 0.1, 1.0)

material = unreal.load_asset(PATH)
# import_sun_model.py made one vector parameter, so it has the first expression name of its kind.
node = unreal.find_object(material, "MaterialExpressionVectorParameter_0")
if node is None or str(node.get_editor_property("parameter_name")) != "Color":
    raise RuntimeError("Color parameter not found in " + PATH)
node.set_editor_property("default_value", COLOR)
unreal.MaterialEditingLibrary.recompile_material(material)
unreal.EditorAssetLibrary.save_asset(PATH, False)
unreal.log("M_SunBody Color = {}".format(COLOR))
