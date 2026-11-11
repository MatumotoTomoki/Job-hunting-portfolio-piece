# Builds /Game/LV_Area1_Ruins, the first area: a ruined town on a mountainside at dusk, climbed from 0 m to about 73 m.
# The way up winds through and over buildings, so what lies above is mostly hidden until the player gets there:
#   A Lower Town (0 m)      a walled plaza. The Hall blocks the view ahead; inside it a stair winds up the walls to
#                           its half-fallen roof. Side ways: crates up onto the town wall lead to a star coin (a dead
#                           end), and a small house to the south is empty (a dead end).
#   B Roofs (10-15 m)       roof to roof, two crumbling floors, a branch roof with a star coin on a column stump (a dead end),
#                           then a lift up to the aqueduct.
#   C Aqueduct (15 m)       a narrow deck on arches with a broken span crossed on fading stones; the checkpoint
#                           pickup before the tower door.
#   D Great Tower (15-43 m) climbed inside: a lift, broken floors, stones jutting from the walls, a pressure plate that
#                           slides stepping stones out of the walls, fading stones, and a breach high in the east wall.
#                           Broken floors and a half roof hide the way above. Torches light it.
#   E Cliff (43-60 m)       ledges up the cliff face under an overhang: a crumbling floor, ledges, a lift, more ledges;
#                           a branch of ledges to a star coin (a dead end).
#   F Courtyard (60 m)      the big mechanism: the lever, and twelve giant steps rising one after another up the face of
#                           the Great Wall (73 m), watched from a side camera; the gate and the exit on the wall.
# Falling inside the town or the tower lands on a lower floor; falling into the abyss, the character's -50 m check
# sends the player to the flag, else the PlayerStart. Gaps and rises are worked out from the player's own jump without
# items (as in build_hell_stage.py); the script stops if one is out of reach.
# The pressure plate is a BP_Lever with its handle hidden and its base flattened; the stones it moves are
# BP_Mechanism, hidden inside the walls until then.
# Also (re)makes LV_Area2_Tower as a placeholder at the height area 1 ends, so the exit can be tried.
# Everything placed here is labelled "A1 ..." and rebuilt on every run. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\build_area1_ruins.py -unattended -nop4 -nosplash -stdout
import math
import os

import unreal

LEVEL = "/Game/LV_Area1_Ruins"
NEXT_LEVEL = "/Game/LV_Area2_Tower"
DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
GIMMICKS = "/Game/ThirdPerson/Blueprints/Gimmicks"
ITEMS = "/Game/ThirdPerson/Item"
GAME_MODE = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode"
FALLBACK_CHARACTER = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1"
FLAT_COLOR = "/Game/LevelPrototyping/Materials/M_FlatCol"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"
PREFIX = "A1 "
FOOT = -4000.0            # anything standing in the abyss goes down to here, lost in the mist
START = unreal.Vector(-3600.0, 0.0, 100.0)

library = unreal.EditorAssetLibrary
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
lines = []


# ----- what a plain jump can do -----
def player_defaults():
    pawn_class = None
    try:
        mode = unreal.load_asset(GAME_MODE)
        pawn_class = unreal.get_default_object(mode.generated_class()).get_editor_property("default_pawn_class")
    except Exception as error:
        lines.append("game mode pawn not read: {}".format(error))
    if pawn_class is None:
        pawn_class = unreal.load_asset(FALLBACK_CHARACTER).generated_class()
    return unreal.get_default_object(pawn_class)


pawn = player_defaults()
move = pawn.get_editor_property("character_movement")
jump_z = move.get_editor_property("jump_z_velocity")
gravity = 980.0 * move.get_editor_property("gravity_scale")
speed = move.get_editor_property("max_walk_speed")
APEX = jump_z * jump_z / (2.0 * gravity)


def reach_up(rise):
    # Running jump, edge to edge, landing `rise` higher.
    fall = APEX - rise
    if fall <= 0:
        return 0.0
    return speed * (jump_z / gravity + math.sqrt(2.0 * fall / gravity))


lines.append("jump {:.0f}, walk {:.0f}: flat reach {:.0f}, apex {:.0f}".format(jump_z, speed, reach_up(0.0), APEX))
checks = []


EASY_LIMIT = 0.8   # most jumps: at most 80 % of what a plain jump can do
HARD_LIMIT = 0.9   # the hard ones (tower, cliff): a running jump, taken off near the edge


def jump(name, gap, rise, ratio=EASY_LIMIT):
    limit = ratio * reach_up(max(rise, 0.0))
    checks.append((name, gap, rise, limit))
    if rise > 0.8 * APEX or gap > limit:
        raise RuntimeError("Out of reach: {} gap {:.0f} rise {:.0f} (limit {:.0f}, apex {:.0f})".format(name, gap, rise, limit, APEX))


# ----- materials -----
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


