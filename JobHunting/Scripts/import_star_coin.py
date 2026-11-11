# Imports the star coin from build_star_coin_blender.py and makes BP_StarCoin:
#   SM_StarCoin      re-imported every run, so a rebuilt model comes through
#   M_StarCoinGold   gold, with a little glow so it still reads in the dark of the Great Tower
#   BP_StarCoin      Pivot (spun and, once taken, lifted and shrunk) > Mesh; Grab, the sphere the player touches.
#                    Variables: SpinSpeed (degrees a second at rest), Collected, CollectedFor.
#   BP_MyGameInstance gets StarCoins, the run's count.
# The graph comes from BP_StarCoin_EventGraph.txt. Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\import_star_coin.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Coin/StarCoin"
MESH = DIR + "/SM_StarCoin"
GOLD = DIR + "/M_StarCoinGold"
COIN = DIR + "/BP_StarCoin"
GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "StarCoin", "SM_StarCoin.fbx")
GRAB_RADIUS = 80.0

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def import_mesh():
    task = unreal.AssetImportTask()
    task.filename = SOURCE
    task.destination_path = DIR
    task.destination_name = "SM_StarCoin"
    task.automated = True
    task.save = True
    task.replace_existing = True
    options = unreal.FbxImportUI()
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    task.options = options
    tools.import_asset_tasks([task])
    lines.append("imported " + str(list(task.imported_object_paths)))
    return unreal.load_asset(MESH)


def gold_material():
    if library.does_asset_exist(GOLD):
        return unreal.load_asset(GOLD)
    folder, name = GOLD.rsplit("/", 1)
    material = tools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
    color = editing.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -700, 0)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("default_value", unreal.LinearColor(1.0, 0.68, 0.16, 1.0))
    metal = editing.create_material_expression(material, unreal.MaterialExpressionConstant, -400, 150)
    metal.set_editor_property("r", 1.0)
    rough = editing.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -400, 250)
    rough.set_editor_property("parameter_name", "Roughness")
    rough.set_editor_property("default_value", 0.3)
    glow = editing.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -700, 350)
    glow.set_editor_property("parameter_name", "Glow")
    glow.set_editor_property("default_value", 0.25)
    times = editing.create_material_expression(material, unreal.MaterialExpressionMultiply, -400, 400)
    editing.connect_material_expressions(color, "", times, "A")
    editing.connect_material_expressions(glow, "", times, "B")
    editing.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    editing.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)
    editing.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    editing.connect_material_property(times, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.recompile_material(material)
    library.save_asset(GOLD, False)
    lines.append("created " + GOLD)
    return material


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


def components(blueprint):
    found = {}
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_associated_object(data_library.get_data(handle))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = (handle, component)
    return found


def add_component(blueprint, component_class, name, parent=None):
    existing = components(blueprint)
    if name in existing:
        return existing[name][1], False
    parent_handle = existing[parent][0] if parent else subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=parent_handle, new_class=component_class, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add {} to {}".format(name, blueprint.get_name()))
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("{}: component {}".format(blueprint.get_name(), name))
    return data_library.get_associated_object(data_library.get_data(handle)), True


mesh = import_mesh()
gold = gold_material()
mesh.set_material(0, gold)
library.save_asset(MESH, False)

game_instance = unreal.load_asset(GAME_INSTANCE)
add_variables(game_instance, [("StarCoins", pins.get_basic_type_by_name("int"), False)])
library.save_asset(GAME_INSTANCE, False)

if library.does_asset_exist(COIN):
    coin = unreal.load_asset(COIN)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    coin = tools.create_asset("BP_StarCoin", DIR, unreal.Blueprint, factory)
    lines.append("created " + COIN)
add_component(coin, unreal.SceneComponent, "Pivot")
body, made = add_component(coin, unreal.StaticMeshComponent, "Mesh", "Pivot")
body.set_editor_property("static_mesh", mesh)
body.set_collision_profile_name("NoCollision")
body.set_editor_property("cast_shadow", True)
grab, made = add_component(coin, unreal.SphereComponent, "Grab")
if made:
    grab.set_editor_property("sphere_radius", GRAB_RADIUS)
    grab.set_collision_profile_name("OverlapOnlyPawn")
defaults = add_variables(coin, [
    ("SpinSpeed", pins.get_basic_type_by_name("real"), True),
    ("Collected", pins.get_basic_type_by_name("bool"), False),
    ("CollectedFor", pins.get_basic_type_by_name("real"), False),
])
if defaults.get_editor_property("SpinSpeed") == 0.0:
    defaults.set_editor_property("SpinSpeed", 90.0)
pins.compile_blueprint(coin)
library.save_asset(COIN, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "star_coin_import.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
