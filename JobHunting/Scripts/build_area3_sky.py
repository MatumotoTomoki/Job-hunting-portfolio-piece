# Builds /Game/LV_Area3_Sky, the third area: floating islands and clouds in bright daylight above a sea of mist, climbed
# from where area 2 ends (149.6 m) to about 226 m. Harder than area 2: vanishing clouds (BP_VanishCloud), wind
# (BP_WindZone: crosswind and headwind gusts, updrafts), moving islands (BP_MovingIsland), fading steps and a crumbling
# floor, two cage traps, two checkpoint flags, three star coins. The route itself is area3_layout.py (checked jump by
# jump there); this places it:
#   A Cloud Harbor     start island, a run of vanishing clouds, an island ferry
#   B Crosswind Beams  narrow marble beams with gusts from the side; a gilded trap island; star coin 1 downwind below
#                      a beam, back by clouds; flag 1
#   C Updraft Gorge    updrafts up between islands (the second gusts); star coin 2 up a narrow third one
#   D Island Chain     a rising island, a trap island, fading steps, a ferry, a vanishing cloud, a crumbling floor; flag 2
#   E Storm Stair      steps into headwind gusts; star coin 3 at the end of a beam into a steady headwind; quick clouds
#   F Cloud Stair      the summit: the lever brings fifteen clouds up out of the mist into a stair round a marble
#                      column; the gate on top leads to LV_Area4_Heaven (a placeholder, made here if missing).
# Everything placed here is labelled "A3 ..." and rebuilt on every run. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\build_area3_sky.py -unattended -nop4 -nosplash -stdout
import math
import os
import random
import sys

import unreal

sys.path.insert(0, os.path.join(os.path.abspath(unreal.Paths.project_dir()), "Scripts"))
import area3_layout  # noqa: E402

LEVEL = "/Game/LV_Area3_Sky"
NEXT_LEVEL = "/Game/LV_Area4_Heaven"
AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
SKY = "/Game/ThirdPerson/Blueprints/Gimmicks/Sky"
MACHINE = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine"
GIMMICKS = "/Game/ThirdPerson/Blueprints/Gimmicks"
ITEMS = "/Game/ThirdPerson/Item"
COIN = "/Game/ThirdPerson/Coin/StarCoin/BP_StarCoin"
GAME_MODE = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode"
FALLBACK_CHARACTER = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"
PREFIX = "A3 "
B = 14960.0                    # area 2's exit: this area's start
MIST = B - 1200.0              # the sea of mist; falling into it ends the fall

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


move = player_defaults().get_editor_property("character_movement")
PLAT = elevator_half()
route = area3_layout.build(B, move.get_editor_property("jump_z_velocity"), 980.0 * move.get_editor_property("gravity_scale"),
                           move.get_editor_property("max_walk_speed"), 2.0 * PLAT.x)
lines.append("jump {:.0f}, walk {:.0f}, platform {:.0f}".format(move.get_editor_property("jump_z_velocity"), move.get_editor_property("max_walk_speed"), 2.0 * PLAT.x))

CLOUD_MESH = unreal.load_asset(SKY + "/SM_SkyCloud")
ISLAND_MESH = unreal.load_asset(SKY + "/SM_SkyIsland")
CLOUD_WHITE = unreal.load_asset(SKY + "/MI_SkyCloud")
MARBLE = unreal.load_asset(SKY + "/MI_SkyMarble")
GOLD = unreal.load_asset(SKY + "/MI_SkyGold")

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
folder = ["Sky"]


def spawn(actor_class, location, name, rotation=None):
    actor = actors.spawn_actor_from_class(actor_class, location, rotation or unreal.Rotator(0.0, 0.0, 0.0))
    if not actor:
        raise RuntimeError("Could not spawn " + name)
    counter[0] += 1
    actor.set_actor_label("{}{:03d} {}".format(PREFIX, counter[0], name))
    actor.set_folder_path("Area3/" + folder[0])
    return actor


def mesh_actor(mesh, location, scale, name, material=None, collide=True, rotation=None):
    actor = spawn(unreal.StaticMeshActor, location, name, rotation)
    component = actor.get_editor_property("static_mesh_component")
    component.set_static_mesh(mesh)
    if material:
        component.set_material(0, material)
    if not collide:
        component.set_collision_profile_name("NoCollision")
        component.set_editor_property("cast_shadow", False)
    actor.set_actor_scale3d(scale)
    return actor