STONE = color_material("MI_RuinsStone", (0.55, 0.46, 0.34))
DARK = color_material("MI_RuinsDark", (0.28, 0.23, 0.19))
PALE = color_material("MI_RuinsPale", (0.72, 0.64, 0.52))
WOOD = color_material("MI_RuinsWood", (0.33, 0.2, 0.1))
EMBER = color_material("MI_RuinsEmber", (1.0, 0.45, 0.1))


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


def bp_class(path):
    asset = unreal.load_asset(path)
    if not asset:
        raise RuntimeError("Missing " + path)
    return asset.generated_class()


falling_class = bp_class(GIMMICKS + "/BP_FallingFloor")
moving_class = bp_class(GIMMICKS + "/BP_MovingPlatform")
timed_class = bp_class(GIMMICKS + "/BP_TimedPlatform")
lever_class = bp_class(DIR + "/BP_Lever")
mechanism_class = bp_class(DIR + "/BP_Mechanism")
exit_class = bp_class(DIR + "/BP_AreaExit")
start_class = bp_class(DIR + "/BP_AreaStart")
system_class = bp_class("/Effekseer/BluePrints/BP_EffekseerSystem")

# ----- the level -----
if library.does_asset_exist(LEVEL):
    if not level_subsystem.load_level(LEVEL):
        raise RuntimeError("Could not open " + LEVEL)
    for actor in actors.get_all_level_actors():
        if actor.get_actor_label().startswith(PREFIX):
            actors.destroy_actor(actor)
else:
    # Not World Partition: everything stays loaded.
    if not level_subsystem.new_level(LEVEL, False):
        raise RuntimeError("Could not create " + LEVEL)
    lines.append("created " + LEVEL)

counter = [0]


def spawn(actor_class, location, name, folder, rotation=None):
    actor = actors.spawn_actor_from_class(actor_class, location, rotation or unreal.Rotator(0.0, 0.0, 0.0))
    if not actor:
        raise RuntimeError("Could not spawn " + name)
    counter[0] += 1
    actor.set_actor_label("{}{:03d} {}".format(PREFIX, counter[0], name))
    actor.set_folder_path("Area1/" + folder)
    return actor


def box(x0, x1, y0, y1, z0, z1, folder, name="Block", material=None, mesh=CUBE):
    # A block between two corners.
    actor = spawn(unreal.StaticMeshActor, unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0), name, folder)
    component = actor.get_editor_property("static_mesh_component")
    component.set_static_mesh(unreal.load_asset(mesh))
    component.set_material(0, material or STONE)
    actor.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0))
    return actor


def ground(x0, x1, y0, y1, top, folder, name="Ground", material=None):
    # Solid from the abyss up to `top`.
    return box(x0, x1, y0, y1, FOOT, top, folder, name, material)


def slab(cx, cy, top, size, folder, name="Ledge", material=None, thick=80.0):
    half = size / 2.0
    return box(cx - half, cx + half, cy - half, cy + half, top - thick, top, folder, name, material)


def rand(i):
    # A fixed scatter, the same on every run.
    return (math.sin(i * 12.9898 + 4.1414) * 43758.5453) % 1.0


TEETH = [0]


def wall(axis, a0, a1, c0, c1, z0, z1, folder, openings=(), teeth=True, material=None):
    # A wall running along `axis` ("x" or "y") from a0 to a1, c0..c1 thick, z0..z1 high. Openings are (u0, u1, v0, v1)
    # holes: u along the wall, v in height. A broken, uneven top when `teeth`.
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
    if teeth:
        u = a0
        while u < a1 - 60.0:
            TEETH[0] += 1
            width = 150.0 + 200.0 * rand(TEETH[0])
            height = 280.0 * rand(TEETH[0] + 500)
            if height > 60.0:
                piece(u, min(u + width, a1), z1, z1 + height)
            u += width + 80.0 * rand(TEETH[0] + 900)


def column(x, y, base, height, folder, radius=45.0):
    return box(x - radius, x + radius, y - radius, y + radius, base, base + height, folder, "Column", PALE, CYLINDER)


def torch(x, y, z, folder):
    # A brazier and a warm light.
    box(x - 25.0, x + 25.0, y - 25.0, y + 25.0, z - 40.0, z, folder, "Brazier", EMBER, CYLINDER)
    light = spawn(unreal.PointLight, unreal.Vector(x, y, z + 40.0), "Torch Light", folder)
    component = light.get_editor_property("point_light_component")
    component.set_editor_property("intensity", 2500.0)
    component.set_editor_property("attenuation_radius", 1400.0)
    component.set_editor_property("light_color", unreal.Color(r=255, g=150, b=70, a=255))
    component.set_editor_property("cast_shadows", False)


def platform(actor_class, x, y, top, name, folder, settings=()):
    actor = spawn(actor_class, unreal.Vector(x, y, top - PLAT.z), name, folder)
    for key, value in settings:
        actor.set_editor_property(key, value)
    return actor


