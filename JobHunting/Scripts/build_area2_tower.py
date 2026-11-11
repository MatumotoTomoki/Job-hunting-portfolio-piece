# Builds /Game/LV_Area2_Tower, the second area: a machine tower at nightfall, climbed from where area 1 ends (72.6 m) to
# about 149 m. Harder than area 1: most jumps near the limit, small footholds, the abyss under nearly everything (a fall
# drops the player into BP_FallCatcher: back to the flag, or to the start), and traps in the dead ends.
#   A Engine Room (73-80 m)   red and blue switch blocks (BP_SwitchBlock) and switches (BP_ToggleSwitch): red steps to
#                             a ledge with a switch, flip, blue steps up to the door. A dark alcove off the ledge is a
#                             cage trap (BP_CageTrap: back to the start).
#   B Gear Shaft (80-97 m)    spinning gears (BP_SpinGear) and pistons in an open shaft; a side ledge with star coin 1
#                             next to a cage trap.
#   C Gondolas (97-103 m)     gondola (BP_Gondola) to a crumbling stop, a second gondola on to the second tower.
#   D Beams (103 m)           the checkpoint flag pickup; narrow beams to the cage room. Off the balcony, hard perches
#                             to the speed item (a dead end); with it, a gap too long for a plain jump leads to star
#                             coin 2. A beam that looks like the way ends in a cage trap.
#   E Heaven or Hell (103 m)  a walled platform: the only way on is one of two birdcages (BP_CagePair, PairId 1); the
#                             heaven one carries the player into the clock room.
#   F Clock Room (109-133 m)  climbed round the inside walls over an open drop: switch blocks with switches on
#                             pedestals, a gear, fading steps, a landing with a time rewind area, a piston, small
#                             ledges. Star coin 3 sits on a blue block off a switch pedestal.
#   G Roof (136-149 m)        a lift through the roof; the lever turns the great gear and slides twelve steps out of
#                             the spire one after another; the exit on top leads to LV_Area3_Sky (a placeholder).
# Jumps are checked against the player's own jump without items (speed 600), except the one speed gap (1500). Everything
# placed here is labelled "A2 ..." and rebuilt on every run. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\build_area2_tower.py -unattended -nop4 -nosplash -stdout
import math
import os

import unreal

LEVEL = "/Game/LV_Area2_Tower"
NEXT_LEVEL = "/Game/LV_Area3_Sky"
AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
MACHINE = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine"
GIMMICKS = "/Game/ThirdPerson/Blueprints/Gimmicks"
HELL = GIMMICKS + "/Hell"
ITEMS = "/Game/ThirdPerson/Item"
COIN = "/Game/ThirdPerson/Coin/StarCoin/BP_StarCoin"
CAGE_DOOR = "/Game/Prototype/Birdcage/BP_BirdcageDoor_Blender"
GAME_MODE = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode"
FALLBACK_CHARACTER = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1"
FLAT_COLOR = "/Game/LevelPrototyping/Materials/M_FlatCol"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"
PREFIX = "A2 "
B = 7260.0                     # area 1's wall top: this area's floor
FOOT = B - 2600.0              # supports end down here, lost in the mist
START = unreal.Vector(300.0, 0.0, B + 100.0)
SPEED_ITEM_SPEED = 1500.0      # BP_Item sets MaxWalkSpeed to this

library = unreal.EditorAssetLibrary
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
lines = []


# ----- what a jump can do -----
def player_defaults():
    pawn_class = None
    try:
        pawn_class = unreal.get_default_object(unreal.load_asset(GAME_MODE).generated_class()).get_editor_property("default_pawn_class")
    except Exception as error:
        lines.append("game mode pawn not read: {}".format(error))
    if pawn_class is None:
        pawn_class = unreal.load_asset(FALLBACK_CHARACTER).generated_class()
    return unreal.get_default_object(pawn_class)


move = player_defaults().get_editor_property("character_movement")
jump_z = move.get_editor_property("jump_z_velocity")
gravity = 980.0 * move.get_editor_property("gravity_scale")
WALK = move.get_editor_property("max_walk_speed")
APEX = jump_z * jump_z / (2.0 * gravity)


def reach_up(rise, speed=None):
    fall = APEX - rise
    if fall <= 0:
        return 0.0
    return (speed or WALK) * (jump_z / gravity + math.sqrt(2.0 * fall / gravity))


lines.append("jump {:.0f}, walk {:.0f}: flat reach {:.0f}, apex {:.0f}".format(jump_z, WALK, reach_up(0.0), APEX))
checks = []
HARD = 0.9


def jump(name, gap, rise, ratio=HARD, speed=None):
    limit = ratio * reach_up(max(rise, 0.0), speed)
    checks.append((name, gap, rise, limit))
    if rise > 0.8 * APEX or gap > limit:
        raise RuntimeError("Out of reach: {} gap {:.0f} rise {:.0f} (limit {:.0f})".format(name, gap, rise, limit))


# Footprints for the checks: ("rect", x0, x1, y0, y1) or ("circle", x, y, r).
def rect(cx, cy, sx, sy=None):
    sy = sx if sy is None else sy
    return ("rect", cx - sx / 2.0, cx + sx / 2.0, cy - sy / 2.0, cy + sy / 2.0)


def span(x0, x1, y0, y1):
    return ("rect", x0, x1, y0, y1)


def circle(cx, cy, r):
    return ("circle", cx, cy, r)


