# Makes a black copy of the birdcage: BP_BirdcageDoor_Black, a duplicate of BP_BirdcageDoor_Blender (same Event
# Graph, components and settings), whose Cage uses black copies of the brass and wood materials
# (M_Birdcage_Brass_Black, M_Birdcage_Wood_Black; they keep the CageFade parameter, so the fade still works).
# The original birdcage is left alone. Safe to run again. In the editor's Python console:
#   exec(open(r"C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\make_black_birdcage.py", encoding="utf-8").read())
import os

import unreal

DIR = "/Game/Prototype/Birdcage"
SOURCE_BP = DIR + "/BP_BirdcageDoor_Blender"
BLACK_BP = DIR + "/BP_BirdcageDoor_Black"
# Base colours: the brass stays metallic, so a little lift keeps its shine readable; the wood is a dull black.
BLACK = {"M_Birdcage_Brass": (0.02, 0.02, 0.02), "M_Birdcage_Wood": (0.01, 0.01, 0.01)}
library = unreal.EditorAssetLibrary
editing = unreal.MaterialEditingLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def black_material(name, color):
    path = DIR + "/" + name + "_Black"
    if not library.does_asset_exist(path):
        library.duplicate_asset(DIR + "/" + name, path)
        lines.append("duplicated " + name)
    material = unreal.load_asset(path)
    # import_birdcage_blender.py made one Constant3Vector, into Base Color.
    base = unreal.find_object(material, "MaterialExpressionConstant3Vector_0")
    if base is None:
        raise RuntimeError("Base colour node not found in " + path)
    base.set_editor_property("constant", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    editing.recompile_material(material)
    library.save_asset(path, False)
    return material


brass = black_material("M_Birdcage_Brass", BLACK["M_Birdcage_Brass"])
wood = black_material("M_Birdcage_Wood", BLACK["M_Birdcage_Wood"])

if not library.does_asset_exist(BLACK_BP):
    library.duplicate_asset(SOURCE_BP, BLACK_BP)
    lines.append("duplicated BP_BirdcageDoor_Blender")
blueprint = unreal.load_asset(BLACK_BP)
cage = None
for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
    component = data_library.get_associated_object(data_library.get_data(handle))
    if component is not None and component.get_name().replace("_GEN_VARIABLE", "") == "Cage":
        cage = component
if cage is None:
    raise RuntimeError("No Cage component in " + BLACK_BP)
# One override per slot of the cage mesh, by slot name as import_birdcage_blender.py assigned them.
# The template's mesh property can read as None here, so fall back to the asset import_birdcage_blender.py gave it.
mesh = cage.get_skeletal_mesh_asset() or unreal.load_asset(DIR + "/SK_Birdcage")
lines.append("cage mesh " + mesh.get_name())
slots = mesh.get_editor_property("materials")
overrides = []
for slot in slots:
    name = str(slot.get_editor_property("material_slot_name"))
    overrides.append(wood if "wood" in name.lower() else brass)
    lines.append("slot {} -> {}".format(name, overrides[-1].get_name()))
cage.set_editor_property("override_materials", overrides)
unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
library.save_asset(BLACK_BP, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "black_birdcage.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
