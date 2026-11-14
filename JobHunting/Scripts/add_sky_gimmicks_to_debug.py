# Puts the area 3 sky gimmicks into LV_Debug for quick testing, on a floor of their own past the "DG" floor on -Y
# (DG floor: y -4000..-800). Each has a label:
#   Vanishing Clouds (BP_VanishCloud, a row of 4 over a low pit), Crosswind (BP_WindZone, steady) and Gusty Crosswind
#   (gusts 1.8 s on / 2.2 s off) over marble beams, Updraft (BP_WindZone at pitch 90) up to a ledge, Moving Island
#   (BP_MovingIsland, rising and sideways ones), Sky Island and Cloud (plain meshes, to check the collision).
# Everything placed here is labelled "DS ..." and rebuilt on every run. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\add_sky_gimmicks_to_debug.py -unattended -nop4 -nosplash -stdout
import os

import unreal

LEVEL = "/Game/LV_Debug"
SKY = "/Game/ThirdPerson/Blueprints/Gimmicks/Sky"
CUBE = "/Engine/BasicShapes/Cube"
PREFIX = "DS "
FLOOR = (-1600.0, 6400.0, -7600.0, -4200.0)   # x0, x1, y0, y1; top at 0

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
MARBLE = unreal.load_asset(SKY + "/MI_SkyMarble")
CLOUD_MESH = unreal.load_asset(SKY + "/SM_SkyCloud")
ISLAND_MESH = unreal.load_asset(SKY + "/SM_SkyIsland")

if not level_subsystem.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith(PREFIX):
        actors.destroy_actor(actor)
# Anything else already standing on the planned floor would be in the way.
for actor in actors.get_all_level_actors():
    where = actor.get_actor_location()
    if FLOOR[0] <= where.x <= FLOOR[1] and FLOOR[2] <= where.y <= FLOOR[3] and -200.0 < where.z < 2000.0:
        lines.append("WARNING something already here: {} at {}".format(actor.get_actor_label(), where))


def spawn(actor_class, location, name, rotation=None):
    actor = actors.spawn_actor_from_class(actor_class, location, rotation or unreal.Rotator(0.0, 0.0, 0.0))
    if not actor:
        raise RuntimeError("Could not spawn " + name)
    actor.set_actor_label(PREFIX + name)
    actor.set_folder_path("SkyGimmicks")
    return actor


def box(x0, x1, y0, y1, z0, z1, name, mat):
    actor = spawn(unreal.StaticMeshActor, unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0), name)
    component = actor.get_editor_property("static_mesh_component")
    component.set_static_mesh(unreal.load_asset(CUBE))
    component.set_material(0, mat)
    actor.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0))
    return actor


def mesh_actor(mesh, location, scale, name):
    actor = spawn(unreal.StaticMeshActor, location, name)
    actor.get_editor_property("static_mesh_component").set_static_mesh(mesh)
    actor.set_actor_scale3d(scale)
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


def wind(x, y, z, along, width, height, yaw, pitch, strength, max_speed, on=0.0, off=0.0, name="Wind"):
    # (x, y, z) is the middle of the zone; "along" is the length in the blowing direction.
    actor = spawn(bp_class(SKY + "/BP_WindZone"), unreal.Vector(x, y, z), name, unreal.Rotator(roll=0.0, pitch=pitch, yaw=yaw))
    actor.set_actor_scale3d(unreal.Vector(along / 100.0, width / 100.0, height / 100.0))
    configure(actor, (("Strength", strength), ("MaxSpeed", max_speed), ("GustOn", on), ("GustOff", off), ("StartDelay", 0.0)))
    return actor


# The floor: two slabs with a shallow pit (-150) between x 0 and 1800 for the vanishing clouds - falling in only
# costs a walk back.
box(FLOOR[0], 0.0, FLOOR[2], FLOOR[3], -100.0, 0.0, "Floor", GREY)
box(1800.0, FLOOR[1], FLOOR[2], FLOOR[3], -100.0, 0.0, "Floor", GREY)
box(0.0, 1800.0, FLOOR[2], FLOOR[3], -250.0, -150.0, "Pit Floor", GREY)

