# The groundwork for splitting the game into area levels, each ending in a big mechanism the player sets off:
#   BP_Lever        touched by the player, it is pulled once (Pulled). If ShowCamera is set, the view cuts to that
#                   camera for ShowSeconds while the mechanism moves, the player held still.
#   BP_Mechanism    one moving part of a big mechanism: once its Lever is Pulled, after StartDelay it moves by
#                   MoveOffset and turns its Body by Turn over Duration (eased), and stays there. Scale the actor to
#                   size its Body; the actor's origin is the top of the Body.
#   BP_AreaExit     the way to the next area: stepping in saves the item effects, sets ChangingArea and opens
#                   NextLevel behind a fade.
#   BP_AreaStart    one in every area level: arriving through an area exit, the item effects come back and the
#                   screen clears.
#   BP_MyGameInstance gets ChangingArea.
# A test in LV_Debug, beside the PlayerStart (the ground is y -800..800): a floor on +Y, a cliff too high to jump,
# a lever, five steps that rise out of the floor up to the cliff, a camera to watch them and an exit on the cliff
# that opens LV_Debug again. Everything it places is labelled "AF ..." and rebuilt on every run.
# Graphs: BP_Lever_EventGraph.txt, BP_Mechanism_EventGraph.txt, BP_AreaExit_EventGraph.txt,
# BP_AreaStart_EventGraph.txt. Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_area_foundation.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
LEVER = DIR + "/BP_Lever"
MECHANISM = DIR + "/BP_Mechanism"
EXIT = DIR + "/BP_AreaExit"
START = DIR + "/BP_AreaStart"
GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
DEBUG_LEVEL = "/Game/LV_Debug"
FLAT_COLOR = "/Game/LevelPrototyping/Materials/M_FlatCol"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"
SPHERE = "/Engine/BasicShapes/Sphere"
PREFIX = "AF "

# The lever's handle leans this way before the pull and the other way after (BP_Lever_EventGraph.txt pulls to -PULL).
PULL = 40.0
# The test: steps of STEP_RISE (a plain jump lifts about 125 cm) and STEP_RUN deep, the cliff one rise above the last.
STEP_COUNT = 5
STEP_RISE = 100.0
STEP_RUN = 300.0
STEP_WIDTH = 400.0
STEP_DELAY = 0.4
STEP_SECONDS = 1.0
# The first step waits for the camera's 1 s blend (BP_Lever_EventGraph.txt) before rising.
FIRST_DELAY = 1.0
TEST_X = -600.0
FLOOR_Y = (800.0, 4000.0)
CLIFF_Y = 3200.0
CLIFF_TOP = STEP_RISE * (STEP_COUNT + 1)

library = unreal.EditorAssetLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
lines = []

REAL = pins.get_basic_type_by_name("real")
BOOL = pins.get_basic_type_by_name("bool")
NAME = pins.get_basic_type_by_name("name")
VECTOR = pins.get_struct_type(unreal.Vector.static_struct())
ROTATOR = pins.get_struct_type(unreal.Rotator.static_struct())


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


def actor_blueprint(path):
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    folder, name = path.rsplit("/", 1)
    lines.append("created " + path)
    return tools.create_asset(name, folder, unreal.Blueprint, factory)


def color_material(name, color):
    path = "{}/{}".format(DIR, name)
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    instance = tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, unreal.load_asset(FLAT_COLOR))
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(instance, "Base Color", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    library.save_asset(path, False)
    lines.append("created " + path)
    return instance


def shape(component, mesh_path, material, location, scale, collide=False, rotation=None):
    component.set_editor_property("static_mesh", unreal.load_asset(mesh_path))
    component.set_material(0, material)
    component.set_editor_property("relative_location", location)
    component.set_editor_property("relative_scale3d", scale)
    if rotation is not None:
        component.set_editor_property("relative_rotation", rotation)
    if not collide:
        component.set_collision_profile_name("NoCollision")


stone = color_material("MI_AreaStone", (0.42, 0.38, 0.32))
iron = color_material("MI_AreaIron", (0.08, 0.08, 0.09))
knob = color_material("MI_AreaKnob", (0.8, 0.08, 0.04))
gate_glow = color_material("MI_AreaExit", (1.0, 0.85, 0.4))

# ----- the game instance -----
game_instance = unreal.load_asset(GAME_INSTANCE)
add_variables(game_instance, [("ChangingArea", BOOL, False)])
library.save_asset(GAME_INSTANCE, False)

# ----- BP_Lever -----
lever_bp = actor_blueprint(LEVER)
base, made = add_component(lever_bp, unreal.StaticMeshComponent, "Base")
if made:
    shape(base, CUBE, iron, unreal.Vector(0.0, 0.0, 25.0), unreal.Vector(0.6, 0.4, 0.5), collide=True)
pivot, made = add_component(lever_bp, unreal.SceneComponent, "Pivot")
if made:
    pivot.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 50.0))
    pivot.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=PULL, yaw=0.0))