def item(path, x, y, top, name, folder):
    return spawn(bp_class(path), unreal.Vector(x, y, top + 100.0), name, folder)


COIN = "/Game/ThirdPerson/Coin/StarCoin/BP_StarCoin"   # import_star_coin.py
coin_count = [0]


def coin(x, y, top, folder):
    # Star coins, three to an area, in place of the power-up items (they made the climb too easy): hidden or hard
    # to reach, worth finding and nothing more.
    coin_count[0] += 1
    return spawn(bp_class(COIN), unreal.Vector(x, y, top + 100.0), "Star Coin", folder)


def mechanism(lever, x, y, top, size, offset, delay, name, folder, seconds=0.8, return_after=None, return_seconds=0.0):
    # A BP_Mechanism stone: its actor origin is the top of its Body. With `return_after`, it slides home again
    # that many seconds after it is out, taking `return_seconds`.
    actor = spawn(mechanism_class, unreal.Vector(x, y, top), name, folder)
    actor.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
    actor.set_editor_property("Lever", lever)
    actor.set_editor_property("MoveOffset", offset)
    actor.set_editor_property("StartDelay", delay)
    actor.set_editor_property("Duration", seconds)
    actor.set_editor_property("Returns", return_after is not None)
    actor.set_editor_property("ReturnAfter", return_after or 0.0)
    actor.set_editor_property("ReturnSeconds", return_seconds)
    return actor


PLATE_HALF = 90.0


def pressure_plate(x, y, top, folder):
    # The new gimmick: a stone plate set in the floor. A BP_Lever without its handle, so stepping on it "pulls" it.
    plate = spawn(lever_class, unreal.Vector(x, y, top), "Pressure Plate", folder)
    for component in plate.get_components_by_class(unreal.StaticMeshComponent):
        name = component.get_name()
        if name.startswith("Handle") or name.startswith("Knob"):
            component.set_visibility(False, False)
            component.set_hidden_in_game(True, False)
            component.set_editor_property("visible", False)
            component.set_editor_property("hidden_in_game", True)
            component.set_collision_profile_name("NoCollision")
        elif name.startswith("Base"):
            component.set_editor_property("relative_scale3d", unreal.Vector(PLATE_HALF / 50.0, PLATE_HALF / 50.0, 0.06))
            component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 3.0))
            component.set_material(0, EMBER)
    for component in plate.get_components_by_class(unreal.BoxComponent):
        component.set_editor_property("box_extent", unreal.Vector(PLATE_HALF, PLATE_HALF, 40.0))
        component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 40.0))
    plate.set_editor_property("ShowCamera", None)
    return plate


# ===== sky =====
sun = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 9000.0), "Sun", "Sky", unreal.Rotator(roll=0.0, pitch=-9.0, yaw=200.0))
sun_light = sun.get_editor_property("directional_light_component")
sun_light.set_editor_property("intensity", 6.0)
sun_light.set_editor_property("light_color", unreal.Color(r=255, g=170, b=120, a=255))
sun_light.set_editor_property("atmosphere_sun_light", True)
sky = spawn(unreal.SkyLight, unreal.Vector(0.0, 0.0, 9000.0), "Sky Light", "Sky")
sky_light = sky.get_editor_property("light_component")
sky_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
sky_light.set_editor_property("real_time_capture", True)
spawn(unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0), "Sky Atmosphere", "Sky")
spawn(unreal.VolumetricCloud, unreal.Vector(0.0, 0.0, 0.0), "Clouds", "Sky")
fog = spawn(unreal.ExponentialHeightFog, unreal.Vector(0.0, 0.0, -1200.0), "Abyss Mist", "Sky")
fog_component = fog.get_editor_property("component")
fog_component.set_editor_property("fog_density", 0.04)
fog_component.set_editor_property("fog_height_falloff", 0.0015)
fog_component.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.55, 0.35, 0.32, 1.0))

spawn(system_class, unreal.Vector(0.0, 0.0, 0.0), "Effekseer System", "A Lower Town")
spawn(unreal.PlayerStart, START, "PlayerStart", "A Lower Town")
spawn(start_class, unreal.Vector(START.x, 300.0, 200.0), "Area Start", "A Lower Town")

# ===== A. Lower Town (0 m) =====
F = "A Lower Town"
ground(-4000.0, 1500.0, -2000.0, 2000.0, 0.0, F, "Town Ground", DARK)
# The town wall: west, north and south.
wall("y", -2000.0, 2000.0, -4000.0, -3800.0, 0.0, 700.0, F)
wall("x", -3800.0, 1500.0, 1800.0, 2000.0, 0.0, 600.0, F, teeth=False)
wall("x", -3800.0, 1500.0, -2000.0, -1800.0, 0.0, 700.0, F)
for i, (x, y, h) in enumerate(((-3300.0, 900.0, 260.0), (-3300.0, -900.0, 380.0), (-1000.0, 1300.0, 180.0), (-200.0, -1300.0, 420.0), (600.0, 1300.0, 300.0))):
    column(x, y, 0.0, h, F)

