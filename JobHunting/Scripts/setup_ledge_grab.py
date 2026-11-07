# Sets up the ledge grab: the IA_Grab input on Q and the gamepad's right shoulder, the character variables IsHanging,
# ClimbLift and ClimbTarget, and a wall with a ledge in LV_Debug in front of the goal. Safe to run again: whatever
# already exists is left alone. The character's part comes from LedgeGrab_Character.txt. With the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=setup_ledge_grab.py -unattended -nop4 -nosplash -stdout
import os

import unreal

CHARACTER_PATH = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1"
ACTION_PATH = "/Game/Input/Actions/IA_Grab"
# A block to hang from: 300 wide, 100 deep, its top 220 above the floor, facing the PlayerStart side of the row.
WALL_SIZE = unreal.Vector(100.0, 300.0, 220.0)
library = unreal.EditorAssetLibrary
bp_library = unreal.BlueprintEditorLibrary
lines = []

if not library.does_asset_exist(ACTION_PATH):
    library.duplicate_asset("/Game/Input/Actions/IA_Jump", ACTION_PATH)
    library.save_asset(ACTION_PATH, False)
    lines.append("IA_Grab: created from IA_Jump")
action = unreal.load_asset(ACTION_PATH)
# IA_Jump fires on Pressed/Released only; with no triggers, IA_Grab fires every frame while held (grab by holding Q).
if len(action.get_editor_property("triggers")):
    action.set_editor_property("triggers", [])
    library.save_loaded_asset(action, False)
    lines.append("IA_Grab: triggers cleared")
context = unreal.load_asset("/Game/Input/IMC_Default")
keys_for = lambda: [str(m.get_editor_property("key").get_editor_property("key_name")) for m in context.get_editor_property("mappings") if m.get_editor_property("action") == action]
for key_name in ("Q", "Gamepad_RightShoulder"):
    if key_name not in keys_for():
        key = unreal.Key()
        key.set_editor_property("key_name", key_name)
        context.map_key(action, key)
library.save_asset("/Game/Input/IMC_Default", False)
lines.append("IA_Grab keys: {}".format(keys_for()))

character = unreal.load_asset(CHARACTER_PATH)
defaults = unreal.get_default_object(character.generated_class())
vector = bp_library.get_struct_type(unreal.Vector.static_struct())
for name, pin_type in (("IsHanging", bp_library.get_basic_type_by_name("bool")), ("ClimbLift", vector), ("ClimbTarget", vector)):
    # add_member_variable would quietly add Name_0 next to an existing one, so check first.
    try:
        defaults.get_editor_property(name)
        lines.append("character {}: already there".format(name))
    except Exception:
        lines.append("character {}: {}".format(name, "added" if bp_library.add_member_variable(character, name, pin_type) else "NOT added"))
bp_library.compile_blueprint(character)
library.save_asset(CHARACTER_PATH, False)

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.load_level("/Game/LV_Debug"):
    raise RuntimeError("Could not open LV_Debug")
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
by_label = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
if "Ledge Wall" in by_label:
    lines.append("LV_Debug: ledge wall already placed")
else:
    spacing, row_length = 800.0, 14
    goal, goal_label = by_label["Goal"], by_label["Label Goal"]
    wall_x = goal.get_actor_location().x
    for actor in (goal, goal_label):
        location = actor.get_actor_location()
        actor.set_actor_location(unreal.Vector(wall_x + spacing, location.y, location.z), False, False)
    # Same formula as build_debug_level.py, so a rebuilt level matches.
    ground = by_label["Floor"]
    ground_length = spacing * (row_length + 3)
    ground.set_actor_location(unreal.Vector(ground_length / 2.0 - spacing * 2.0, 0.0, -50.0), False, False)
    ground.set_actor_scale3d(unreal.Vector(ground_length / 100.0, 16.0, 1.0))
    wall = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(wall_x, 0.0, WALL_SIZE.z / 2.0))
    wall.set_actor_label("Ledge Wall")
    mesh = wall.get_editor_property("static_mesh_component")
    mesh.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Cube"))
    mesh.set_material(0, unreal.load_asset("/Game/LevelPrototyping/Materials/MI_PrototypeGrid_Gray"))
    wall.set_actor_scale3d(unreal.Vector(WALL_SIZE.x / 100.0, WALL_SIZE.y / 100.0, WALL_SIZE.z / 100.0))
    label = actors.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(wall_x - 60.0, 0.0, 320.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
    label.set_actor_label("Label Ledge Wall")
    text = label.get_editor_property("text_render")
    text.set_text(unreal.Text("Ledge Wall (Q)"))
    text.set_editor_property("world_size", 50.0)
    text.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    lines.append("LV_Debug: ledge wall at x {} (top {}), goal moved to x {}, saved {}".format(wall_x, WALL_SIZE.z, wall_x + spacing, level.save_current_level()))
with open(os.path.join(unreal.Paths.project_saved_dir(), "ledge_grab_setup.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