def gap(a, b):
    def nearest(shape, px, py):
        if shape[0] == "rect":
            return min(max(px, shape[1]), shape[2]), min(max(py, shape[3]), shape[4])
        dx, dy = px - shape[1], py - shape[2]
        d = math.hypot(dx, dy) or 1.0
        return shape[1] + dx / d * min(d, shape[3]), shape[2] + dy / d * min(d, shape[3])

    if a[0] == "rect" and b[0] == "rect":
        gx = max(0.0, b[1] - a[2], a[1] - b[2])
        gy = max(0.0, b[3] - a[4], a[3] - b[4])
        return math.hypot(gx, gy)
    if a[0] == "circle" and b[0] == "circle":
        return max(0.0, math.hypot(a[1] - b[1], a[2] - b[2]) - a[3] - b[3])
    c, r = (a, b) if a[0] == "circle" else (b, a)
    px, py = nearest(r, c[1], c[2])
    return max(0.0, math.hypot(px - c[1], py - c[2]) - c[3])


# ----- materials -----
def flat(name, color):
    path = MACHINE + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    instance = tools.create_asset(name, MACHINE, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, unreal.load_asset(FLAT_COLOR))
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(instance, "Base Color", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    library.save_asset(path, False)
    lines.append("created " + path)
    return instance


IRON = unreal.load_asset(MACHINE + "/MI_MachineIron")
BRASS = unreal.load_asset(MACHINE + "/MI_MachineBrass")
WALL = flat("MI_TowerWall", (0.17, 0.18, 0.21))
FLOOR = flat("MI_TowerFloor", (0.3, 0.28, 0.26))
EMBER = unreal.load_asset(AREA + "/MI_RuinsEmber")
RED_SOLID = unreal.load_asset(MACHINE + "/MI_SwitchRed")
BLUE_SOLID = unreal.load_asset(MACHINE + "/MI_SwitchBlue")
RED_GHOST = unreal.load_asset(MACHINE + "/MI_SwitchGhostRed")
BLUE_GHOST = unreal.load_asset(MACHINE + "/MI_SwitchGhostBlue")


def bp_class(path):
    asset = unreal.load_asset(path)
    if not asset:
        raise RuntimeError("Missing " + path)
    return asset.generated_class()


def elevator_half():
    source = unreal.load_asset(GIMMICKS + "/BP_Elevator")
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(source):
        component = data_library.get_object(data_library.get_data(handle))
        if isinstance(component, unreal.StaticMeshComponent):
            scale = component.get_editor_property("relative_scale3d")
            extent = component.get_editor_property("static_mesh").get_bounds().box_extent
            return unreal.Vector(extent.x * scale.x, extent.y * scale.y, extent.z * scale.z)
    raise RuntimeError("No floor in BP_Elevator")


PLAT = elevator_half()
P = 2.0 * PLAT.x   # the platform gimmicks' width

# ----- the level -----
if library.does_asset_exist(LEVEL):
    if not level_subsystem.load_level(LEVEL):
        raise RuntimeError("Could not open " + LEVEL)
    for actor in actors.get_all_level_actors():
        label = actor.get_actor_label()
        # The placeholder's actors go too.
        if label.startswith(PREFIX) or label in ("PlayerStart", "Sun", "Sky Light", "Sky Atmosphere", "Effekseer System"):
            actors.destroy_actor(actor)
else:
    if not level_subsystem.new_level(LEVEL, False):
        raise RuntimeError("Could not create " + LEVEL)

counter = [0]


def spawn(actor_class, location, name, folder, rotation=None):
    actor = actors.spawn_actor_from_class(actor_class, location, rotation or unreal.Rotator(0.0, 0.0, 0.0))
    if not actor:
        raise RuntimeError("Could not spawn " + name)
    counter[0] += 1
    actor.set_actor_label("{}{:03d} {}".format(PREFIX, counter[0], name))
    actor.set_folder_path("Area2/" + folder)
    return actor


def box(x0, x1, y0, y1, z0, z1, folder, name="Block", material=None, mesh=CUBE):
    actor = spawn(unreal.StaticMeshActor, unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0), name, folder)
    component = actor.get_editor_property("static_mesh_component")
    component.set_static_mesh(unreal.load_asset(mesh))
    component.set_material(0, material or WALL)
    actor.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0))
    return actor


def ledge(shape, top, folder, name="Ledge", material=None, thick=60.0, support=False):
    # A foothold on `shape` (a rect footprint); with `support`, a girder under it down into the mist.
    _, x0, x1, y0, y1 = shape
    box(x0, x1, y0, y1, top - thick, top, folder, name, material or IRON)
    if support:
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        box(cx - 25.0, cx + 25.0, cy - 25.0, cy + 25.0, FOOT, top - thick, folder, "Girder", IRON)
    return shape


def wall(axis, a0, a1, c0, c1, z0, z1, folder, openings=(), material=None):
    def piece(u0, u1, v0, v1):
        if u1 - u0 < 1.0 or v1 - v0 < 1.0:
            return
        if axis == "x":
            box(u0, u1, c0, c1, v0, v1, folder, "Wall", material)
        else:
            box(c0, c1, u0, u1, v0, v1, folder, "Wall", material)

    cursor = a0
    for u0, u1, v0, v1 in sorted(openings):
        piece(cursor, u0, z0, z1)
        piece(u0, u1, z0, v0)
        piece(u0, u1, v1, z1)
        cursor = u1
    piece(cursor, a1, z0, z1)


def lamp(x, y, z, folder, strength=4000.0, radius=1600.0):
    box(x - 20.0, x + 20.0, y - 20.0, y + 20.0, z - 30.0, z, folder, "Lamp", EMBER, CYLINDER)
    light = spawn(unreal.PointLight, unreal.Vector(x, y, z + 40.0), "Lamp Light", folder)
    component = light.get_editor_property("point_light_component")
    component.set_editor_property("intensity", strength)
    component.set_editor_property("attenuation_radius", radius)
    component.set_editor_property("light_color", unreal.Color(r=255, g=170, b=90, a=255))
    component.set_editor_property("cast_shadows", False)