# The Hall: in at the west door, up a stair winding round the inside of the walls, out under the fallen half of
# the roof (its south half is gone) onto what is left of it.
HALL = (-2600.0, -1400.0, -700.0, 700.0)
HALL_TOP = 960.0
x0, x1, y0, y1 = HALL
wall("y", y0, y1, x0, x0 + 200.0, 0.0, HALL_TOP, F, openings=[(-200.0, 200.0, 0.0, 380.0)], teeth=False)
wall("y", y0, y1, x1 - 200.0, x1, 0.0, HALL_TOP, F, openings=[(-100.0, 200.0, 450.0, 700.0)], teeth=False)
wall("x", x0 + 200.0, x1 - 200.0, y1 - 200.0, y1, 0.0, HALL_TOP, F, openings=[(-2200.0, -1900.0, 500.0, 750.0)], teeth=False)
wall("x", x0 + 200.0, x1 - 200.0, y0, y0 + 200.0, 0.0, HALL_TOP, F, teeth=False)
box(x0, x1, 0.0, y1, HALL_TOP - 60.0, HALL_TOP, F, "Hall Roof", DARK)
STAIR_RISE = 90.0
STAIR_RUN = 180.0
STAIR_WIDTH = 250.0
path = [(-2275.0, 375.0), (-1725.0, 375.0), (-1725.0, -375.0), (-2275.0, -375.0)]
segments = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
step = 0
distance = STAIR_RUN / 2.0
walked = 0.0
for (ax, ay), (bx, by) in segments:
    length = math.hypot(bx - ax, by - ay)
    while distance <= walked + length + 1.0 and step < 10:
        t = (distance - walked) / length
        cx, cy = ax + (bx - ax) * t, ay + (by - ay) * t
        step += 1
        half_x = STAIR_RUN / 2.0 if abs(bx - ax) > 1.0 else STAIR_WIDTH / 2.0
        half_y = STAIR_WIDTH / 2.0 if abs(bx - ax) > 1.0 else STAIR_RUN / 2.0
        box(cx - half_x, cx + half_x, cy - half_y, cy + half_y, 0.0, STAIR_RISE * step, F, "Hall Stair", PALE)
        distance += STAIR_RUN
    walked += length
last_top = STAIR_RISE * step
jump("hall stair -> roof edge", 250.0, HALL_TOP - last_top)
torch(-2000.0, 0.0, 40.0, F)

# Dead end 1: crates up onto the north town wall, along it to the corner.
for i in range(6):
    x = -1700.0 - 240.0 * i
    box(x - 110.0, x + 110.0, 1580.0, 1800.0, 0.0, 90.0 * (i + 1), F, "Crate", WOOD)
# Star coin 1: at the far end of the town wall, out of sight behind the Hall.
coin(-3720.0, 1900.0, 600.0, F)

# Dead end 2: a little house to the south, empty.
wall("y", -1600.0, -1000.0, -3300.0, -3150.0, 0.0, 450.0, F, teeth=False)
wall("y", -1600.0, -1000.0, -2850.0, -2700.0, 0.0, 450.0, F, teeth=False)
wall("x", -3150.0, -2850.0, -1600.0, -1450.0, 0.0, 450.0, F, teeth=False)
wall("x", -3150.0, -2850.0, -1150.0, -1000.0, 0.0, 450.0, F, openings=[(-3080.0, -2920.0, 0.0, 280.0)], teeth=False)
box(-3300.0, -2700.0, -1600.0, -1000.0, 450.0, 510.0, F, "House Roof", DARK)

# ===== B. Roofs (10-15 m) =====
F = "B Roofs"
B3 = (-1020.0, -500.0, -500.0, 300.0, 1020.0)
box(B3[0], B3[1], B3[2], B3[3], 0.0, B3[4], F, "House")
jump("hall roof -> house", B3[0] - x1, B3[4] - HALL_TOP)
# Dead end 3: the roof to the north.
B5 = (-1020.0, -500.0, 680.0, 1300.0, 1080.0)
box(B5[0], B5[1], B5[2], B5[3], 0.0, B5[4], F, "House")
jump("house -> north roof", B5[2] - B3[3], B5[4] - B3[4])
# Star coin 2: on a stump of a column at the back of the north roof, a careful hop up.
column(-640.0, 1160.0, B5[4], 100.0, F, 60.0)
coin(-640.0, 1160.0, B5[4] + 100.0, F)
jump("north roof -> column stump", 0.0, 100.0)
# Two crumbling floors, then the long roof.
B4 = (650.0, 1300.0, -400.0, 400.0, 1150.0)
tops = [1070.0, 1110.0]
xs = [-200.0, 300.0]
edge, top = B3[1], B3[4]
for x, t in zip(xs, tops):
    platform(falling_class, x, 0.0, t, "Crumbling Floor", F)
    jump("crumbling floor", x - PLAT.x - edge, t - top)
    edge, top = x + PLAT.x, t
