# Puts area 4's light gimmicks into LV_Debug for quick testing, on a floor of their own past the "DS" floor on -Y
# (DS floor: y -7600..-4200). Each has a label:
#   Row 1  Blinking Beam  (BP_LightBeam, 2.5 s on / 1.5 s off) over 3 BP_LightPlatforms across a pit
#   Row 2  Sweeping Beam  (BP_LightBeam swaying 16 m along the row, 4 s each way) over 6 platforms: follow the light
#   Row 3  3 BP_LightShards and a BP_Iwato: once all 3 are taken its hidden lever is pulled, the rock (a BP_Mechanism)
#          sinks, the view cuts to the rock and the level's light goes from dim to its usual brightness. Behind the
#          rock: BP_Wings. Glide test: stairs up a 10 m tower (x 3200..3600) and a 20 m gap east to a 3 m ledge.
# Everything placed here is labelled "DH ..." and rebuilt on every run. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\add_heaven_light_to_debug.py -unattended -nop4 -nosplash -stdout
import os

import unreal

LEVEL = "/Game/LV_Debug"
HEAVEN = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
CUBE = "/Engine/BasicShapes/Cube"
PREFIX = "DH "
FLOOR = (-1600.0, 6400.0, -11600.0, -8200.0)   # x0, x1, y0, y1; top at 0
PIT = (0.0, 2700.0)                            # x range of the pit (floor at -250)

library = unreal.EditorAssetLibrary
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lines = []


def bp_class(path):
    asset = unreal.load_asset(path)
    if not asset:
        raise RuntimeError("Missing " + path)
    return asset.generated_class()


GREY = unreal.load_asset("/Game/LevelPrototyping/Materials/MI_PrototypeGrid_Gray")
MARBLE = unreal.load_asset(HEAVEN + "/MI_HeavenMarble")
STONE = unreal.load_asset(HEAVEN + "/MI_HeavenStone")

if not level_subsystem.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith(PREFIX):
        actors.destroy_actor(actor)
for actor in actors.get_all_level_actors():
    where = actor.get_actor_location()
    if FLOOR[0] <= where.x <= FLOOR[1] and FLOOR[2] <= where.y <= FLOOR[3] and -400.0 < where.z < 2000.0:
        lines.append("WARNING something already here: {} at {}".format(actor.get_actor_label(), where))


def spawn(actor_class, location, name, rotation=None):
    actor = actors.spawn_actor_from_class(actor_class, location, rotation or unreal.Rotator(0.0, 0.0, 0.0))
    if not actor:
        raise RuntimeError("Could not spawn " + name)
    actor.set_actor_label(PREFIX + name)
    actor.set_folder_path("HeavenLight")
    return actor


def box(x0, x1, y0, y1, z0, z1, name, mat):
    actor = spawn(unreal.StaticMeshActor, unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0), name)
    component = actor.get_editor_property("static_mesh_component")
    component.set_static_mesh(unreal.load_asset(CUBE))
    component.set_material(0, mat)
    actor.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0))
    return actor


def label(text, x, y, z=320.0):
    actor = spawn(unreal.TextRenderActor, unreal.Vector(x, y, z), "Label " + text, unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
    render = actor.get_editor_property("text_render")
    render.set_text(unreal.Text(text))
    render.set_editor_property("world_size", 50.0)
    render.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)


def configure(actor, pairs):
    for name, value in pairs:
        actor.set_editor_property(name, value)


def beam(x, y, width, z0, z1, name, pairs):
    actor = spawn(bp_class(HEAVEN + "/BP_LightBeam"), unreal.Vector(x, y, (z0 + z1) / 2.0), name)
    actor.set_actor_scale3d(unreal.Vector(width / 100.0, width / 100.0, (z1 - z0) / 100.0))
    configure(actor, pairs)
    return actor


def platform(x, y, size, light, name="Light Platform"):
    # Top at 0, 40 thick.
    actor = spawn(bp_class(HEAVEN + "/BP_LightPlatform"), unreal.Vector(x, y, -20.0), name)
    actor.set_actor_scale3d(unreal.Vector(size / 100.0, size / 100.0, 0.4))
    actor.set_editor_property("Beam", light)
    return actor


# The floor: two slabs with a pit (-250) between - falling in only costs a walk back.
box(FLOOR[0], PIT[0], FLOOR[2], FLOOR[3], -100.0, 0.0, "Floor", GREY)
box(PIT[1], FLOOR[1], FLOOR[2], FLOOR[3], -100.0, 0.0, "Floor", GREY)
box(PIT[0], PIT[1], FLOOR[2], FLOOR[3], -350.0, -250.0, "Pit Floor", GREY)

