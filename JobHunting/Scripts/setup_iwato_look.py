# The light shards' and the Iwato's look (area 4; the user, 2026-11-20: shards beautiful, the Iwato weighty).
# Meshes from build_iwato_shard.py (SourceArt/Models/Heaven), imported into Gimmicks/Heaven:
#   SM_LightShard + M_ShardCrystal/MI_ShardCrystal  a faceted crystal, lit so its facets show, glowing more at its
#       edges (emissive Color x Glow x (Base + Fresnel)). Put on BP_LightShard's Mesh (scale 1, upright); the
#       BP's spin and glow light are unchanged.
#   SM_IwatoRock + MI_IwatoRock / MI_IwatoRope / MI_IwatoPaper  the rock door with its shimenawa and shide, on
#       area 1's M_RuinsSurface (rock, plaster textures; tinted). Simple box collision.
# With --levels the "Iwato Rock" BP_Mechanism in LV_Area4_Heaven (and LV_Debug's, if any) gets the rock as its Body
# mesh at actor scale 1 (it was a cube scaled 2 x 7 x 13; same size, same top), its old colour override cleared.
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript "-script=<full path>\setup_iwato_look.py [--levels]" -unattended -nop4 -nosplash -stdout
import os
import sys

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
RUINS = "/Game/Art/Ruins"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Heaven")
LEVELS = ["/Game/LV_Area4_Heaven", "/Game/LV_Debug"]

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")


def import_mesh(name):
    path = DIR + "/" + name
    task = unreal.AssetImportTask()
    task.filename = os.path.join(SOURCE, name + ".fbx")
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
    mesh = unreal.load_asset(path)
    if mesh is None:
        raise RuntimeError(name + " did not import")
    return mesh


def instance(name, parent):
    path = DIR + "/" + name
    mi = unreal.load_asset(path) if library.does_asset_exist(path) else \
        tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    if mi.get_editor_property("parent") != parent:
        editing.set_material_instance_parent(mi, parent)
    return mi


# ----- the crystal material -----
path = DIR + "/M_ShardCrystal"
if not library.does_asset_exist(path):
    m = tools.create_asset("M_ShardCrystal", DIR, unreal.Material, unreal.MaterialFactoryNew())

    def node(kind, x, y):
        return editing.create_material_expression(m, kind, x, y)

    def param(kind, name, value, x, y):
        n = node(kind, x, y)
        n.set_editor_property("parameter_name", name)
        n.set_editor_property("default_value", value)
        return n

    color = param(unreal.MaterialExpressionVectorParameter, "Color", unreal.LinearColor(1.0, 0.92, 0.7, 1.0), -800, -200)
    glow = param(unreal.MaterialExpressionScalarParameter, "Glow", 6.0, -800, 0)
    base = param(unreal.MaterialExpressionScalarParameter, "Base", 0.35, -800, 150)
    edge = param(unreal.MaterialExpressionScalarParameter, "EdgeGlow", 1.5, -800, 300)
    rough = param(unreal.MaterialExpressionScalarParameter, "Roughness", 0.12, -800, 450)
    fresnel = node(unreal.MaterialExpressionFresnel, -600, 300)
    edge_part = node(unreal.MaterialExpressionMultiply, -450, 300)
    amount = node(unreal.MaterialExpressionAdd, -300, 200)
    tint = node(unreal.MaterialExpressionMultiply, -450, -100)
    emissive = node(unreal.MaterialExpressionMultiply, -150, 0)
    editing.connect_material_expressions(fresnel, "", edge_part, "A")
    editing.connect_material_expressions(edge, "", edge_part, "B")
    editing.connect_material_expressions(base, "", amount, "A")
    editing.connect_material_expressions(edge_part, "", amount, "B")
    editing.connect_material_expressions(color, "", tint, "A")
    editing.connect_material_expressions(glow, "", tint, "B")
    editing.connect_material_expressions(tint, "", emissive, "A")
    editing.connect_material_expressions(amount, "", emissive, "B")
    editing.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    editing.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    editing.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.recompile_material(m)
    library.save_asset(path, False)
    lines.append("created " + path)