box(B4[0], B4[1], B4[2], B4[3], 0.0, B4[4], F, "Long House")
jump("crumbling floor -> long roof", B4[0] - edge, B4[4] - top)
box(B4[0] + 80.0, B4[0] + 200.0, B4[3] - 200.0, B4[3] - 80.0, B4[4], B4[4] + 220.0, F, "Chimney", DARK)
AQUEDUCT_TOP = 1500.0
platform(moving_class, 1550.0, 0.0, B4[4], "Lift", F,
         (("MoveOffset", unreal.Vector(0.0, 0.0, AQUEDUCT_TOP - B4[4])), ("MoveSeconds", 2.2), ("WaitSeconds", 1.0)))
jump("long roof -> lift", 1550.0 - PLAT.x - B4[1], 0.0)

# ===== C. Aqueduct (15 m) =====
F = "C Aqueduct"
DECK = (1700.0, 4800.0)
BREAK = (2800.0, 3900.0)
for a, b in ((DECK[0], BREAK[0]), (BREAK[1], DECK[1])):
    box(a, b, -150.0, 150.0, AQUEDUCT_TOP - 150.0, AQUEDUCT_TOP, F, "Deck", PALE)
for x in (2000.0, 2600.0, 4100.0, 4600.0):
    box(x - 100.0, x + 100.0, -120.0, 120.0, FOOT, AQUEDUCT_TOP - 150.0, F, "Pier")
    box(x - 300.0, x + 300.0, -130.0, 130.0, AQUEDUCT_TOP - 300.0, AQUEDUCT_TOP - 150.0, F, "Arch")
edge = BREAK[0]
for i, x in enumerate((3100.0, 3600.0)):
    platform(timed_class, x, 0.0, AQUEDUCT_TOP, "Fading Stone", F,
             (("VisibleSeconds", 2.0), ("HiddenSeconds", 1.2), ("FadeSeconds", 0.4), ("StartDelay", 0.7 * i)))
    jump("aqueduct fading stone", x - PLAT.x - edge, 0.0)
    edge = x + PLAT.x
jump("fading stone -> deck", BREAK[1] - edge, 0.0)
item(ITEMS + "/Checkpoint/BP_CheckpointItem", 4500.0, 0.0, AQUEDUCT_TOP, "Checkpoint Item", F)

# ===== D. Great Tower (15-43 m) =====
F = "D Great Tower"
IX0, IX1, IY0, IY1 = 5100.0, 6900.0, -900.0, 900.0     # inside
T = 300.0                                             # wall thickness
TOWER_TOP = 5000.0
S1, S2, S3, S4 = AQUEDUCT_TOP, 2700.0, 3400.0, 3800.0
BREACH = 4200.0
wall("y", IY0 - T, IY1 + T, IX0 - T, IX0, FOOT, TOWER_TOP, F,
     openings=[(-200.0, 200.0, S1, S1 + 350.0), (-700.0, -400.0, 3000.0, 3400.0)])
wall("y", IY0 - T, IY1 + T, IX1, IX1 + T, FOOT, TOWER_TOP, F,
     openings=[(200.0, 700.0, BREACH, BREACH + 380.0), (-600.0, -300.0, 2200.0, 2600.0)])
wall("x", IX0, IX1, IY1, IY1 + T, FOOT, TOWER_TOP, F, openings=[(5300.0, 5600.0, 2000.0, 2400.0)])
wall("x", IX0, IX1, IY0 - T, IY0, FOOT, TOWER_TOP, F, openings=[(5600.0, 5900.0, 2000.0, 2400.0), (6200.0, 6500.0, 4300.0, 4650.0)])
jump("aqueduct -> tower door", 0.0, 0.0)
box(IX0, IX1, IY0, IY1, S1 - 100.0, S1, F, "Story 1 Floor", DARK)
# Half a roof: the top of the climb stays out of sight from below.
box(IX0, 6300.0, IY0, IY1, 4900.0, 5000.0, F, "Broken Roof", DARK)
torch(5300.0, 0.0, S1 + 40.0, F)

# The floors above story 1 are only narrow balconies along the walls: the middle of the tower is open from top to
# bottom, so a slip high up drops all the way back to story 1.
def rect_gap(a, b):
    # Edge to edge between two (x0, x1, y0, y1) footprints.
    gx = max(0.0, b[0] - a[1], a[0] - b[1])
    gy = max(0.0, b[2] - a[3], a[2] - b[3])
    return math.hypot(gx, gy)


