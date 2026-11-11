# Puts the newer gimmicks into LV_Debug for quick testing, on a floor of their own beside the PlayerStart on -Y (the
# ground is y -800..800; the lever test from setup_area_foundation.py is on +Y). Each has a label:
#   Spinning Gear (BP_SpinGear), Switch + red and blue blocks (BP_ToggleSwitch, BP_SwitchBlock), Cage Trap
#   (BP_CageTrap: back to the PlayerStart), Gondola (BP_Gondola) to a raised platform, Pressure Plate (a BP_Lever with
#   its handle hidden) that slides two stones out of a wall for a while, Star Coin (BP_StarCoin).
# Everything placed here is labelled "DG ..." and rebuilt on every run. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\add_new_gimmicks_to_debug.py -unattended -nop4 -nosplash -stdout
import math
import os

import unreal

LEVEL = "/Game/LV_Debug"
MACHINE = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine"
AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
COIN = "/Game/ThirdPerson/Coin/StarCoin/BP_StarCoin"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"
PREFIX = "DG "
FLOOR = (-1600.0, 6400.0, -4000.0, -800.0)   # x0, x1, y0, y1; top at 0

library = unreal.EditorAssetLibrary
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lines = []


def bp_class(path):
    asset = unreal.load_asset(path)
    if not asset:
        raise RuntimeError("Missing " + path)
    return asset.generated_class()


def material(path):
    return unreal.load_asset(path)


GREY = material("/Game/LevelPrototyping/Materials/MI_PrototypeGrid_Gray")
IRON = material(MACHINE + "/MI_MachineIron")
BRASS = material(MACHINE + "/MI_MachineBrass")
EMBER = material(AREA + "/MI_RuinsEmber")
RED_SOLID, BLUE_SOLID = material(MACHINE + "/MI_SwitchRed"), material(MACHINE + "/MI_SwitchBlue")
RED_GHOST, BLUE_GHOST = material(MACHINE + "/MI_SwitchGhostRed"), material(MACHINE + "/MI_SwitchGhostBlue")

if not level_subsystem.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith(PREFIX):
        actors.destroy_actor(actor)
start = next((a for a in actors.get_all_level_actors() if isinstance(a, unreal.PlayerStart)), None)
if start is None:
    raise RuntimeError("No PlayerStart in LV_Debug")
START = start.get_actor_location()


def spawn(actor_class, location, name, rotation=None):
    actor = actors.spawn_actor_from_class(actor_class, location, rotation or unreal.Rotator(0.0, 0.0, 0.0))
    if not actor:
        raise RuntimeError("Could not spawn " + name)
    actor.set_actor_label(PREFIX + name)
    actor.set_folder_path("NewGimmicks")
    return actor


def box(x0, x1, y0, y1, z0, z1, name, mat, mesh=CUBE):
    actor = spawn(unreal.StaticMeshActor, unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0), name)
    component = actor.get_editor_property("static_mesh_component")
    component.set_static_mesh(unreal.load_asset(mesh))
    component.set_material(0, mat)
    actor.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0))
    return actor


def label(text, x, y, z=320.0):
    actor = spawn(unreal.TextRenderActor, unreal.Vector(x, y, z), "Label " + text, unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
    render = actor.get_editor_property("text_render")
    render.set_text(unreal.Text(text))
    render.set_editor_property("world_size", 50.0)
    render.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)


def switch_block(x, y, top, red, size=300.0, thick=60.0):
    actor = spawn(bp_class(MACHINE + "/BP_SwitchBlock"), unreal.Vector(x, y, top - thick / 2.0), "Red Block" if red else "Blue Block")
    actor.set_actor_scale3d(unreal.Vector(size / 100.0, size / 100.0, thick / 100.0))
    actor.set_editor_property("IsRed", red)
    for component in actor.get_components_by_class(unreal.StaticMeshComponent):
        solid = component.get_name().startswith("Solid")
        component.set_material(0, (RED_SOLID if red else BLUE_SOLID) if solid else (RED_GHOST if red else BLUE_GHOST))


# The floor.
box(FLOOR[0], FLOOR[1], FLOOR[2], FLOOR[3], -100.0, 0.0, "Floor", GREY)
ROW = -1700.0

# Spinning gear: a big one to stand on, 60 cm up.
gear = spawn(bp_class(MACHINE + "/BP_SpinGear"), unreal.Vector(-1000.0, ROW, 45.0), "Spinning Gear")
gear.set_actor_scale3d(unreal.Vector(2.0, 2.0, 1.0))
gear.set_editor_property("SpinSpeed", 30.0)
label("Spinning Gear", -1000.0, ROW)

# Switch: red steps up while red is on, blue steps once switched.
spawn(bp_class(MACHINE + "/BP_ToggleSwitch"), unreal.Vector(300.0, ROW + 500.0, 0.0), "Switch")
switch_block(700.0, ROW, 100.0, True)
switch_block(1100.0, ROW, 200.0, False)
switch_block(1500.0, ROW, 300.0, True)
switch_block(1100.0, ROW - 400.0, 100.0, False)
label("Switch / Red & Blue Blocks", 900.0, ROW + 500.0)