crystal_look = instance("MI_ShardCrystal", unreal.load_asset(path))
library.save_asset(DIR + "/MI_ShardCrystal", False)

# ----- the shard -----
shard_mesh = import_mesh("SM_LightShard")
shard_mesh.set_material(0, crystal_look)
library.save_asset(DIR + "/SM_LightShard", False)
bp = unreal.load_asset(DIR + "/BP_LightShard")
for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
    c = data_library.get_associated_object(data_library.get_data(h))
    if c is not None and c.get_name().replace("_GEN_VARIABLE", "") == "Mesh":
        c.set_editor_property("static_mesh", shard_mesh)
        c.set_material(0, crystal_look)
        c.set_editor_property("relative_scale3d", unreal.Vector(1.0, 1.0, 1.0))
        c.set_editor_property("relative_rotation", unreal.Rotator(0.0, 0.0, 0.0))
        lines.append("BP_LightShard: Mesh is SM_LightShard")
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
library.save_asset(DIR + "/BP_LightShard", False)

# ----- the rock -----
surface = unreal.load_asset(RUINS + "/M_RuinsSurface")
looks = {}
for name, texture, tint, roughness, glow in (("MI_IwatoRock", "Rock", (0.42, 0.41, 0.44), 0.9, 0.0),
                                              ("MI_IwatoRope", "Plaster", (0.95, 0.78, 0.45), 0.9, 0.0),
                                              ("MI_IwatoPaper", "Plaster", (1.3, 1.3, 1.25), 0.8, 0.15)):
    mi = instance(name, surface)
    editing.set_material_instance_texture_parameter_value(mi, "Color", unreal.load_asset(RUINS + "/Textures/T_Ruins" + texture + "_C"))
    editing.set_material_instance_texture_parameter_value(mi, "Normal", unreal.load_asset(RUINS + "/Textures/T_Ruins" + texture + "_N"))
    editing.set_material_instance_scalar_parameter_value(mi, "Roughness", roughness)
    editing.set_material_instance_scalar_parameter_value(mi, "Metallic", 0.0)
    editing.set_material_instance_scalar_parameter_value(mi, "Emissive", glow)
    editing.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(*tint, 1.0))
    library.save_asset(DIR + "/" + name, False)
    looks["M_" + name[3:]] = mi
rock_mesh = import_mesh("SM_IwatoRock")
for i, static_material in enumerate(rock_mesh.get_editor_property("static_materials")):
    slot = str(static_material.get_editor_property("material_slot_name"))
    if slot in looks:
        rock_mesh.set_material(i, looks[slot])
    else:
        lines.append("no material for slot " + slot)
unreal.EditorStaticMeshLibrary.remove_collisions(rock_mesh)
unreal.EditorStaticMeshLibrary.add_simple_collisions(rock_mesh, unreal.ScriptCollisionShapeType.BOX)
library.save_asset(DIR + "/SM_IwatoRock", False)
lines.append("SM_IwatoRock bounds {}".format(rock_mesh.get_bounds().box_extent))

# ----- the levels -----
if "--levels" in sys.argv:
    level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for level in LEVELS:
        if not library.does_asset_exist(level):
            continue
        level_editor.load_level(level)
        changed = 0
        for a in actors.get_all_level_actors():
            if a.get_class().get_name() != "BP_Mechanism_C" or "Iwato" not in a.get_actor_label():
                continue
            scale = a.get_actor_scale3d()
            body = [c for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.get_name() == "Body"][0]
            if body.static_mesh == rock_mesh:
                continue
            if abs(scale.x - 2) > 0.01 or abs(scale.y - 7) > 0.01 or abs(scale.z - 13) > 0.01:
                lines.append("{}: {} is scaled {}, not 2 x 7 x 13; left as it is".format(level, a.get_actor_label(), scale))
                continue
            body.set_editor_property("static_mesh", rock_mesh)
            body.set_editor_property("override_materials", [])
            a.set_actor_scale3d(unreal.Vector(1.0, 1.0, 1.0))
            changed += 1
            lines.append("{}: {} now SM_IwatoRock".format(level, a.get_actor_label()))
        if changed:
            level_editor.save_current_level()

with open(os.path.join(unreal.Paths.project_saved_dir(), "iwato_look.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
