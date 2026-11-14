# Builds /Game/LV_Area4_Heaven, the last area: heaven above the sky, from where area 3 ends (226.1 m). The longest area
# (about 25 minutes) and the one with every kind of gimmick: a hub (Heaven's Plaza) and three wings played in any order,
# each with more than one way through and a lever at its end that sinks one of the three doors of the great gate. The
# route itself is area4_layout.py (checked jump by jump there; see its header for what is where); this places it, with
# the gimmicks of areas 1-3: vanishing clouds, wind and updrafts, moving islands, the sun, spinning gears, red and
# blue switch blocks, flipping floors, gondolas, cage traps, the speed item, the time rewind area, pressure plate
# stones, flame jets, the heaven-or-hell birdcages, ledge-grab climbs, fading steps, crumbling floors, pistons.
# Three checkpoint flags, five star coins. Behind the last door: the goal spot (a placeholder for the ending).
# Everything placed here is labelled "A4 ..." and rebuilt on every run; the placeholder's actors go too. Run
# setup_area4_assets.py first. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\build_area4_heaven.py -unattended -nop4 -nosplash -stdout
import math
import os
import random
import sys

import unreal

sys.path.insert(0, os.path.join(os.path.abspath(unreal.Paths.project_dir()), "Scripts"))
import area4_layout  # noqa: E402

LEVEL = "/Game/LV_Area4_Heaven"
AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
SKY = "/Game/ThirdPerson/Blueprints/Gimmicks/Sky"
MACHINE = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine"
HEAVEN = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
GIMMICKS = "/Game/ThirdPerson/Blueprints/Gimmicks"
HELL = GIMMICKS + "/Hell"
ITEMS = "/Game/ThirdPerson/Item"
COIN = "/Game/ThirdPerson/Coin/StarCoin/BP_StarCoin"
CAGE_DOOR = "/Game/Prototype/Birdcage/BP_BirdcageDoor_Blender"
GAME_MODE = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode"
FALLBACK_CHARACTER = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"
SPHERE = "/Engine/BasicShapes/Sphere"
PREFIX = "A4 "
B = 22610.0                    # area 3's gate: this area's plaza
MIST = B - 1800.0              # the sea of mist far below

library = unreal.EditorAssetLibrary
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def bp_class(path):
    asset = unreal.load_asset(path)
    if not asset:
        raise RuntimeError("Missing " + path)
    return asset.generated_class()


def load(path):
    asset = unreal.load_asset(path)
    if not asset:
        raise RuntimeError("Missing " + path + " (run setup_area4_assets.py first)")
    return asset


def player_defaults():
    pawn_class = None
    try:
        pawn_class = unreal.get_default_object(unreal.load_asset(GAME_MODE).generated_class()).get_editor_property("default_pawn_class")
    except Exception as error:
        lines.append("game mode pawn not read: {}".format(error))
    if pawn_class is None:
        pawn_class = unreal.load_asset(FALLBACK_CHARACTER).generated_class()
    return unreal.get_default_object(pawn_class)


def elevator_half():
    source = unreal.load_asset(GIMMICKS + "/BP_Elevator")
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(source):
        component = data_library.get_object(data_library.get_data(handle))
        if isinstance(component, unreal.StaticMeshComponent):
            scale = component.get_editor_property("relative_scale3d")
            extent = component.get_editor_property("static_mesh").get_bounds().box_extent
            return unreal.Vector(extent.x * scale.x, extent.y * scale.y, extent.z * scale.z)
    raise RuntimeError("No floor in BP_Elevator")


# ----- the level -----
if library.does_asset_exist(LEVEL):
    if not level_subsystem.load_level(LEVEL):
        raise RuntimeError("Could not open " + LEVEL)
    for actor in actors.get_all_level_actors():
        label = actor.get_actor_label()
        if label.startswith(PREFIX) or label in ("PlayerStart", "Sun", "Sky Light", "Sky Atmosphere", "Effekseer System"):
            actors.destroy_actor(actor)
else:
    if not level_subsystem.new_level(LEVEL, False):
        raise RuntimeError("Could not create " + LEVEL)