def square(cx, cy, size):
    return (cx - size / 2.0, cx + size / 2.0, cy - size / 2.0, cy + size / 2.0)


# Story 1 -> 2: the lift in the north-east corner, up to the north balcony.
LIFT_X, LIFT_Y = 6600.0, 600.0
platform(moving_class, LIFT_X, LIFT_Y, S1 + 10.0, "Tower Lift", F,
         (("MoveOffset", unreal.Vector(0.0, 0.0, S2 - S1 - 10.0)), ("MoveSeconds", 3.0), ("WaitSeconds", 1.2)))
S2_AREA = (IX0, 6350.0, 500.0, IY1)
box(S2_AREA[0], S2_AREA[1], S2_AREA[2], S2_AREA[3], S2 - 80.0, S2, F, "Story 2 Balcony", DARK)
jump("tower lift -> story 2", rect_gap(square(LIFT_X, LIFT_Y, 2.0 * PLAT.x), S2_AREA), 0.0)
torch(5300.0, 750.0, S2 + 40.0, F)

# Story 2 -> 3: small stones jutting from the west, south and east walls, a step up each, far apart.
WALL_STONE = 160.0
IN = WALL_STONE / 2.0
ledges = [(IX0 + IN, 90.0), (IX0 + IN, -410.0), (5600.0, IY0 + IN), (6110.0, IY0 + IN), (6620.0, IY0 + IN), (IX1 - IN, -320.0)]
previous = S2_AREA
top = S2
for i, (lx, ly) in enumerate(ledges):
    top += 100.0
    slab(lx, ly, top, WALL_STONE, F, "Wall Stone", PALE)
    here = square(lx, ly, WALL_STONE)
    jump("tower wall stone {}".format(i + 1), rect_gap(previous, here), 100.0, HARD_LIMIT)
    previous = here
S3_AREA = (6500.0, IX1, 100.0, IY1)
box(S3_AREA[0], S3_AREA[1], S3_AREA[2], S3_AREA[3], S3 - 80.0, S3, F, "Story 3 Balcony", DARK)
jump("wall stone -> story 3", rect_gap(previous, S3_AREA), S3 - top, HARD_LIMIT)
torch(6800.0, 800.0, S3 + 40.0, F)

# Story 3: the pressure plate slides three stones out of the walls, up to story 4.
plate = pressure_plate(6700.0, 300.0, S3, F)
SLIDE = 200.0
# The stones stay out a while, then slide back into the walls one after another, first to last: hurry.
# When all are home the plate springs back up, ready to be stepped on again.
STONE_OUT = 0.8
STONE_STAYS = 3.5
STONE_BACK = 2.5
plate.set_editor_property("ResetAfter", 0.6 + STONE_OUT + STONE_STAYS + STONE_BACK + 0.3)
north = [(6050.0, 3500.0), (5500.0, 3600.0)]
previous = S3_AREA
for i, (sx, st) in enumerate(north):
    # Hidden in the north wall, then out by SLIDE.
    mechanism(plate, sx, IY1 + SLIDE / 2.0, st, (200.0, SLIDE, 60.0), unreal.Vector(0.0, -SLIDE, 0.0), 0.3 * i, "Sliding Stone", F, STONE_OUT, STONE_STAYS, STONE_BACK)
    here = (sx - 100.0, sx + 100.0, IY1 - SLIDE, IY1)
    jump("sliding stone {}".format(i + 1), rect_gap(previous, here), 100.0, HARD_LIMIT)
    previous = here
west_y = 270.0
mechanism(plate, IX0 - SLIDE / 2.0, west_y, 3700.0, (SLIDE, 200.0, 60.0), unreal.Vector(SLIDE, 0.0, 0.0), 0.6, "Sliding Stone", F, STONE_OUT, STONE_STAYS, STONE_BACK)
here = (IX0, IX0 + SLIDE, west_y - 100.0, west_y + 100.0)
jump("sliding stone 3", rect_gap(previous, here), 100.0, HARD_LIMIT)
previous = here
# Story 4: an L of balconies along the west and south walls.
S4_WEST = (IX0, 5500.0, IY0, -180.0)
S4_SOUTH = (IX0, 6200.0, IY0, -500.0)
for area in (S4_WEST, S4_SOUTH):
    box(area[0], area[1], area[2], area[3], S4 - 80.0, S4, F, "Story 4 Balcony", DARK)
jump("sliding stone 3 -> story 4", rect_gap(previous, S4_WEST), S4 - 3700.0, HARD_LIMIT)
torch(5300.0, -800.0, S4 + 40.0, F)