# Row 1 (y -4900): vanishing clouds across the pit, 360 apart, flat.
ROW1 = -4900.0
for i in range(4):
    cloud = spawn(bp_class(SKY + "/BP_VanishCloud"), unreal.Vector(180.0 + 360.0 * i + 180.0, ROW1, 0.0), "Vanishing Cloud")
    cloud.set_actor_scale3d(unreal.Vector(2.6, 2.6, 1.0))
    configure(cloud, (("StaySeconds", 0.7), ("GoneSeconds", 3.0)))
label("Vanishing Clouds", 900.0, ROW1, 400.0)

# Row 1, far side: plain island and cloud meshes to stand on.
mesh_actor(ISLAND_MESH, unreal.Vector(2600.0, ROW1, 120.0), unreal.Vector(4.0, 4.0, 2.8), "Sky Island")
mesh_actor(CLOUD_MESH, unreal.Vector(3300.0, ROW1, 100.0), unreal.Vector(2.6, 2.6, 1.2), "Cloud")
label("Sky Island / Cloud", 2950.0, ROW1, 450.0)

# Row 2 (y -5900): two marble beams across the pit, crosswind blowing toward -Y (steady on the first, gusts on the second).
ROW2 = -5900.0
for i, (y, gusty) in enumerate(((ROW2 + 350.0, False), (ROW2 - 350.0, True))):
    box(0.0, 1800.0, y - 50.0, y + 50.0, -40.0, 0.0, "Marble Beam", MARBLE)
    wind(900.0, y, 150.0, 600.0, 1800.0, 300.0, -90.0, 0.0, 900.0, 600.0,
         1.8 if gusty else 0.0, 2.2 if gusty else 0.0, "Gusty Crosswind" if gusty else "Crosswind")
    label("Gusty Crosswind" if gusty else "Crosswind", 900.0, y, 400.0)

# Row 2, far side: updraft up to a ledge 6 m up.
box(3400.0, 3900.0, ROW2 - 250.0, ROW2 + 250.0, 500.0, 600.0, "Updraft Ledge", MARBLE)
wind(3000.0, ROW2, 400.0, 800.0, 300.0, 300.0, 0.0, 90.0, 2200.0, 900.0, name="Updraft")
box(2850.0, 3150.0, ROW2 - 150.0, ROW2 + 150.0, 0.0, 2.0, "Updraft Pad", MARBLE)
label("Updraft", 3000.0, ROW2, 950.0)

# Row 3 (y -6900): moving islands - one rising 4 m to a ledge, one ferrying 12 m across the pit.
ROW3 = -6900.0
rising = spawn(bp_class(SKY + "/BP_MovingIsland"), unreal.Vector(-600.0, ROW3, 0.0), "Moving Island Up")
configure(rising, (("MoveOffset", unreal.Vector(0.0, 0.0, 400.0)), ("MoveSeconds", 3.0), ("WaitSeconds", 1.5)))
box(-300.0, 200.0, ROW3 - 250.0, ROW3 + 250.0, 0.0, 400.0, "Rising Island Ledge", MARBLE)
side = spawn(bp_class(SKY + "/BP_MovingIsland"), unreal.Vector(300.0, ROW3 - 200.0, 0.0), "Moving Island Side")
configure(side, (("MoveOffset", unreal.Vector(1200.0, 0.0, 0.0)), ("MoveSeconds", 4.0), ("WaitSeconds", 1.5)))
label("Moving Island (up)", -600.0, ROW3, 600.0)
label("Moving Island (across the pit)", 900.0, ROW3 - 200.0, 400.0)

lines.append("LV_Debug saved {}".format(level_subsystem.save_current_level()))
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith(PREFIX) and not actor.get_actor_label().startswith(PREFIX + "Label"):
        lines.append("{} at {}".format(actor.get_actor_label(), actor.get_actor_location()))
with open(os.path.join(unreal.Paths.project_saved_dir(), "debug_sky_gimmicks.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