# The flipping floor's size and where its top is, measured on a spawned one.
probe = actors.spawn_actor_from_class(bp_class(GIMMICKS + "/BP_RotatingFloor"), unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0))
origin, extent = probe.get_actor_bounds(False)
ROT_SIZE = 2.0 * min(extent.x, extent.y)
ROT_TOP = origin.z + extent.z
actors.destroy_actor(probe)
lines.append("flipping floor {:.0f} across, top {:.0f} above its origin".format(ROT_SIZE, ROT_TOP))

move = player_defaults().get_editor_property("character_movement")
PLAT = elevator_half()
route = area4_layout.build(B, move.get_editor_property("jump_z_velocity"), 980.0 * move.get_editor_property("gravity_scale"),
                           move.get_editor_property("max_walk_speed"), 2.0 * PLAT.x, ROT_SIZE)
lines.append("jump {:.0f}, walk {:.0f}, platform {:.0f}".format(move.get_editor_property("jump_z_velocity"), move.get_editor_property("max_walk_speed"), 2.0 * PLAT.x))

CLOUD_MESH = load(SKY + "/SM_SkyCloud")
ISLAND_MESH = load(SKY + "/SM_SkyIsland")
CLOUD_WHITE = load(SKY + "/MI_SkyCloud")
GOLD = load(SKY + "/MI_SkyGold")
LOOKS = {
    "marble": load(HEAVEN + "/MI_HeavenMarble"), "gold": GOLD, "stone": load(HEAVEN + "/MI_HeavenStone"),
    "darkstone": load(HEAVEN + "/MI_HeavenDarkStone"), "sky": load(HEAVEN + "/MI_HeavenSky"),
    "ember": load(AREA + "/MI_RuinsEmber"), "glow": load(HEAVEN + "/MI_HeavenGlow"),
}
SHAFT = load(HEAVEN + "/MI_LightShaft")
RED_SOLID, BLUE_SOLID = load(MACHINE + "/MI_SwitchRed"), load(MACHINE + "/MI_SwitchBlue")
RED_GHOST, BLUE_GHOST = load(MACHINE + "/MI_SwitchGhostRed"), load(MACHINE + "/MI_SwitchGhostBlue")
IRON = load(MACHINE + "/MI_MachineIron")

counter = [0]
folder = ["Sky"]


def spawn(actor_class, location, name, rotation=None):
    actor = actors.spawn_actor_from_class(actor_class, location, rotation or unreal.Rotator(0.0, 0.0, 0.0))
    if not actor:
        raise RuntimeError("Could not spawn " + name)
    counter[0] += 1
    actor.set_actor_label("{}{:03d} {}".format(PREFIX, counter[0], name))
    actor.set_folder_path("Area4/" + folder[0])
    return actor


def yaw(degrees):
    return unreal.Rotator(roll=0.0, pitch=0.0, yaw=degrees)


def mesh_actor(mesh, location, scale, name, material=None, collide=True, rotation=None, shadow=True):
    actor = spawn(unreal.StaticMeshActor, location, name, rotation)
    component = actor.get_editor_property("static_mesh_component")
    component.set_static_mesh(mesh)
    if material:
        for slot in range(max(1, component.get_num_materials())):
            component.set_material(slot, material)
    if not collide:
        component.set_collision_profile_name("NoCollision")
    if not collide or not shadow:
        component.set_editor_property("cast_shadow", False)
    actor.set_actor_scale3d(scale)
    return actor


def box(x0, x1, y0, y1, z0, z1, name, material, mesh=CUBE, collide=True):
    return mesh_actor(unreal.load_asset(mesh), unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0),
                      unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0), name, material, collide)


def configure(actor, settings):
    for key, value in settings:
        actor.set_editor_property(key, value)
    return actor


def text(x, y, z, facing, words, size=60.0):
    actor = spawn(unreal.TextRenderActor, unreal.Vector(x, y, z), "Sign", yaw(facing))
    render = actor.get_editor_property("text_render")
    render.set_text(unreal.Text(words))
    render.set_editor_property("world_size", size)
    render.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    return actor