def box(x0, x1, y0, y1, z0, z1, name, material):
    return mesh_actor(unreal.load_asset(CUBE), unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0),
                      unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0), name, material)


def configure(actor, settings):
    for key, value in settings:
        actor.set_editor_property(key, value)
    return actor


START = None
lever = None
stair_steps = []
coins = 0
for piece in route.pieces:
    kind = piece[0]
    if kind == "section":
        folder[0] = piece[1]
    elif kind == "start":
        _, x, y, top = piece
        START = unreal.Vector(x, y, top + 100.0)
        spawn(unreal.PlayerStart, START, "PlayerStart")
        spawn(bp_class(AREA + "/BP_AreaStart"), unreal.Vector(x, y + 300.0, top + 200.0), "Area Start")
        spawn(bp_class("/Effekseer/BluePrints/BP_EffekseerSystem"), unreal.Vector(0.0, 0.0, 0.0), "Effekseer System")
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
    elif kind == "timed":
        _, x, y, top, delay = piece
        actor = spawn(bp_class(GIMMICKS + "/BP_TimedPlatform"), unreal.Vector(x, y, top - PLAT.z), "Fading Step")
        configure(actor, (("VisibleSeconds", 1.8), ("HiddenSeconds", 1.2), ("FadeSeconds", 0.4), ("StartDelay", delay)))
    elif kind == "falling":
        _, x, y, top = piece
        spawn(bp_class(GIMMICKS + "/BP_FallingFloor"), unreal.Vector(x, y, top - PLAT.z), "Crumbling Floor")
    elif kind == "marble":
        _, x0, x1, y0, y1, top, thick = piece
        box(x0, x1, y0, y1, top - thick, top, "Marble", MARBLE)
    elif kind == "deco":
        _, x0, x1, y0, y1, z0, z1 = piece
        box(x0, x1, y0, y1, z0, z1, "Old Gate", MARBLE)
    elif kind == "wind":
        _, x, y, z, along, width, height, yaw, pitch, strength, max_speed, on, off, delay = piece
        actor = spawn(bp_class(SKY + "/BP_WindZone"), unreal.Vector(x, y, z), "Updraft" if pitch else "Wind",
                      unreal.Rotator(roll=0.0, pitch=pitch, yaw=yaw))
        actor.set_actor_scale3d(unreal.Vector(along / 100.0, width / 100.0, height / 100.0))
        configure(actor, (("Strength", strength), ("MaxSpeed", max_speed), ("GustOn", on), ("GustOff", off), ("StartDelay", delay)))
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
        configure(actor, (("RespawnLocation", START), ("RespawnYaw", 0.0)))
    elif kind == "lure":
        # Something shiny to walk up to: a gilded pedestal with a gold ball.
        _, x, y, top = piece
        box(x - 50.0, x + 50.0, y - 50.0, y + 50.0, top, top + 70.0, "Gold Pedestal", GOLD)
        mesh_actor(unreal.load_asset("/Engine/BasicShapes/Sphere"), unreal.Vector(x, y, top + 70.0), unreal.Vector(0.6, 0.6, 0.6), "Gold Ball", GOLD)
    elif kind == "lever":
        _, x, y, top, yaw = piece
        lever = spawn(bp_class(AREA + "/BP_Lever"), unreal.Vector(x, y, top), "Lever", unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
    elif kind == "stair":
        stair_steps.append(piece)
    elif kind == "column":
        _, x, y, top, r = piece
        mesh_actor(unreal.load_asset(CYLINDER), unreal.Vector(x, y, (top + MIST) / 2.0), unreal.Vector(2.0 * r / 100.0, 2.0 * r / 100.0, (top - MIST) / 100.0), "Column", MARBLE)
        mesh_actor(unreal.load_asset(CYLINDER), unreal.Vector(x, y, top - 20.0), unreal.Vector(2.0 * (r + 40.0) / 100.0, 2.0 * (r + 40.0) / 100.0, 0.4), "Column Top", GOLD)
    elif kind == "gate":
        _, x, y, top = piece
        for side in (-1, 1):
            box(x - 60.0, x + 60.0, y + side * 250.0 - 60.0, y + side * 250.0 + 60.0, top, top + 700.0, "Gate Pillar", MARBLE)
        box(x - 80.0, x + 80.0, y - 340.0, y + 340.0, top + 700.0, top + 800.0, "Gate Lintel", GOLD)
        gate = spawn(bp_class(AREA + "/BP_AreaExit"), unreal.Vector(x, y, top), "Exit", unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
        gate.set_editor_property("NextLevel", NEXT_LEVEL.rsplit("/", 1)[1])
    else:
        raise RuntimeError("Unknown piece " + kind)

# ----- the cloud stair: each cloud starts down in the mist and rises into place, one after another -----
folder[0] = "F Cloud Stair"
FIRST, DELAY, SECONDS, RISE = 1.0, 0.25, 1.6, 1800.0
for _, x, y, top, size, index in stair_steps:
    step = spawn(bp_class(AREA + "/BP_Mechanism"), unreal.Vector(x, y, top - RISE), "Cloud Step {:02d}".format(index + 1))
    step.set_actor_scale3d(unreal.Vector(size / 100.0, size / 100.0, 1.2))
    configure(step, (("Lever", lever), ("MoveOffset", unreal.Vector(0.0, 0.0, RISE)), ("StartDelay", FIRST + DELAY * index),
                     ("Duration", SECONDS), ("Returns", False)))
    for component in step.get_components_by_class(unreal.StaticMeshComponent):
        component.set_editor_property("static_mesh", CLOUD_MESH)
        component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
        component.set_material(0, CLOUD_WHITE)
lever.set_editor_property("ShowSeconds", FIRST + DELAY * (len(stair_steps) - 1) + SECONDS + 1.0)
cx, cy = route.column
eye = unreal.Vector(cx - 2600.0, cy - 2400.0, route.summit_top + 1100.0)
look = unreal.Vector(cx, cy, route.summit_top + 700.0)
camera = spawn(unreal.CameraActor, eye, "Show Camera", unreal.MathLibrary.find_look_at_rotation(eye, look))
camera.get_editor_property("camera_component").set_editor_property("constrain_aspect_ratio", False)
lever.set_editor_property("ShowCamera", camera)

# ===== sky: bright day over a sea of mist =====
folder[0] = "Sky"
sun = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, B + 9000.0), "Sun", unreal.Rotator(roll=0.0, pitch=-50.0, yaw=130.0))
sun_light = sun.get_editor_property("directional_light_component")
sun_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
sun_light.set_editor_property("intensity", 8.0)
sun_light.set_editor_property("light_color", unreal.Color(r=255, g=246, b=230, a=255))
sun_light.set_editor_property("atmosphere_sun_light", True)
sky = spawn(unreal.SkyLight, unreal.Vector(0.0, 0.0, B + 9000.0), "Sky Light")
sky_light = sky.get_editor_property("light_component")
sky_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
sky_light.set_editor_property("real_time_capture", True)
sky_light.set_editor_property("intensity", 1.4)
spawn(unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0), "Sky Atmosphere")
fog = spawn(unreal.ExponentialHeightFog, unreal.Vector(0.0, 0.0, MIST), "Mist")
fog_component = fog.get_editor_property("component")
fog_component.set_editor_property("fog_density", 0.05)
fog_component.set_editor_property("fog_height_falloff", 0.004)
fog_component.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.85, 0.9, 1.0, 1.0))