handle, made = add_component(lever_bp, unreal.StaticMeshComponent, "Handle", "Pivot")
if made:
    shape(handle, CYLINDER, iron, unreal.Vector(0.0, 0.0, 45.0), unreal.Vector(0.08, 0.08, 0.9))
grip, made = add_component(lever_bp, unreal.StaticMeshComponent, "Knob", "Pivot")
if made:
    shape(grip, SPHERE, knob, unreal.Vector(0.0, 0.0, 92.0), unreal.Vector(0.25, 0.25, 0.25))
trigger, made = add_component(lever_bp, unreal.BoxComponent, "Trigger")
if made:
    trigger.set_editor_property("box_extent", unreal.Vector(120.0, 120.0, 100.0))
    trigger.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 100.0))
    trigger.set_collision_profile_name("OverlapOnlyPawn")
lever_defaults = add_variables(lever_bp, [
    ("ShowCamera", pins.get_object_reference_type(unreal.Actor.static_class()), True),
    ("ShowSeconds", REAL, True),
    ("Pulled", BOOL, False),
    # When it was last pulled (game seconds, 0 = never): the mechanisms time their moves from it.
    ("PulledAt", REAL, False),
    # Seconds after a pull until it springs back and can be pulled again (0 = stays pulled).
    ("ResetAfter", REAL, True),
])
if lever_defaults.get_editor_property("ShowSeconds") == 0.0:
    lever_defaults.set_editor_property("ShowSeconds", 3.0)
library.save_asset(LEVER, False)

# ----- BP_Mechanism -----
mechanism_bp = actor_blueprint(MECHANISM)
body, made = add_component(mechanism_bp, unreal.StaticMeshComponent, "Body")
if made:
    shape(body, CUBE, stone, unreal.Vector(0.0, 0.0, -50.0), unreal.Vector(1.0, 1.0, 1.0), collide=True)
mechanism_defaults = add_variables(mechanism_bp, [
    ("Lever", pins.get_object_reference_type(lever_bp.generated_class()), True),
    ("MoveOffset", VECTOR, True),
    ("Turn", ROTATOR, True),
    ("StartDelay", REAL, True),
    ("Duration", REAL, True),
    ("Elapsed", REAL, False),
    ("StartLocation", VECTOR, False),
    ("EndLocation", VECTOR, False),
    ("Done", BOOL, False),
    # Going back: when Returns, it waits ReturnAfter seconds out there, then slides home over ReturnSeconds.
    ("Returns", BOOL, True),
    ("ReturnAfter", REAL, True),
    ("ReturnSeconds", REAL, True),
])
if mechanism_defaults.get_editor_property("Duration") == 0.0:
    mechanism_defaults.set_editor_property("Duration", 2.0)
library.save_asset(MECHANISM, False)

# ----- BP_AreaExit -----
exit_bp = actor_blueprint(EXIT)
area, made = add_component(exit_bp, unreal.BoxComponent, "Area")
if made:
    area.set_editor_property("box_extent", unreal.Vector(110.0, 110.0, 100.0))
    area.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 100.0))
    area.set_collision_profile_name("OverlapOnlyPawn")
pad, made = add_component(exit_bp, unreal.StaticMeshComponent, "Pad")
if made:
    shape(pad, CYLINDER, gate_glow, unreal.Vector(0.0, 0.0, 2.5), unreal.Vector(2.0, 2.0, 0.05))
label, made = add_component(exit_bp, unreal.TextRenderComponent, "Label")
if made:
    label.set_editor_property("text", unreal.Text("NEXT AREA"))
    label.set_editor_property("world_size", 60.0)
    label.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    label.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 260.0))
    label.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
exit_defaults = add_variables(exit_bp, [("NextLevel", NAME, True), ("Leaving", BOOL, False)])
library.save_asset(EXIT, False)

# ----- BP_AreaStart -----
start_bp = actor_blueprint(START)
add_component(start_bp, unreal.BillboardComponent, "Icon")
pins.compile_blueprint(start_bp)
library.save_asset(START, False)


