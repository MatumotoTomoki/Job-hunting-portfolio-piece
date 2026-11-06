# Sets up the checkpoint item: BP_CheckpointFlag (the flag that gets planted, and breaks once used), BP_CheckpointItem
# (the pickup), their materials, the IA_UseItem input on E and the gamepad's left face button, the character
# variables HasFlagItem and ActiveFlag, and a pickup in LV_Debug in front of the goal. Safe to run again: whatever
# already exists is left alone. The Event Graphs come from BP_CheckpointFlag_EventGraph.txt,
# BP_CheckpointItem_EventGraph.txt and Checkpoint_Character.txt. With the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=setup_checkpoint.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Item/Checkpoint"
FLAG_PATH = DIR + "/BP_CheckpointFlag"
ITEM_PATH = DIR + "/BP_CheckpointItem"
CHARACTER_PATH = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1"
FLAT_COLOR = "/Game/LevelPrototyping/Materials/M_FlatCol"
CYLINDER = "/Engine/BasicShapes/Cylinder"
CUBE = "/Engine/BasicShapes/Cube"
SPHERE = "/Engine/BasicShapes/Sphere"
# The basic shapes are 100 cm across, centered on their pivot.
POLE_HALF = 55.0
POLE_SCALE = unreal.Vector(0.05, 0.05, POLE_HALF / 100.0)
# Behind the flag, the player's capsule half height (90) above the ground: where a respawn puts the player.
RESPAWN_OFFSET = unreal.Vector(-60.0, 0.0, 92.0)

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
bp_library = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def color_material(name, color):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    instance = tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, unreal.load_asset(FLAT_COLOR))
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(instance, "Base Color", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    library.save_asset(path, False)
    return instance


def new_blueprint(path):
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    name = path.split("/")[-1]
    blueprint = tools.create_asset(name, DIR, unreal.Blueprint, factory)
    if not blueprint:
        raise RuntimeError("Could not create " + path)
    return blueprint, subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]


