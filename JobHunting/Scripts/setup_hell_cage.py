# Sets up the heaven-or-hell birdcage choice: two identical cages (BP_BirdcageDoor_Blender), one of which sends the
# player to a hell level instead of its Destination. Which one is random, but fixed for the whole run of the game.
#   BP_MyGameInstance    remembers the run's choice and what must survive a level change:
#                        HellSeed (0 until the first pair picks it), HellPairId and ReturnLevel (where the player fell
#                        from), ReturnFromHell, and the item effects (SavedWalkSpeed, SavedJumpZ, SavedJumpCount,
#                        HasSavedStats).
#   BP_BirdcageDoor_Blender  ToHell and PairId (set by its pair at Begin Play) and HellLevel (the level it opens).
#   BP_CagePair          ties CageA and CageB together under a PairId; its graph picks the hell cage and, on the way
#                        back, puts the player past the right cage.
#   BP_HellExit          the way out of hell: a glowing pad that opens ReturnLevel again.
#   LV_Hell              a placeholder hell to climb: a dark floor, a few steps up, the exit at the top.
#   LV_Debug             a test pair behind the PlayerStart.
# The graphs come from BP_BirdcageDoor_Blender_EventGraph.txt, BP_CagePair_EventGraph.txt and
# BP_HellExit_EventGraph.txt. Safe to run again: whatever already exists is left alone. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_hell_cage.py -unattended -nop4 -nosplash -stdout
import os

import unreal

GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
CAGE = "/Game/Prototype/Birdcage/BP_BirdcageDoor_Blender"
DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Hell"
PAIR = DIR + "/BP_CagePair"
EXIT = DIR + "/BP_HellExit"
HELL_LEVEL = "/Game/LV_Hell"
DEBUG_LEVEL = "/Game/LV_Debug"
FLAT_COLOR = "/Game/LevelPrototyping/Materials/M_FlatCol"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"

# LV_Hell: steps of STEP_RISE, within a plain jump (JumpZ 500 lifts about 125 cm).
STEP_COUNT = 6
STEP_RISE = 100.0
STEP_RUN = 380.0
STEP_SIZE = unreal.Vector(3.0, 3.0, 0.4)       # 300 x 300 x 40 cm
# LV_Debug: behind the PlayerStart (-800, 0), on the ground (x -1600..8800, y -800..800); doors face +X (yaw -90),
# toward the PlayerStart. Both cages share one Destination: only the hell one goes elsewhere.
PAIR_X = -1350.0
CAGE_Y = 300.0
PAIR_TARGET = unreal.Vector(-450.0, 600.0, 0.0)

library = unreal.EditorAssetLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lines = []

REAL = pins.get_basic_type_by_name("real")
INT = pins.get_basic_type_by_name("int")
BOOL = pins.get_basic_type_by_name("bool")
NAME = pins.get_basic_type_by_name("name")


def add_variables(blueprint, variables):
    # add_member_variable quietly adds Name_0 next to an existing one, so check the CDO first.
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


def add_component(blueprint, component_class, name):
    existing = components(blueprint)
    if name in existing:
        return existing[name][1], False
    root = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=component_class, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add {} to {}".format(name, blueprint.get_name()))
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("{}: component {}".format(blueprint.get_name(), name))
    return data_library.get_associated_object(data_library.get_data(handle)), True


def actor_blueprint(path):
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    folder, name = path.rsplit("/", 1)
    lines.append("created " + path)
    return unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, folder, unreal.Blueprint, factory)