def platform(actor_class, x, y, top, name, folder, settings=()):
    actor = spawn(actor_class, unreal.Vector(x, y, top - PLAT.z), name, folder)
    for key, value in settings:
        actor.set_editor_property(key, value)
    return rect(x, y, P)


def gear(x, y, top, radius, spin, folder):
    actor = spawn(bp_class(MACHINE + "/BP_SpinGear"), unreal.Vector(x, y, top - 15.0), "Spinning Gear", folder)
    actor.set_actor_scale3d(unreal.Vector(radius / 100.0, radius / 100.0, 1.0))
    actor.set_editor_property("SpinSpeed", spin)
    box(x - 18.0, x + 18.0, y - 18.0, y + 18.0, FOOT, top - 40.0, folder, "Axle", IRON, CYLINDER)
    return circle(x, y, radius * 0.92)   # a little inside the tooth tips


def switch_block(shape, top, red, folder, thick=60.0):
    _, x0, x1, y0, y1 = shape
    actor = spawn(bp_class(MACHINE + "/BP_SwitchBlock"), unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, top - thick / 2.0),
                  "Red Block" if red else "Blue Block", folder)
    actor.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, thick / 100.0))
    actor.set_editor_property("IsRed", red)
    for component in actor.get_components_by_class(unreal.StaticMeshComponent):
        if component.get_name().startswith("Solid"):
            component.set_material(0, RED_SOLID if red else BLUE_SOLID)
        else:
            component.set_material(0, RED_GHOST if red else BLUE_GHOST)
    return shape


def toggle(x, y, top, folder):
    spawn(bp_class(MACHINE + "/BP_ToggleSwitch"), unreal.Vector(x, y, top), "Switch", folder)


def trap(shape, top, folder):
    _, x0, x1, y0, y1 = shape
    actor = spawn(bp_class(MACHINE + "/BP_CageTrap"), unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, top), "Cage Trap", folder)
    for component in actor.get_components_by_class(unreal.BoxComponent):
        component.set_editor_property("box_extent", unreal.Vector((x1 - x0) / 2.0 - 20.0, (y1 - y0) / 2.0 - 20.0, 100.0))
    actor.set_editor_property("RespawnLocation", START)
    actor.set_editor_property("RespawnYaw", 0.0)
    return actor


def coin(x, y, top, folder):
    return spawn(bp_class(COIN), unreal.Vector(x, y, top + 100.0), "Star Coin", folder)


def item(path, x, y, top, name, folder):
    return spawn(bp_class(path), unreal.Vector(x, y, top + 100.0), name, folder)


def cable(a, b, folder):
    d = unreal.Vector(b.x - a.x, b.y - a.y, b.z - a.z)
    length = math.sqrt(d.x * d.x + d.y * d.y + d.z * d.z)
    mid = unreal.Vector((a.x + b.x) / 2.0, (a.y + b.y) / 2.0, (a.z + b.z) / 2.0)
    actor = spawn(unreal.StaticMeshActor, mid, "Cable", folder, unreal.MathLibrary.make_rot_from_z(d))
    component = actor.get_editor_property("static_mesh_component")
    component.set_static_mesh(unreal.load_asset(CYLINDER))
    component.set_material(0, IRON)
    component.set_collision_profile_name("NoCollision")
    actor.set_actor_scale3d(unreal.Vector(0.08, 0.08, length / 100.0))


def gondola(shape, top, offset, seconds, folder):
    _, x0, x1, y0, y1 = shape
    start = unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, top)
    actor = spawn(bp_class(MACHINE + "/BP_Gondola"), start, "Gondola", folder)
    actor.set_editor_property("TravelOffset", offset)
    actor.set_editor_property("TravelSeconds", seconds)
    actor.set_editor_property("WaitSeconds", 2.5)
    hang = 440.0
    a = unreal.Vector(start.x, start.y, start.z + hang)
    b = unreal.Vector(start.x + offset.x, start.y + offset.y, start.z + offset.z + hang)
    reach = 600.0
    length = math.sqrt(offset.x ** 2 + offset.y ** 2 + offset.z ** 2)
    ux, uy, uz = offset.x / length, offset.y / length, offset.z / length
    cable(unreal.Vector(a.x - ux * reach, a.y - uy * reach, a.z - uz * reach), unreal.Vector(b.x + ux * reach, b.y + uy * reach, b.z + uz * reach), folder)
    return rect(start.x + offset.x, start.y + offset.y, x1 - x0)   # where it arrives


def mechanism(lever, location, size, offset, delay, seconds, name, folder, material=None):
    actor = spawn(bp_class(AREA + "/BP_Mechanism"), location, name, folder)
    actor.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
    actor.set_editor_property("Lever", lever)
    actor.set_editor_property("MoveOffset", offset)
    actor.set_editor_property("StartDelay", delay)
    actor.set_editor_property("Duration", seconds)
    actor.set_editor_property("Returns", False)
    if material:
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            component.set_material(0, material)
    return actor