# Cage trap: step onto the dark pad.
pad = (2200.0, 2600.0, ROW - 200.0, ROW + 200.0)
box(pad[0], pad[1], pad[2], pad[3], 0.0, 2.0, "Trap Pad", material(MACHINE + "/MI_MachineShadow"))
trap = spawn(bp_class(MACHINE + "/BP_CageTrap"), unreal.Vector((pad[0] + pad[1]) / 2.0, (pad[2] + pad[3]) / 2.0, 0.0), "Cage Trap")
for component in trap.get_components_by_class(unreal.BoxComponent):
    component.set_editor_property("box_extent", unreal.Vector(180.0, 180.0, 100.0))
trap.set_editor_property("RespawnLocation", START)
trap.set_editor_property("RespawnYaw", start.get_actor_rotation().yaw)
label("Cage Trap", 2400.0, ROW)

# Gondola: from the floor to a platform 3 m up, 20 m away.
station = unreal.Vector(3200.0, ROW, 0.0)
offset = unreal.Vector(2000.0, 0.0, 300.0)
gondola = spawn(bp_class(MACHINE + "/BP_Gondola"), station, "Gondola")
gondola.set_editor_property("TravelOffset", offset)
gondola.set_editor_property("TravelSeconds", 5.0)
gondola.set_editor_property("WaitSeconds", 2.5)
end = unreal.Vector(station.x + offset.x, station.y + offset.y, station.z + offset.z)
box(end.x + 160.0, end.x + 900.0, ROW - 400.0, ROW + 400.0, -100.0, end.z, "Gondola Platform", BRASS)
hang = 440.0
d = unreal.Vector(offset.x, offset.y, offset.z)
length = math.sqrt(d.x ** 2 + d.y ** 2 + d.z ** 2)
reach = 500.0
a = unreal.Vector(station.x - d.x / length * reach, station.y, station.z + hang - d.z / length * reach)
b = unreal.Vector(end.x + d.x / length * reach, end.y, end.z + hang + d.z / length * reach)
cable = spawn(unreal.StaticMeshActor, unreal.Vector((a.x + b.x) / 2.0, (a.y + b.y) / 2.0, (a.z + b.z) / 2.0), "Cable",
              unreal.MathLibrary.make_rot_from_z(unreal.Vector(b.x - a.x, b.y - a.y, b.z - a.z)))
cable_mesh = cable.get_editor_property("static_mesh_component")
cable_mesh.set_static_mesh(unreal.load_asset(CYLINDER))
cable_mesh.set_material(0, IRON)
cable_mesh.set_collision_profile_name("NoCollision")
cable.set_actor_scale3d(unreal.Vector(0.08, 0.08, math.sqrt((b.x - a.x) ** 2 + (b.z - a.z) ** 2) / 100.0))
label("Gondola", 3200.0, ROW, 600.0)

# Pressure plate: two stones slide out of a wall, stay a while, slide back; the plate springs up again.
ROW2 = -3200.0
plate = spawn(bp_class(AREA + "/BP_Lever"), unreal.Vector(-1000.0, ROW2, 0.0), "Pressure Plate")
for component in plate.get_components_by_class(unreal.StaticMeshComponent):
    name = component.get_name()
    if name.startswith("Handle") or name.startswith("Knob"):
        component.set_visibility(False, False)
        component.set_hidden_in_game(True, False)
        component.set_collision_profile_name("NoCollision")
    elif name.startswith("Base"):
        component.set_editor_property("relative_scale3d", unreal.Vector(1.8, 1.8, 0.06))
        component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 3.0))
        component.set_material(0, EMBER)
for component in plate.get_components_by_class(unreal.BoxComponent):
    component.set_editor_property("box_extent", unreal.Vector(90.0, 90.0, 40.0))
    component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 40.0))
plate.set_editor_property("ShowCamera", None)
plate.set_editor_property("ResetAfter", 8.0)
WALL_X = 600.0
box(WALL_X, WALL_X + 300.0, ROW2 - 600.0, ROW2 + 600.0, 0.0, 600.0, "Stone Wall", IRON)
for i, (y, top) in enumerate(((ROW2 - 250.0, 120.0), (ROW2 + 250.0, 240.0))):
    stone = spawn(bp_class(AREA + "/BP_Mechanism"), unreal.Vector(WALL_X + 150.0, y, top), "Sliding Stone")
    stone.set_actor_scale3d(unreal.Vector(2.0, 2.0, 0.6))
    stone.set_editor_property("Lever", plate)
    stone.set_editor_property("MoveOffset", unreal.Vector(-250.0, 0.0, 0.0))
    stone.set_editor_property("StartDelay", 0.3 * i)
    stone.set_editor_property("Duration", 0.8)
    stone.set_editor_property("Returns", True)
    stone.set_editor_property("ReturnAfter", 3.5)
    stone.set_editor_property("ReturnSeconds", 2.5)
label("Pressure Plate", -300.0, ROW2)

# Star coin.
spawn(bp_class(COIN), unreal.Vector(2400.0, ROW2, 100.0), "Star Coin")
label("Star Coin", 2400.0, ROW2)

lines.append("LV_Debug saved {}".format(level_subsystem.save_current_level()))
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith(PREFIX) and not actor.get_actor_label().startswith(PREFIX + "Label"):
        lines.append("{} at {}".format(actor.get_actor_label(), actor.get_actor_location()))
with open(os.path.join(unreal.Paths.project_saved_dir(), "debug_new_gimmicks.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