# Where everything is, for the mist's clouds and the catcher.
xs = [p[1] for p in route.pieces if p[0] in ("island", "cloud", "vanish", "mover", "timed", "falling", "stair")]
ys = [p[2] for p in route.pieces if p[0] in ("island", "cloud", "vanish", "mover", "timed", "falling", "stair")]
X0, X1, Y0, Y1 = min(xs) - 3000.0, max(xs) + 3000.0, min(ys) - 3000.0, max(ys) + 3000.0
catcher = spawn(bp_class(MACHINE + "/BP_FallCatcher"), unreal.Vector((X0 + X1) / 2.0, (Y0 + Y1) / 2.0, MIST + 200.0), "Fall Catcher")
catcher.set_actor_scale3d(unreal.Vector((X1 - X0) / 100.0, (Y1 - Y0) / 100.0, 4.0))
# The sea of mist: big flat clouds without collision, and a few drifting ones round the route at its own height.
rand = random.Random(12)
for i in range(70):
    x, y = rand.uniform(X0, X1), rand.uniform(Y0, Y1)
    size = rand.uniform(2500.0, 5000.0)
    mesh_actor(CLOUD_MESH, unreal.Vector(x, y, MIST + rand.uniform(-100.0, 250.0)), unreal.Vector(size / 100.0, size / 100.0, rand.uniform(6.0, 12.0)),
               "Mist Cloud", CLOUD_WHITE, collide=False, rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=rand.uniform(0.0, 360.0)))