# ===== sky: nightfall over the machine tower =====
F = "Sky"
sun = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, B + 9000.0), "Sun", F, unreal.Rotator(roll=0.0, pitch=-8.0, yaw=150.0))
sun_light = sun.get_editor_property("directional_light_component")
sun_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
sun_light.set_editor_property("intensity", 3.5)
sun_light.set_editor_property("light_color", unreal.Color(r=255, g=150, b=130, a=255))
sun_light.set_editor_property("atmosphere_sun_light", True)
sky = spawn(unreal.SkyLight, unreal.Vector(0.0, 0.0, B + 9000.0), "Sky Light", F)
sky_light = sky.get_editor_property("light_component")
sky_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
sky_light.set_editor_property("real_time_capture", True)
spawn(unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0), "Sky Atmosphere", F)
spawn(unreal.VolumetricCloud, unreal.Vector(0.0, 0.0, 0.0), "Clouds", F)
fog = spawn(unreal.ExponentialHeightFog, unreal.Vector(0.0, 0.0, B - 1500.0), "Mist", F)
fog_component = fog.get_editor_property("component")
fog_component.set_editor_property("fog_density", 0.035)
fog_component.set_editor_property("fog_height_falloff", 0.0012)
fog_component.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.22, 0.2, 0.3, 1.0))
# Just under the engine room's floor: everything else is higher.
catcher = spawn(bp_class(MACHINE + "/BP_FallCatcher"), unreal.Vector(7000.0, 3500.0, B - 500.0), "Fall Catcher", F)
catcher.set_actor_scale3d(unreal.Vector(220.0, 160.0, 4.0))

# ===== A. Engine Room (73-80 m) =====
F = "A Engine Room"
spawn(unreal.PlayerStart, START, "PlayerStart", F)
spawn(bp_class(AREA + "/BP_AreaStart"), unreal.Vector(START.x, 300.0, B + 200.0), "Area Start", F)
spawn(bp_class("/Effekseer/BluePrints/BP_EffekseerSystem"), unreal.Vector(0.0, 0.0, 0.0), "Effekseer System", F)
RX0, RX1, RY0, RY1 = 0.0, 2400.0, -1200.0, 1200.0
T = 300.0
ROOM_TOP = B + 1400.0
box(RX0 - T, RX1 + T, RY0 - T, RY1 + T, B - 300.0, B, F, "Room Floor", FLOOR)
DOOR_SILL = B + 700.0
wall("y", RY0 - T, RY1 + T, RX0 - T, RX0, B, ROOM_TOP, F)
wall("y", RY0 - T, RY1 + T, RX1, RX1 + T, B, ROOM_TOP, F, openings=[(600.0, 1000.0, DOOR_SILL, DOOR_SILL + 380.0)])
wall("x", RX0, RX1, RY1, RY1 + T, B, ROOM_TOP, F)
wall("x", RX0, RX1, RY0 - T, RY0, B, ROOM_TOP, F, openings=[(2000.0, 2400.0, B + 400.0, B + 700.0)])
box(RX0 - T, RX1 + T, RY0 - T, RY1 + T, ROOM_TOP, ROOM_TOP + 100.0, F, "Room Ceiling", WALL)
toggle(500.0, 650.0, B, F)
previous, top = span(RX0, RX1, RY0, RY1), B
for i, x in enumerate((600.0, 1000.0, 1400.0)):
    top += 100.0
    here = switch_block(rect(x, -700.0, 300.0), top, True, F)
    if i:
        jump("engine room red step", gap(previous, here), 100.0)
    previous = here
top += 100.0
LEDGE_A = ledge(span(1700.0, 2100.0, -900.0, -500.0), top, F, "Switch Ledge", FLOOR)
box(1700.0, 2100.0, -900.0, -500.0, B, top - 60.0, F, "Ledge Pillar", WALL)
jump("red step -> switch ledge", gap(previous, LEDGE_A), 100.0)
toggle(1900.0, -700.0, top, F)
# Trap 1: the dark alcove beside the switch ledge.
alcove = ledge(span(2000.0, 2400.0, -1200.0, -900.0), top, F, "Alcove Floor", FLOOR)
trap(alcove, top, F)
previous = LEDGE_A
for x, y in ((1900.0, -150.0), (1900.0, 350.0), (2150.0, 800.0)):
    top += 100.0
    here = switch_block(rect(x, y, 300.0), top, False, F)
    jump("engine room blue step", gap(previous, here), 100.0)
    previous = here
jump("blue step -> door", RX1 - previous[2], DOOR_SILL - top)
for x, y in ((300.0, -900.0), (1200.0, 1000.0), (2200.0, 0.0)):
    lamp(x, y, B + 1000.0, F, 3000.0, 1500.0)

# ===== B. Gear Shaft (80-97 m) =====
F = "B Gear Shaft"
STEP0 = ledge(span(RX1 + T, 3000.0, 650.0, 950.0), DOOR_SILL, F, "Door Bracket", IRON, support=True)
route = [
    ("gear", 3400.0, 800.0, 160.0, 60.0, 35.0),
    ("gear", 3850.0, 330.0, 160.0, 100.0, -45.0),
]
previous, top = STEP0, DOOR_SILL
for kind, x, y, r, rise, spin in route:
    top += rise
    here = gear(x, y, top, r, spin, F)
    jump("shaft gear", gap(previous, here), rise)
    previous = here
piston1 = platform(bp_class(GIMMICKS + "/BP_MovingPlatform"), 3900.0, -300.0, top, "Piston", F,
                   (("MoveOffset", unreal.Vector(0.0, 0.0, 600.0)), ("MoveSeconds", 2.2), ("WaitSeconds", 0.8)))