# Story 4 -> the breach: fading stones over the open middle, up to the hole in the east wall.
FADE_X = 6700.0
previous = S4_SOUTH
top = S4
for i, (fy, ft) in enumerate(((-600.0, 3900.0), (50.0, 4000.0), (680.0, 4100.0))):
    platform(timed_class, FADE_X, fy, ft, "Fading Stone", F,
             (("VisibleSeconds", 2.4), ("HiddenSeconds", 1.0), ("FadeSeconds", 0.4), ("StartDelay", 0.6 * i)))
    here = square(FADE_X, fy, 2.0 * PLAT.x)
    jump("tower fading stone {}".format(i + 1), rect_gap(previous, here), ft - top, HARD_LIMIT)
    previous, top = here, ft
jump("fading stone -> breach", IX1 - previous[1], BREACH - top)

# ===== E. Cliff (43-60 m) =====
F = "E Cliff"
CLIFF_X = 8400.0
BRIDGE = (7300.0, 7700.0, 200.0, 700.0)
ground(BRIDGE[0], BRIDGE[1], BRIDGE[2], BRIDGE[3], BREACH, F, "Broken Bridge")
jump("breach -> broken bridge", BRIDGE[0] - (IX1 + T), 0.0)
# The overhang: the cliff top is out of sight from the ledges.
box(7700.0, CLIFF_X, -2000.0, 2000.0, 6300.0, 6500.0, F, "Overhang", DARK)
# Small ledges against the cliff face, far apart.
CLIFF_LEDGE = 180.0
LX = CLIFF_X - CLIFF_LEDGE / 2.0
GAP = 350.0
crumble = square(CLIFF_X - PLAT.x, 450.0, 2.0 * PLAT.x)
platform(falling_class, CLIFF_X - PLAT.x, 450.0, BREACH + 60.0, "Crumbling Ledge", F)
jump("broken bridge -> crumbling ledge", rect_gap(BRIDGE, crumble), 60.0, HARD_LIMIT)


def ledge_run(start, start_top, count, direction, name):
    # Ledges along the cliff face, GAP apart and a step up each, from the footprint `start` (+1 north, -1 south).
    previous, top, placed = start, start_top, []
    for i in range(count):
        top += 100.0
        edge = previous[3] if direction > 0 else previous[2]
        ly = edge + direction * (GAP + CLIFF_LEDGE / 2.0)
        slab(LX, ly, top, CLIFF_LEDGE, F, "Cliff Ledge", PALE)
        here = square(LX, ly, CLIFF_LEDGE)
        jump(name, rect_gap(previous, here), 100.0, HARD_LIMIT)
        previous = here
        placed.append(ly)
    return previous, top


previous, top = ledge_run(crumble, BREACH + 60.0, 3, -1, "cliff ledge")
lift_y = previous[2] - GAP - PLAT.y
lift = square(CLIFF_X - PLAT.x, lift_y, 2.0 * PLAT.x)
platform(moving_class, CLIFF_X - PLAT.x, lift_y, top, "Cliff Lift", F,
         (("MoveOffset", unreal.Vector(0.0, 0.0, 900.0)), ("MoveSeconds", 3.0), ("WaitSeconds", 1.2)))
jump("cliff ledge -> lift", rect_gap(previous, lift), 0.0, HARD_LIMIT)
previous, top = ledge_run(lift, top + 900.0, 4, 1, "upper cliff ledge")
COURT_TOP = top + 100.0
jump("last ledge -> courtyard", 0.0, COURT_TOP - top)
# Dead end 4: ledges off to the north.
previous, dead_top = ledge_run(crumble, BREACH + 60.0, 2, 1, "north ledge")
# Star coin 3: at the end of the hard ledges off to the north.
coin(LX, (previous[2] + previous[3]) / 2.0, dead_top, F)

# ===== F. Courtyard (60 m) and the big mechanism =====
F = "F Courtyard"
STEPS = 12
STEP_RISE = 100.0
STEP_DEPTH = 220.0
STEP_WIDTH = 700.0
STEP_DELAY = 0.25
STEP_SECONDS = 1.2
FIRST_DELAY = 1.0
WALL_FACE = 12500.0
WALL_DEPTH = 1400.0
WALL_TOP = COURT_TOP + STEP_RISE * (STEPS + 1)
ground(CLIFF_X, WALL_FACE, -2000.0, 2000.0, COURT_TOP, F, "Cliff and Courtyard", STONE)
ground(WALL_FACE, WALL_FACE + WALL_DEPTH, -1300.0, 1300.0, WALL_TOP, F, "Great Wall", DARK)
for i, (x, y, h) in enumerate(((9000.0, 1600.0, 300.0), (9800.0, -1600.0, 450.0), (10600.0, 1600.0, 200.0), (11400.0, -1600.0, 380.0))):
    column(x, y, COURT_TOP, h, F)