def color_material(name, color, glow=0.0):
    path = "{}/{}".format(DIR, name)
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    factory = unreal.MaterialInstanceConstantFactoryNew()
    instance = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, DIR, unreal.MaterialInstanceConstant, factory)
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, unreal.load_asset(FLAT_COLOR))
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(instance, "Base Color", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    library.save_asset(path, False)
    lines.append("created " + path)
    return instance


# ----- the run's state, on the game instance -----
game_instance = unreal.load_asset(GAME_INSTANCE)
gi_defaults = add_variables(game_instance, [
    ("HellSeed", INT, False), ("HellPairId", INT, False), ("ReturnLevel", NAME, False), ("ReturnFromHell", BOOL, False),
    ("HasSavedStats", BOOL, False), ("SavedWalkSpeed", REAL, False), ("SavedJumpZ", REAL, False), ("SavedJumpCount", INT, False),
])
# Where the exit leads when LV_Hell was opened directly (testing): the main stage.
if str(gi_defaults.get_editor_property("ReturnLevel")) in ("", "None"):
    gi_defaults.set_editor_property("ReturnLevel", "Lvl_ThirdPerson")
library.save_asset(GAME_INSTANCE, False)

# ----- the cage -----
cage_bp = unreal.load_asset(CAGE)
cage_defaults = add_variables(cage_bp, [("ToHell", BOOL, False), ("PairId", INT, False), ("HellLevel", NAME, True)])
if str(cage_defaults.get_editor_property("HellLevel")) in ("", "None"):
    cage_defaults.set_editor_property("HellLevel", "LV_Hell")
library.save_asset(CAGE, False)

# ----- materials -----
rock = color_material("MI_HellRock", (0.18, 0.04, 0.03))
exit_glow = color_material("MI_HellExit", (0.4, 0.9, 1.0))

# ----- BP_CagePair -----
pair_bp = actor_blueprint(PAIR)
add_component(pair_bp, unreal.BillboardComponent, "Icon")
add_variables(pair_bp, [
    ("CageA", pins.get_object_reference_type(cage_bp.generated_class()), True),
    ("CageB", pins.get_object_reference_type(cage_bp.generated_class()), True),
    ("PairId", INT, True),
])
library.save_asset(PAIR, False)

# ----- BP_HellExit -----
exit_bp = actor_blueprint(EXIT)
area, made = add_component(exit_bp, unreal.BoxComponent, "Area")
if made:
    area.set_editor_property("box_extent", unreal.Vector(110.0, 110.0, 100.0))
    area.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 100.0))
    area.set_collision_profile_name("OverlapOnlyPawn")
pad, made = add_component(exit_bp, unreal.StaticMeshComponent, "Pad")
if made:
    pad.set_editor_property("static_mesh", unreal.load_asset(CYLINDER))
    pad.set_editor_property("relative_scale3d", unreal.Vector(2.0, 2.0, 0.05))
    pad.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 2.5))
    pad.set_collision_profile_name("NoCollision")
    pad.set_material(0, exit_glow)
label, made = add_component(exit_bp, unreal.TextRenderComponent, "Label")
if made:
    label.set_editor_property("text", unreal.Text("EXIT"))
    label.set_editor_property("world_size", 60.0)
    label.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    label.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 260.0))
    label.set_editor_property("relative_rotation", unreal.Rotator(0.0, 0.0, 180.0))
add_variables(exit_bp, [("Leaving", BOOL, False)])
library.save_asset(EXIT, False)


def spawn(actor_class, location, label_text, yaw=0.0, pitch=0.0):
    actor = actors.spawn_actor_from_class(actor_class, location, unreal.Rotator(roll=0.0, pitch=pitch, yaw=yaw))
    if not actor:
        raise RuntimeError("Could not spawn " + label_text)
    actor.set_actor_label(label_text)
    return actor


def block(location, scale, label_text):
    actor = spawn(unreal.StaticMeshActor, location, label_text)
    mesh = actor.get_editor_property("static_mesh_component")
    mesh.set_static_mesh(unreal.load_asset(CUBE))
    mesh.set_material(0, rock)
    actor.set_actor_scale3d(scale)
    return actor


# ----- LV_Hell -----
if library.does_asset_exist(HELL_LEVEL):
    lines.append("LV_Hell: already there, left as it is")