jump("gear -> piston", gap(previous, piston1), 0.0)
top += 600.0
L3 = ledge(span(4200.0, 4500.0, -450.0, -150.0), top, F, "Bracket", IRON, support=True)
jump("piston -> bracket", gap(piston1, L3), 0.0)
top += 100.0
G3 = gear(4900.0, -300.0, top, 200.0, 30.0, F)
jump("bracket -> big gear", gap(L3, G3), 100.0)
# Star coin 1 on a small bracket beyond the big gear, next to a doorway that is a trap.
D1 = ledge(rect(5300.0, -750.0, 180.0), top + 100.0, F, "Coin Bracket", BRASS, support=True)
jump("big gear -> coin bracket", gap(G3, D1), 100.0)
coin(5300.0, -750.0, top + 100.0, F)
D2 = ledge(span(5050.0, 5550.0, -1450.0, -1050.0), top + 100.0, F, "Dead End", FLOOR, support=True)
box(5050.0, 5550.0, -1550.0, -1450.0, top + 100.0, top + 600.0, F, "Doorway Wall", WALL)
box(5200.0, 5400.0, -1460.0, -1440.0, top + 100.0, top + 420.0, F, "Dark Door", unreal.load_asset(MACHINE + "/MI_MachineShadow"))
trap(D2, top + 100.0, F)
top += 100.0
G4 = gear(5100.0, 350.0, top, 160.0, -40.0, F)
jump("big gear -> gear", gap(G3, G4), 100.0)
piston2 = platform(bp_class(GIMMICKS + "/BP_MovingPlatform"), 4500.0, 800.0, top, "Piston", F,
                   (("MoveOffset", unreal.Vector(0.0, 0.0, 700.0)), ("MoveSeconds", 2.6), ("WaitSeconds", 0.8)))
jump("gear -> piston", gap(G4, piston2), 0.0)
top += 700.0
U1_TOP = top + 40.0
U1 = ledge(span(3000.0, 4200.0, 600.0, 1200.0), U1_TOP, F, "Upper Balcony", FLOOR, thick=100.0, support=True)
jump("piston -> upper balcony", gap(piston2, U1), U1_TOP - top)
for x, y, z in ((3000.0, -600.0, B + 1300.0), (5200.0, 0.0, B + 1900.0), (3600.0, 900.0, U1_TOP + 300.0)):
    lamp(x, y, z, F)
# Background machinery: tall girders.
for x, y in ((2900.0, -1300.0), (5800.0, -300.0), (5800.0, 1300.0), (4300.0, -1500.0)):
    box(x - 60.0, x + 60.0, y - 60.0, y + 60.0, FOOT, U1_TOP + 900.0, F, "Column", IRON)

# ===== C. Gondolas (97-103 m) =====
F = "C Gondolas"
station1 = rect(3300.0, 1400.0, P)
jump("balcony -> gondola", gap(U1, station1), 0.0)
arrive1 = gondola(station1, U1_TOP, unreal.Vector(0.0, 2000.0, 300.0), 6.0, F)
stop_top = U1_TOP + 300.0
mid = platform(bp_class(GIMMICKS + "/BP_FallingFloor"), 3300.0, 3800.0, stop_top, "Crumbling Stop", F)
jump("gondola -> crumbling stop", gap(arrive1, mid), 0.0)
station2 = rect(3300.0, 4200.0, P)
jump("crumbling stop -> gondola", gap(mid, station2), 0.0)
arrive2 = gondola(station2, stop_top, unreal.Vector(0.0, 2300.0, 400.0), 7.0, F)
D_TOP = stop_top + 400.0

# ===== D. Beams (103 m) =====
F = "D Beams"
T2 = ledge(span(2800.0, 4400.0, 6700.0, 7600.0), D_TOP, F, "Second Tower Balcony", FLOOR, thick=150.0, support=True)
jump("gondola -> balcony", gap(arrive2, T2), 0.0)
item(ITEMS + "/Checkpoint/BP_CheckpointItem", 3600.0, 7150.0, D_TOP, "Checkpoint Item", F)
lamp(3000.0, 7500.0, D_TOP + 300.0, F)
# Dead end with the speed item: hard perches off the balcony's west side.
previous, perch_top = T2, D_TOP
for x in (2440.0, 1940.0):
    perch_top += 100.0
    here = ledge(rect(x, 7400.0, 160.0), perch_top, F, "Perch", BRASS, support=True)
    jump("speed perch", gap(previous, here), 100.0)
    previous = here
item(ITEMS + "/BP_Item", 1940.0, 7400.0, perch_top, "Speed Item", F)
# The way on: narrow beams.
previous = T2
BEAM_Y = 7150.0
for x0, x1 in ((4720.0, 5600.0), (5950.0, 6800.0), (7150.0, 8000.0)):
    here = ledge(span(x0, x1, BEAM_Y - 50.0, BEAM_Y + 50.0), D_TOP, F, "Beam", IRON, support=True)
    jump("beam", gap(previous, here), 0.0)
    previous = here
# Trap 3: a beam off to the south that looks like the way, ending on a landing that is a trap.
side = ledge(span(6300.0, 6400.0, 6300.0, 7100.0), D_TOP, F, "Side Beam", IRON, support=True)
fake = ledge(span(6050.0, 6650.0, 5750.0, 6300.0), D_TOP, F, "Landing", FLOOR, support=True)
trap(fake, D_TOP, F)
# With the speed item: a run the length of the balcony and one long jump off its north edge to star coin 2.
K = ledge(span(3400.0, 3800.0, 8400.0, 8700.0), D_TOP, F, "Far Ledge", BRASS, support=True)
jump("balcony -> far ledge (speed)", gap(T2, K), 0.0, 0.6, SPEED_ITEM_SPEED)
if gap(T2, K) < reach_up(0.0):
    raise RuntimeError("The far ledge can be reached without the speed item")
