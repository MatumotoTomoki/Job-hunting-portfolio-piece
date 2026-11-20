# The wings' look (BP_Wings, area 4; the user, 2026-11-20): feathered angel wings in place of the four glowing
# squashed spheres.
#   SM_AngelWings  from build_wings_blender.py (SourceArt/Models/Heaven), vertex colours kept, no collision.
#   M_WingFeather / MI_WingFeather  two-sided lit: base colour = vertex colour (white, gold at the primaries' tips)
#       x Tint; emissive = the same x Glow, so they stay bright like the player.
#   BP_Wings: "WingArt" on the Wings pivot (so the graph's fold / spread scaling still works); the old FeatherL1..R2
#       are hidden (kept, nothing in the graph uses them). Nothing in the graph changes.
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_wings_look.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Heaven", "SM_AngelWings.fbx")

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")   # keep vertex colours

# ----- the material -----
path = DIR + "/M_WingFeather"
if not library.does_asset_exist(path):
    m = tools.create_asset("M_WingFeather", DIR, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("two_sided", True)

    def node(kind, x, y):
        return editing.create_material_expression(m, kind, x, y)

    def param(kind, name, value, x, y):
        n = node(kind, x, y)
        n.set_editor_property("parameter_name", name)
        n.set_editor_property("default_value", value)
        return n

    tint = param(unreal.MaterialExpressionVectorParameter, "Tint", unreal.LinearColor(1.0, 1.0, 1.0, 1.0), -700, -200)
    glow = param(unreal.MaterialExpressionScalarParameter, "Glow", 0.8, -700, 100)
    rough = param(unreal.MaterialExpressionScalarParameter, "Roughness", 0.6, -700, 250)
    vertex = node(unreal.MaterialExpressionVertexColor, -700, -50)
    coloured = node(unreal.MaterialExpressionMultiply, -450, -100)
    bright = node(unreal.MaterialExpressionMultiply, -250, 50)
    editing.connect_material_expressions(vertex, "", coloured, "A")
    editing.connect_material_expressions(tint, "", coloured, "B")
    editing.connect_material_expressions(coloured, "", bright, "A")
    editing.connect_material_expressions(glow, "", bright, "B")
    editing.connect_material_property(coloured, "", unreal.MaterialProperty.MP_BASE_COLOR)
    editing.connect_material_property(bright, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    editing.recompile_material(m)
    library.save_asset(path, False)
    lines.append("created " + path)
mi_path = DIR + "/MI_WingFeather"
look = unreal.load_asset(mi_path) if library.does_asset_exist(mi_path) else \
    tools.create_asset("MI_WingFeather", DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
editing.set_material_instance_parent(look, unreal.load_asset(path))
library.save_asset(mi_path, False)

# ----- the mesh -----
task = unreal.AssetImportTask()
task.filename = SOURCE
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
data.set_editor_property("vertex_color_import_option", unreal.VertexColorImportOption.REPLACE)
task.options = options
tools.import_asset_tasks([task])
mesh = unreal.load_asset(DIR + "/SM_AngelWings")
if mesh is None:
    raise RuntimeError("SM_AngelWings did not import")
mesh.set_material(0, look)
library.save_asset(DIR + "/SM_AngelWings", False)
lines.append("SM_AngelWings bounds {}".format(mesh.get_bounds().box_extent))

# ----- BP_Wings -----
bp = unreal.load_asset(DIR + "/BP_Wings")
found = {}
for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
    c = data_library.get_associated_object(data_library.get_data(h))
    if c is not None:
        found[c.get_name().replace("_GEN_VARIABLE", "")] = (h, c)
if "WingArt" in found:
    art = found["WingArt"][1]
else:
    params = unreal.AddNewSubobjectParams(parent_handle=found["Wings"][0], new_class=unreal.StaticMeshComponent, blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("WingArt"))
    art = data_library.get_associated_object(data_library.get_data(handle))
    lines.append("BP_Wings: component WingArt")
art.set_editor_property("static_mesh", mesh)
art.set_material(0, look)
art.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -5.0))
art.set_collision_profile_name("NoCollision")
art.set_editor_property("cast_shadow", False)
for name in ("FeatherL1", "FeatherL2", "FeatherR1", "FeatherR2"):
    if name in found:
        found[name][1].set_editor_property("visible", False)
        found[name][1].set_editor_property("hidden_in_game", True)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
library.save_asset(DIR + "/BP_Wings", False)
lines.append("BP_Wings: WingArt shown, old feathers hidden")

with open(os.path.join(unreal.Paths.project_saved_dir(), "wings_look.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