def lamp(x, y, z, color, strength=5000.0, radius=1800.0):
    mesh_actor(unreal.load_asset(SPHERE), unreal.Vector(x, y, z), unreal.Vector(0.3, 0.3, 0.3), "Lamp", LOOKS["glow"], collide=False)
    light = spawn(unreal.PointLight, unreal.Vector(x, y, z), "Lamp Light")
    component = light.get_editor_property("point_light_component")
    component.set_editor_property("intensity", strength)
    component.set_editor_property("attenuation_radius", radius)
    component.set_editor_property("light_color", unreal.Color(r=color[0], g=color[1], b=color[2], a=255))
    component.set_editor_property("cast_shadows", False)


def shaft(x, y, z_top, z_bottom, radius):
    length = z_top - z_bottom
    mesh_actor(unreal.load_asset(CYLINDER), unreal.Vector(x, y, (z_top + z_bottom) / 2.0),
               unreal.Vector(2.0 * radius / 100.0, 2.0 * radius / 100.0, length / 100.0), "Light Shaft", SHAFT, collide=False)
    light = spawn(unreal.SpotLight, unreal.Vector(x, y, z_top - 20.0), "Shaft Light", unreal.Rotator(roll=0.0, pitch=-90.0, yaw=0.0))
    component = light.get_editor_property("spot_light_component")
    component.set_editor_property("intensity", 60000.0)
    component.set_editor_property("attenuation_radius", length + 400.0)
    cone = math.degrees(math.atan2(1.6 * radius, length))
    component.set_editor_property("outer_cone_angle", max(cone, 4.0))
    component.set_editor_property("inner_cone_angle", max(cone * 0.5, 2.0))
    component.set_editor_property("light_color", unreal.Color(r=255, g=236, b=200, a=255))
    component.set_editor_property("cast_shadows", False)


def platform(class_path, x, y, top, name, settings=()):
    actor = spawn(bp_class(class_path), unreal.Vector(x, y, top - PLAT.z), name)
    return configure(actor, settings)


# ----- first: the named spots and the levers, which other pieces point at -----
folder[0] = "Spots"
spots = {}
spot_points = {}
for piece in route.pieces:
    if piece[0] == "spot":
        _, name, x, y, top = piece
        spots[name] = unreal.Vector(x, y, top + 100.0)
        spot_points[name] = spawn(unreal.TargetPoint, spots[name], "Respawn " + name)
START = spots["start"]
levers = {}
cameras = {}
section = "Spots"
for piece in route.pieces:
    if piece[0] == "section":
        section = piece[1]
    elif piece[0] == "lever":
        _, name, x, y, top, facing, reset = piece
        folder[0] = section
        lever = spawn(bp_class(AREA + "/BP_Lever"), unreal.Vector(x, y, top), "Pressure Plate" if reset else "Lever " + name, yaw(facing))
        if reset:
            for component in lever.get_components_by_class(unreal.StaticMeshComponent):
                part = component.get_name()
                if part.startswith("Handle") or part.startswith("Knob"):
                    component.set_visibility(False, False)
                    component.set_hidden_in_game(True, False)
                    component.set_collision_profile_name("NoCollision")
                elif part.startswith("Base"):
                    component.set_editor_property("relative_scale3d", unreal.Vector(1.8, 1.8, 0.06))
                    component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 3.0))
                    component.set_material(0, LOOKS["ember"])
            for component in lever.get_components_by_class(unreal.BoxComponent):
                component.set_editor_property("box_extent", unreal.Vector(90.0, 90.0, 40.0))
                component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 40.0))
            lever.set_editor_property("ShowCamera", None)
            lever.set_editor_property("ResetAfter", reset)
        levers[name] = lever