coin(3600.0, 8550.0, D_TOP, F)
E_X0 = 8400.0
E = span(E_X0, 9600.0, 6600.0, 7700.0)
jump("beam -> cage platform", gap(previous, E), 0.0)

# ===== E. Heaven or Hell (103 m) =====
F = "E Heaven or Hell"
ledge(E, D_TOP, F, "Cage Platform", FLOOR, thick=150.0, support=True)
wall("y", 6500.0, 7800.0, 9600.0, 9700.0, D_TOP, D_TOP + 900.0, F)
wall("x", E_X0, 9600.0, 7700.0, 7800.0, D_TOP, D_TOP + 900.0, F)
wall("x", E_X0, 9600.0, 6500.0, 6600.0, D_TOP, D_TOP + 900.0, F)
F_TOP = D_TOP + 500.0
LANDING = (10250.0, 6500.0)
target = spawn(unreal.TargetPoint, unreal.Vector(LANDING[0], LANDING[1], F_TOP), "Cage Destination", F)
cage_class = bp_class(CAGE_DOOR)
cage_a = spawn(cage_class, unreal.Vector(9250.0, 6850.0, D_TOP), "Choice Cage A", F, unreal.Rotator(roll=0.0, pitch=0.0, yaw=90.0))
cage_b = spawn(cage_class, unreal.Vector(9250.0, 7450.0, D_TOP), "Choice Cage B", F, unreal.Rotator(roll=0.0, pitch=0.0, yaw=90.0))
for cage in (cage_a, cage_b):
    cage.set_editor_property("Destination", target)