else:
    if not level_subsystem.new_level(HELL_LEVEL, False):
        raise RuntimeError("Could not create " + HELL_LEVEL)
    block(unreal.Vector(1000.0, 0.0, -50.0), unreal.Vector(36.0, 16.0, 1.0), "Hell Floor")
    top = 0.0
    for step in range(STEP_COUNT):
        top = STEP_RISE * (step + 1)
        block(unreal.Vector(STEP_RUN * (step + 1), 0.0, top - 20.0), STEP_SIZE, "Hell Step {}".format(step + 1))
    spawn(exit_bp.generated_class(), unreal.Vector(STEP_RUN * (STEP_COUNT + 1), 0.0, top), "Hell Exit")
    block(unreal.Vector(STEP_RUN * (STEP_COUNT + 1), 0.0, top - 20.0), STEP_SIZE, "Hell Exit Floor")
    spawn(unreal.PlayerStart, unreal.Vector(0.0, 0.0, 100.0), "PlayerStart")
    light = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 1000.0), "Hell Light", yaw=30.0, pitch=-40.0)
    light_component = light.get_editor_property("directional_light_component")
    light_component.set_editor_property("light_color", unreal.Color(r=255, g=90, b=40, a=255))
    light_component.set_editor_property("intensity", 3.0)
    sky = spawn(unreal.SkyLight, unreal.Vector(0.0, 0.0, 1000.0), "Sky Light")
    sky_light = sky.get_editor_property("light_component")
    sky_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    sky_light.set_editor_property("real_time_capture", True)
    spawn(unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0), "Sky Atmosphere")
    fog = spawn(unreal.ExponentialHeightFog, unreal.Vector(0.0, 0.0, 0.0), "Hell Fog")
    fog_component = fog.get_editor_property("component")
    fog_component.set_editor_property("fog_density", 0.05)
    fog_component.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.35, 0.03, 0.01, 1.0))
    system = unreal.load_asset("/Effekseer/BluePrints/BP_EffekseerSystem")
    spawn(system.generated_class(), unreal.Vector(0.0, 0.0, 0.0), "Effekseer System")
    lines.append("LV_Hell saved {}".format(level_subsystem.save_current_level()))

# ----- the test pair in LV_Debug -----
if not level_subsystem.load_level(DEBUG_LEVEL):
    raise RuntimeError("Could not open " + DEBUG_LEVEL)
all_actors = actors.get_all_level_actors()
pair = next((a for a in all_actors if a.get_actor_label() == "Cage Pair"), None)
if pair:
    lines.append("LV_Debug: Cage Pair already there")
else:
    target = spawn(unreal.TargetPoint, PAIR_TARGET, "Cage Pair Target")
    cage_a = spawn(cage_bp.generated_class(), unreal.Vector(PAIR_X, -CAGE_Y, 0.0), "Choice Cage A", yaw=-90.0)
    cage_b = spawn(cage_bp.generated_class(), unreal.Vector(PAIR_X, CAGE_Y, 0.0), "Choice Cage B", yaw=-90.0)
    for cage in (cage_a, cage_b):
        cage.set_editor_property("Destination", target)
    pair = spawn(pair_bp.generated_class(), unreal.Vector(PAIR_X, 0.0, 150.0), "Cage Pair")
    pair.set_editor_property("CageA", cage_a)
    pair.set_editor_property("CageB", cage_b)
    pair.set_editor_property("PairId", 0)
    sign = spawn(unreal.TextRenderActor, unreal.Vector(PAIR_X, 0.0, 320.0), "Label Heaven or Hell", yaw=0.0)
    text = sign.get_editor_property("text_render")
    text.set_text(unreal.Text("Heaven or Hell"))
    text.set_editor_property("world_size", 50.0)
    text.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    lines.append("LV_Debug: pair placed at x {}".format(PAIR_X))
for actor in actors.get_all_level_actors():
    location = actor.get_actor_location()
    if location.x < -1000.0 and abs(location.y) < 900.0:
        lines.append("  near the pair: {} {}".format(actor.get_actor_label(), location))
lines.append("LV_Debug saved {}".format(level_subsystem.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "hell_cage_setup.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