# Row 1: one wide blinking beam over 3 platforms, 480 apart (gaps of 280).
ROW1 = -8900.0
blink = beam(1350.0, ROW1, 1500.0, -300.0, 1500.0, "Blinking Beam",
             (("OnSeconds", 2.5), ("OffSeconds", 1.5), ("StartDelay", 0.0)))
for i in range(3):
    platform(870.0 + 480.0 * i, ROW1, 200.0, blink)
box(PIT[0] + 300.0, PIT[0] + 500.0, ROW1 - 100.0, ROW1 + 100.0, -40.0, 0.0, "Start Step", MARBLE)
box(PIT[1] - 500.0, PIT[1] - 300.0, ROW1 - 100.0, ROW1 + 100.0, -40.0, 0.0, "End Step", MARBLE)
label("Blinking Beam (2.5 s on / 1.5 s off)", 1350.0, ROW1, 900.0)

# Row 2: a narrow beam sweeping 1600 along the row over 6 platforms 330 apart: only those in the light hold.
ROW2 = -9900.0
sweep = beam(400.0, ROW2, 450.0, -300.0, 1500.0, "Sweeping Beam",
             (("MoveOffset", unreal.Vector(1900.0, 0.0, 0.0)), ("MoveSeconds", 4.0)))
for i in range(6):
    platform(400.0 + 380.0 * i, ROW2, 180.0, sweep)
label("Sweeping Beam (follow the light)", 1350.0, ROW2, 900.0)

# Row 3: 3 shards, the rock and its keeper.
ROW3 = -10900.0
for i in range(3):
    box(3400.0 + 500.0 * i - 60.0, 3400.0 + 500.0 * i + 60.0, ROW3 - 60.0, ROW3 + 60.0, 0.0, 80.0, "Shard Stand", MARBLE)
shards = [spawn(bp_class(HEAVEN + "/BP_LightShard"), unreal.Vector(3400.0 + 500.0 * i, ROW3, 160.0), "Light Shard")
          for i in range(3)]
lever = spawn(bp_class(AREA + "/BP_Lever"), unreal.Vector(5000.0, ROW3, -1500.0), "Iwato Lever (hidden)")
lever.set_actor_hidden_in_game(True)
rock = spawn(bp_class(AREA + "/BP_Mechanism"), unreal.Vector(5600.0, ROW3, 500.0), "Iwato Rock")
rock.set_actor_scale3d(unreal.Vector(1.0, 6.0, 5.0))
configure(rock, (("Lever", lever), ("MoveOffset", unreal.Vector(0.0, 0.0, -520.0)), ("StartDelay", 1.0), ("Duration", 3.0)))
try:
    rock.get_editor_property("Body").set_material(0, STONE)
except Exception as error:
    lines.append("rock material not set: {}".format(error))
camera = spawn(unreal.CameraActor, unreal.Vector(4300.0, ROW3 - 1400.0, 700.0), "Iwato Camera",
               unreal.Rotator(roll=0.0, pitch=-15.0, yaw=47.0))