# ----- everything else -----
coins = 0
for piece in route.pieces:
    kind = piece[0]
    if kind == "section":
        folder[0] = piece[1]
    elif kind in ("spot", "lever"):
        pass
    elif kind == "start":
        _, x, y, top, facing = piece
        spawn(unreal.PlayerStart, unreal.Vector(x, y, top + 100.0), "PlayerStart", yaw(facing))
        spawn(bp_class(AREA + "/BP_AreaStart"), unreal.Vector(x + 300.0, y, top + 200.0), "Area Start")
        spawn(bp_class("/Effekseer/BluePrints/BP_EffekseerSystem"), unreal.Vector(0.0, 0.0, 0.0), "Effekseer System")
    elif kind == "block":
        _, x0, x1, y0, y1, z0, z1, look, name = piece
        box(x0, x1, y0, y1, z0, z1, name, LOOKS[look])
    elif kind == "glass":
        _, x0, x1, y0, y1, z0, z1 = piece
        pane = box(x0, x1, y0, y1, z0, z1, "Glass", SHAFT)
        pane.set_actor_hidden_in_game(True)
        pane.get_editor_property("static_mesh_component").set_editor_property("cast_shadow", False)
    elif kind == "disk":
        _, x, y, top, r, thick, look, name = piece
        mesh_actor(unreal.load_asset(CYLINDER), unreal.Vector(x, y, top - thick / 2.0), unreal.Vector(2.0 * r / 100.0, 2.0 * r / 100.0, thick / 100.0), name, LOOKS[look])
    elif kind == "island_deco":
        _, x, y, top, size = piece
        mesh_actor(ISLAND_MESH, unreal.Vector(x, y, top), unreal.Vector(size / 100.0, size / 100.0, size / 100.0 * 0.5), "Plaza Rock", collide=False)
    elif kind == "island":
        _, x, y, top, size = piece
        mesh_actor(ISLAND_MESH, unreal.Vector(x, y, top), unreal.Vector(size / 100.0, size / 100.0, size / 100.0 * 0.7), "Island")
    elif kind == "cloud":
        _, x, y, top, size = piece
        mesh_actor(CLOUD_MESH, unreal.Vector(x, y, top), unreal.Vector(size / 100.0, size / 100.0, 1.2), "Cloud")
    elif kind == "vanish":
        _, x, y, top, size, stay, gone = piece
        actor = spawn(bp_class(SKY + "/BP_VanishCloud"), unreal.Vector(x, y, top), "Vanishing Cloud")
        actor.set_actor_scale3d(unreal.Vector(size / 100.0, size / 100.0, 1.0))
        configure(actor, (("StaySeconds", stay), ("GoneSeconds", gone)))
    elif kind == "mover":
        _, x, y, top, offset, seconds, wait = piece
        actor = spawn(bp_class(SKY + "/BP_MovingIsland"), unreal.Vector(x, y, top), "Moving Island")
        configure(actor, (("MoveOffset", unreal.Vector(*offset)), ("MoveSeconds", seconds), ("WaitSeconds", wait)))
    elif kind == "moving":
        _, x, y, top, offset, seconds, wait = piece
        platform(GIMMICKS + "/BP_MovingPlatform", x, y, top, "Piston" if offset[2] else "Moving Platform",
                 (("MoveOffset", unreal.Vector(*offset)), ("MoveSeconds", seconds), ("WaitSeconds", wait)))
    elif kind == "timed":
        _, x, y, top, delay = piece
        platform(GIMMICKS + "/BP_TimedPlatform", x, y, top, "Fading Step",
                 (("VisibleSeconds", 1.8), ("HiddenSeconds", 1.2), ("FadeSeconds", 0.4), ("StartDelay", delay)))
    elif kind == "falling":
        _, x, y, top = piece
        platform(GIMMICKS + "/BP_FallingFloor", x, y, top, "Crumbling Floor")
    elif kind == "rotating":
        _, x, y, top = piece
        spawn(bp_class(GIMMICKS + "/BP_RotatingFloor"), unreal.Vector(x, y, top - ROT_TOP), "Flipping Floor")
    elif kind == "marble":
        _, x0, x1, y0, y1, top, thick = piece
        box(x0, x1, y0, y1, top - thick, top, "Marble", LOOKS["marble"])
    elif kind == "wind":
        _, x, y, z, along, width, height, facing, pitch, strength, max_speed, on, off, delay = piece
        actor = spawn(bp_class(SKY + "/BP_WindZone"), unreal.Vector(x, y, z), "Updraft" if pitch else "Wind",
                      unreal.Rotator(roll=0.0, pitch=pitch, yaw=facing))
        actor.set_actor_scale3d(unreal.Vector(along / 100.0, width / 100.0, height / 100.0))
        configure(actor, (("Strength", strength), ("MaxSpeed", max_speed), ("GustOn", on), ("GustOff", off), ("StartDelay", delay)))
    elif kind == "gear":
        _, x, y, top, r, spin = piece
        actor = spawn(bp_class(MACHINE + "/BP_SpinGear"), unreal.Vector(x, y, top - 15.0), "Spinning Gear")
        actor.set_actor_scale3d(unreal.Vector(r / 100.0, r / 100.0, 1.0))
        actor.set_editor_property("SpinSpeed", spin)
        box(x - 18.0, x + 18.0, y - 18.0, y + 18.0, top - 1500.0, top - 40.0, "Axle", IRON, CYLINDER)
    elif kind == "sblock":
        _, x, y, top, size, red = piece
        thick = 60.0
        actor = spawn(bp_class(MACHINE + "/BP_SwitchBlock"), unreal.Vector(x, y, top - thick / 2.0), "Red Block" if red else "Blue Block")
        actor.set_actor_scale3d(unreal.Vector(size / 100.0, size / 100.0, thick / 100.0))
        actor.set_editor_property("IsRed", red)
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            solid = component.get_name().startswith("Solid")
            component.set_material(0, (RED_SOLID if red else BLUE_SOLID) if solid else (RED_GHOST if red else BLUE_GHOST))
    elif kind == "switch":
        _, x, y, top = piece
        spawn(bp_class(MACHINE + "/BP_ToggleSwitch"), unreal.Vector(x, y, top), "Switch")
    elif kind == "gondola":
        _, x, y, top, offset, seconds = piece
        actor = spawn(bp_class(MACHINE + "/BP_Gondola"), unreal.Vector(x, y, top), "Gondola")
        configure(actor, (("TravelOffset", unreal.Vector(*offset)), ("TravelSeconds", seconds), ("WaitSeconds", 2.5)))
        hang, reach = 440.0, 600.0
        length = math.sqrt(sum(c * c for c in offset))
        ux, uy, uz = offset[0] / length, offset[1] / length, offset[2] / length
        a = unreal.Vector(x - ux * reach, y - uy * reach, top + hang - uz * reach)
        b = unreal.Vector(x + offset[0] + ux * reach, y + offset[1] + uy * reach, top + offset[2] + hang + uz * reach)
        d = unreal.Vector(b.x - a.x, b.y - a.y, b.z - a.z)
        cable = mesh_actor(unreal.load_asset(CYLINDER), unreal.Vector((a.x + b.x) / 2.0, (a.y + b.y) / 2.0, (a.z + b.z) / 2.0),
                           unreal.Vector(0.08, 0.08, math.sqrt(d.x * d.x + d.y * d.y + d.z * d.z) / 100.0), "Cable", IRON,
                           collide=False, rotation=unreal.MathLibrary.make_rot_from_z(d))
    elif kind == "flame":
        _, x, y, top, facing, delay, warn, burn, off, respawn = piece
        actor = spawn(bp_class(HELL + "/BP_FlameJet"), unreal.Vector(x, y, top), "Flame Jet", yaw(facing))
        configure(actor, (("StartDelay", delay), ("WarnSeconds", warn), ("BurnSeconds", burn), ("OffSeconds", off), ("RespawnLocation", spots[respawn])))
    elif kind == "sun":
        _, x, y, top, respawn = piece
        actor = spawn(bp_class(GIMMICKS + "/Sun/BP_Sun"), unreal.Vector(x, y, top), "Sun")
        actor.set_editor_property("RespawnPoint", spot_points[respawn])
    elif kind == "rewind":
        _, x, y, top = piece
        actor = spawn(bp_class(GIMMICKS + "/BP_TimeRewindArea"), unreal.Vector(x, y, top), "Time Rewind Area")
        configure(actor, (("CountSeconds", 3.0), ("CooldownSeconds", 10.0), ("NightSunPitch", 15.0), ("NightBlendSpeed", 1.0), ("TextHeight", 140.0)))
    elif kind == "cages":
        _, x, y, top, dest, pair_id = piece
        target = spawn(unreal.TargetPoint, unreal.Vector(*dest), "Cage Destination")
        cage_class = bp_class(CAGE_DOOR)
        cage_a = spawn(cage_class, unreal.Vector(x - 300.0, y, top), "Choice Cage A")
        cage_b = spawn(cage_class, unreal.Vector(x + 300.0, y, top), "Choice Cage B")
        for cage in (cage_a, cage_b):
            cage.set_editor_property("Destination", target)
        pair = spawn(bp_class(HELL + "/BP_CagePair"), unreal.Vector(x, y, top + 150.0), "Cage Pair")
        configure(pair, (("CageA", cage_a), ("CageB", cage_b), ("PairId", pair_id)))
    elif kind == "speed":
        _, x, y, top = piece
        spawn(bp_class(ITEMS + "/BP_Item"), unreal.Vector(x, y, top + 100.0), "Speed Item")
    elif kind == "coin":
        _, x, y, top = piece
        spawn(bp_class(COIN), unreal.Vector(x, y, top + 100.0), "Star Coin")
        coins += 1
    elif kind == "flag":
        _, x, y, top = piece
        spawn(bp_class(ITEMS + "/Checkpoint/BP_CheckpointItem"), unreal.Vector(x, y, top + 100.0), "Checkpoint Item")
    elif kind == "trap":
        _, x0, x1, y0, y1, top = piece
        actor = spawn(bp_class(MACHINE + "/BP_CageTrap"), unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, top), "Cage Trap")
        for component in actor.get_components_by_class(unreal.BoxComponent):
            component.set_editor_property("box_extent", unreal.Vector((x1 - x0) / 2.0, (y1 - y0) / 2.0, 100.0))
        configure(actor, (("RespawnLocation", START), ("RespawnYaw", 90.0)))
    elif kind == "lure":
        _, x, y, top = piece
        box(x - 50.0, x + 50.0, y - 50.0, y + 50.0, top, top + 70.0, "Gold Pedestal", GOLD)
        mesh_actor(unreal.load_asset(SPHERE), unreal.Vector(x, y, top + 70.0), unreal.Vector(0.6, 0.6, 0.6), "Gold Ball", GOLD)
    elif kind in ("mech", "door"):
        if kind == "door":
            _, lever_name, x, y, size, look = piece
            top, offset, delay, seconds, back, name = B + size[2], (0.0, 0.0, -size[2] - 50.0), 1.0, 3.0, None, "Gate Door"
        else:
            _, lever_name, x, y, top, size, offset, delay, seconds, back, look, name = piece
        actor = spawn(bp_class(AREA + "/BP_Mechanism"), unreal.Vector(x, y, top), name)
        actor.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
        configure(actor, (("Lever", levers[lever_name]), ("MoveOffset", unreal.Vector(*offset)), ("StartDelay", delay),
                          ("Duration", seconds), ("Returns", back is not None)))
        if back:
            configure(actor, (("ReturnAfter", back[0]), ("ReturnSeconds", back[1])))
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            component.set_material(0, LOOKS[look])
    elif kind == "camera":
        _, lever_name, eye, look_at, seconds = piece
        eye_v, look_v = unreal.Vector(*eye), unreal.Vector(*look_at)
        camera = spawn(unreal.CameraActor, eye_v, "Show Camera " + lever_name, unreal.MathLibrary.find_look_at_rotation(eye_v, look_v))
        camera.get_editor_property("camera_component").set_editor_property("constrain_aspect_ratio", False)
        configure(levers[lever_name], (("ShowCamera", camera), ("ShowSeconds", seconds)))
    elif kind == "shaft":
        _, x, y, z_top, z_bottom, r = piece
        shaft(x, y, z_top, z_bottom, r)
    elif kind == "lamp":
        _, x, y, z, color = piece
        lamp(x, y, z, color)
    elif kind == "sign":
        _, x, y, z, facing, words = piece
        text(x, y, z, facing, words)
    elif kind == "goal":
        _, x, y, top = piece
        spawn(unreal.TargetPoint, unreal.Vector(x, y, top + 100.0), "Goal Spot")
        text(x, y + 400.0, top + 500.0, -90.0, "GOAL  (coming soon)", 80.0)
    elif kind == "catcher":
        _, x0, x1, y0, y1, z = piece
        catcher = spawn(bp_class(MACHINE + "/BP_FallCatcher"), unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, z), "Fall Catcher")
        catcher.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, 4.0))
    else:
        raise RuntimeError("Unknown piece " + kind)