pair = spawn(bp_class(HELL + "/BP_CagePair"), unreal.Vector(9250.0, 7150.0, D_TOP + 150.0), "Cage Pair", F)
pair.set_editor_property("CageA", cage_a)
pair.set_editor_property("CageB", cage_b)
pair.set_editor_property("PairId", 1)
sign = spawn(unreal.TextRenderActor, unreal.Vector(8900.0, 7150.0, D_TOP + 450.0), "Sign", F, unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
text = sign.get_editor_property("text_render")
text.set_text(unreal.Text("Heaven or Hell"))
text.set_editor_property("world_size", 60.0)
text.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
lamp(8600.0, 7150.0, D_TOP + 600.0, F)

# ===== F. Clock Room (109-133 m) =====
F = "F Clock Room"
CX0, CX1, CY0, CY1 = 10000.0, 12400.0, 5300.0, 7700.0
CLOCK_TOP = F_TOP + 2800.0      # the roof's top
wall("y", CY0 - T, CY1 + T, CX0 - T, CX0, FOOT, CLOCK_TOP, F)
wall("y", CY0 - T, CY1 + T, CX1, CX1 + T, FOOT, CLOCK_TOP, F)
wall("x", CX0, CX1, CY1, CY1 + T, FOOT, CLOCK_TOP, F)
wall("x", CX0, CX1, CY0 - T, CY0, FOOT, CLOCK_TOP, F)
L = ledge(span(CX0, 10500.0, 6250.0, 6750.0), F_TOP, F, "Arrival Landing", FLOOR, thick=150.0)
toggle(10120.0, 6330.0, F_TOP, F)
lamp(10100.0, 6700.0, F_TOP + 300.0, F)
# Round the walls, counter-clockwise from the landing: down the west wall, along the south, up the east, back along
# the north, a second lap higher up. Each piece: (kind, size); a step up of 100 each.
INSET = 170.0
loop = [(CX0 + INSET, 6250.0), (CX0 + INSET, CY0 + INSET), (CX1 - INSET, CY0 + INSET), (CX1 - INSET, CY1 - INSET),
        (CX0 + INSET, CY1 - INSET), (CX0 + INSET, CY0 + INSET), (CX1 - INSET, CY0 + INSET), (CX1 - INSET, CY1 - INSET)]
lengths = [math.hypot(loop[i + 1][0] - loop[i][0], loop[i + 1][1] - loop[i][1]) for i in range(len(loop) - 1)]


def along(s):
    for i, length in enumerate(lengths):
        if s <= length:
            t = s / length
            return loop[i][0] + (loop[i + 1][0] - loop[i][0]) * t, loop[i][1] + (loop[i + 1][1] - loop[i][1]) * t
        s -= length
    raise RuntimeError("The clock room path ran out")


pieces = [("red", 250.0), ("red", 250.0), ("pedestal", 350.0), ("blue", 250.0), ("blue", 250.0), ("blue", 250.0),
          ("pedestal", 350.0), ("red", 250.0), ("red", 250.0), ("gear", 300.0), ("fade", P), ("fade", P),
          ("landing", 500.0), ("piston", P), ("small", 180.0), ("small", 180.0), ("small", 180.0), ("small", 180.0),
          ("top", 600.0)]
STEP_GAP = 330.0
s = 0.0   # the loop starts at the landing's south edge
previous, top, prev_size = L, F_TOP, 0.0
placed = []
for index, (kind, size) in enumerate(pieces):
    s += prev_size / 2.0 + STEP_GAP + size / 2.0 if index else STEP_GAP + size / 2.0
    x, y = along(max(s, 0.0))
    rise = 100.0
    if kind == "piston":
        rise = 0.0
    top += rise
    if kind in ("red", "blue"):
        here = switch_block(rect(x, y, size), top, kind == "red", F)
    elif kind == "pedestal":
        here = ledge(rect(x, y, size), top, F, "Pedestal", FLOOR)
        toggle(x, y, top, F)
    elif kind == "gear":
        here = gear(x, y, top, size / 2.0, 35.0, F)
    elif kind == "fade":
        here = platform(bp_class(GIMMICKS + "/BP_TimedPlatform"), x, y, top, "Fading Step", F,
                        (("VisibleSeconds", 2.0), ("HiddenSeconds", 1.2), ("FadeSeconds", 0.4), ("StartDelay", 0.5 * index)))
    elif kind == "landing":
        here = ledge(rect(x, y, size), top, F, "Clock Landing", FLOOR)
        rewind = spawn(bp_class(GIMMICKS + "/BP_TimeRewindArea"), unreal.Vector(x, y, top), "Time Rewind Area", F)
        for key, value in (("CountSeconds", 3.0), ("CooldownSeconds", 10.0), ("NightSunPitch", 15.0), ("NightBlendSpeed", 1.0), ("TextHeight", 140.0)):
            rewind.set_editor_property(key, value)
        lamp(x, y, top + 350.0, F)
    elif kind == "piston":
        here = platform(bp_class(GIMMICKS + "/BP_MovingPlatform"), x, y, top, "Piston", F,
                        (("MoveOffset", unreal.Vector(0.0, 0.0, 600.0)), ("MoveSeconds", 2.4), ("WaitSeconds", 1.0)))
    elif kind == "small":
        here = ledge(rect(x, y, size), top, F, "Wall Stone", IRON)
    else:
        here = ledge(rect(x, y, size), top, F, "Top Landing", FLOOR)
    jump("clock room {} {}".format(index + 1, kind), gap(previous, here), rise)
    placed.append((kind, x, y, top, here))
    if kind == "piston":
        top += 600.0
    previous, prev_size = here, size
    if kind == "pedestal" and index == 6:
        # Star coin 3: a blue block in from this pedestal. Flip back to blue, hop over, flip again to go on.
        cx, cy = (CX0 + CX1) / 2.0, (CY0 + CY1) / 2.0
        dx, dy = cx - x, cy - y
        d = math.hypot(dx, dy)
        # A long jump in over the drop.
        bx, by = x + dx / d * (size / 2.0 + 380.0 + 125.0), y + dy / d * (size / 2.0 + 380.0 + 125.0)
        bonus = switch_block(rect(bx, by, 250.0), top + 100.0, False, F)
        jump("pedestal -> coin block", gap(here, bonus), 100.0)
        coin(bx, by, top + 100.0, F)
TOP_KIND, TX, TY, TTOP, TOP_SHAPE = placed[-1]
# Half a roof: the way up stays hidden; the lift on the top landing rises through its hole.
HOLE = (TX - 350.0, TX + 350.0, TY - 350.0, TY + 350.0)
roof_z0, roof_z1 = CLOCK_TOP - 100.0, CLOCK_TOP
for x0, x1, y0, y1 in ((CX0 - T, HOLE[0], CY0 - T, CY1 + T), (HOLE[1], CX1 + T, CY0 - T, CY1 + T),
                       (HOLE[0], HOLE[1], CY0 - T, HOLE[2]), (HOLE[0], HOLE[1], HOLE[3], CY1 + T)):
    if x1 - x0 > 1.0 and y1 - y0 > 1.0:
        box(x0, x1, y0, y1, roof_z0, roof_z1, F, "Roof", WALL)
lift_rise = CLOCK_TOP - TTOP
if lift_rise < 250.0:
    raise RuntimeError("The clock room top landing is too close under the roof: {}".format(lift_rise))
platform(bp_class(GIMMICKS + "/BP_MovingPlatform"), TX, TY, TTOP, "Roof Lift", F,
         (("MoveOffset", unreal.Vector(0.0, 0.0, lift_rise)), ("MoveSeconds", 2.5), ("WaitSeconds", 1.5)))
for i in range(4):
    a = 2.0 * math.pi * i / 4.0
    lamp((CX0 + CX1) / 2.0 + 900.0 * math.cos(a), (CY0 + CY1) / 2.0 + 900.0 * math.sin(a), F_TOP + 1200.0 + 300.0 * i, F)

# ===== G. Roof (136-149 m) and the big mechanism =====
F = "G Roof"
STEPS = 12
STEP_RISE = 100.0
STEP_DEPTH = 220.0
STEP_WIDTH = 700.0
SPIRE_X0 = CX1 + T
SPIRE = (SPIRE_X0, SPIRE_X0 + 2900.0, 5700.0, 7300.0)
SPIRE_TOP = CLOCK_TOP + STEP_RISE * (STEPS + 1)
box(SPIRE[0], SPIRE[1], SPIRE[2], SPIRE[3], FOOT, SPIRE_TOP, F, "Spire", WALL)
lever = spawn(bp_class(AREA + "/BP_Lever"), unreal.Vector(10400.0, 5700.0, CLOCK_TOP), "Lever", F, unreal.Rotator(roll=0.0, pitch=0.0, yaw=90.0))
FIRST = 1.5
DELAY = 0.3
SECONDS = 1.5
lever.set_editor_property("ShowSeconds", FIRST + DELAY * (STEPS - 1) + SECONDS + 1.0)
for i in range(STEPS):
    step_top = CLOCK_TOP + STEP_RISE * (i + 1)
    final_x = SPIRE_X0 - STEP_DEPTH / 2.0 - STEP_DEPTH * (STEPS - 1 - i)
    hidden_x = SPIRE_X0 + STEP_DEPTH / 2.0 + 20.0
    mechanism(lever, unreal.Vector(hidden_x, 6500.0, step_top), (STEP_DEPTH, STEP_WIDTH, 80.0),
              unreal.Vector(final_x - hidden_x, 0.0, 0.0), FIRST + DELAY * i, SECONDS, "Drawer Step {:02d}".format(i + 1), F + "/Steps", BRASS)
    jump("drawer step", 0.0, STEP_RISE)
# The great gear on the spire's face, beside the steps: it turns two full turns as the steps come out.
GEAR_Y, GEAR_Z = 5000.0, CLOCK_TOP + 800.0
box(SPIRE_X0 - 20.0, SPIRE_X0 + 300.0, GEAR_Y - 60.0, GEAR_Y + 60.0, GEAR_Z - 60.0, GEAR_Z + 60.0, F, "Axle", IRON)
box(SPIRE_X0 + 300.0, SPIRE_X0 + 600.0, GEAR_Y - 150.0, GEAR_Y + 150.0, FOOT, GEAR_Z + 150.0, F, "Gear Column", WALL)
great = mechanism(lever, unreal.Vector(SPIRE_X0 - 40.0, GEAR_Y, GEAR_Z), (600.0, 600.0, 1.0),
                  unreal.Vector(0.0, 0.0, 0.0), 0.5, FIRST + DELAY * STEPS + SECONDS, "Great Gear", F)
great.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=90.0, yaw=0.0), False)
great.set_editor_property("Turn", unreal.Rotator(roll=0.0, pitch=0.0, yaw=720.0))
gear_mesh = unreal.load_asset(MACHINE + "/SM_Gear")
for component in great.get_components_by_class(unreal.StaticMeshComponent):
    component.set_editor_property("static_mesh", gear_mesh)
    component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
    for slot, material in enumerate((IRON, BRASS, unreal.load_asset(MACHINE + "/MI_MachineShadow"))):
        component.set_material(slot, material)
