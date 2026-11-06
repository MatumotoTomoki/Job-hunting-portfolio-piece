# Creates /Game/LV_Debug: a flat floor with each gimmick and item in a row, labelled, for quick testing.
# Editor only: nothing in the game opens this level. Never overwrites an existing LV_Debug.
import os
import unreal

LEVEL_PATH = "/Game/LV_Debug"
FLOOR_MESH = "/Engine/BasicShapes/Cube"
FLOOR_MATERIAL = "/Game/LevelPrototyping/Materials/MI_PrototypeGrid_Gray"
SPACING = 800.0
ITEM_HEIGHT = 100.0
ROTATING_FLOOR_HEIGHT = 60.0
# Half its 20 cm thickness down and half its 300 cm width past the 1600 cm wide ground: flush with the edge.
FALLING_FLOOR_HEIGHT = -10.0
FALLING_FLOOR_Y = 950.0
MOVING_PLATFORM_HEIGHT = 60.0
MOVING_PLATFORM_Y = -300.0

# (label, blueprint, height above the floor), in walking order from the PlayerStart.
ROW = [
    ("Item: Speed", "/Game/ThirdPerson/Item/BP_Item", ITEM_HEIGHT),
    ("Item: Jump Power", "/Game/ThirdPerson/Item/BP_Item2", ITEM_HEIGHT),
    ("Item: Double Jump", "/Game/ThirdPerson/Item/BP_2jump", ITEM_HEIGHT),
    ("Elevator", "/Game/ThirdPerson/Blueprints/Gimmicks/BP_Elevator", 0.0),
    ("Jump Pad", "/Game/LevelPrototyping/Interactable/JumpPad/BP_JumpPad", 0.0),
    ("Door", "/Game/LevelPrototyping/Interactable/Door/BP_DoorFrame", 0.0),
    ("Wobble Target", "/Game/LevelPrototyping/Interactable/Target/BP_WobbleTarget", ITEM_HEIGHT),
    ("Rotating Floor", "/Game/ThirdPerson/Blueprints/Gimmicks/BP_RotatingFloor", ROTATING_FLOOR_HEIGHT),
    # Off the edge of the ground (optional 4th value: Y) so there is open space to see it fall into.
    ("Falling Floor", "/Game/ThirdPerson/Blueprints/Gimmicks/BP_FallingFloor", FALLING_FLOOR_HEIGHT, FALLING_FLOOR_Y),
    # Starts on one side of the row and travels its default 600 across it.
    ("Moving Platform", "/Game/ThirdPerson/Blueprints/Gimmicks/BP_MovingPlatform", MOVING_PLATFORM_HEIGHT, MOVING_PLATFORM_Y),
    ("Timed Platform", "/Game/ThirdPerson/Blueprints/Gimmicks/BP_TimedPlatform", MOVING_PLATFORM_HEIGHT),
    ("Checkpoint Item", "/Game/ThirdPerson/Item/Checkpoint/BP_CheckpointItem", ITEM_HEIGHT),
    # The goal stays last: taking it ends the game, so everything else gets tested first.
    ("Goal", "/Game/ThirdPerson/Blueprints/BP_GoalItem", ITEM_HEIGHT),
]

if unreal.EditorAssetLibrary.does_asset_exist(LEVEL_PATH):
    raise RuntimeError(LEVEL_PATH + " already exists; delete it first to rebuild")

# Not World Partition: everything in this small level stays loaded.
if not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).new_level(LEVEL_PATH, False):
    raise RuntimeError("Could not create " + LEVEL_PATH)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def spawn(actor_class, location, label, yaw=0.0, pitch=0.0):
    rotation = unreal.Rotator(roll=0.0, pitch=pitch, yaw=yaw)
    actor = actors.spawn_actor_from_class(actor_class, location, rotation)
    if not actor:
        raise RuntimeError("Could not spawn " + label)
    actor.set_actor_label(label)
    return actor


def spawn_label(text, x, y):
    # Yaw 180 turns the text toward the PlayerStart side of the row.
    actor = spawn(unreal.TextRenderActor, unreal.Vector(x, y, 320.0), "Label " + text, yaw=180.0)
    component = actor.get_editor_property("text_render")
    component.set_text(unreal.Text(text))
    component.set_editor_property("world_size", 50.0)
    component.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)


# Floor: top surface at Z 0, running from behind the PlayerStart to past the last gimmick.
floor_length = SPACING * (len(ROW) + 3)
floor = spawn(unreal.StaticMeshActor, unreal.Vector(floor_length / 2.0 - SPACING * 2.0, 0.0, -50.0), "Floor")
floor_mesh = floor.get_editor_property("static_mesh_component")
floor_mesh.set_static_mesh(unreal.load_asset(FLOOR_MESH))
floor_mesh.set_material(0, unreal.load_asset(FLOOR_MATERIAL))
floor.set_actor_scale3d(unreal.Vector(floor_length / 100.0, 16.0, 1.0))

spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 1000.0), "Sun", yaw=30.0, pitch=-50.0)
sky = spawn(unreal.SkyLight, unreal.Vector(0.0, 0.0, 1000.0), "Sky Light")
sky_light = sky.get_editor_property("light_component")
sky_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
sky_light.set_editor_property("real_time_capture", True)
spawn(unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0), "Sky Atmosphere")

spawn(unreal.PlayerStart, unreal.Vector(-SPACING, 0.0, 100.0), "PlayerStart")
# Effekseer draws nothing without its system actor at the origin.
system = unreal.load_asset("/Effekseer/BluePrints/BP_EffekseerSystem")
spawn(system.generated_class(), unreal.Vector(0.0, 0.0, 0.0), "Effekseer System")

for index, entry in enumerate(ROW):
    label, path, height = entry[:3]
    y = entry[3] if len(entry) > 3 else 0.0
    x = SPACING * index
    blueprint = unreal.load_asset(path)
    if not blueprint:
        raise RuntimeError("Missing blueprint: " + path)
    spawn(blueprint.generated_class(), unreal.Vector(x, y, height), label)
    spawn_label(label, x, y)

if not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level():
    raise RuntimeError("Could not save " + LEVEL_PATH)

report = ["%s  %s  %s" % (a.get_actor_label(), a.get_class().get_name(), a.get_actor_location()) for a in actors.get_all_level_actors()]
with open(os.path.join(unreal.Paths.project_saved_dir(), "debug_level_report.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(report))