# ===== sky: bright heaven above a sea of mist =====
folder[0] = "Sky"
sun = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, B + 9000.0), "Sun", unreal.Rotator(roll=0.0, pitch=-62.0, yaw=115.0))
sun_light = sun.get_editor_property("directional_light_component")
sun_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
sun_light.set_editor_property("intensity", 10.0)
sun_light.set_editor_property("light_color", unreal.Color(r=255, g=244, b=222, a=255))
sun_light.set_editor_property("atmosphere_sun_light", True)
try:
    sun_light.set_editor_property("volumetric_scattering_intensity", 2.0)
except Exception as error:
    lines.append("sun scattering not set: {}".format(error))
sky = spawn(unreal.SkyLight, unreal.Vector(0.0, 0.0, B + 9000.0), "Sky Light")
sky_light = sky.get_editor_property("light_component")
sky_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
sky_light.set_editor_property("real_time_capture", True)
sky_light.set_editor_property("intensity", 1.5)
spawn(unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0), "Sky Atmosphere")
fog = spawn(unreal.ExponentialHeightFog, unreal.Vector(0.0, 0.0, MIST), "Mist")
fog_component = fog.get_editor_property("component")
fog_component.set_editor_property("fog_density", 0.04)
fog_component.set_editor_property("fog_height_falloff", 0.003)
fog_component.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(1.0, 0.95, 0.85, 1.0))
try:
    fog_component.set_editor_property("enable_volumetric_fog", True)
    fog_component.set_editor_property("volumetric_fog_scattering_distribution", 0.6)