camera.get_editor_property("camera_component").set_editor_property("constrain_aspect_ratio", False)
keeper = spawn(bp_class(HEAVEN + "/BP_Iwato"), unreal.Vector(5450.0, ROW3, 650.0), "Iwato", unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
configure(keeper, (("Shard1", shards[0]), ("Shard2", shards[1]), ("Shard3", shards[2]), ("Lever", lever),
                   ("ShowCamera", camera), ("ShowSeconds", 6.0), ("BlendSeconds", 4.0)))
# Dim to bright around the debug level's own light, without turning its sun.
for actor in actors.get_all_level_actors():
    if isinstance(actor, unreal.DirectionalLight):
        rotation = actor.get_actor_rotation()
        brightness = actor.get_editor_property("light_component").get_editor_property("intensity")
        configure(keeper, (("DarkRotation", rotation), ("BrightRotation", rotation),
                           ("DarkSun", brightness * 0.15), ("BrightSun", brightness)))
        lines.append("sun {} brightness {} mobility {}".format(rotation, brightness, actor.get_editor_property("light_component").get_editor_property("mobility")))
        break
for actor in actors.get_all_level_actors():
    if isinstance(actor, unreal.SkyLight):
        intensity = actor.get_editor_property("light_component").get_editor_property("intensity")
        configure(keeper, (("DarkSky", intensity * 0.2), ("BrightSky", intensity)))
        lines.append("sky light intensity {}".format(intensity))
        break
box(6000.0, 6400.0, ROW3 - 400.0, ROW3 + 400.0, 0.0, 1.0, "Behind the Rock", MARBLE)
label("Light Shards -> Iwato", 4400.0, ROW3, 500.0)
# Behind the rock: the wings (BP_Wings), and the glide test - stairs up a 10 m tower, then a 20 m gap to a 3 m ledge
# that a plain jump cannot reach.
spawn(bp_class(HEAVEN + "/BP_Wings"), unreal.Vector(6200.0, ROW3, 80.0), "Wings")
label("Wings", 6200.0, ROW3, 350.0)
for i in range(10):
    box(3200.0, 3600.0, -8200.0 - 100.0 * (i + 1), -8200.0 - 100.0 * i, 0.0, 100.0 * (i + 1), "Glide Stair", MARBLE)
box(3200.0, 3600.0, -9600.0, -9200.0, 0.0, 1000.0, "Glide Tower", STONE)
box(5600.0, 6000.0, -9600.0, -9200.0, 0.0, 300.0, "Glide Ledge", MARBLE)
label("Glide: hold Jump while falling", 4600.0, -9400.0, 1300.0)

# Melody stair (y -10300): 6 BP_ChimeJewels rising 80 cm each, ringing one after another up a pentatonic scale, each
# for 2 beats of 0.45 s out of a loop of 8 - jump on the beat. Falling only drops to the floor.
CHIME_ROW = -10300.0
PITCHES = (1.0, 9.0 / 8.0, 5.0 / 4.0, 3.0 / 2.0, 5.0 / 3.0, 2.0)
for i, pitch in enumerate(PITCHES):
    top = 80.0 * (i + 1)
    jewel = spawn(bp_class(HEAVEN + "/BP_ChimeJewel"), unreal.Vector(3900.0 + 400.0 * i, CHIME_ROW, top - 20.0), "Chime Jewel")
    jewel.set_actor_scale3d(unreal.Vector(2.2, 2.2, 0.4))
    # (0.45 s a beat was too fast for the user, 2026-11-14.)
    configure(jewel, (("BeatSeconds", 0.7), ("LoopBeats", 8), ("StartBeat", i), ("RingBeats", 2), ("Pitch", pitch)))
box(6200.0, 6400.0, CHIME_ROW - 150.0, CHIME_ROW + 150.0, 0.0, 560.0, "Melody Top", MARBLE)
label("Melody Stair (jump on the beat, 0.7 s)", 5000.0, CHIME_ROW, 900.0)

# Spider threads (west end, before the pit). 1: a still 15 m thread up to a ledge. 2: a swinging thread (28 deg,
# 3.5 s) that snaps after 7 s, from a step to a goal ledge over the pit.
thread1 = spawn(bp_class(HEAVEN + "/BP_SpiderThread"), unreal.Vector(-800.0, -9000.0, 1700.0), "Spider Thread")
configure(thread1, (("Length", 1500.0),))
box(-650.0, -250.0, -9200.0, -8800.0, 0.0, 1500.0, "Thread Top", STONE)
label("Spider Thread (W/S climb, Jump to let go)", -800.0, -9000.0, 1900.0)
thread2 = spawn(bp_class(HEAVEN + "/BP_SpiderThread"), unreal.Vector(-800.0, -10300.0, 1800.0), "Swinging Thread")
configure(thread2, (("Length", 1400.0), ("SwingDegrees", 28.0), ("SwingSeconds", 3.5), ("HoldSeconds", 7.0)))
box(-1100.0, -900.0, -10450.0, -10150.0, 0.0, 300.0, "Thread Step", MARBLE)
box(300.0, 600.0, -10450.0, -10150.0, -250.0, 700.0, "Swing Goal", MARBLE)
label("Swinging Thread (snaps after 7 s)", -800.0, -10300.0, 2000.0)

# Upside down (y -11350, west end): a BP_GravityZone 14 m long under a ceiling 6 m up with a 3 m gap. Walk in and
# fall up to the ceiling, cross the gap upside down, walk out the far end and fall back down.
GRAV_Y = -11350.0
gravity = spawn(bp_class(HEAVEN + "/BP_GravityZone"), unreal.Vector(-800.0, GRAV_Y, 300.0), "Gravity Zone")
gravity.set_actor_scale3d(unreal.Vector(14.0, 4.0, 6.0))
box(-1500.0, -950.0, GRAV_Y - 220.0, GRAV_Y + 220.0, 600.0, 650.0, "Ceiling", STONE)
box(-650.0, -100.0, GRAV_Y - 220.0, GRAV_Y + 220.0, 600.0, 650.0, "Ceiling", STONE)
label("Upside Down (walk in)", -800.0, GRAV_Y, 900.0)

lines.append("LV_Debug saved {}".format(level_subsystem.save_current_level()))
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith(PREFIX) and not actor.get_actor_label().startswith(PREFIX + "Label"):
        lines.append("{} at {}".format(actor.get_actor_label(), actor.get_actor_location()))
with open(os.path.join(unreal.Paths.project_saved_dir(), "debug_heaven_light.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