def add(blueprint, parent, component_class, name, location=None):
    params = unreal.AddNewSubobjectParams(parent_handle=parent, new_class=component_class, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add " + name)
    subsystem.rename_subobject(handle, unreal.Text(name))
    component = data_library.get_object(data_library.get_data(handle))
    if location is not None:
        component.set_editor_property("relative_location", location)
    return handle, component


def add_mesh(blueprint, parent, name, shape, location, scale, material):
    _, mesh = add(blueprint, parent, unreal.StaticMeshComponent, name, location)
    mesh.set_editor_property("static_mesh", unreal.load_asset(shape))
    mesh.set_editor_property("relative_scale3d", scale)
    mesh.set_material(0, material)
    # Decoration only: it must not block the player or the camera.
    mesh.set_collision_profile_name("NoCollision")
    return mesh


def add_flag_shape(blueprint, parent, materials, size=1.0):
    # Lower pole on Base; the upper pole, the cloth and the knob on Upper, which is what tips over when the flag breaks.
    pole, cloth, knob = materials
    s = lambda v: unreal.Vector(v.x * size, v.y * size, v.z * size)
    add_mesh(blueprint, parent, "PoleLower", CYLINDER, s(unreal.Vector(0.0, 0.0, POLE_HALF / 2.0)), s(POLE_SCALE), pole)
    upper_handle, upper = add(blueprint, parent, unreal.SceneComponent, "Upper", s(unreal.Vector(0.0, 0.0, POLE_HALF)))
    add_mesh(blueprint, upper_handle, "PoleUpper", CYLINDER, s(unreal.Vector(0.0, 0.0, POLE_HALF / 2.0)), s(POLE_SCALE), pole)
    add_mesh(blueprint, upper_handle, "Cloth", CUBE, s(unreal.Vector(0.0, 25.0, 40.0)), s(unreal.Vector(0.02, 0.45, 0.3)), cloth)
    add_mesh(blueprint, upper_handle, "Knob", SPHERE, s(unreal.Vector(0.0, 0.0, POLE_HALF + 3.0)), s(unreal.Vector(0.09, 0.09, 0.09)), knob)
    return upper


def build_flag(materials):
    if library.does_asset_exist(FLAG_PATH):
        lines.append("BP_CheckpointFlag: already there")
        return unreal.load_asset(FLAG_PATH)
    blueprint, root = new_blueprint(FLAG_PATH)
    # Base drops into the ground when planted; RespawnPoint stays put, on the root.
    base_handle, _ = add(blueprint, root, unreal.SceneComponent, "Base")
    add_flag_shape(blueprint, base_handle, materials)
    add(blueprint, root, unreal.SceneComponent, "RespawnPoint", RESPAWN_OFFSET)
    bp_library.compile_blueprint(blueprint)
    library.save_asset(FLAG_PATH, False)
    lines.append("BP_CheckpointFlag: created")
    return blueprint


def build_item(materials):
    if library.does_asset_exist(ITEM_PATH):
        lines.append("BP_CheckpointItem: already there")
        return
    blueprint, root = new_blueprint(ITEM_PATH)
    visual_handle, _ = add(blueprint, root, unreal.SceneComponent, "Visual", unreal.Vector(0.0, 0.0, -35.0))
    add_flag_shape(blueprint, visual_handle, materials, size=0.6)
    _, trigger = add(blueprint, root, unreal.SphereComponent, "Trigger")
    trigger.set_editor_property("sphere_radius", 60.0)
    trigger.set_collision_profile_name("OverlapOnlyPawn")
    # Turns slowly in place, so it reads as something to pick up.
    _, spin = add(blueprint, root, unreal.RotatingMovementComponent, "Spin")
    spin.set_editor_property("rotation_rate", unreal.Rotator(0.0, 90.0, 0.0))
    bp_library.compile_blueprint(blueprint)
    library.save_asset(ITEM_PATH, False)
    lines.append("BP_CheckpointItem: created")


def setup_input():
    path = "/Game/Input/Actions/IA_UseItem"
    if not library.does_asset_exist(path):
        library.duplicate_asset("/Game/Input/Actions/IA_Jump", path)
        library.save_asset(path, False)
        lines.append("IA_UseItem: created from IA_Jump")
    action = unreal.load_asset(path)
    context = unreal.load_asset("/Game/Input/IMC_Default")
    keys_for = lambda: [str(m.get_editor_property("key").get_editor_property("key_name")) for m in context.get_editor_property("mappings") if m.get_editor_property("action") == action]
    mapped = keys_for()
    for key_name in ("E", "Gamepad_FaceButton_Left"):
        if key_name not in mapped:
            key = unreal.Key()
            key.set_editor_property("key_name", key_name)
            context.map_key(action, key)
            lines.append("IA_UseItem mapped to " + key_name)
    library.save_asset("/Game/Input/IMC_Default", False)
    lines.append("IA_UseItem keys now: {}".format(keys_for()))


def add_character_variables(flag):
    character = unreal.load_asset(CHARACTER_PATH)
    defaults = unreal.get_default_object(character.generated_class())
    wanted = (("HasFlagItem", bp_library.get_basic_type_by_name("bool")),
              ("ActiveFlag", bp_library.get_object_reference_type(flag.generated_class())))
    for name, pin_type in wanted:
        # add_member_variable would quietly add Name_0 next to an existing one, so check first.
        try:
            defaults.get_editor_property(name)
            lines.append("character {}: already there".format(name))
        except Exception:
            lines.append("character {}: {}".format(name, "added" if bp_library.add_member_variable(character, name, pin_type) else "NOT added"))
    bp_library.compile_blueprint(character)
    library.save_asset(CHARACTER_PATH, False)


def place_in_debug_level():
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not level.load_level("/Game/LV_Debug"):
        raise RuntimeError("Could not open LV_Debug")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    by_label = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
    if "Checkpoint Item" in by_label:
        lines.append("LV_Debug: pickup already placed")
        return
    spacing, row_length = 800.0, 13
    goal, goal_label = by_label["Goal"], by_label["Label Goal"]
    item_x = goal.get_actor_location().x
    for actor in (goal, goal_label):
        location = actor.get_actor_location()
        actor.set_actor_location(unreal.Vector(item_x + spacing, location.y, location.z), False, False)
    # Same formula as build_debug_level.py, so a rebuilt level matches.
    ground = by_label["Floor"]
    ground_length = spacing * (row_length + 3)
    ground.set_actor_location(unreal.Vector(ground_length / 2.0 - spacing * 2.0, 0.0, -50.0), False, False)
    ground.set_actor_scale3d(unreal.Vector(ground_length / 100.0, 16.0, 1.0))
    item = actors.spawn_actor_from_class(unreal.load_asset(ITEM_PATH).generated_class(), unreal.Vector(item_x, 0.0, 100.0))
    item.set_actor_label("Checkpoint Item")
    label = actors.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(item_x, 0.0, 320.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
    label.set_actor_label("Label Checkpoint Item")
    text = label.get_editor_property("text_render")
    text.set_text(unreal.Text("Checkpoint Item"))
    text.set_editor_property("world_size", 50.0)
    text.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    lines.append("LV_Debug: pickup at {}, goal moved to x {}, saved {}".format(item.get_actor_location(), item_x + spacing, level.save_current_level()))


flag_materials = (color_material("MI_FlagPole", (0.9, 0.88, 0.82)), color_material("MI_FlagCloth", (0.85, 0.1, 0.1)), color_material("MI_FlagKnob", (0.9, 0.65, 0.15)))
flag_blueprint = build_flag(flag_materials)
build_item(flag_materials)
setup_input()
add_character_variables(flag_blueprint)
place_in_debug_level()
with open(os.path.join(unreal.Paths.project_saved_dir(), "checkpoint_setup.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