except Exception as error:
    lines.append("volumetric fog not set: {}".format(error))

X0, X1, Y0, Y1 = route.bounds
U0, U1, V0, V1 = route.under
rand = random.Random(4)
placed = 0
while placed < 80:
    x, y = rand.uniform(X0, X1), rand.uniform(Y0, Y1)
    size = rand.uniform(2500.0, 5000.0)
    if U0 - size / 2.0 < x < U1 + size / 2.0 and V0 - size / 2.0 < y < V1 + size / 2.0:
        continue
    mesh_actor(CLOUD_MESH, unreal.Vector(x, y, MIST + rand.uniform(-100.0, 250.0)), unreal.Vector(size / 100.0, size / 100.0, rand.uniform(6.0, 12.0)),
               "Mist Cloud", CLOUD_WHITE, collide=False, rotation=yaw(rand.uniform(0.0, 360.0)))
    placed += 1
for i in range(28):
    a = rand.uniform(0.0, 2.0 * math.pi)
    x = (X0 + X1) / 2.0 + math.cos(a) * rand.uniform(0.55, 0.75) * (X1 - X0)
    y = (Y0 + Y1) / 2.0 + math.sin(a) * rand.uniform(0.55, 0.75) * (Y1 - Y0)
    size = rand.uniform(1500.0, 3500.0)
    mesh_actor(CLOUD_MESH, unreal.Vector(x, y, rand.uniform(B, route.summit_top + 1500.0)), unreal.Vector(size / 100.0, size / 100.0, rand.uniform(4.0, 9.0)),
               "Far Cloud", CLOUD_WHITE, collide=False)
for i in range(10):
    a = rand.uniform(0.0, 2.0 * math.pi)
    d = rand.uniform(2500.0, 9000.0)
    x, y = math.cos(a) * d, math.sin(a) * d + 2000.0
    if U0 - 500.0 < x < U1 + 500.0 and V0 - 500.0 < y < V1 + 500.0:
        continue
    shaft(x, y, B + 6000.0, MIST, rand.uniform(200.0, 450.0))

for name, g, rise, limit in route.checks:
    lines.append("  {:<40} gap {:>5.0f} rise {:>6.0f} (limit {:>5.0f})".format(name, g, rise, limit))
for name, z in route.heights.items():
    lines.append("  {:<18} {:>7.0f}  ({:+.0f} from the plaza)".format(name, z, z - B))
lines.append("{} coins; {} jumps; {} actors".format(coins, len(route.checks), counter[0]))
lines.append("{} saved {}".format(LEVEL, level_subsystem.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "area4_build.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