for i in range(24):
    a = rand.uniform(0.0, 2.0 * math.pi)
    x = (X0 + X1) / 2.0 + math.cos(a) * rand.uniform(0.55, 0.75) * (X1 - X0)
    y = (Y0 + Y1) / 2.0 + math.sin(a) * rand.uniform(0.55, 0.75) * (Y1 - Y0)
    size = rand.uniform(1500.0, 3500.0)
    mesh_actor(CLOUD_MESH, unreal.Vector(x, y, rand.uniform(B, route.gate_top + 1500.0)), unreal.Vector(size / 100.0, size / 100.0, rand.uniform(4.0, 9.0)),
               "Far Cloud", CLOUD_WHITE, collide=False)

for name, g, rise, limit in route.checks:
    lines.append("  {:<40} gap {:>5.0f} rise {:>5.0f} (limit {:>5.0f})".format(name, g, rise, limit))
for a, b in area3_layout.crowding(route):
    lines.append("  crowded: {} / {}".format(a, b))
lines.append("summit {:.0f}, gate {:.0f} cm; {} coins; {} actors".format(route.summit_top, route.gate_top, coins, counter[0]))
lines.append("{} saved {}".format(LEVEL, level_subsystem.save_current_level()))

# ===== the area 4 placeholder (only if there is none yet) =====
if not library.does_asset_exist(NEXT_LEVEL):
    if not level_subsystem.new_level(NEXT_LEVEL, False):
        raise RuntimeError("Could not create " + NEXT_LEVEL)
    base = route.gate_top
    floor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, base - 50.0))
    floor.set_actor_label("A4 Floor")
    floor_mesh = floor.get_editor_property("static_mesh_component")
    floor_mesh.set_static_mesh(unreal.load_asset(CUBE))
    floor_mesh.set_material(0, MARBLE)
    floor.set_actor_scale3d(unreal.Vector(30.0, 30.0, 1.0))
    actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0.0, 0.0, base + 100.0)).set_actor_label("PlayerStart")
    actors.spawn_actor_from_class(bp_class(AREA + "/BP_AreaStart"), unreal.Vector(0.0, 300.0, base + 200.0)).set_actor_label("A4 Area Start")
    actors.spawn_actor_from_class(bp_class("/Effekseer/BluePrints/BP_EffekseerSystem"), unreal.Vector(0.0, 0.0, 0.0)).set_actor_label("Effekseer System")
    light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, base + 1000.0), unreal.Rotator(roll=0.0, pitch=-60.0, yaw=30.0))
    light.set_actor_label("Sun")
    light.get_editor_property("directional_light_component").set_editor_property("atmosphere_sun_light", True)
    sky4 = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0.0, 0.0, base + 1000.0))
    sky4.set_actor_label("Sky Light")
    sky4.get_editor_property("light_component").set_editor_property("real_time_capture", True)
    sky4.get_editor_property("light_component").set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    actors.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0)).set_actor_label("Sky Atmosphere")
    label4 = actors.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(800.0, 0.0, base + 300.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
    label4.set_actor_label("A4 Label")
    render = label4.get_editor_property("text_render")
    render.set_text(unreal.Text("AREA 4 (coming soon)"))
    render.set_editor_property("world_size", 80.0)
    render.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    lines.append("{} placeholder saved {} (floor at {:.0f} cm)".format(NEXT_LEVEL, level_subsystem.save_current_level(), base))

with open(os.path.join(unreal.Paths.project_saved_dir(), "area3_build.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