gate_x = SPIRE_X0 + 800.0
for side in (-1, 1):
    box(gate_x - 150.0, gate_x + 150.0, 6500.0 + side * 450.0 - 150.0, 6500.0 + side * 450.0 + 150.0, SPIRE_TOP, SPIRE_TOP + 800.0, F, "Gate Tower", IRON)
box(gate_x - 150.0, gate_x + 150.0, 5900.0, 7100.0, SPIRE_TOP + 800.0, SPIRE_TOP + 900.0, F, "Gate Lintel", BRASS)
gate = spawn(bp_class(AREA + "/BP_AreaExit"), unreal.Vector(gate_x, 6500.0, SPIRE_TOP), "Exit", F, unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
gate.set_editor_property("NextLevel", NEXT_LEVEL.rsplit("/", 1)[1])
eye = unreal.Vector(SPIRE_X0 - 1500.0, 3300.0, CLOCK_TOP + 1100.0)
look = unreal.Vector(SPIRE_X0 - 900.0, 6000.0, CLOCK_TOP + 600.0)
camera = spawn(unreal.CameraActor, eye, "Show Camera", F, unreal.MathLibrary.find_look_at_rotation(eye, look))
camera.get_editor_property("camera_component").set_editor_property("constrain_aspect_ratio", False)
lever.set_editor_property("ShowCamera", camera)
lamp(10400.0, 6000.0, CLOCK_TOP + 300.0, F)
lamp(SPIRE_X0 - 300.0, 6500.0, CLOCK_TOP + 900.0, F)

for name, g, rise, limit in checks:
    lines.append("  {:<36} gap {:>4.0f} rise {:>4.0f} (limit {:>4.0f})".format(name, g, rise, limit))
lines.append("clock room top landing {:.0f}, roof {:.0f}, spire top {:.0f} cm; {} actors".format(TTOP, CLOCK_TOP, SPIRE_TOP, counter[0]))
lines.append("{} saved {}".format(LEVEL, level_subsystem.save_current_level()))

# ===== the area 3 placeholder =====
if library.does_asset_exist(NEXT_LEVEL):
    library.delete_asset(NEXT_LEVEL)
if not level_subsystem.new_level(NEXT_LEVEL, False):
    raise RuntimeError("Could not create " + NEXT_LEVEL)
base = SPIRE_TOP
floor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, base - 50.0))
floor.set_actor_label("A3 Floor")
floor_mesh = floor.get_editor_property("static_mesh_component")
floor_mesh.set_static_mesh(unreal.load_asset(CUBE))
floor_mesh.set_material(0, FLOOR)
floor.set_actor_scale3d(unreal.Vector(30.0, 30.0, 1.0))
actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0.0, 0.0, base + 100.0)).set_actor_label("PlayerStart")
actors.spawn_actor_from_class(bp_class(AREA + "/BP_AreaStart"), unreal.Vector(0.0, 300.0, base + 200.0)).set_actor_label("A3 Area Start")
actors.spawn_actor_from_class(bp_class("/Effekseer/BluePrints/BP_EffekseerSystem"), unreal.Vector(0.0, 0.0, 0.0)).set_actor_label("Effekseer System")
light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, base + 1000.0), unreal.Rotator(roll=0.0, pitch=-45.0, yaw=30.0))
light.set_actor_label("Sun")
sky3 = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0.0, 0.0, base + 1000.0))
sky3.set_actor_label("Sky Light")
sky3.get_editor_property("light_component").set_editor_property("real_time_capture", True)
sky3.get_editor_property("light_component").set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
actors.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0)).set_actor_label("Sky Atmosphere")
label3 = actors.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(800.0, 0.0, base + 300.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
label3.set_actor_label("A3 Label")
render = label3.get_editor_property("text_render")
render.set_text(unreal.Text("AREA 3 (coming soon)"))
render.set_editor_property("world_size", 80.0)
render.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
lines.append("{} placeholder saved {} (floor at {:.0f} cm)".format(NEXT_LEVEL, level_subsystem.save_current_level(), base))

with open(os.path.join(unreal.Paths.project_saved_dir(), "area2_build.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