# ----- the test in LV_Debug -----
def spawn(actor_class, location, label_text, rotation=None):
    actor = actors.spawn_actor_from_class(actor_class, location, rotation or unreal.Rotator(0.0, 0.0, 0.0))
    if not actor:
        raise RuntimeError("Could not spawn " + label_text)
    actor.set_actor_label(PREFIX + label_text)
    actor.set_folder_path("AreaTest")
    return actor


def block(center, size, label_text):
    actor = spawn(unreal.StaticMeshActor, center, label_text)
    mesh = actor.get_editor_property("static_mesh_component")
    mesh.set_static_mesh(unreal.load_asset(CUBE))
    mesh.set_material(0, stone)
    actor.set_actor_scale3d(unreal.Vector(size.x / 100.0, size.y / 100.0, size.z / 100.0))
    return actor


if not level_subsystem.load_level(DEBUG_LEVEL):
    raise RuntimeError("Could not open " + DEBUG_LEVEL)
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith(PREFIX):
        actors.destroy_actor(actor)

floor_length = FLOOR_Y[1] - FLOOR_Y[0]
block(unreal.Vector(TEST_X, (FLOOR_Y[0] + FLOOR_Y[1]) / 2.0, -50.0), unreal.Vector(2000.0, floor_length, 100.0), "Floor")
cliff_depth = FLOOR_Y[1] - CLIFF_Y
block(unreal.Vector(TEST_X, CLIFF_Y + cliff_depth / 2.0, CLIFF_TOP / 2.0), unreal.Vector(2000.0, cliff_depth, CLIFF_TOP), "Cliff")

lever = spawn(lever_bp.generated_class(), unreal.Vector(TEST_X - 500.0, 1400.0, 0.0), "Lever", unreal.Rotator(roll=0.0, pitch=0.0, yaw=90.0))
lever.set_editor_property("ShowSeconds", FIRST_DELAY + STEP_DELAY * (STEP_COUNT - 1) + STEP_SECONDS + 0.5)

for i in range(STEP_COUNT):
    top = STEP_RISE * (i + 1)
    y = CLIFF_Y - STEP_RUN / 2.0 - STEP_RUN * (STEP_COUNT - 1 - i)
    # Hidden in the floor until the lever is pulled: the top starts just under the floor's surface.
    step = spawn(mechanism_bp.generated_class(), unreal.Vector(TEST_X, y, -10.0), "Step {}".format(i + 1))
    step.set_actor_scale3d(unreal.Vector(STEP_WIDTH / 100.0, STEP_RUN / 100.0, (top + 20.0) / 100.0))
    step.set_editor_property("Lever", lever)
    step.set_editor_property("MoveOffset", unreal.Vector(0.0, 0.0, top + 10.0))
    step.set_editor_property("StartDelay", FIRST_DELAY + STEP_DELAY * i)
    step.set_editor_property("Duration", STEP_SECONDS)

# The camera off to the side, looking at the middle of the stairs.
eye = unreal.Vector(TEST_X + 1600.0, 1300.0, 800.0)
target = unreal.Vector(TEST_X, CLIFF_Y - STEP_RUN * STEP_COUNT / 2.0, CLIFF_TOP / 2.0)
camera = spawn(unreal.CameraActor, eye, "Show Camera", unreal.MathLibrary.find_look_at_rotation(eye, target))
# A CameraActor keeps 16:9 by default, which puts black bars on a wider window: fill the window instead.
camera.get_editor_property("camera_component").set_editor_property("constrain_aspect_ratio", False)
lever.set_editor_property("ShowCamera", camera)

gate = spawn(exit_bp.generated_class(), unreal.Vector(TEST_X, CLIFF_Y + cliff_depth / 2.0, CLIFF_TOP), "Exit")
gate.set_editor_property("NextLevel", "LV_Debug")

existing_start = [a for a in actors.get_all_level_actors() if a.get_class() == start_bp.generated_class()]
if not existing_start:
    spawn(start_bp.generated_class(), unreal.Vector(-800.0, 0.0, 200.0), "Area Start")

text = spawn(unreal.TextRenderActor, unreal.Vector(TEST_X - 500.0, 1400.0, 320.0), "Label Lever", unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
render = text.get_editor_property("text_render")
render.set_text(unreal.Text("Lever"))
render.set_editor_property("world_size", 50.0)
render.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)

lines.append("level saved: {}".format(level_subsystem.save_current_level()))
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith(PREFIX):
        lines.append("{} at {}".format(actor.get_actor_label(), actor.get_actor_location()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "area_foundation.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
