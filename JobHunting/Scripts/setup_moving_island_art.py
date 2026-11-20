# BP_MovingIsland in area 3's "garden ruins" look (the user, 2026-11-19): SM_MovingIslandArt (build_moving_island_art.py,
# the same island dressing as the static islands) imported into Gimmicks/Sky with the static islands' materials
# (/Game/Art/Sky/MI_SkyArt<Slot>, from import_sky_art.py), and put on BP_MovingIsland as "Art" on Lift (no collision).
# The old FloorMesh (SM_SkyIsland) is hidden but kept: it is still the island's collision. The floating crystal
# (setup_float_crystal.py) stays under it. Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_moving_island_art.py -unattended -nop4 -nosplash -stdout
import os

import unreal

SKY = "/Game/ThirdPerson/Blueprints/Gimmicks/Sky"
ART = "/Game/Art/Sky"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Sky", "Moving", "SM_MovingIslandArt.fbx")

unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")   # keep vertex colours
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

path = SKY + "/SM_MovingIslandArt"
if library.does_asset_exist(path):
    library.delete_asset(path)
task = unreal.AssetImportTask()
task.filename = SOURCE
task.destination_path = SKY
task.automated = True
task.save = True
task.replace_existing = True
options = unreal.FbxImportUI()
options.set_editor_property("import_materials", False)
options.set_editor_property("import_textures", False)
data = options.get_editor_property("static_mesh_import_data")
data.set_editor_property("combine_meshes", True)
data.set_editor_property("auto_generate_collision", False)
data.set_editor_property("vertex_color_import_option", unreal.VertexColorImportOption.REPLACE)
task.options = options
tools.import_asset_tasks([task])
mesh = unreal.load_asset(path)
if mesh is None:
    raise RuntimeError("SM_MovingIslandArt did not import")
for i, static_material in enumerate(mesh.get_editor_property("static_materials")):
    slot = str(static_material.get_editor_property("material_slot_name"))      # M_SkyArt<Slot>
    mi = unreal.load_asset(ART + "/MI_" + slot[2:]) if slot.startswith("M_") else None
    if mi:
        mesh.set_material(i, mi)
    else:
        lines.append("no material for slot " + slot)
library.save_asset(path, False)
lines.append("SM_MovingIslandArt bounds {}".format(mesh.get_bounds().box_extent))

bp = unreal.load_asset(SKY + "/BP_MovingIsland")
found = {}
for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
    c = data_library.get_associated_object(data_library.get_data(h))
    if c is not None:
        found[c.get_name().replace("_GEN_VARIABLE", "")] = (h, c)
if "Art" in found:
    art = found["Art"][1]
else:
    params = unreal.AddNewSubobjectParams(parent_handle=found["Lift"][0], new_class=unreal.StaticMeshComponent, blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("Art"))
    art = data_library.get_associated_object(data_library.get_data(handle))
    lines.append("BP_MovingIsland: component Art")
art.set_editor_property("static_mesh", mesh)
art.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
art.set_editor_property("relative_scale3d", unreal.Vector(1.0, 1.0, 1.0))
art.set_collision_profile_name("NoCollision")
floor = found["FloorMesh"][1]
floor.set_editor_property("visible", False)        # still the collision
floor.set_editor_property("hidden_in_game", True)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
library.save_asset(SKY + "/BP_MovingIsland", False)
lines.append("BP_MovingIsland: Art shown, FloorMesh hidden (collision only)")

with open(os.path.join(unreal.Paths.project_saved_dir(), "moving_island_art.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