lever = spawn(lever_class, unreal.Vector(9100.0, -600.0, COURT_TOP), "Lever", F, unreal.Rotator(roll=0.0, pitch=0.0, yaw=90.0))
lever.set_editor_property("ShowSeconds", FIRST_DELAY + STEP_DELAY * (STEPS - 1) + STEP_SECONDS + 0.8)
for i in range(STEPS):
    step_top = COURT_TOP + STEP_RISE * (i + 1)
    x = WALL_FACE - STEP_DEPTH / 2.0 - STEP_DEPTH * (STEPS - 1 - i)
    # Hidden in the courtyard until the lever is pulled: the top starts just under its surface.
    giant = mechanism(lever, x, 0.0, COURT_TOP - 10.0, (STEP_DEPTH, STEP_WIDTH, step_top - COURT_TOP + 30.0),
                      unreal.Vector(0.0, 0.0, step_top - COURT_TOP + 10.0), FIRST_DELAY + STEP_DELAY * i,
                      "Giant Step {:02d}".format(i + 1), F + "/Steps", STEP_SECONDS)
    for component in giant.get_components_by_class(unreal.StaticMeshComponent):
        component.set_material(0, PALE)
    jump("giant step", 0.0, STEP_RISE)
gate_x = WALL_FACE + 500.0
for side in (-1, 1):
    box(gate_x - 150.0, gate_x + 150.0, side * 450.0 - 150.0, side * 450.0 + 150.0, WALL_TOP, WALL_TOP + 800.0, F, "Gate Tower")
box(gate_x - 150.0, gate_x + 150.0, -600.0, 600.0, WALL_TOP + 800.0, WALL_TOP + 900.0, F, "Gate Lintel")
gate = spawn(exit_class, unreal.Vector(gate_x, 0.0, WALL_TOP), "Exit", F, unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
gate.set_editor_property("NextLevel", NEXT_LEVEL.rsplit("/", 1)[1])
eye = unreal.Vector(WALL_FACE - STEP_DEPTH * STEPS * 0.55, -2800.0, COURT_TOP + 900.0)
target = unreal.Vector(WALL_FACE - STEP_DEPTH * STEPS * 0.5, 0.0, COURT_TOP + STEP_RISE * STEPS * 0.45)
camera = spawn(unreal.CameraActor, eye, "Show Camera", F, unreal.MathLibrary.find_look_at_rotation(eye, target))
camera.get_editor_property("camera_component").set_editor_property("constrain_aspect_ratio", False)
lever.set_editor_property("ShowCamera", camera)
torch(9100.0, -300.0, COURT_TOP + 40.0, F)

for name, gap, rise, limit in checks:
    lines.append("  {:<34} gap {:>4.0f} rise {:>4.0f} (limit {:>4.0f})".format(name, gap, rise, limit))
lines.append("wall top {:.0f} cm; {} actors, {} coins".format(WALL_TOP, counter[0], coin_count[0]))
lines.append("{} saved {}".format(LEVEL, level_subsystem.save_current_level()))

# ===== the area 2 placeholder, at the height area 1 ends =====
if library.does_asset_exist(NEXT_LEVEL):
    library.delete_asset(NEXT_LEVEL)
if not level_subsystem.new_level(NEXT_LEVEL, False):
    raise RuntimeError("Could not create " + NEXT_LEVEL)
base = WALL_TOP
floor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, base - 50.0))
floor.set_actor_label("A2 Floor")
floor_mesh = floor.get_editor_property("static_mesh_component")
floor_mesh.set_static_mesh(unreal.load_asset(CUBE))
floor_mesh.set_material(0, DARK)
floor.set_actor_scale3d(unreal.Vector(30.0, 30.0, 1.0))
actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0.0, 0.0, base + 100.0)).set_actor_label("PlayerStart")
actors.spawn_actor_from_class(start_class, unreal.Vector(0.0, 300.0, base + 200.0)).set_actor_label("A2 Area Start")
actors.spawn_actor_from_class(system_class, unreal.Vector(0.0, 0.0, 0.0)).set_actor_label("Effekseer System")
light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, base + 1000.0), unreal.Rotator(roll=0.0, pitch=-45.0, yaw=30.0))
light.set_actor_label("Sun")
sky2 = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0.0, 0.0, base + 1000.0))
sky2.set_actor_label("Sky Light")
sky2_light = sky2.get_editor_property("light_component")
sky2_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
sky2_light.set_editor_property("real_time_capture", True)
actors.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0)).set_actor_label("Sky Atmosphere")
text = actors.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(800.0, 0.0, base + 300.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
text.set_actor_label("A2 Label")
render = text.get_editor_property("text_render")
render.set_text(unreal.Text("AREA 2 (coming soon)"))
render.set_editor_property("world_size", 80.0)
render.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
lines.append("{} placeholder saved {} (floor at {:.0f} cm)".format(NEXT_LEVEL, level_subsystem.save_current_level(), base))

with open(os.path.join(unreal.Paths.project_saved_dir(), "area1_build.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
